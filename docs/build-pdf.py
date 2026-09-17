"""Render the architecture diagram to PDF.

    pip3 install svglib
    python3 docs/build-pdf.py docs/architecture-en.html docs/architecture-en.pdf

The HTML is the source. svglib understands neither CSS custom properties nor web fonts, so
the SVG is flattened first. Three things here are not obvious, and each of them fails
silently rather than raising:

1. `var(--x)` and `currentColor` resolve to nothing, so the drawing comes out unpainted.
   They are substituted for the light-theme literals.
2. reportlab's built-in CID fonts render CJK as entirely the wrong glyphs through svglib,
   so a real TrueType face is registered instead.
3. svglib does not resolve `font-weight` through `registerFontFamily`. Bold text falls back
   to Helvetica-Bold, which has no CJK glyphs, so bold labels come out as empty boxes.
   Bold elements are given a bold font by name and the weight attribute is dropped.

Points 2 and 3 only bite on a page with CJK text. They are kept because the diagram has
been bilingual before and may be again.
"""
import re
import sys
import pathlib

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

pdfmetrics.registerFont(TTFont("CJK", "/System/Library/Fonts/STHeiti Light.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont("CJK-Bold", "/System/Library/Fonts/STHeiti Medium.ttc", subfontIndex=0))
pdfmetrics.registerFontFamily("CJK", normal="CJK", bold="CJK-Bold",
                              italic="CJK", boldItalic="CJK-Bold")

COLOURS = {
    "--paper": "#F5F7F8", "--surface": "#FFFFFF", "--sunk": "#EDF1F2",
    "--ink": "#12171C", "--ink-2": "#3E4A55", "--ink-3": "#6D7A86",
    "--line": "#DCE2E6", "--line-2": "#C3CDD3",
    "--accent": "#14666B", "--accent-w": "#E0EEEE",
    "--crit": "#A8301C", "--major": "#9A5406", "--nice": "#0A6A42",
}


def flatten(svg):
    """Resolve the CSS variables, fonts and weights svglib cannot handle."""
    svg = re.sub(r"var\((--[a-z0-9-]+)\s*,\s*[^)]+\)", lambda m: COLOURS[m.group(1)], svg)
    svg = re.sub(r"var\((--[a-z0-9-]+)\)", lambda m: COLOURS[m.group(1)], svg)
    svg = svg.replace("currentColor", COLOURS["--ink-2"])

    # Monospace is only safe for ASCII: Courier carries no CJK glyphs.
    svg = re.sub(
        r'<text([^>]*?)\sclass="m"([^>]*?)>(.*?)</text>',
        lambda m: f'<text{m.group(1)}{m.group(2)} font-family='
                  f'"{"Courier" if m.group(3).isascii() else "CJK"}">{m.group(3)}</text>',
        svg, flags=re.S)

    def bold(m):
        attrs, body = m.group(1) + m.group(2), m.group(3)
        font = "Helvetica-Bold" if body.isascii() else "CJK-Bold"
        attrs = re.sub(r'\sfont-family="[^"]*"', "", attrs)
        return f'<text{attrs} font-family="{font}">{body}</text>'

    svg = re.sub(r'<text([^>]*?)\sfont-weight="600"([^>]*?)>(.*?)</text>', bold, svg, flags=re.S)
    return svg.replace("<svg ", '<svg font-family="Helvetica" ', 1)


def convert(html_path, pdf_path):
    src = pathlib.Path(html_path).read_text()
    svg = src[src.index("<svg "):src.index("</svg>") + 6]
    tmp = pathlib.Path("/tmp/architecture-flat.svg")
    tmp.write_text(flatten(svg))
    drawing = svg2rlg(str(tmp))
    renderPDF.drawToFile(drawing, pdf_path)
    tmp.unlink(missing_ok=True)
    return round(drawing.width), round(drawing.height)


if __name__ == "__main__":
    w, h = convert(sys.argv[1], sys.argv[2])
    print(f"{sys.argv[2]}  {w} x {h} pt")
