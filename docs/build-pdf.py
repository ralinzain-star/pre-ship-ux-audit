"""Render the architecture diagram to PDF.

    pip3 install svglib
    python3 docs/build-pdf.py docs/architecture-zh.html docs/architecture-zh.pdf
    python3 docs/build-pdf.py docs/architecture-en.html docs/architecture-en.pdf

把架構圖的 SVG 轉成 PDF。

SVG 用 CSS 變數與網頁字型，svglib 兩者都不懂，所以先攤平顏色、再把字型換成
系統上真的有中文字形的那幾支。兩個踩過的坑：粗體要另外註冊一支字型，否則
font-weight 會 fallback 到沒有中文的 Helvetica-Bold；等寬只能給純 ASCII 用，
Courier 沒有中文字形。
"""
import re, sys, pathlib
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

pdfmetrics.registerFont(TTFont("CJK",      "/System/Library/Fonts/STHeiti Light.ttc",  subfontIndex=0))
pdfmetrics.registerFont(TTFont("CJK-Bold", "/System/Library/Fonts/STHeiti Medium.ttc", subfontIndex=0))
pdfmetrics.registerFontFamily("CJK", normal="CJK", bold="CJK-Bold",
                              italic="CJK", boldItalic="CJK-Bold")

COLOURS = {"--paper":"#F5F7F8","--surface":"#FFFFFF","--sunk":"#EDF1F2",
           "--ink":"#12171C","--ink-2":"#3E4A55","--ink-3":"#6D7A86",
           "--line":"#DCE2E6","--line-2":"#C3CDD3","--accent":"#14666B",
           "--accent-w":"#E0EEEE","--crit":"#A8301C","--major":"#9A5406","--nice":"#0A6A42"}

def convert(html_path, pdf_path):
    src = pathlib.Path(html_path).read_text()
    svg = src[src.index("<svg "):src.index("</svg>") + 6]

    svg = re.sub(r"var\((--[a-z0-9-]+)\s*,\s*[^)]+\)", lambda m: COLOURS[m.group(1)], svg)
    svg = re.sub(r"var\((--[a-z0-9-]+)\)",             lambda m: COLOURS[m.group(1)], svg)
    svg = svg.replace("currentColor", COLOURS["--ink-2"])

    # 等寬只給純 ASCII，含中文的 mono 標籤改用中文字型
    def pick(m):
        attrs, body = m.group(1), m.group(2)
        font = "Courier" if body.isascii() else "CJK"
        return f'<text{attrs.replace(chr(34) + "m" + chr(34), chr(34) + font + chr(34))} >{body}</text>' \
            if False else f'<text{attrs} font-family="{font}">{body}</text>'
    svg = re.sub(r'<text([^>]*?)\sclass="m"([^>]*?)>(.*?)</text>',
                 lambda m: f'<text{m.group(1)}{m.group(2)} font-family='
                           f'"{"Courier" if m.group(3).isascii() else "CJK"}">{m.group(3)}</text>',
                 svg, flags=re.S)
    # svglib 不會用字型家族解析粗體，font-weight 會 fallback 到沒有中文的
    # Helvetica-Bold。直接把粗體元素指定成粗體字型，並拿掉 font-weight。
    def bold(m):
        attrs, body = m.group(1) + m.group(2), m.group(3)
        font = "Helvetica-Bold" if body.isascii() else "CJK-Bold"
        attrs = re.sub(r'\sfont-family="[^"]*"', "", attrs)
        return f'<text{attrs} font-family="{font}">{body}</text>'
    svg = re.sub(r'<text([^>]*?)\sfont-weight="600"([^>]*?)>(.*?)</text>', bold, svg, flags=re.S)

    svg = svg.replace("<svg ", '<svg font-family="CJK" ', 1)

    flat = pathlib.Path("/tmp/arch-flat.svg"); flat.write_text(svg)
    d = svg2rlg(str(flat))
    renderPDF.drawToFile(d, pdf_path)
    return round(d.width), round(d.height)

if __name__ == "__main__":
    w, h = convert(sys.argv[1], sys.argv[2])
    print(f"{sys.argv[2]}  {w} x {h} pt")
