#!/usr/bin/env python3
"""Convert investor/*.md to PDFs on Desktop (no pandoc required)."""
from __future__ import annotations

import re
from pathlib import Path

from fpdf import FPDF

SRC = Path(__file__).resolve().parent
OUT = Path("/Users/sinakazemnezhad/Desktop/Sina-Investor-Package-PDF")
OUT.mkdir(parents=True, exist_ok=True)

MARGIN = 18
LINE = 5.5
FONT = 10
FONT_H1 = 14
FONT_H2 = 12


def ascii_safe(s: str) -> str:
    s = (
        s.replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2192", "->")
        .replace("\u2713", "[x]")
        .replace("\u2717", "[ ]")
    )
    # Box-drawing / diagrams -> plain ASCII
    for ch in "┌┐└┘├┤┬┴┼─│▼▲◄►":
        s = s.replace(ch, " ")
    return "".join(c if ord(c) < 128 else " " for c in s)


def strip_md_line(line: str) -> str:
    line = ascii_safe(line.rstrip())
    if line.startswith("#"):
        level = len(line) - len(line.lstrip("#"))
        text = line.lstrip("#").strip()
        if level == 1:
            return f"\n{text.upper()}\n"
        if level == 2:
            return f"\n{text}\n"
        return text
    line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
    line = line.replace("**", "").replace("`", "")
    if line.startswith("|") and line.endswith("|"):
        line = line.replace("|", " ").strip()
    if line.strip() in ("---", "***"):
        return "-" * 50
    return line


def needs_unicode_font(md_path: Path, text: str) -> bool:
    if "_FA" in md_path.stem or "SPEAKER_SCRIPT_FA" in md_path.name:
        return True
    return any("\u0600" <= c <= "\u06FF" or "\u0750" <= c <= "\u077F" for c in text[:8000])


def setup_font(pdf: FPDF, unicode_mode: bool) -> tuple[str, str]:
    if unicode_mode:
        font_path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
        pdf.add_font("UnicodeFont", "", font_path)
        return "UnicodeFont", "UnicodeFont"
    return "Helvetica", "Helvetica"


def build_pdf(md_path: Path, pdf_path: Path) -> None:
    text = md_path.read_text(encoding="utf-8")
    unicode_mode = needs_unicode_font(md_path, text)
    lines = (
        [strip_md_line(ln) for ln in text.splitlines()]
        if not unicode_mode
        else text.splitlines()
    )

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=MARGIN)
    pdf.set_margins(MARGIN, MARGIN, MARGIN)
    pdf.add_page()
    body, bold = setup_font(pdf, unicode_mode)
    pdf.set_font(body, size=FONT)
    w = pdf.epw

    for raw in lines:
        line = raw.strip() if unicode_mode else ascii_safe(raw.strip())
        if not line:
            pdf.ln(LINE)
            continue
        if pdf.get_y() > 270:
            pdf.add_page()
        if not unicode_mode and raw.startswith("\n") and line == line.upper() and len(line) < 80:
            pdf.ln(4)
            pdf.set_font(bold, "B", FONT_H1)
            pdf.multi_cell(w, LINE + 1, line)
            pdf.set_font(body, size=FONT)
            continue
        if not unicode_mode and raw.startswith("\n") and len(line) < 100:
            pdf.ln(2)
            pdf.set_font(bold, "B", FONT_H2)
            pdf.multi_cell(w, LINE + 1, line)
            pdf.set_font(body, size=FONT)
            continue
        if unicode_mode and line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            line = line.lstrip("#").strip()
            if level <= 2:
                pdf.ln(3)
                pdf.set_font(body, size=FONT_H2 if level == 2 else FONT_H1)
                pdf.multi_cell(w, LINE + 1, line)
                pdf.set_font(body, size=FONT)
                continue
        if unicode_mode:
            line = line.replace("**", "").replace("`", "")
        pdf.multi_cell(w, LINE, line)

    pdf.output(str(pdf_path))


def main() -> None:
    files = sorted(SRC.glob("*.md"))
    if not files:
        raise SystemExit("No .md files found")
    for md in files:
        if md.name.startswith("_"):
            continue
        pdf = OUT / f"{md.stem}.pdf"
        print(f"  {md.name} -> {pdf.name}")
        build_pdf(md, pdf)
    print(f"\nDone: {len(list(OUT.glob('*.pdf')))} PDFs in {OUT}")


if __name__ == "__main__":
    main()
