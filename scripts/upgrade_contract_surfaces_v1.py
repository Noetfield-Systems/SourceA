#!/usr/bin/env python3
"""Apply steps 2–7 contract surface upgrades to SKU HTML pages."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREEN = ROOT / "sites" / "SourceA-landing" / "green-unified"

PROOF_STRIP = (
    '<div class="proof-strip wrap" role="region" aria-label="Technical proof">'
    "<p><strong>Verify in 5 minutes:</strong> "
    '<a href="/eval">Run sourcea-boot eval</a> → <code>BOOT_REPORT.json</code> logged · '
    '<a href="https://github.com/kazemnezhadsina144-dot/sourcea-boot" target="_blank" rel="noopener">Public GitHub repo</a>'
    "</p></div>"
)

BUYER_PATH = (
    '<div class="buyer-path wrap" role="navigation" aria-label="Buyer path">'
    '<p class="buyer-path-title">Buyer path</p>'
    "<ul>"
    "<li><strong>Contract SKU</strong> — {contract_line}</li>"
    '<li><strong>Enterprise OS</strong> — <a href="https://www.noetfield.com/ai-value-governance-os/">Noetfield AI Value Governance OS</a> · '
    '<a href="https://www.noetfield.com/trust-brief/intake/?interest=enterprise">Trust brief intake</a></li>'
    '<li><strong>Technical proof</strong> — <a href="https://sourcea.app/eval">sourcea.app/eval</a></li>'
    '<li><strong>Procurement</strong> — <a href="/attach/procurement-pack.html">Security &amp; data pack</a></li>'
    "</ul></div>"
)

SVG_BRAIN = """<svg class="diagram-svg" viewBox="0 0 720 160" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Operating brain control flow"><defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#7df2c2" opacity="0.7"/></marker></defs><rect x="10" y="55" width="110" height="44" rx="10" fill="#112530" stroke="#7df2c2" stroke-opacity="0.45"/><text x="65" y="82" fill="#eef6f7" font-size="12" text-anchor="middle">Definitions</text><rect x="150" y="55" width="110" height="44" rx="10" fill="#112530" stroke="#7df2c2" stroke-opacity="0.45"/><text x="205" y="82" fill="#eef6f7" font-size="12" text-anchor="middle">Policy gates</text><rect x="290" y="55" width="110" height="44" rx="10" fill="#112530" stroke="#7df2c2" stroke-opacity="0.45"/><text x="345" y="82" fill="#eef6f7" font-size="12" text-anchor="middle">Sandbox</text><rect x="430" y="55" width="110" height="44" rx="10" fill="#112530" stroke="#7df2c2" stroke-opacity="0.45"/><text x="485" y="82" fill="#eef6f7" font-size="12" text-anchor="middle">Receipts</text><rect x="570" y="55" width="110" height="44" rx="10" fill="#112530" stroke="#9bbcff" stroke-opacity="0.45"/><text x="625" y="82" fill="#eef6f7" font-size="12" text-anchor="middle">Live routing</text><line x1="120" y1="77" x2="150" y2="77" stroke="#7df2c2" stroke-opacity="0.5" marker-end="url(#arr)"/><line x1="260" y1="77" x2="290" y2="77" stroke="#7df2c2" stroke-opacity="0.5" marker-end="url(#arr)"/><line x1="400" y1="77" x2="430" y2="77" stroke="#7df2c2" stroke-opacity="0.5" marker-end="url(#arr)"/><line x1="540" y1="77" x2="570" y2="77" stroke="#7df2c2" stroke-opacity="0.5" marker-end="url(#arr)"/><path d="M625 99 Q625 130 345 130 Q65 130 65 99" fill="none" stroke="#9bbcff" stroke-opacity="0.35" stroke-dasharray="4 4"/><text x="360" y="148" fill="#9eb0b8" font-size="11" text-anchor="middle">Improvement loop</text></svg><p class="diagram-caption">Illustrative — client topology produced during Brain Audit.</p>"""

SVG_CA = """<svg class="diagram-svg" viewBox="0 0 720 180" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Canada cost-to-value control"><rect x="20" y="40" width="140" height="50" rx="10" fill="#112530" stroke="#7df2c2" stroke-opacity="0.45"/><text x="90" y="70" fill="#eef6f7" font-size="11" text-anchor="middle">Vendor spend</text><rect x="200" y="40" width="160" height="50" rx="10" fill="#112530" stroke="#7df2c2" stroke-opacity="0.45"/><text x="280" y="70" fill="#eef6f7" font-size="11" text-anchor="middle">Workflow attribution</text><rect x="400" y="40" width="140" height="50" rx="10" fill="#112530" stroke="#9bbcff" stroke-opacity="0.45"/><text x="470" y="70" fill="#eef6f7" font-size="11" text-anchor="middle">Board pack</text><rect x="200" y="110" width="200" height="44" rx="10" fill="#0d1820" stroke="#7df2c2" stroke-opacity="0.35"/><text x="300" y="137" fill="#9eb0b8" font-size="11" text-anchor="middle">PIPEDA · OSFI E-23 · AIDA-ready hooks</text><line x1="160" y1="65" x2="200" y2="65" stroke="#7df2c2" stroke-opacity="0.5"/><line x1="360" y1="65" x2="400" y2="65" stroke="#7df2c2" stroke-opacity="0.5"/><line x1="280" y1="90" x2="280" y2="110" stroke="#7df2c2" stroke-opacity="0.35"/></svg><p class="diagram-caption">Illustrative — client data flows produced during sprint intake.</p>"""

SVG_UK = """<svg class="diagram-svg" viewBox="0 0 720 180" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="UK enterprise control plane"><rect x="15" y="45" width="120" height="44" rx="10" fill="#112530" stroke="#8ec5ff" stroke-opacity="0.45"/><text x="75" y="72" fill="#eef6f7" font-size="11" text-anchor="middle">Telemetry</text><rect x="155" y="45" width="130" height="44" rx="10" fill="#112530" stroke="#8ec5ff" stroke-opacity="0.45"/><text x="220" y="72" fill="#eef6f7" font-size="11" text-anchor="middle">Identity bind</text><rect x="305" y="45" width="130" height="44" rx="10" fill="#112530" stroke="#8ec5ff" stroke-opacity="0.45"/><text x="370" y="72" fill="#eef6f7" font-size="11" text-anchor="middle">Policy gate</text><rect x="455" y="45" width="120" height="44" rx="10" fill="#112530" stroke="#8ec5ff" stroke-opacity="0.45"/><text x="515" y="72" fill="#eef6f7" font-size="11" text-anchor="middle">Execution</text><rect x="595" y="45" width="110" height="44" rx="10" fill="#112530" stroke="#7df2c2" stroke-opacity="0.45"/><text x="650" y="72" fill="#eef6f7" font-size="11" text-anchor="middle">Evidence</text><rect x="305" y="115" width="130" height="40" rx="10" fill="#0d1820" stroke="#9bbcff" stroke-opacity="0.35"/><text x="370" y="140" fill="#9eb0b8" font-size="10" text-anchor="middle">Optimization</text><line x1="135" y1="67" x2="155" y2="67" stroke="#8ec5ff" stroke-opacity="0.5"/><line x1="285" y1="67" x2="305" y2="67" stroke="#8ec5ff" stroke-opacity="0.5"/><line x1="435" y1="67" x2="455" y2="67" stroke="#8ec5ff" stroke-opacity="0.5"/><line x1="575" y1="67" x2="595" y2="67" stroke="#8ec5ff" stroke-opacity="0.5"/></svg><p class="diagram-caption">Illustrative — institution-specific topology produced during Discovery Brief.</p>"""

PAGES = {
    "operating-brain-install.html": {
        "procurement_secondary": '<a class="btn secondary" href="/attach/procurement-pack.html">Procurement pack</a>',
        "contract_line": "contract@sourcea.app on this page",
        "proof_grid": (
            '<div class="proofgrid"><div class="proofmetric"><span class="proof-label">Portable eval</span>'
            "<b>4 checks</b><span>sourcea-boot PASS/BLOCK — policy, provider, receipt freshness, queue truth. "
            '<a href="/eval">Run eval</a> · <a href="https://github.com/kazemnezhadsina144-dot/sourcea-boot" target="_blank" rel="noopener">GitHub</a></span></div>'
            '<div class="proofmetric"><span class="proof-label">Case proof</span>'
            "<b>PureFlow</b><span>Live trades operator verification — 48-hour MVP path. "
            '<a href="/sourcea/case-studies/pureflow">Case study</a> · receipt-backed delivery.</span></div></div>'
        ),
        "svg": SVG_BRAIN,
    },
    "ai-value-governance.html": {
        "procurement_secondary": '<a class="btn secondary" href="/attach/procurement-pack.html">Procurement pack</a>',
        "contract_line": "contract@sourcea.ca on this page",
        "proof_grid": (
            '<div class="proofgrid"><div class="proofmetric"><span class="proof-label">Deliverables</span>'
            "<b>6</b><span>Sprint outputs — usage map, cost-to-value taxonomy, governance rules, dashboard blueprint, 30/60/90 plan, partner path.</span></div>"
            '<div class="proofmetric"><span class="proof-label">Regulatory scope</span>'
            "<b>CA</b><span>PIPEDA · provincial privacy · OSFI E-23 alignment · AIDA-ready monitoring hooks — orientation only, not certification.</span></div></div>"
        ),
        "svg": SVG_CA,
    },
    "enterprise-ai-control-plane.html": {
        "procurement_secondary": '<a class="btn secondary" href="/attach/procurement-pack.html">Procurement pack</a>',
        "contract_line": "contract@sourcea.uk on this page",
        "proof_grid": (
            '<div class="proofgrid"><div class="proofmetric"><span class="proof-label">Architecture</span>'
            "<b>6 layers</b><span>Telemetry, attribution, policy, evidence, optimization, leadership visibility — UK-scoped control plane.</span></div>"
            '<div class="proofmetric"><span class="proof-label">Procurement</span>'
            "<b>Pack</b><span>ISO 42001 mapping, data handling, reference pilot structure — "
            '<a href="/attach/procurement-pack.html">download procurement pack</a> (educational maps).</span></div></div>'
        ),
        "svg": SVG_UK,
    },
}


def patch_nav(html: str) -> str:
    if "href=\"/attach/procurement-pack.html\">Procurement</a>" in html:
        return html
    return html.replace(
        '<a href="#proof">Proof</a>',
        '<a href="#proof">Proof</a><a href="/attach/procurement-pack.html">Procurement</a>',
        1,
    )


def patch_hero_actions(html: str, procurement_secondary: str) -> str:
    if procurement_secondary in html:
        return html
    return re.sub(
        r'(<div class="actions">.*?<a class="btn secondary" href="#[^"]+">[^<]+</a>)',
        r"\1" + procurement_secondary,
        html,
        count=1,
        flags=re.S,
    )


def patch_proof_strip(html: str) -> str:
    if "proof-strip" in html:
        return html
    return html.replace("</header>", PROOF_STRIP + "\n    </header>", 1)


def patch_buyer_path(html: str, contract_line: str) -> str:
    block = BUYER_PATH.format(contract_line=contract_line)
    if "buyer-path" in html:
        return html
    return html.replace("<footer class=\"footer\">", block + "\n  <footer class=\"footer\">", 1)


def patch_proof_section(html: str, proof_grid: str, svg: str) -> str:
    html = re.sub(
        r'<div class="proofgrid">.*?</div>\s*(?=<table class="scan-table"|</div></section>)',
        proof_grid + "\n        ",
        html,
        count=1,
        flags=re.S,
    )
    html = re.sub(
        r'<div class="diagram"[^>]*>.*?</div>\s*(?=<p class="note")',
        f'<div class="diagram" aria-label="Architecture diagram">{svg}</div>\n        ',
        html,
        count=1,
        flags=re.S,
    )
    html = html.replace("placeholder", "")
    html = html.replace("(placeholder)", "")
    return html


def main() -> None:
    for name, cfg in PAGES.items():
        path = GREEN / name
        html = path.read_text(encoding="utf-8")
        html = patch_nav(html)
        html = patch_hero_actions(html, cfg["procurement_secondary"])
        html = patch_proof_strip(html)
        html = patch_proof_section(html, cfg["proof_grid"], cfg["svg"])
        html = patch_buyer_path(html, cfg["contract_line"])
        path.write_text(html, encoding="utf-8")
        print(f"OK {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
