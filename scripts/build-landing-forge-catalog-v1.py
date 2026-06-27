#!/usr/bin/env python3
"""Build SourceA landing Prompt Forge subpages from forge-catalog.json."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "SourceA-landing" / "green-unified"
CATALOG_PATH = LANDING / "data" / "forge-catalog.json"
FORGE_DIR = LANDING / "forge"

HEADER = """<header class="ar-header sa-header">
  <div class="ar-container ar-header-shell">
    <div class="ar-header-inner">
      <a class="ar-logo" href="/sourcea/" aria-label="SourceA home">
        <span class="ar-logo-text">Source<span class="ar-logo-run sa-logo-run">A</span></span>
      </a>
      <nav class="ar-nav" id="ar-nav" aria-label="Primary">
        <a href="/sourcea/" data-sa-nav>Home</a>
        <a href="/sourcea/platform" data-sa-nav>Platform</a>
        <a href="/sourcea/forge/" data-sa-nav>Prompt Forge</a>
        <a href="/sourcea/proof" data-sa-nav>>Verification</a>
        <a href="/sourcea/pricing" data-sa-nav>Pricing</a>
        <a class="ar-btn ar-btn-primary ar-btn-sm ar-nav-cta-mobile sa-btn-glow" href="mailto:forge@sourcea.app">Forge a mission</a>
      </nav>
      <button type="button" class="ar-nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="ar-nav">
        <span class="ar-nav-toggle-bar"></span><span class="ar-nav-toggle-bar"></span><span class="ar-nav-toggle-bar"></span>
      </button>
      <a class="ar-btn ar-btn-primary ar-btn-sm sa-btn-glow ar-header-cta" href="mailto:forge@sourcea.app">Forge a mission</a>
    </div>
  </div>
</header>"""

FOOTER = """<footer class="ar-site-footer sa-footer-rich">
  <div class="ar-container sa-footer-grid">
    <div class="sa-footer-brand"><strong>SourceA</strong><p>SourceA is an AI execution platform powered by Forge — real builds, automations, and agent workflows.</p></div>
    <div><h4>Prompt Forge</h4>
      <a href="/sourcea/forge/">All pages</a>
      <a href="/sourcea/forge/how-it-works">How it works</a>
      <a href="/sourcea/forge/mission-template">Mission template</a>
      <a href="/sourcea/forge/try">Try Forge</a>
    </div>
    <div><h4>Contact</h4>
      <a href="mailto:forge@sourcea.app">forge@sourcea.app</a>
      <a href="mailto:hello@sourcea.app">hello@sourcea.app</a>
      <a href="mailto:proof@sourcea.app">proof@sourcea.app</a>
      <a href="mailto:contact@sourcea.app">contact@sourcea.app</a>
    </div>
  </div>
  <div class="ar-container sa-footer-bottom"><p>© SourceA 2026 · <a href="/sourcea/forge/">Prompt Forge</a> · <a href="https://sourcea.app">sourcea.app</a></p></div>
</footer>"""

BODY_COPY: dict[str, str] = {
    "how-it-works": """
        <h2>Two layers — policy first</h2>
        <p><strong>Layer 1 (always on):</strong> deterministic SSOT policy parses your text, detects direction vs prescription mode, names systems (Vercel, Cloudflare, Railway…), and assembles the mission template. Zero API cost.</p>
        <p><strong>Layer 2 (optional):</strong> OpenRouter rewrites prose into template fields under the SSOT system prompt — then policy <em>re-asserts</em> guardrails so the model cannot strip them.</p>
        <h2>What you paste</h2>
        <pre class="sa-email-snippet">fix the dns for sourcea.app — wire old vercel page as subpage, no rebuild</pre>
        <h2>What Forge returns</h2>
        <p>One bounded Cursor mission with GOAL · CONTEXT (ALREADY DONE) · DONE · VERIFY · CONSTRAINTS · IF BLOCKED — ready to paste into Worker chat.</p>
    """,
    "mission-template": """
        <h2>Output shape (every run)</h2>
        <pre class="sa-email-snippet">GOAL: Wire sourcea.app DNS to Cloudflare Pages with clean URLs — no .html in the address bar.

CONTEXT (true now — do not re-derive):
- ALREADY DONE / DEPLOYED (do NOT redo): green-unified dist logged · _redirects written
- Systems involved: Cloudflare Pages · sourcea.app DNS · publish script

WHAT I WANT: Live site shows extensionless URLs; old .html paths 301 to clean paths.

DONE = curl -I https://sourcea.app/sourcea/proof returns 200 at clean URL; .html URL 301s.

VERIFY: curl -sI https://sourcea.app/sourcea/proof | head · curl -sI https://sourcea.app/sourcea/proof.html | grep -i location

CONSTRAINTS:
- NO rebuild from scratch if dist already correct
- One job only — DNS + publish, not unrelated product work

IF BLOCKED or ambiguous: STOP and tell me what's missing or which decision is mine.</pre>
        <p>This is the same shape enforced by <code>scripts/prompt_forge_pipeline_v1.py</code> — not a marketing abstraction.</p>
    """,
    "ssot-policy": """
        <h2>Standing constraints (injected every time)</h2>
        <ul>
          <li>NO rebuild / redeploy / start over if it already exists — wire and fix.</li>
          <li>One job only — no bundled unrelated work.</li>
          <li>Do not break anything already working (TLS / live state).</li>
          <li>Verdicts from receipts only — no build theater.</li>
        </ul>
        <h2>Policy detects</h2>
        <p>Destructive shell patterns · multi-job inputs · missing founder decisions (naming, paths, provider choice). Forge surfaces warnings before you waste a Cursor turn.</p>
        <h2>Law in repository</h2>
        <p>SSOT v3: <code>brain-os/ssot/SOURCEA_LLM_AGENT_OPERATING_LAW_SSOT_v3.md</code> — Forge is the outbound machine that applies this law to what you send agents.</p>
    """,
    "chat-unify": """
        <h2>Pipeline #3 in Chat Unify</h2>
        <p>Open <strong>Chat Unify.app</strong> (Mac control panel :13023). On <strong>Home</strong>, paste founder language in the quick paste strip — Forge runs as pipeline three alongside Verify &amp; Act and Proof Pack.</p>
        <h2>Closed cycle</h2>
        <p>Forge → Cursor Worker → reply → ORD + Truth gate → Founder loop → bounded order. Each machine has a name so they stop being islands.</p>
        <h2>Version</h2>
        <p>UI 4.1+ ships Forge wiring; restart the app after bundle sync if the tab is stale.</p>
    """,
    "cursor-bridge": """
        <h2>Direction, not force</h2>
        <p>Forge carries your <strong>goal</strong> and guardrails. It does not inflate scope, add steps you did not ask for, or guess paths you have not named.</p>
        <h2>Founder decisions stay yours</h2>
        <p>Naming · which project · which provider · what a page shows — the forged prompt tells the agent to STOP and ask, never substitute.</p>
        <h2>After Worker runs</h2>
        <p>ORD truth gate validates the reply against disk. Proof Pack exports receipts when you need counsel-grade evidence.</p>
    """,
    "try": """
        <h2>Three ways to start</h2>
        <ol>
          <li><strong>Email</strong> — send raw founder language to <a href="mailto:forge@sourcea.app">forge@sourcea.app</a> · one job per message.</li>
          <li><strong>Chat Unify</strong> — paste on Home · copy forged mission into Cursor Worker.</li>
          <li><strong>CLI</strong> — <code>python3 scripts/prompt_forge_pipeline_v1.py --text "your request" --json</code></li>
        </ol>
        <h2>Demo flag</h2>
        <p><code>python3 scripts/prompt_forge_pipeline_v1.py --demo</code> — sample run with receipt under <code>~/.sina/prompt-forge-receipts/</code>.</p>
        <h2>Book a walkthrough</h2>
        <p>15 minutes — we screen-share founder paste → forged prompt → Worker execute → receipt. Procurement uses <a href="mailto:proof@sourcea.app">proof@sourcea.app</a>; general intake uses <a href="mailto:contact@sourcea.app">contact@sourcea.app</a>.</p>
    """,
}


def _shell(title: str, desc: str, slug: str, body: str, *, is_hub: bool = False) -> str:
    main = f"""
<main id="main-content">
{body}
</main>"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <title>{title} | Prompt Forge · SourceA</title>
  <meta name="description" content="{desc}" />
  <meta name="theme-color" content="#044441" />
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" />
  <link rel="stylesheet" href="/assets/agentrun.css" />
  <link rel="stylesheet" href="/sourcea/sourcea.css" />
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml" />
</head>
<body class="ar-body sa-v2 sa-agentic" data-sa-page="forge-{slug}">
<div class="ar-scroll-progress" aria-hidden="true"><div class="ar-scroll-progress-bar"></div></div>
<a class="skip-link" href="#main-content">Skip to content</a>
<div class="ar-nav-backdrop" aria-hidden="true"></div>
{HEADER}
{main}
{FOOTER}
<script src="/assets/agentrun.js" defer></script>
<script src="/sourcea/sourcea-forge-hub.js" defer></script>
</body>
</html>
"""


def detail_page(page: dict, catalog: dict) -> str:
    slug = page["id"]
    body_html = BODY_COPY.get(slug, f"<p>{page['summary']}</p>")
    siblings = "".join(
        f'<a href="{p["href"]}">{p["title"]}</a> · '
        for p in catalog["pages"]
        if p["id"] != slug
    ).rstrip(" · ")
    body = f"""
  <section class="ar-section ar-page-hero sa-sub-hero ar-reveal">
    <div class="ar-container">
      <nav class="ar-breadcrumb" aria-label="Breadcrumb">
        <a href="/sourcea/">Home</a><span class="ar-breadcrumb-sep">/</span>
        <a href="/sourcea/platform">Platform</a><span class="ar-breadcrumb-sep">/</span>
        <a href="/sourcea/forge/">Prompt Forge</a><span class="ar-breadcrumb-sep">/</span>
        <span>{page['title']}</span>
      </nav>
      <span class="sa-loop-badge pass">{page['badge_label']}</span>
      <h1>{page['title']}</h1>
      <p class="ar-lead">{page['summary']}</p>
    </div>
  </section>
  <section class="ar-section ar-section-muted ar-reveal">
    <div class="ar-container ar-content-layout">
      <div class="ar-prose">{body_html}</div>
      <aside>
        <div class="ar-aside-card is-highlight">
          <h3>Forge this job</h3>
          <p>Email raw founder language — one bounded mission back.</p>
          <a class="ar-btn ar-btn-primary ar-btn-sm" href="mailto:forge@sourcea.app?subject=Prompt%20Forge%20mission">forge@sourcea.app →</a>
        </div>
        <div class="ar-aside-card">
          <h3>Other Forge pages</h3>
          <p>{siblings}</p>
        </div>
      </aside>
    </div>
  </section>
"""
    return _shell(page["title"], page["summary"], slug, body)


def hub_page(catalog: dict) -> str:
    body = """
  <section class="ar-section ar-page-hero sa-sub-hero ar-reveal">
    <div class="ar-container">
      <nav class="ar-breadcrumb" aria-label="Breadcrumb">
        <a href="/sourcea/">Home</a><span class="ar-breadcrumb-sep">/</span>
        <a href="/sourcea/platform">Platform</a><span class="ar-breadcrumb-sep">/</span>
        <span>Prompt Forge</span>
      </nav>
      <p class="ar-kicker">Outbound machine · SSOT v3</p>
      <h1>Founder language → <span class="ar-hero-accent">bounded Cursor missions.</span></h1>
      <p class="ar-lead">Prompt Forge is the product lane that converts what you say into one provable agent job — policy before LLM, guardrails re-asserted, receipts logged. Not the FBE factory line · not ICP compile · the Forge product.</p>
      <div class="ar-hero-actions" style="margin-top:1.25rem">
        <a class="ar-btn ar-btn-primary sa-btn-glow" href="/sourcea/forge/try">Try Forge<span class="ar-btn-arrow">→</span></a>
        <a class="ar-btn ar-btn-ghost" href="mailto:forge@sourcea.app">Email forge@sourcea.app<span class="ar-btn-arrow ar-btn-arrow-dark">→</span></a>
      </div>
    </div>
  </section>
  <section class="ar-section ar-section-muted ar-reveal" aria-label="SourceA email roles">
    <div class="ar-container">
      <div class="ar-section-head ar-section-head-center">
        <p class="ar-kicker">Contact lanes</p>
        <h2>One domain · <span class="ar-hero-accent">four professional inboxes.</span></h2>
      </div>
      <table class="sa-matrix" style="max-width:720px;margin:0 auto">
        <thead><tr><th>Field</th><th>Address</th><th>Use</th></tr></thead>
        <tbody>
          <tr><td>Signature / outbound</td><td><a href="mailto:hello@sourcea.app">hello@sourcea.app</a></td><td>Commercial · AB1 · signature block</td></tr>
          <tr><td>Intake</td><td><a href="mailto:contact@sourcea.app">contact@sourcea.app</a></td><td>Forms · MVP intake · general contact</td></tr>
          <tr><td>Proof booking</td><td><a href="mailto:proof@sourcea.app">proof@sourcea.app</a></td><td>Procurement · demo · proof walkthrough</td></tr>
          <tr><td><strong>Prompt Forge</strong></td><td><a href="mailto:forge@sourcea.app">forge@sourcea.app</a></td><td>Mission prompts · product lane</td></tr>
        </tbody>
      </table>
      <p class="sa-metric-note" style="margin-top:1rem;text-align:center">Signature URL: <a href="https://sourcea.app">https://sourcea.app</a> · retired poison: hello@sourcea.com</p>
    </div>
  </section>
  <section class="ar-section ar-reveal" id="forge-catalog-section">
    <div class="ar-container">
      <div class="ar-section-head ar-section-head-center">
        <p class="ar-kicker">Product subpages</p>
        <h2>Six chapters. <span class="ar-hero-accent">One Forge spine.</span></h2>
      </div>
      <div class="sa-loop-hub-grid sa-loop-pro-grid ar-stagger" id="sa-forge-catalog"></div>
    </div>
  </section>
  <section class="sa-cta-band ar-reveal">
    <div class="ar-container sa-cta-inner">
      <h2>Paste founder language</h2>
      <p>One job · SSOT-shaped · Forge executes it — not chat theater.</p>
      <div class="sa-cta-actions">
        <a class="ar-btn ar-btn-primary sa-btn-glow" href="mailto:forge@sourcea.app?subject=Forge%20my%20mission">Email forge@sourcea.app</a>
        <a class="ar-btn ar-btn-ghost" href="/sourcea/forge/how-it-works">How it works</a>
      </div>
    </div>
  </section>
"""
    return _shell("Prompt Forge", "Founder language to bounded Cursor missions — SSOT policy, Chat Unify pipeline #3.", "hub", body, is_hub=True)


def build(*, write_html: bool = True) -> dict:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    FORGE_DIR.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    if write_html:
        hub = hub_page(catalog)
        (FORGE_DIR / "index.html").write_text(hub, encoding="utf-8")
        written.append("forge/index.html")
        for page in catalog["pages"]:
            slug = page["id"]
            html = detail_page(page, catalog)
            (FORGE_DIR / f"{slug}.html").write_text(html, encoding="utf-8")
            written.append(f"forge/{slug}.html")
    catalog["built_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    CATALOG_PATH.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "pages": len(catalog["pages"]) + 1, "written": written}


def main() -> int:
    ap = argparse.ArgumentParser(description="Build Prompt Forge landing subpages")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = build()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK: forge pages={row['pages']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
