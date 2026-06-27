#!/usr/bin/env python3
"""Render brain-os Farsi SSOT markdown → founder-readable PDF (RTL, v1.1-style layout)."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.fenced_code import FencedCodeExtension

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_SRC = ROOT / "brain-os/ssot/SOURCEA_DISK_ALIGNED_OPERATING_SSOT_FA_v1.md"
DEFAULT_OUT = ROOT / "brain-os/ssot/SOURCEA_DISK_ALIGNED_OPERATING_SSOT_FA_v1.pdf"

CSS = """
@page { size: A4; margin: 18mm 16mm 22mm 16mm; }
* { box-sizing: border-box; }
body {
  font-family: Tahoma, "Arial Unicode MS", "Geeza Pro", "Noto Sans Arabic", sans-serif;
  direction: rtl;
  text-align: right;
  color: #1a2332;
  font-size: 10.5pt;
  line-height: 1.55;
  margin: 0;
  background: #fff;
}
.cover {
  page-break-after: always;
  min-height: 250mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  background: linear-gradient(145deg, #0f172a 0%, #1e3a5f 45%, #0c4a6e 100%);
  color: #f8fafc;
  padding: 24mm 18mm;
  margin: -18mm -16mm 0;
}
.cover .eyebrow {
  letter-spacing: 0.35em;
  font-size: 9pt;
  opacity: 0.85;
  margin-bottom: 12mm;
}
.cover h1 {
  font-size: 26pt;
  font-weight: 700;
  margin: 0 0 6mm;
  line-height: 1.25;
  color: #fff;
}
.cover h2 {
  font-size: 14pt;
  font-weight: 400;
  margin: 0 0 14mm;
  color: #bae6fd;
}
.cover .meta { font-size: 10pt; opacity: 0.9; margin: 2mm 0; }
.cover .badges {
  display: flex;
  gap: 10mm;
  margin-top: 16mm;
  flex-wrap: wrap;
  justify-content: center;
}
.badge {
  border: 1px solid rgba(255,255,255,0.35);
  border-radius: 8px;
  padding: 4mm 8mm;
  min-width: 36mm;
}
.badge .val { font-size: 16pt; font-weight: 700; display: block; }
.badge .lbl { font-size: 8pt; opacity: 0.85; }
.cover .locked {
  margin-top: 14mm;
  padding: 3mm 10mm;
  border: 2px solid #38bdf8;
  border-radius: 999px;
  font-size: 9pt;
  letter-spacing: 0.2em;
}
.content { padding-top: 4mm; }
h2 {
  font-size: 14pt;
  color: #0f4c81;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 2mm;
  margin-top: 10mm;
  page-break-after: avoid;
}
h3 {
  font-size: 11.5pt;
  color: #334155;
  margin-top: 6mm;
  page-break-after: avoid;
}
p { margin: 3mm 0; }
blockquote {
  border-right: 4px solid #0ea5e9;
  margin: 4mm 0;
  padding: 3mm 5mm;
  background: #f0f9ff;
  color: #0c4a6e;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin: 4mm 0 6mm;
  font-size: 9pt;
  page-break-inside: avoid;
}
th {
  background: #0f4c81;
  color: #fff;
  padding: 2.5mm 3mm;
  text-align: right;
  font-weight: 600;
}
td {
  border: 1px solid #cbd5e1;
  padding: 2.5mm 3mm;
  vertical-align: top;
}
tr:nth-child(even) td { background: #f8fafc; }
code, pre {
  font-family: "SF Mono", Menlo, Monaco, Consolas, monospace;
  direction: ltr;
  text-align: left;
}
code {
  background: #f1f5f9;
  padding: 0.5px 4px;
  border-radius: 3px;
  font-size: 8.5pt;
  unicode-bidi: embed;
}
pre {
  background: #0f172a;
  color: #e2e8f0;
  padding: 4mm;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 8pt;
  line-height: 1.45;
  white-space: pre-wrap;
  word-break: break-word;
}
hr {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 8mm 0;
}
ul { margin: 2mm 0; padding-right: 6mm; }
li { margin: 1.5mm 0; }
.footer-note {
  margin-top: 12mm;
  padding-top: 4mm;
  border-top: 1px solid #cbd5e1;
  font-size: 8.5pt;
  color: #64748b;
  text-align: center;
}
"""


def _cover_html() -> str:
    return """
<section class="cover">
  <div class="eyebrow">SINGLE SOURCE OF TRUTH</div>
  <h1>سیستم‌عامل عامل هوشمند Source-A</h1>
  <h2>سند معماری اصلی — نسخه هم‌راستا با دیسک</h2>
  <p class="meta">نسخه ۱.۰ (FA) · Consolidated Edition · Disk + ROI</p>
  <p class="meta">Noetfield Systems Inc. · TrustField Technologies Inc.</p>
  <p class="meta">Vancouver, BC — ۲۰۲۶</p>
  <div class="badges">
    <div class="badge"><span class="val">۸۵٪</span><span class="lbl">هم‌راستایی روح معماری</span></div>
    <div class="badge"><span class="val">۱۰۰٪</span><span class="lbl">قانون عامل SSOT v3</span></div>
    <div class="badge"><span class="val">۱۰۰</span><span class="lbl">Blueprint JSON</span></div>
  </div>
  <div class="locked">LOCKED · RECEIPT-NATIVE · FOUNDER READABLE</div>
</section>
"""


def _strip_duplicate_title(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    skipped = 0
    for line in lines:
        if skipped < 3 and (line.startswith("# ") or line.strip() == "---"):
            if line.strip() == "---":
                skipped = 3
            continue
        out.append(line)
    return "\n".join(out).lstrip()


def _md_to_html(body_md: str) -> str:
    body_md = _strip_duplicate_title(body_md)
    body_md = body_md.replace("✅", '<span style="color:#059669">✓</span>')
    body_md = body_md.replace("❌", '<span style="color:#dc2626">✗</span>')
    body_md = body_md.replace("🟡", '<span style="color:#d97706">◐</span>')
    body_md = body_md.replace("⏳", '<span style="color:#6366f1">…</span>')
    return markdown.markdown(
        body_md,
        extensions=[TableExtension(), FencedCodeExtension()],
    )


def build_html(md_path: Path) -> str:
    body = md_path.read_text(encoding="utf-8")
    content = _md_to_html(body)
    content = re.sub(
        r"<em>نسخه فارسی.*?</em>",
        "",
        content,
        flags=re.DOTALL,
    )
    return f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8"/>
  <title>Source-A SSOT FA v1.0</title>
  <style>{CSS}</style>
</head>
<body>
{_cover_html()}
<main class="content">
{content}
<div class="footer-note">
Source-A · Disk-Aligned Operating SSOT FA v1.0 · brain-os/ssot/ · authored law plane
</div>
</main>
</body>
</html>
"""


def render_pdf(html: str, out_path: Path) -> None:
    from playwright.sync_api import sync_playwright

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        page.pdf(
            path=str(out_path),
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=(
                '<div style="width:100%;font-size:8px;color:#64748b;text-align:center;'
                'font-family:Tahoma;padding:0 16mm;">'
                "Source-A SSOT FA v1.0 · <span class='pageNumber'></span> / "
                "<span class='totalPages'></span></div>"
            ),
        )
        browser.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="Render Farsi SSOT MD → PDF")
    ap.add_argument("--src", type=Path, default=DEFAULT_SRC)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--html-only", type=Path, default=None, help="Optional HTML debug output")
    args = ap.parse_args()
    if not args.src.is_file():
        print(f"Missing source: {args.src}", file=sys.stderr)
        return 1
    html = build_html(args.src)
    if args.html_only:
        args.html_only.write_text(html, encoding="utf-8")
        print(f"HTML: {args.html_only}")
    render_pdf(html, args.out)
    print(f"PDF: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
