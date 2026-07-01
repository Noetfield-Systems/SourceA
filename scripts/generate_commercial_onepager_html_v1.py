#!/usr/bin/env python3
"""Generate commercial one-pager HTML (Noetfield NW1 + SourceA AB1 only). Witness BC → WitnessBC-landing/bundle_html.py"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SINA = Path.home() / ".sina"
SOURCEA = Path(__file__).resolve().parents[1]

NOETFIELD_HTML = SINA / "noetfield-pilot-onepager-external-v1.html"
AB1_HTML = SINA / "sourcea-ab1-governed-automation-onepager-v1.html"
_HTML = SINA / "sourcea--platform-onepager-v1.html"
_ARCHIVE = SOURCEA / "archive/attachments/commercial/sourcea--platform-onepager-v1.html"
LANDING_DIR = SOURCEA / "SourceA-landing"
C13_DIR = SOURCEA / "C13"

SHARED_CSS = """
:root {
  --bg: #070b12;
  --surface: #0f1623;
  --surface-2: #151d2e;
  --border: #243044;
  --text: #eef2f7;
  --muted: #8fa3bc;
  --accent: #4d9fff;
  --accent-dim: rgba(77, 159, 255, 0.12);
  --pass: #3ecf8e;
  --fail: #ff6b6b;
  --warn: #f0b429;
  --font: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --mono: ui-monospace, "SF Mono", Menlo, monospace;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  line-height: 1.55;
  font-size: 1rem;
  -webkit-font-smoothing: antialiased;
}
.wrap { max-width: 1040px; margin: 0 auto; padding: 0 1.5rem; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.topbar {
  padding: 1.25rem 0;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.brand { font-weight: 700; font-size: 1.1rem; letter-spacing: -0.02em; }
.brand span { color: var(--muted); font-weight: 500; font-size: 0.85rem; margin-left: 0.5rem; }
.pill {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  border: 1px solid var(--border);
  color: var(--muted);
  background: var(--surface);
}
.pill.accent { border-color: var(--accent); color: var(--accent); background: var(--accent-dim); }
.hero { padding: 3.5rem 0 2.5rem; }
.hero h1 {
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 700;
  line-height: 1.12;
  letter-spacing: -0.03em;
  max-width: 18ch;
}
.hero .lead {
  margin-top: 1.25rem;
  font-size: 1.15rem;
  color: var(--muted);
  max-width: 52ch;
}
.hero .quote {
  margin-top: 1.75rem;
  padding: 1.25rem 1.5rem;
  border-left: 3px solid var(--accent);
  background: var(--surface);
  border-radius: 0 10px 10px 0;
  font-size: 1.05rem;
  color: #c5d4e8;
}
.cta-row { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 2rem; }
.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.75rem 1.35rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  border: 1px solid transparent;
}
.btn-primary { background: var(--accent); color: #041018; }
.btn-primary:hover { filter: brightness(1.08); text-decoration: none; }
.btn-ghost { border-color: var(--border); color: var(--text); background: var(--surface); }
.btn-ghost:hover { border-color: var(--accent); text-decoration: none; }
.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin: 2rem 0 0;
}
@media (max-width: 720px) { .stats { grid-template-columns: 1fr; } }
.stat {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.25rem 1.35rem;
}
.stat .num { font-size: 1.75rem; font-weight: 700; letter-spacing: -0.02em; }
.stat .lbl { font-size: 0.82rem; color: var(--muted); margin-top: 0.35rem; }
section { padding: 2.75rem 0; border-top: 1px solid var(--border); }
section h2 {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--muted);
  margin-bottom: 1rem;
  font-weight: 600;
}
section h3 { font-size: 1.35rem; font-weight: 650; margin-bottom: 0.75rem; letter-spacing: -0.02em; }
.prose { color: var(--muted); max-width: 68ch; }
.prose p { margin-bottom: 0.85rem; }
.chain { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1.25rem; }
.beat {
  font-family: var(--mono);
  font-size: 0.78rem;
  padding: 0.45rem 0.7rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: #b8c9de;
}
.beat.arrow { border: none; background: none; color: var(--muted); padding: 0.45rem 0.2rem; }
.beat.pass { border-color: rgba(62, 207, 142, 0.4); color: var(--pass); }
.beat.fail { border-color: rgba(255, 107, 107, 0.4); color: var(--fail); }
.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-top: 1.25rem;
}
@media (max-width: 900px) { .grid-3 { grid-template-columns: 1fr; } }
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
}
.card.featured {
  border-color: var(--accent);
  box-shadow: 0 8px 40px rgba(77, 159, 255, 0.15);
}
.card .tier { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }
.card .price { font-size: 2rem; font-weight: 700; margin: 0.5rem 0 0.25rem; letter-spacing: -0.03em; }
.card .sub { font-size: 0.85rem; color: var(--muted); margin-bottom: 1rem; }
.card ul { list-style: none; font-size: 0.9rem; color: #b8c9de; }
.card li { padding: 0.35rem 0; padding-left: 1.1rem; position: relative; }
.card li::before { content: "✓"; position: absolute; left: 0; color: var(--pass); font-size: 0.75rem; }
.table-wrap { overflow-x: auto; margin-top: 1rem; }
table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
th, td { text-align: left; padding: 0.75rem 0.85rem; border-bottom: 1px solid var(--border); vertical-align: top; }
th { color: var(--muted); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; }
.footer {
  padding: 2.5rem 0 3rem;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 0.88rem;
}
.footer strong { color: var(--text); }
.no-print { }
@media print {
  body { background: #fff; color: #111; font-size: 10pt; }
  .wrap { max-width: 100%; }
  :root { --surface: #f8fafc; --surface-2: #f1f5f9; --border: #e2e8f0; --text: #111; --muted: #555; --accent: #2563eb; }
  .btn-primary { background: #2563eb; color: #fff; }
  .no-print { display: none !important; }
  section { break-inside: avoid; }
  .card { break-inside: avoid; }
}
"""


def _shell(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>{SHARED_CSS}</style>
</head>
<body>
{body}
</body>
</html>"""


def noetfield_html() -> str:
    body = """
<div class="wrap">
  <div class="topbar">
    <div class="brand">Noetfield <span>Copilot governance &amp; evidence</span></div>
    <span class="pill accent">Founding customer pilot · NF-RD</span>
  </div>
  <header class="hero">
    <h1>Prove what Copilot was permitted to do.</h1>
    <p class="lead">Cryptographic proof per action — policy version, signed receipt, replay, tamper detection. Built for boards and regulators who will not accept slides alone.</p>
    <blockquote class="quote">Noetfield gives your board cryptographic proof of what Microsoft Copilot was <strong>permitted</strong> to do, under which <strong>policy version</strong> — with governance receipts on <strong>every in-scope action</strong>, not a quarterly assessment.</blockquote>
    <div class="cta-row no-print">
      <a class="btn btn-primary" href="https://www.noetfield.com/copilot/pilot/">Book 15-min walkthrough</a>
      <a class="btn btn-ghost" href="https://project-gc7lm.vercel.app/copilot/demo/">Watch 5-min demo</a>
    </div>
    <div class="stats">
      <div class="stat"><div class="num">72%</div><div class="lbl">Enterprises lack formal agent governance (pitch hypothesis)</div></div>
      <div class="stat"><div class="num">5 min</div><div class="lbl">Live proof chain — block, allow, tamper-FAIL, replay</div></div>
      <div class="stat"><div class="num">Shadow</div><div class="lbl">Parallel to M365 — zero production cutover</div></div>
    </div>
  </header>

  <section>
    <h2>The problem</h2>
    <h3>Governance at session start is not enough.</h3>
    <div class="prose">
      <p>Your Copilot program is live — or your agents are in production. When something goes wrong there is no signed record of what the agent was allowed to do, what it did, or whether the log was tampered with.</p>
      <p>Noetfield governs execution <strong>before the model acts</strong>. Every in-scope action is gated by policy at dispatch, written to a signed replayable ledger, and protected by tamper detection.</p>
    </div>
    <h2 style="margin-top:1.75rem">The proof</h2>
    <div class="chain">
      <span class="beat">request</span><span class="beat arrow">→</span>
      <span class="beat">policy eval</span><span class="beat arrow">→</span>
      <span class="beat">decision</span><span class="beat arrow">→</span>
      <span class="beat">enforcement</span><span class="beat arrow">→</span>
      <span class="beat pass">signed receipt</span><span class="beat arrow">→</span>
      <span class="beat">replay</span><span class="beat arrow">→</span>
      <span class="beat fail">tamper-FAIL</span><span class="beat arrow">→</span>
      <span class="beat pass">audit chain</span>
    </div>
  </section>

  <section>
    <h2>Founding pilot</h2>
    <h3>NF-RD · CAD $5,000–$10,000</h3>
    <div class="grid-3">
      <div class="card">
        <div class="tier">Deposit</div>
        <div class="price">$2K</div>
        <div class="sub">CAD minimum to start · refunded if we miss agreed metric</div>
        <ul><li>Shadow mode only</li><li>One workflow slice</li><li>30–60 days</li></ul>
      </div>
      <div class="card featured">
        <div class="tier">NF-RD · Recommended</div>
        <div class="price">$5–10K</div>
        <div class="sub">Founding-customer band · 4–6 weeks standard</div>
        <ul>
          <li>Trust Ledger export (TLE v1)</li>
          <li>Board PDF + Procurement ZIP</li>
          <li>One success metric agreed up front</li>
          <li>Converts to annual at founding price on hit</li>
        </ul>
      </div>
      <div class="card">
        <div class="tier">You receive</div>
        <div class="price" style="font-size:1.25rem">Evidence pack</div>
        <div class="sub">Reference + case study if pilot succeeds (your approval)</div>
        <ul><li>Direct roadmap input</li><li>Priority support</li><li>Founding pricing lock</li></ul>
      </div>
    </div>
    <div class="table-wrap" style="margin-top:1.5rem">
      <table>
        <tr><th>Term</th><th>Detail</th></tr>
        <tr><td>Mode</td><td>Shadow — parallel to existing M365 / agent stack</td></tr>
        <tr><td>Scope</td><td>One Copilot workflow · one agent fleet you nominate</td></tr>
        <tr><td>Success</td><td>One number up front (e.g. % policy-gated with full replay)</td></tr>
        <tr><td>Win line</td><td>Purview tells you something happened. Noetfield proves what was <em>permitted</em>, under which policy version, tamper-evident.</td></tr>
      </table>
    </div>
  </section>

  <section>
    <h2>Why now</h2>
    <h3>Request-level governance is the 2026 bar.</h3>
    <div class="prose"><p>Enterprises put agents and Copilot into production faster than they built controls. Static, session-level governance is insufficient — governance must run on <strong>every action</strong>. Noetfield closes that gap at the execution layer with proof density, not prose.</p></div>
  </section>

  <footer class="footer wrap">
    <p><strong>Next step:</strong> 15-minute live walkthrough of the full governance-receipt chain.</p>
    <p style="margin-top:0.5rem"><strong>Contact:</strong> <a href="mailto:operations@noetfield.com">operations@noetfield.com</a></p>
    <p style="margin-top:0.5rem"><strong>Pilot:</strong> <a href="https://www.noetfield.com/copilot/pilot/">noetfield.com/copilot/pilot</a> · <strong>Demo:</strong> <a href="https://project-gc7lm.vercel.app/copilot/demo/">5-min governance demo</a></p>
    <p style="margin-top:1.25rem;font-size:0.8rem">Noetfield Systems Inc. · Built on SourceA runtime governance infrastructure · On your invoice: Noetfield only.</p>
  </footer>
</div>
"""
    return _shell("Noetfield — Founding Customer Pilot", body)


def ab1_html() -> str:
    body = """
<div class="wrap">
  <div class="topbar">
    <div class="brand">SourceA <span>Governed agentic automation</span></div>
    <span class="pill accent">Asset B · DFY · fastest cash</span>
  </div>
  <header class="hero">
    <h1>Agent loops that ship with receipts.</h1>
    <p class="lead">Done-for-you governed automation — outreach, ops, research — built on the same factory stack we run daily. Policy at dispatch. Signed proof on closeout.</p>
    <blockquote class="quote">We run this stack on our own factory every day. Your loop gets the same receipts — what ran, what was blocked, what policy applied.</blockquote>
    <div class="cta-row no-print">
      <a class="btn btn-primary" href="mailto:hello@sourcea.app">Book discovery call</a>
      <a class="btn btn-ghost" href="https://github.com/kazemnezhadsina144-dot/sourcea-boot">Try sourcea-boot</a>
    </div>
    <div class="stats">
      <div class="stat"><div class="num">Weeks</div><div class="lbl">Typical time to first live loop — not quarters</div></div>
      <div class="stat"><div class="num">$3–10K</div><div class="lbl">Project band · Agent Loop Build (SKU-DFY-001)</div></div>
      <div class="stat"><div class="num">$2–5K</div><div class="lbl">Monthly retainer · ongoing ops + weekly proof</div></div>
    </div>
  </header>

  <section>
    <h2>What you get</h2>
    <h3>Governed execution — not glue scripts without audit.</h3>
    <div class="prose">
      <p>Asset B is the agentic orchestration capability SourceA uses internally — packaged as done-for-you delivery for agencies, founders, and ops teams who need automation that survives scrutiny.</p>
    </div>
    <div class="grid-3" style="margin-top:1.25rem">
      <div class="card">
        <div class="tier">Outreach</div>
        <div class="price" style="font-size:1.1rem">Research → send</div>
        <ul><li>Approval-gated drafts</li><li>Send receipts</li><li>Book/debrief trail</li></ul>
      </div>
      <div class="card featured">
        <div class="tier">Ops</div>
        <div class="price" style="font-size:1.1rem">Monitor → export</div>
        <ul><li>Health checks · validators</li><li>Weekly PDF/HTML proof</li><li>Self-healing monitor</li></ul>
      </div>
      <div class="card">
        <div class="tier">Research</div>
        <div class="price" style="font-size:1.1rem">Gather → disk</div>
        <ul><li>Brief + attachment path</li><li>Receipt JSON</li><li>SAVE-path governance</li></ul>
      </div>
    </div>
  </section>

  <section>
    <h2>Pricing</h2>
    <h3>Fixed outcome bands — no hourly glue billing.</h3>
    <div class="grid-3">
      <div class="card">
        <div class="tier">Lead-in</div>
        <div class="price">$750</div>
        <div class="sub">Ops Health Audit · 48h · feeder to DFY</div>
        <ul><li>Spine audit</li><li>PDF-ready report</li></ul>
      </div>
      <div class="card featured">
        <div class="tier">Agent Loop Build</div>
        <div class="price">$3–10K</div>
        <div class="sub">One governed loop live · handoff · 30-day fix window</div>
        <ul><li>Outreach, ops, or research loop</li><li>Policy at dispatch</li><li>Closeout replay demo</li></ul>
      </div>
      <div class="card">
        <div class="tier">Retainer</div>
        <div class="price">$2–5K</div>
        <div class="sub">Per month · SKU-RET-001</div>
        <ul><li>Weekly receipt export</li><li>Approval-gated changes</li><li>Optional + governance pack</li></ul>
      </div>
    </div>
  </section>

  <section>
    <h2>Combined motion</h2>
    <h3>Cash now · live deployment · case study.</h3>
    <div class="prose">
      <p>One engagement: build your agent loop <strong>and</strong> instrument it with signed receipts and tamper-checked export. Separate vocabulary on compliance calls — Noetfield board pack only when buyer asks.</p>
    </div>
    <div class="chain" style="margin-top:1rem">
      <span class="beat">discover</span><span class="beat arrow">→</span>
      <span class="beat">build loop</span><span class="beat arrow">→</span>
      <span class="beat">instrument</span><span class="beat arrow">→</span>
      <span class="beat pass">handoff + retainer</span>
    </div>
  </section>

  <footer class="footer wrap">
    <p><strong>From:</strong> <a href="mailto:hello@sourcea.app">hello@sourcea.app</a> · SourceA</p>
    <p style="margin-top:0.5rem"><strong>Subject line (AB1):</strong> Can you prove what your agents executed last night?</p>
    <p style="margin-top:1.25rem;font-size:0.8rem">SourceA · Runtime governance infrastructure · Pre-LLM policy at dispatch · Ledger + replay</p>
  </footer>
</div>
"""
    return _shell("SourceA — Governed Agentic Automation (Asset B)", body)


def bundle__layout_html() -> str:
    """Self-contained SourceA landing — .ai layout (fleet panel · pillars · matrix · 4-tier pricing)."""
    html = (LANDING_DIR / ".html").read_text(encoding="utf-8")
    base_css = (C13_DIR / "styles.css").read_text(encoding="utf-8")
    theme_css = (LANDING_DIR / "sourcea-theme.css").read_text(encoding="utf-8")
    js = (C13_DIR / "main.js").read_text(encoding="utf-8")
    fonts = (
        '<link rel="preconnect" href="https://fonts.googleapis.com" />'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700'
        '&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />'
    )
    import re

    html = re.sub(r'\s*<link rel="stylesheet" href="\.\./C13/styles\.css" />\s*', "", html)
    html = re.sub(r'\s*<link rel="stylesheet" href="sourcea-theme\.css" />\s*', "", html)
    html = re.sub(r'\s*<script src="\.\./C13/main\.js"></script>\s*', "", html)
    html = html.replace("</head>", f"<style>{base_css}\n{theme_css}</style>\n</head>", 1)
    html = html.replace("</body>", f"<script>{js}</script>\n</body>", 1)
    if "fonts.googleapis.com" not in html:
        html = html.replace("<head>", f"<head>\n  {fonts}", 1)
    return html


def write_all() -> dict[str, str]:
    SINA.mkdir(parents=True, exist_ok=True)
    paths = {}
    NOETFIELD_HTML.write_text(noetfield_html(), encoding="utf-8")
    paths["noetfield"] = str(NOETFIELD_HTML)
    AB1_HTML.write_text(ab1_html(), encoding="utf-8")
    paths["ab1"] = str(AB1_HTML)
     = bundle__layout_html()
    _HTML.write_text(, encoding="utf-8")
    paths[""] = str(_HTML)
    _ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    _ARCHIVE.write_text(, encoding="utf-8")
    paths["_archive"] = str(_ARCHIVE)
    return paths


def open_file(path: str) -> None:
    subprocess.run(["open", path], check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "target",
        nargs="?",
        choices=["all", "noetfield", "ab1", ""],
        default="all",
        help="Which one-pager to generate",
    )
    parser.add_argument("--open", action="store_true", help="Open in default browser after write")
    parser.add_argument("--json", action="store_true", help="Print paths as JSON")
    args = parser.parse_args()

    paths = write_all()
    selected = paths if args.target == "all" else {args.target: paths[args.target]}
    if args.target == "":
        selected = {"": paths[""], "_archive": paths["_archive"]}

    if args.json:
        import json

        print(json.dumps({"ok": True, "paths": selected}, indent=2))
    else:
        for p in selected.values():
            print(p)

    if args.open:
        for p in selected.values():
            open_file(p)

    return 0


if __name__ == "__main__":
    sys.exit(main())
