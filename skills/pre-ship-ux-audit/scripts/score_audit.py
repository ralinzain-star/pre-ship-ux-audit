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
}


def rule_impacts():
    """Read each rule's declared impact from rules/*.md frontmatter."""
    impacts = {}
    for path in RULES.glob("*.md"):
        if path.name.startswith("_"):
            continue
        m = re.search(r"^impact:\s*(\w+)\s*$", path.read_text(), re.M)
        if m:
            impacts[path.stem] = m.group(1).strip()
    return impacts


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


def tally(reports, impacts):
    """Score each layer and the whole audit. Overall is computed across every check,
    not as an average of layer scores: averaging would let a two-check layer outweigh
    a six-check one."""
    layers, findings = [], []
    earned = possible = verifiable = scored = 0

    for report in reports:
        l_earned = l_possible = l_scored = l_unverifiable = 0
        for check in report.get("checks", []):
            result = check.get("result")
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
            findings.append(f)

    return {
        "layers": layers,
        "findings": findings,
        "score": round(100 * earned / possible) if possible else None,
        "coverage": round(100 * verifiable / scored) if scored else None,
        "counts": {
            k: sum(1 for f in findings if f.get("severity") == k)
            for k in SEVERITY_LABEL
        },
    }


def delta(current, previous):
    if previous is None:
        return ""
    sign = "+" if current > previous else ""
    return f" ({sign}{current - previous})"


def render(result, feature, rnd, prev=None):
    crit = result["counts"]["critical"]
    verdict = (
        "🛑 **Do not ship**" if crit else "✅ **Ship**"
    )
    prev_layers = {l["layer"]: l["score"] for l in prev["layers"]} if prev else {}

    out = [f"# UX audit scorecard: {feature}", ""]
    meta = [f"Round {rnd}"] if rnd else []
    meta.append(f"{len(result['findings'])} findings across {len(result['layers'])} dimensions")
    out += ["_" + " · ".join(meta) + "_", ""]

    out += [
        f"## {verdict}",
        "",
        "| | |",
        "|---|---|",
        f"| **Score** | {result['score']}/100"
        + (delta(result["score"], prev["score"]) if prev else "")
        + " |",
        f"| **Coverage** | {result['coverage']}% of checks were verifiable |",
        f"| 🔴 Critical | {crit} |",
        f"| 🟡 Major | {result['counts']['major']} |",
        f"| 🟢 Nice to have | {result['counts']['nice_to_have']} |",
        "",
    ]

    if crit:
        out += [
            f"{crit} Critical finding(s) block this release. Downgrading to "
            "⚠️ Ship with fixes is a human decision and needs a written justification "
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
        group = [f for f in result["findings"] if f.get("severity") == key]
        if not group:
            continue
        out += [f"## {emoji} {label} ({when})", ""]
        for i, f in enumerate(group, 1):
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
                "",
            ]

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
    ap.add_argument("--previous", default=None, help="previous round's directory, for deltas")
    ap.add_argument("-o", "--output", default=None, help="write markdown here instead of stdout")
    args = ap.parse_args()

    impacts = rule_impacts()
    reports = load(args.directory)
    result = tally(reports, impacts)
    prev = tally(load(args.previous), impacts) if args.previous else None

    feature = args.feature or next(
        (r.get("feature") for r in reports if r.get("feature")), "Untitled feature"
    )
    rnd = args.round or next((r.get("round") for r in reports if r.get("round")), None)

    md = render(result, feature, rnd, prev)
    if args.output:
        Path(args.output).write_text(md)
        print(f"wrote {args.output}  ({result['score']}/100, coverage {result['coverage']}%)")
    else:
        print(md)


if __name__ == "__main__":
    main()
