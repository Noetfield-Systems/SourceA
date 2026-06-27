#!/usr/bin/env python3
"""Build locked Forge Terminal v1.4.0 best-UI reference DOCX with embedded screenshot."""
from __future__ import annotations

import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "FORGE_TERMINAL_BEST_UI_LOCKED_v1.4.0.docx"
SCREENSHOT = ROOT / "docs" / "FORGE_TERMINAL_BEST_UI_v1.4.0_REFERENCE_SCREENSHOT.png"
IMAGE_NAME = "forge-terminal-best-ui-v1.4.0.png"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def para(text: str, bold: bool = False) -> str:
    rpr = "<w:rPr><w:b/></w:rPr>" if bold else ""
    return f"<w:p><w:r>{rpr}<w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r></w:p>"


def heading(text: str, level: int) -> str:
    style = "Heading1" if level == 1 else "Heading2"
    return (
        f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
        f'<w:r><w:t>{esc(text)}</w:t></w:r></w:p>'
    )


def bullet(text: str) -> str:
    return (
        '<w:p><w:pPr><w:pStyle w:val="ListParagraph"/></w:pPr>'
        f'<w:r><w:t>{esc(text)}</w:t></w:r></w:p>'
    )


def image_para(rel_id: str, cx: int = 5486400, cy: int = 3200400) -> str:
    return f"""<w:p>
  <w:r>
    <w:drawing>
      <wp:inline distT="0" distB="0" distL="0" distR="0">
        <wp:extent cx="{cx}" cy="{cy}"/>
        <wp:docPr id="1" name="Screenshot"/>
        <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
              <pic:nvPicPr>
                <pic:cNvPr id="0" name="{IMAGE_NAME}"/>
                <pic:cNvPicPr/>
              </pic:nvPicPr>
              <pic:blipFill>
                <a:blip r:embed="{rel_id}"/>
                <a:stretch><a:fillRect/></a:stretch>
              </pic:blipFill>
              <pic:spPr>
                <a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
                <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
              </pic:spPr>
            </pic:pic>
          </a:graphicData>
        </a:graphic>
      </wp:inline>
    </w:drawing>
  </w:r>
</w:p>"""


def build_document(image_rel_id: str) -> str:
    parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">',
        "<w:body>",
        heading("Forge Terminal — Best UI (Locked Reference v1.4.0)", 1),
        para(f"Document generated: {NOW}", bold=False),
        para(
            "FOUNDER PIN — This document freezes the ONLY approved public Forge Terminal UI. "
            "URL: https://sourcea.app/sourcea/forge/terminal",
            bold=True,
        ),
        heading("1. Reference screenshot", 2),
        para("Founder-approved layout captured 2026-06-25: living chat + Brain sidebar + Tools/Feedback."),
        image_para(image_rel_id),
        heading("2. Version pins", 2),
        bullet("Demo version: 1.4.0 (meta sourcea-forge-demo-version)"),
        bullet("CSS: sourcea-forge-terminal-demo.css?v=1.4.0"),
        bullet("JS: sourcea-forge-terminal-demo.js?v=1.4.0"),
        bullet("Brain widget: sourcea-chatbot.js"),
        heading("3. Disk source files", 2),
        bullet("SourceA-landing/green-unified/forge/terminal.html"),
        bullet("SourceA-landing/green-unified/sourcea-forge-terminal-demo.css"),
        bullet("SourceA-landing/green-unified/sourcea-forge-terminal-demo.js"),
        bullet("SourceA-landing/green-unified/sourcea-chatbot.js"),
        heading("4. Layout", 2),
        bullet("Header: SourceA + Forge Terminal · demo badge + About / Talk to human"),
        bullet("Left: What this is + try-asking chips + sign-in link"),
        bullet("Center: Living chat — founder sections, white assistant text, green send"),
        bullet("Right: ◎ Brain chatbot panel (separate from living chat)"),
        bullet("Floats: Tools + Feedback bottom-left"),
        heading("5. Design tokens", 2),
        bullet("--ft-bg #0c0e12 · --ft-surface #141820 · --ft-accent #3ecf8e"),
        bullet("Section headers #5ef0a8 · assistant text #ffffff on #1a2230"),
        heading("6. NOT this version", 2),
        bullet("NOT signin/signup/profile/workspace pages"),
        bullet("NOT Mac Forge Terminal.app IDE"),
        bullet("Do NOT add auth fields to the public demo"),
        heading("7. Founder lock", 2),
        para(
            '"This is the BEST UI — this version only." — Any redesign forks a new version doc; v1.4.0 stays frozen.',
            bold=True,
        ),
        '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>',
        "</w:body></w:document>",
    ]
    return "".join(parts)


def main() -> None:
    if not SCREENSHOT.is_file():
        raise SystemExit(f"Missing screenshot: {SCREENSHOT}")

    image_bytes = SCREENSHOT.read_bytes()
    document_xml = build_document("rId5")

    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    doc_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/""" + IMAGE_NAME + """"/>
</Relationships>"""

    styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/><w:qFormat/>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:qFormat/>
    <w:rPr><w:b/><w:sz w:val="32"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:qFormat/>
    <w:rPr><w:b/><w:sz w:val="26"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="ListParagraph">
    <w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/>
    <w:pPr><w:ind w:left="720"/></w:pPr>
  </w:style>
</w:styles>"""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document_xml)
        zf.writestr("word/_rels/document.xml.rels", doc_rels)
        zf.writestr("word/styles.xml", styles)
        zf.writestr(f"word/media/{IMAGE_NAME}", image_bytes)

    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
