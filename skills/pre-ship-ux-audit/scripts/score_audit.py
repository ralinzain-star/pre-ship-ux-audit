#!/usr/bin/env python3
"""Aggregate auditor-agent JSON into a scorecard, a verdict, and a round-over-round delta.

Six agents running in parallel will not agree about what 100 means, and models are
unreliable at consistent weighted arithmetic. So the agents only report what they
observed, and the arithmetic happens exactly once, here.

    python3 scripts/score_audit.py <dir-of-agent-json> --feature "Name" --round 2
    python3 scripts/score_audit.py results/round-2 --previous results/round-1

See references/eval-protocol.md for the schema and the scoring rules.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / "rules"

WEIGHT = {"CRITICAL": 3, "MAJOR": 2, "NICE_TO_HAVE": 1}

# The artefact ladder. A stage is the earliest point at which ABSENCE is trustworthy:
# "the build does not do X" only means "X was not designed" from the right stage onward.
STAGES = ["spec", "static", "prototype", "build"]
STAGE_RANK = {name: i for i, name in enumerate(STAGES)}
STAGE_LABEL = {
    "spec": "a written spec, tickets or a PRD",
    "static": "a static design: Figma frames or screenshots",
    "prototype": "a clickable prototype with staged data and no backend",
    "build": "a real build on staging or production",
}
# A prototype cannot earn a ship verdict, so do not print one.
VERDICT_NOUN = {
    "spec": ("Ready to design", "Not ready to design"),
    "static": ("Ready to prototype", "Not ready to prototype"),
    "prototype": ("Ready for build handoff", "Not ready for handoff"),
    "build": ("Ship", "Do not ship"),
}
SEVERITY_LABEL = {
    "critical": ("🔴", "Critical", "must fix before ship"),
    "major": ("🟡", "Major", "fix in sprint 1 post-launch"),
    "nice_to_have": ("🟢", "Nice to have", "polish backlog"),
}
RESULT_MARK = {
    "pass": "✅ Pass",
    "fail": "❌ Fail",
    "not_verifiable": "⚠️ Not verifiable",
    "not_applicable": "➖ N/A",
    "out_of_stage": "🚧 Too early to judge",
}

# Findings resting on staged demo data describe the artefact, not the design.
EVIDENCE_CLASSES = {"design", "fidelity-artifact", "unknown"}

SEVERITY_RANK = {"nice_to_have": 0, "major": 1, "critical": 2}
# Auditors kept inventing an "out of scope" line to hand something to another owner.
# Without somewhere to put it, it landed in Nice to have and inflated the count.
OUT_OF_SCOPE = "out_of_scope"

# A finding is read by someone deciding what to fix this sprint. Length does not make it
# more convincing, it makes it easier to skip. Proof goes in `evidence`, which has no budget.
BUDGET = {"title": 100, "problem": 300, "impact": 200, "recommendation": 250,
          "fix": 70, "expected": 120, "actual": 160}
# Words that carry no signal when comparing two finding titles.
_STOP = set("""a an the and or but is are was were be been it its this that these those
of in on at to for from with without by as into over under after before during
no not nothing never any every all some one two both each other same
does do did done can cannot could will would still yet only just even
user users product system screen page button copy state states""".split())


def rule_meta():
    """Read each rule's declared impact and earliest trustworthy stage from
    rules/*.md frontmatter."""
    impacts, stages, titles = {}, {}, {}
    for path in RULES.glob("*.md"):
        if path.name.startswith("_"):
            continue
        text = path.read_text()
        m = re.search(r"^impact:\s*(\w+)\s*$", text, re.M)
        if m:
            impacts[path.stem] = m.group(1).strip()
        m = re.search(r"^title:\s*(.+?)\s*$", text, re.M)
        if m:
            titles[path.stem] = m.group(1).strip()
        m = re.search(r"^earliestStage:\s*(\w+)\s*$", text, re.M)
        if m:
            stage = m.group(1).strip()
            if stage not in STAGE_RANK:
                sys.exit(f"rule '{path.stem}': unknown earliestStage '{stage}'")
            stages[path.stem] = stage
    return impacts, stages, titles


def load(directory):
    reports = []
    for path in sorted(Path(directory).glob("*.json")):
        try:
            reports.append(json.loads(path.read_text()))
        except json.JSONDecodeError as exc:
            sys.exit(f"{path}: not valid JSON ({exc})")
    if not reports:
        sys.exit(f"{directory}: no agent JSON files found")
    return reports


def weight_for(check, impacts):
    """Weight comes from the rule file, or from an inline impact for agents
    (usability, accessibility) whose checks do not live in rules/."""
    impact = impacts.get(check["rule"]) or check.get("impact")
    if not impact:
        sys.exit(
            f"check '{check['rule']}' has no impact: it is not in rules/ and the agent "
            f"did not declare one. See references/eval-protocol.md."
        )
    impact = impact.upper().replace(" ", "_").replace("-", "_")
    if impact not in WEIGHT:
        sys.exit(f"check '{check['rule']}': unknown impact '{impact}'")
    return WEIGHT[impact]


def tally(reports, impacts, stages=None, stage=None):
    """Score each layer and the whole audit. Overall is computed across every check,
    not as an average of layer scores: averaging would let a two-check layer outweigh
    a six-check one."""
    stages = stages or {}
    rank = STAGE_RANK[stage] if stage else None
    layers, findings, deferred, fidelity, notes = [], [], [], [], []
    earned = possible = verifiable = scored = 0

    for report in reports:
        l_earned = l_possible = l_scored = l_unverifiable = 0
        for check in report.get("checks", []):
            result = check.get("result")
            # A check the artefact is too early to answer is not a failure. Scoring it
            # would measure the stage, not the design, and would make rounds run at
            # different stages incomparable.
            need = stages.get(check["rule"]) or check.get("earliestStage")
            if rank is not None and need and STAGE_RANK.get(need, 0) > rank:
                check["result"] = "out_of_stage"
                check["earliestStage"] = need
                deferred.append({**check, "layer": report.get("layer", "?")})
                continue
            if result == "out_of_stage":
                deferred.append({**check, "layer": report.get("layer", "?")})
                continue
            if result == "not_applicable":
                # An N/A with no stated reason is how a scorecard gets gamed.
                if not check.get("reason", "").strip():
                    check["result"] = result = "not_verifiable"
                    check["reason"] = "N/A claimed with no reason, scored as not verifiable"
                else:
                    continue
            if result not in RESULT_MARK:
                sys.exit(f"check '{check.get('rule')}': unknown result '{result}'")
            w = weight_for(check, impacts)
            l_possible += w
            l_scored += 1
            if result == "pass":
                l_earned += w
            if result == "not_verifiable":
                l_unverifiable += 1

        layers.append(
            {
                "layer": report.get("layer", report.get("agent", "?")),
                "agent": report.get("agent", "?"),
                "earned": l_earned,
                "possible": l_possible,
                "scored": l_scored,
                "unverifiable": l_unverifiable,
                "score": round(100 * l_earned / l_possible) if l_possible else None,
                "checks": report.get("checks", []),
            }
        )
        earned += l_earned
        possible += l_possible
        scored += l_scored
        verifiable += l_scored - l_unverifiable

        for f in report.get("findings", []):
            f.setdefault("layer", report.get("layer", "?"))
            klass = f.get("evidence_class", "unknown")
            if klass not in EVIDENCE_CLASSES:
                sys.exit(
                    f"finding '{f.get('title', '?')}': unknown evidence_class "
                    f"'{klass}'. Use one of {sorted(EVIDENCE_CLASSES)}."
                )
            # Staged demo data is a fact about the prototype, not about the design.
            if f.get("severity") == OUT_OF_SCOPE:
                notes.append(f)
            elif klass == "fidelity-artifact":
                fidelity.append(f)
            else:
                findings.append(f)

    clusters = cluster_findings(findings)
    overlong = []
    for f in findings + fidelity + notes:
        for field, cap in BUDGET.items():
            n = len(f.get(field) or "")
            if n > cap:
                overlong.append((n - cap, field, n, cap, f.get("title", "?")))
    overlong.sort(reverse=True)

    return {
        "stage": stage,
        "clusters": clusters,
        "notes": notes,
        "suspects": suspect_duplicates(findings),
        "overlong": overlong,
        "layers": layers,
        "findings": findings,
        "deferred": deferred,
        "fidelity": fidelity,
        "score": round(100 * earned / possible) if possible else None,
        "coverage": round(100 * verifiable / scored) if scored else None,
        # The headline counts DISTINCT root causes. The same defect reported by four
        # auditors is one thing to fix, and counting it four times buries the others.
        "counts": {
            k: sum(1 for c in clusters if c["severity"] == k) for k in SEVERITY_LABEL
        },
        "raw_counts": {
            k: sum(1 for f in findings if f.get("severity") == k) for k in SEVERITY_LABEL
        },
    }


def _tokens(title):
    out = set()
    for w in re.findall(r"[a-z0-9']+", (title or "").lower()):
        if len(w) > 2 and w not in _STOP:
            out.add(w)
    return out


def cluster_findings(findings):
    """Group findings that name the same root cause. Grouping is the model's job:
    the script only honours a declared `cluster` and counts what it is given."""
    groups = {}
    for i, f in enumerate(findings):
        key = f.get("cluster") or f"_solo{i}"
        groups.setdefault(key, []).append(f)
    out = []
    for key, members in groups.items():
        sev = max(
            (m.get("severity", "nice_to_have") for m in members),
            key=lambda s: SEVERITY_RANK.get(s, 0),
        )
        out.append(
            {
                "key": key,
                "severity": sev,
                "members": members,
                "title": members[0].get("title", "Untitled"),
                "declared": not key.startswith("_solo"),
            }
        )
    order = {k: i for i, k in enumerate(SEVERITY_LABEL)}
    out.sort(key=lambda c: order.get(c["severity"], 99))
    return out


def suspect_duplicates(findings, threshold=0.5):
    """Flag findings that look like the same defect but were never clustered. This
    warns, it never merges: silently folding two real defects together loses one.

    Scored by overlap coefficient, not Jaccard. Auditors write titles of very different
    lengths for the same defect, and Jaccard punishes that by inflating the union, which
    is exactly the case this needs to catch."""
    undeclared = [f for f in findings if not f.get("cluster")]
    pairs = []
    for i, a in enumerate(undeclared):
        ta = _tokens(a.get("title"))
        if len(ta) < 3:
            continue
        for b in undeclared[i + 1 :]:
            tb = _tokens(b.get("title"))
            if len(tb) < 3:
                continue
            score = len(ta & tb) / min(len(ta), len(tb))
            # Same rule cited by two auditors is corroborating evidence, not proof.
            if a.get("rule") and a.get("rule") == b.get("rule"):
                score += 0.1
            if score >= threshold:
                pairs.append((round(min(score, 1.0), 2), a, b))
    pairs.sort(key=lambda p: -p[0])
    return pairs


def _raw(result, key):
    """Show the raw finding count beside the root-cause count when they differ."""
    raw = result["raw_counts"][key]
    n = result["counts"][key]
    return f" _({raw} findings)_" if raw != n else ""


def delta(current, previous):
    if previous is None:
        return ""
    sign = "+" if current > previous else ""
    return f" ({sign}{current - previous})"


def render(result, feature, rnd, prev=None):
    crit = result["counts"]["critical"]
    stage = result.get("stage") or "build"
    ok, blocked = VERDICT_NOUN[stage]
    verdict = f"🛑 **{blocked}**" if crit else f"✅ **{ok}**"
    prev_layers = {l["layer"]: l["score"] for l in prev["layers"]} if prev else {}

    out = [f"# UX audit scorecard: {feature}", ""]
    meta = [f"Round {rnd}"] if rnd else []
    meta.append(f"{len(result['findings'])} findings across {len(result['layers'])} dimensions")
    meta.append(f"stage: {STAGE_LABEL[stage]}")
    out += ["_" + " · ".join(meta) + "_", ""]

    out += [
        f"## {verdict}",
        "",
        "| | |",
        "|---|---|",
        f"| **Score** | {result['score']}/100"
        + (delta(result["score"], prev["score"]) if prev else "")
        + " |",
        f"| **Coverage** | {result['coverage']}% of the checks this stage can answer |",
        f"| 🔴 Critical | {crit}{_raw(result, 'critical')} |",
        f"| 🟡 Major | {result['counts']['major']}{_raw(result, 'major')} |",
        f"| 🟢 Nice to have | {result['counts']['nice_to_have']}{_raw(result, 'nice_to_have')} |",
        "",
    ]
    merged = sum(len(c["members"]) - 1 for c in result["clusters"] if c["declared"])
    if merged:
        out += [
            f"Counts are distinct root causes. {merged} finding(s) were merged into one "
            "another: the same defect reported by several auditors is one thing to fix, and "
            "counting it once is what keeps the real Criticals visible.",
            "",
        ]

    if crit:
        out += [
            f"{crit} Critical finding(s) block this. Downgrading to "
            f"⚠️ {ok} with fixes is a human decision and needs a written justification "
            "per Critical: who owns the fix and when it lands.",
            "",
        ]
    if result["coverage"] is not None and result["coverage"] < 70:
        out += [
            f"⚠️ Coverage is {result['coverage']}%. Most of this feature could not be "
            "examined, usually because the states do not exist yet. Read the score as "
            "provisional: the gaps below are the real finding.",
            "",
        ]

    out += ["## By dimension", "", "| Dimension | Score | Checks | Not verifiable |", "|---|---|---|---|"]
    for l in result["layers"]:
        if l["score"] is None:
            out.append(f"| {l['layer']} | n/a | 0 | 0 |")
            continue
        d = delta(l["score"], prev_layers.get(l["layer"]))
        out.append(
            f"| {l['layer']} | {l['score']}{d} | {l['scored']} | {l['unverifiable'] or '0'} |"
        )
    out.append("")

    for key, (emoji, label, when) in SEVERITY_LABEL.items():
        group = [c for c in result["clusters"] if c["severity"] == key]
        if not group:
            continue
        out += [f"## {emoji} {label} ({when})", ""]
        for i, cl in enumerate(group, 1):
            f = cl["members"][0]
            if len(cl["members"]) > 1:
                also = "; ".join(
                    f"{m.get('layer')} · `{m.get('rule', 'n/a')}`" for m in cl["members"][1:]
                )
                f = {**f, "recommendation": f.get("recommendation", "")}
            tags = []
            if f.get("confidence") == "inferred":
                tags.append("inferred, not verified against the design")
            if f.get("recurring_from_round"):
                tags.append(f"still open from Round {f['recurring_from_round']}")
            suffix = f" _({'; '.join(tags)})_" if tags else ""
            screens = ", ".join(f.get("screens", [])) or "not specified"
            out += [
                f"{i}. **{f.get('title', 'Untitled')}**{suffix}  ",
                f"   {f.get('problem', '')} {f.get('impact', '')}  ",
                f"   → {f.get('recommendation', '')}  ",
                f"   _{f.get('layer')} · `{f.get('rule', 'n/a')}` · {screens}_",
            ]
            if len(cl["members"]) > 1:
                out.append(
                    f"   _Also reported by {len(cl['members']) - 1} other auditor(s): {also}_"
                )
            shot = next((m.get("screenshot") for m in cl["members"] if m.get("screenshot")), None)
            if shot:
                out += ["", f"   ![{f.get('title', 'screenshot')}]({shot})"]
            out.append("")

    gaps = [
        (l["layer"], c)
        for l in result["layers"]
        for c in l["checks"]
        if c.get("result") == "not_verifiable"
    ]
    if gaps:
        out += [
            "## ⚠️ Could not be checked",
            "",
            "These scored as failures because an undesigned state ships as whatever gets "
            "improvised. Each one is a gap to close, not a neutral result.",
            "",
            "| Dimension | Check | Why |",
            "|---|---|---|",
        ]
        for layer, c in gaps:
            out.append(f"| {layer} | `{c['rule']}` | {c.get('reason', 'artefact does not exist')} |")
        out.append("")

    if result.get("deferred"):
        out += [
            f"## 🚧 Too early to judge at this stage ({len(result['deferred'])})",
            "",
            f"This round ran against {STAGE_LABEL[stage]}. These checks were excluded from "
            "the score, not failed: at this stage, absence in the artefact does not mean "
            "absence in the design. Scoring them would measure the stage rather than the "
            "work, and would make this round incomparable with one run later.",
            "",
            "| Dimension | Check | Trustworthy from |",
            "|---|---|---|",
        ]
        for c in result["deferred"]:
            out.append(
                f"| {c.get('layer', '?')} | `{c['rule']}` | {c.get('earliestStage', '?')} |"
            )
        out.append("")

    if result.get("fidelity"):
        out += [
            f"## 🧪 Artefact fidelity, not design defects ({len(result['fidelity'])})",
            "",
            "Each of these was verified and is real, but the evidence rests on how the "
            "artefact was staged: seeded demo data, unwired controls, hardcoded values. "
            "They are excluded from the counts and the score. Re-test them at the next "
            "stage, and if one survives, it becomes a finding.",
            "",
        ]
        for i, f in enumerate(result["fidelity"], 1):
            out += [
                f"{i}. **{f.get('title', 'Untitled')}**  ",
                f"   {f.get('problem', '')}  ",
                f"   _{f.get('layer')} · `{f.get('rule', 'n/a')}`_",
                "",
            ]

    gaps = [c for c in result["clusters"] if c["severity"] in ("critical", "major")]
    if gaps:
        titles = result.get("rule_titles", {})
        out += [
            "## What should be true, and what is",
            "",
            "Left is the rule: what a shipped feature is supposed to do. Right is what this "
            "build does. Everything else in this report is evidence for one of these rows.",
            "",
            "| | Should be | Is |",
            "|---|---|---|",
        ]
        rank = {"critical": 0, "major": 1}
        gaps.sort(key=lambda c: (rank.get(c["severity"], 9), -len(c["members"])))
        for c in gaps:
            f = c["members"][0]
            mark = "🔴" if c["severity"] == "critical" else "🟡"
            exp = f.get("expected") or titles.get(f.get("rule", "")) or f.get("rule", "?")
            act = f.get("actual") or f.get("title", "?")
            out.append(
                f"| {mark} | {str(exp).replace('|', ' ')} | {str(act).replace('|', ' ')} |"
            )
        out.append("")

    scope = [c for c in result["clusters"] if c["severity"] in ("critical", "major")]
    if scope:
        out += [
            "## 🔧 Fix scope",
            "",
            "One row per defect, not per finding. **Closes** is how many findings that single "
            "fix retires, so a row closing four is worth scoping before a row closing one of "
            "the same severity. **Decide first** names a product question the fix cannot be "
            "specified without: those rows are blocked, not small.",
            "",
            "| | Fix | Touches | Closes | Decide first |",
            "|---|---|---|---|---|",
        ]
        rank = {"critical": 0, "major": 1}
        scope.sort(key=lambda c: (rank.get(c["severity"], 9), -len(c["members"])))
        for i, c in enumerate(scope, 1):
            f = c["members"][0]
            mark = "🔴" if c["severity"] == "critical" else "🟡"
            touches = sorted({m.get("layer", "?") for m in c["members"]})
            screens = sorted({s for m in c["members"] for s in (m.get("screens") or [])})
            where = ", ".join(screens[:2]) if screens else ", ".join(touches[:2])
            n = len(c["members"])
            closes = f"{n} finding" + ("s" if n != 1 else "")
            decide = next(
                (m["decision_needed"] for m in c["members"] if m.get("decision_needed")), ""
            )
            label = f.get("fix") or f.get("title", "?") or "?"
            title = label.replace("|", "\\|")
            out.append(
                f"| {mark} | {title} | {where.replace('|', ' ')} | {closes} | {decide} |"
            )
        out.append("")

    if result.get("notes"):
        out += [
            f"## 📋 Passed to another owner ({len(result['notes'])})",
            "",
            "Real observations that sit outside the auditor's remit. They are not scored and "
            "not counted: an auditor handing something to the right owner should not cost the "
            "team a finding.",
            "",
        ]
        for i, f in enumerate(result["notes"], 1):
            out += [
                f"{i}. {f.get('problem') or f.get('title', '')}  ",
                f"   _{f.get('layer')}_",
                "",
            ]

    if result.get("suspects"):
        out += [
            f"## 🔁 Possible duplicates, not merged ({len(result['suspects'])})",
            "",
            "These findings were never given a `cluster`, and their titles overlap enough "
            "that they may be the same defect seen by two auditors. Nothing was merged "
            "automatically: folding two real defects together loses one, and that is a "
            "judgement, not arithmetic. Read each pair and set `cluster` on both, or leave "
            "them apart deliberately.",
            "",
            "| Overlap | One | The other |",
            "|---|---|---|",
        ]
        for j, a, b in result["suspects"][:20]:
            ta = a.get("title", "?").replace("|", "\\|")
            tb = b.get("title", "?").replace("|", "\\|")
            out.append(f"| {j} | {ta} | {tb} |")
        out.append("")

    out += ["## Full checklist", "", "| Dimension | Check | Result |", "|---|---|---|"]
    for l in result["layers"]:
        for c in l["checks"]:
            note = f" · {c['reason']}" if c.get("reason") else ""
            out.append(f"| {l['layer']} | `{c['rule']}` | {RESULT_MARK[c['result']]}{note} |")
    out.append("")

    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("directory", help="directory of per-agent JSON reports")
    ap.add_argument("--feature", default=None)
    ap.add_argument("--round", default=None)
    ap.add_argument(
        "--stage",
        required=True,
        choices=STAGES,
        help="what the audit actually ran against. Required on purpose: scoring a "
             "prototype as though it were a build measures the artefact, not the design.",
    )
    ap.add_argument("--previous", default=None, help="previous round's directory, for deltas")
    ap.add_argument(
        "--previous-stage",
        default=None,
        choices=STAGES,
        help="the stage the previous round ran against, if it differs",
    )
    ap.add_argument("-o", "--output", default=None, help="write markdown here instead of stdout")
    args = ap.parse_args()

    impacts, stages, titles = rule_meta()
    reports = load(args.directory)
    result = tally(reports, impacts, stages, args.stage)
    result["rule_titles"] = titles
    prev_stage = args.previous_stage or args.stage
    prev = (
        tally(load(args.previous), impacts, stages, prev_stage) if args.previous else None
    )
    if args.previous and prev_stage != args.stage:
        print(
            f"note: comparing a '{args.stage}' round against a '{prev_stage}' one. "
            "Different stages answer different checks, so read the deltas as indicative.",
            file=sys.stderr,
        )

    feature = args.feature or next(
        (r.get("feature") for r in reports if r.get("feature")), "Untitled feature"
    )
    rnd = args.round or next((r.get("round") for r in reports if r.get("round")), None)

    missing = [
        f.get("title", "?")
        for f in result["findings"]
        if f.get("severity") in ("critical", "major") and not f.get("expected")
    ]
    if missing:
        print(
            f"\n{len(missing)} finding(s) have no `expected`, so the report falls back to the "
            f"rule's own title. That reads as a generic principle rather than a defect, which "
            f"is the main thing this table exists to avoid. Write the specific expectation:",
            file=sys.stderr,
        )
        for t in missing[:10]:
            print(f"  {t[:76]}", file=sys.stderr)
        print("", file=sys.stderr)

    if result["overlong"]:
        worst = result["overlong"]
        print(
            f"\n{len(worst)} field(s) over budget. A PM reads these four fields to decide what "
            f"to fix: put the proof in `evidence`, which has no limit, and cut the rest.",
            file=sys.stderr,
        )
        for _, field, n, cap, title in worst[:12]:
            print(f"  {field:16} {n:5} / {cap:<4} {title[:64]}", file=sys.stderr)
        if len(worst) > 12:
            print(f"  ... and {len(worst) - 12} more", file=sys.stderr)
        print("", file=sys.stderr)

    md = render(result, feature, rnd, prev)
    if args.output:
        Path(args.output).write_text(md)
        print(
            f"wrote {args.output}  ({result['score']}/100, coverage {result['coverage']}%, "
            f"stage {args.stage}, {len(result['deferred'])} deferred)"
        )
    else:
        print(md)


if __name__ == "__main__":
    main()
