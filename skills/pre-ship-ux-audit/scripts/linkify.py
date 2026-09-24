#!/usr/bin/env python3
"""Add ticket and screen links to a finished report, in any language.

`score_audit.py` links the English report as it renders it. A translated report is written
separately and would otherwise ship without links, which is how a translation quietly
becomes the worse copy. Run this over it instead of re-linking by hand.

    python3 scripts/linkify.py report-zh.md --tickets tickets.json

Idempotent: text already inside a markdown link is left alone, so running it twice is safe.
"""
import argparse, json, re, sys
from pathlib import Path

# "ticket 6.1", "票 6.1", "5.2", "5.6:", but not a version number or a decimal in prose
# A score and a ticket number are the same shape. Only cued references link: "ticket 6.1",
# "票 6.1", "5.2's", "3.6:", "7.3 says". A bare 8.1 in prose is a score, and linking it is worse
# than missing it.
TICKET = re.compile(
    r"(?:(?<=ticket )|(?<=Ticket )|(?<=票 )|(?<=票))(?P<num>\d\.\d)(?![\d.%])"
    r"|(?<![\w.\-/])(?P<num2>\d\.\d)(?=['’]s\b|:|\s+(?:AC|QA|TC|says|specifies|requires)\b)")
FR = re.compile(r"(?<![\w\-])FR-\d+\b")
# already-linked spans, so a second run does not nest links
LINKED = re.compile(r"\[[^\]]*\]\([^)]*\)")


def protect(text):
    spans, out, last = [], [], 0
    for m in LINKED.finditer(text):
        out.append((text[last:m.start()], True))
        out.append((m.group(0), False))
        last = m.end()
    out.append((text[last:], True))
    return out


def linkify(text, tickets):
    base = tickets.get("_base", "https://app.notion.com/p/")
    fr_page = tickets.get("FR")

    def one(chunk):
        def sub(m):
            num = m.group("num") or m.group("num2")
            page = tickets.get(num)
            return f"[{m.group(0)}]({base}{page})" if page else m.group(0)
        chunk = TICKET.sub(sub, chunk)
        if fr_page:
            chunk = FR.sub(lambda m: f"[{m.group(0)}]({base}{fr_page})", chunk)
        return chunk

    return "".join(one(part) if editable else part for part, editable in protect(text))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file")
    ap.add_argument("--tickets", required=True)
    ap.add_argument("-o", "--output", default=None, help="default: edit in place")
    a = ap.parse_args()
    tickets = json.loads(Path(a.tickets).read_text())
    src = Path(a.file).read_text()
    out = linkify(src, tickets)
    Path(a.output or a.file).write_text(out)
    added = out.count("](" + tickets.get("_base", "https://app.notion.com/p/")) - \
            src.count("](" + tickets.get("_base", "https://app.notion.com/p/"))
    print(f"{a.output or a.file}: {added} ticket link(s) added")
