#!/usr/bin/env python3
"""Check the skill and its agents for drift.

This system grew incrementally, and the failure mode of that is silent drift: a count
that is still "seven", a path that moved, a check id an agent invented that the scorer
cannot weight. None of it breaks loudly. It just produces a wrong report one day.

    python3 scripts/check_consistency.py

Exit code is the number of errors. Warnings do not fail.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = Path.home() / ".claude" / "agents"

errors, warnings = [], []


def err(where, msg):
    errors.append(f"ERROR {where}: {msg}")


def warn(where, msg):
    warnings.append(f"WARN  {where}: {msg}")


def rel(p):
    return str(p).replace(str(Path.home()), "~")


# ---------------------------------------------------------------- collect
rule_files = {p.stem for p in ROOT.glob("rules/*.md") if not p.name.startswith("_")}
rule_impacts = {}
for p in ROOT.glob("rules/*.md"):
    if p.name.startswith("_"):
        continue
    m = re.search(r"^impact:\s*(\w+)\s*$", p.read_text(), re.M)
    if not m:
        err(rel(p), "rule file has no `impact:` in frontmatter, score_audit cannot weight it")
    else:
        rule_impacts[p.stem] = m.group(1)
    if not re.search(r"^order:\s*\d+\s*$", p.read_text(), re.M):
        err(rel(p), "rule file has no `order:`, build_agents will sort it last")

agent_files = sorted(AGENTS.glob("ux-*.md"))
if not agent_files:
    err(rel(AGENTS), "no ux-* agent files found")

# ---------------------------------------------------------------- per agent
declared_checks = defaultdict(list)  # check id -> [agent files]
declared_layers = defaultdict(list)  # layer name -> [agent files]
for p in agent_files:
    text = p.read_text()
    name = rel(p)

    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not fm:
        err(name, "no YAML frontmatter")
        continue
    for field in ("name", "description", "color"):
        if not re.search(rf"^{field}:", fm.group(1), re.M):
            err(name, f"frontmatter missing `{field}` (lint-agents.sh requires it)")

    is_orchestrator = "orchestrator" in p.stem
    if not is_orchestrator:
        if "## Output contract" not in text:
            err(name, "auditor agent has no Output contract section, it will not return scorable JSON")
        if '"agent": "' not in text:
            err(name, "Output contract has no concrete agent id")
        else:
            aid = re.search(r'"agent": "([^"]+)"', text).group(1)
            if aid in ("AGENT_ID", ""):
                err(name, "Output contract still has the AGENT_ID placeholder")
            # the contract was copied between agents once and the substitution silently
            # no-opped, so every agent reported itself as flow-integrity and the scorer
            # merged every dimension into one. Pin the id to the filename.
            expected = p.stem.replace("ux-audit-", "").replace("ux-", "")
            if aid != expected:
                err(name, f'Output contract says `"agent": "{aid}"` but this file is '
                          f'`{p.stem}`, so its JSON would be scored as another agent')
            lay = re.search(r'"layer": "([^"]+)"', text)
            if lay:
                declared_layers[lay.group(1)].append(name)
        if "## Scoring discipline" not in text:
            warn(name, "no Scoring discipline section")

    # check ids this agent claims, from its `| \`id\` | IMPACT |` table rows
    for cid, impact in re.findall(r"^\|\s*`([a-z0-9-]+)`\s*\|\s*([A-Z_]+)\s*\|", text, re.M):
        declared_checks[cid].append((name, impact))
        if cid in rule_files:
            if rule_impacts.get(cid) != impact:
                err(name, f"check `{cid}` declares {impact} but rules/{cid}.md says {rule_impacts.get(cid)}")
        else:
            if "declare" not in text or "impact" not in text:
                err(name, f"check `{cid}` is not in rules/ and the agent never says to declare impact inline")

    # referenced paths must exist
    for path in set(re.findall(r"`?(/Users/[^\s`)]+?\.(?:md|py))`?", text)):
        if "<" in path:  # a documented placeholder such as rules/<id>.md, not a real path
            continue
        if not Path(path).exists():
            err(name, f"references a path that does not exist: {rel(Path(path))}")
    for relpath in set(re.findall(r"`((?:references|assets|scripts|rules)/[a-z_-]+\.(?:md|py))`", text)):
        if not (ROOT / relpath).exists():
            err(name, f"references missing skill file: {relpath}")

    if "—" in text:
        err(name, "contains an em-dash, which Iris has asked never to appear in her copy")

# ---------------------------------------------------------------- cross-agent
for cid, owners in declared_checks.items():
    if len({o[0] for o in owners}) > 1:
        err("cross-agent", f"check `{cid}` is claimed by more than one agent: "
                           + ", ".join(sorted({o[0] for o in owners}))
                           + " (findings would double-count)")

for layer, owners in declared_layers.items():
    if len(owners) > 1:
        err("cross-agent", f'layer "{layer}" is declared by more than one agent: '
                           + ", ".join(sorted(owners))
                           + " (their findings would collapse into one dimension)")

covered = {c for c in declared_checks if c in rule_files}
for missing in sorted(rule_files - covered):
    err("coverage", f"rules/{missing}.md is owned by no agent, so it is never checked in a scored run")

# ---------------------------------------------------------------- skill files
for f in ("SKILL.md", "README.md", "AGENTS.md", "metadata.json"):
    if not (ROOT / f).exists():
        err(rel(ROOT / f), "missing")

skill = (ROOT / "SKILL.md").read_text()
readme = (ROOT / "README.md").read_text()

n_agents = len(agent_files)
n_specialists = n_agents - 1
WORDS = {"six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
for label, text in (("SKILL.md", skill), ("README.md", readme)):
    for m in re.finditer(r"\b(%s)\b([^.,;:\n]{0,30}?)agent" % "|".join(WORDS), text, re.I):
        num = WORDS[m.group(1).lower()]
        # "ten agents" means all of them; "nine specialist agents" means the batch
        expected = n_specialists if "specialist" in m.group(2).lower() else n_agents
        if num != expected:
            err(label, f'says "{m.group(0).strip()}" but there are {n_agents} agents '
                       f"({n_specialists} specialists plus the orchestrator)")

for relpath in set(re.findall(r"`((?:references|assets|scripts|rules)/[a-z_-]+\.(?:md|py))`", skill + readme)):
    if not (ROOT / relpath).exists():
        err("SKILL/README", f"references missing file: {relpath}")

for text, label in ((skill, "SKILL.md"), (readme, "README.md")):
    if "—" in text:
        err(label, "contains an em-dash")

# every rule id named in SKILL.md quick reference must exist
for cid in set(re.findall(r"^- `([a-z]+-[a-z0-9-]+)`", skill, re.M)):
    if cid not in rule_files:
        err("SKILL.md", f"quick reference names `{cid}` but rules/{cid}.md does not exist")

meta = json.loads((ROOT / "metadata.json").read_text())
for field in ("version", "abstract", "references"):
    if field not in meta:
        err("metadata.json", f"missing `{field}`")

# ---------------------------------------------------------------- report
print(f"skill:  {rel(ROOT)}")
print(f"rules:  {len(rule_files)}")
print(f"agents: {n_agents} ({n_specialists} specialists + orchestrator)")
print(f"checks: {len(declared_checks)} declared, {len(covered)} of them backed by rule files")
print()
for line in errors + warnings:
    print(line)
print()
print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
sys.exit(len(errors))
