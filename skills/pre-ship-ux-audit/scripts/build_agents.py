#!/usr/bin/env python3
"""Compile rules/ into AGENTS.md, the single-file version of this skill.

SKILL.md is the index an agent reads first: it points at individual rule files so
only the relevant layers get loaded. AGENTS.md is the opposite trade, every rule
expanded in one document, for agents or humans that want the whole thing at once.

Run after editing any rule:  python3 scripts/build_agents.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / "rules"

IMPACT_ORDER = {"CRITICAL": 0, "MAJOR": 1, "NICE_TO_HAVE": 2}
IMPACT_LABEL = {"CRITICAL": "Critical", "MAJOR": "Major", "NICE_TO_HAVE": "Nice to have"}


def parse_frontmatter(text):
    """Return (frontmatter dict, body). Values are flat strings, which is all we use."""
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not match:
        return {}, text
    meta = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta, match.group(2).strip()


def parse_sections():
    """Read _sections.md for layer order, impact, and description."""
    text = (RULES / "_sections.md").read_text()
    pattern = re.compile(
        r"^## \d+\.\s*(?P<title>.+?)\s*\((?P<prefix>[\w-]+)\)\s*$"
        r"(?P<rest>.*?)(?=^## |\Z)",
        re.S | re.M,
    )
    sections = []
    for m in pattern.finditer(text):
        rest = m.group("rest")
        impact = re.search(r"\*\*Impact:\*\*\s*(\w+)", rest)
        desc = re.search(r"\*\*Description:\*\*\s*(.+?)(?=\n\n|\Z)", rest, re.S)
        sections.append(
            {
                "title": m.group("title"),
                "prefix": m.group("prefix"),
                "impact": impact.group(1) if impact else "MAJOR",
                "description": " ".join(desc.group(1).split()) if desc else "",
                "rules": [],
            }
        )
    return sections


def anchor(number, title):
    slug = re.sub(r"[^\w\s-]", "", f"{number} {title}".lower())
    return "#" + re.sub(r"[\s]+", "-", slug.strip())


def main():
    meta = json.loads((ROOT / "metadata.json").read_text())
    sections = parse_sections()

    for path in sorted(RULES.glob("*.md")):
        if path.name.startswith("_"):
            continue
        fm, body = parse_frontmatter(path.read_text())
        prefix = path.name.split("-")[0]
        section = next((s for s in sections if s["prefix"] == prefix), None)
        if section is None:
            raise SystemExit(f"{path.name}: prefix '{prefix}' matches no section in _sections.md")
        section["rules"].append({"meta": fm, "body": body, "file": path.name})

    for section in sections:
        # Journey order, not impact order: the auditor walks the flow in sequence,
        # and a checklist that jumps around is one people lose their place in.
        section["rules"].sort(key=lambda r: (int(r["meta"].get("order", 99)), r["file"]))

    out = [
        f"# {meta.get('abstract', '').split('.')[0]}",
        "",
        f"**Version {meta['version']}**  ",
        f"{meta['organization']}  ",
        f"{meta['date']}",
        "",
        "> **Note:**  ",
        "> This is the compiled, single-file version of the pre-ship-ux-audit skill.  ",
        "> Generated from `rules/` by `scripts/build_agents.py`. Edit the rule files,  ",
        "> not this document. `SKILL.md` is the index to read first when you only need  ",
        "> one or two layers.",
        "",
        "---",
        "",
        "## Abstract",
        "",
        meta["abstract"],
        "",
        "---",
        "",
        "## Table of Contents",
        "",
    ]

    for i, section in enumerate(sections, 1):
        out.append(
            f"{i}. [{section['title']}]({anchor(i, section['title'])}) "
            f"· **{IMPACT_LABEL.get(section['impact'], section['impact'])}**"
        )
        for j, rule in enumerate(section["rules"], 1):
            title = rule["meta"].get("title", rule["file"])
            out.append(f"   - {i}.{j} [{title}]({anchor(f'{i}{j}', title)})")
    out += ["", "---", ""]

    for i, section in enumerate(sections, 1):
        out += [
            f"## {i}. {section['title']}",
            "",
            f"**Impact: {IMPACT_LABEL.get(section['impact'], section['impact'])}**",
            "",
            section["description"],
            "",
        ]
        for j, rule in enumerate(section["rules"], 1):
            fm = rule["meta"]
            title = fm.get("title", rule["file"])
            impact = IMPACT_LABEL.get(fm.get("impact", "MAJOR"), fm.get("impact"))
            out += [
                f"### {i}.{j} {title}",
                "",
                f"**Impact: {impact} ({fm.get('impactDescription', '')})**",
                "",
                re.sub(r"^## .+\n+", "", rule["body"], count=1),
                "",
                f"_Rule file: `rules/{rule['file']}`_",
                "",
            ]

    out += [
        "---",
        "",
        "## References",
        "",
    ] + [f"- {r}" for r in meta.get("references", [])] + [""]

    (ROOT / "AGENTS.md").write_text("\n".join(out))
    total = sum(len(s["rules"]) for s in sections)
    print(f"AGENTS.md written: {total} rules across {len(sections)} layers")


if __name__ == "__main__":
    main()
