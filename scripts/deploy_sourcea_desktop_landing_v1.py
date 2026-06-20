#!/usr/bin/env python3
"""Deploy SourceA commercial landing into Desktop AgentGo (SA4) + Agent Run apps."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREEN_UNIFIED = ROOT / "SourceA-landing" / "green-unified"
SINA = Path.home() / ".sina"
AGENTGO = Path.home() / "Desktop/SA4"
AGENTRUN = Path.home() / "Desktop/agentrun-app"

SOURCEA_EMAIL = "hello@sourcea.com"
SOURCEA_URL = "https://sourcea.com"
GITHUB_BOOT = "https://github.com/sourcea-io/sourcea-boot"


def agentgo_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <title>SourceA | Runtime governance infrastructure</title>
  <meta name="description" content="Controlled agentic automation — policy at dispatch, signed ledger, replay. Asset B DFY $3–10K. Buyer 1 eval via sourcea-boot." />
  <meta name="theme-color" content="#060a12" />
  <meta property="og:site_name" content="SourceA" />
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap" />
  <link rel="stylesheet" href="/assets/styles.css" />
  <link rel="stylesheet" href="/assets/ui-polish.css" />
  <link rel="stylesheet" href="/assets/responsive.css" />
  <link rel="stylesheet" href="/assets/agentic.css" />
  <link rel="stylesheet" href="/sourcea/sourcea.css" />
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml" />
</head>
<body>
<div class="pe-scroll-progress" aria-hidden="true"><div class="pe-scroll-progress-bar"></div></div>
<a class="skip-link" href="#main-content">Skip to content</a>
<main id="main-content" class="pe-page sa-page">

  <div class="pe-topbar pe-topbar-agentic">
    <a class="pe-brand" href="/sourcea/" aria-label="SourceA">
      <span class="pe-brand-mark" aria-hidden="true">
        <svg viewBox="0 0 20 20" fill="none"><rect x="3" y="3" width="14" height="14" rx="3" stroke="#4d9fff" stroke-width="1.5"/><path d="M7 10h6M10 7v6" stroke="#34d399" stroke-width="1.5" stroke-linecap="round"/></svg>
      </span>
      <span><strong>SourceA</strong><small>sourcea.com</small></span>
    </a>
    <nav class="pe-nav" aria-label="Primary">
      <a href="/">← AgentGo</a>
      <a href="#proof">>Verification</a>
      <a href="#pricing">Asset B</a>
      <a href="#eval">Eval</a>
      <a class="pe-btn pe-btn-primary" href="mailto:{SOURCEA_EMAIL}">Book 15 min</a>
    </nav>
  </div>

  <header class="pe-section pe-hero pe-hero-cinematic sa-hero" id="top">
    <div class="pe-hero-grid">
      <div>
        <p class="pe-tracking-pill pe-agent-pill"><span class="pe-tracking-dot"></span>Runtime governance infrastructure</p>
        <h1><span class="pe-line-reveal">Agent loops need</span><span class="pe-line-reveal"><em class="pe-gradient-text">receipts logged.</em></span></h1>
        <p class="pe-subhead">Pre-LLM policy at dispatch · signed ledger · replay · tamper-evidence.</p>
        <p class="pe-subhead pe-subhead-muted">We operate a self-healing factory daily and deliver the same controlled spine as done-for-you automation — outreach, ops, research.</p>
        <div class="pe-hero-actions">
          <a class="pe-btn pe-btn-primary" href="mailto:{SOURCEA_EMAIL}">Screen-share today's receipts</a>
          <a class="pe-btn pe-btn-ghost" href="{GITHUB_BOOT}">Try sourcea-boot</a>
        </div>
        <div class="pe-signals">
          <span class="pe-signal"><strong>2–3 wk</strong> DFY delivery</span>
          <span class="pe-signal"><strong>$3–10K</strong> Agent Loop Build</span>
          <span class="pe-signal"><strong>PASS/BLOCK</strong> critic_boot</span>
          <span class="pe-signal"><strong>Buyer 1</strong> not Noetfield</span>
        </div>
      </div>
      <div class="sa-fleet-panel">
        <p class="sa-panel-label">Factory roster · live</p>
        <ul class="sa-roster">
          <li><code>outreach-loop</code><span class="sa-pass">PASS</span></li>
          <li><code>ops-monitor</code><span class="sa-block">BLOCK</span></li>
          <li><code>research-gather</code><span class="sa-pass">PASS</span></li>
          <li><code>tamper-check</code><span class="sa-fail">FAIL</span></li>
        </ul>
      </div>
    </div>
  </header>

  <section class="pe-section" id="proof">
    <div class="pe-section-inner">
      <h2 class="pe-section-title">Verification — under five minutes</h2>
      <p class="pe-section-lead">Not slides. The same spine we run on the factory every day.</p>
      <div class="sa-chain">
        <span>request</span><span>→</span><span>policy</span><span>→</span><span>decision</span><span>→</span>
        <span class="sa-pass">receipt</span><span>→</span><span>replay</span><span>→</span><span class="sa-fail">tamper-FAIL</span>
      </div>
      <div class="sa-pillar-grid">
        <article><h3>Policy</h3><p>LOCKED SSOT at dispatch — law in repository.</p></article>
        <article><h3>Dispatch gate</h3><p>Session gate PASS · role-scoped execution.</p></article>
        <article><h3>Receipt ledger</h3><p>Signed record · export bundle on closeout.</p></article>
        <article><h3>Replay</h3><p>Cold-start replay without chat memory.</p></article>
        <article><h3>Tamper check</h3><p>Fake-green detection on altered records.</p></article>
        <article><h3>Self-heal</h3><p>Weekly proof export · tier validators.</p></article>
      </div>
    </div>
  </section>

  <section class="pe-section pe-section-muted" id="pricing">
    <div class="pe-section-inner">
      <h2 class="pe-section-title">Asset B — fastest cash</h2>
      <div class="sa-price-grid">
        <article class="sa-price"><h3>Ops Health Audit</h3><p class="sa-amt">$750</p><p>48h spine audit · feeder to DFY</p></article>
        <article class="sa-price sa-featured"><h3>Agent Loop Build</h3><p class="sa-amt">$3–10K</p><p>One scoped loop live · 30-day fix window</p></article>
        <article class="sa-price"><h3>Retainer</h3><p class="sa-amt">$2–5K/mo</p><p>Weekly receipt export · approval-gated ops</p></article>
      </div>
      <p class="sa-quote">We run this stack on our own factory every day. Your loop gets the same receipts — what ran, what was blocked, what policy applied.</p>
    </div>
  </section>

  <section class="pe-section" id="eval">
    <div class="pe-section-inner sa-cta-band">
      <h2>Buyer 1 eval — no sales call required</h2>
      <p>GitHub + sourcea-boot · README under 5 minutes · BOOT_REPORT.json PASS/BLOCK.</p>
      <div class="pe-hero-actions">
        <a class="pe-btn pe-btn-primary" href="mailto:{SOURCEA_EMAIL}">{SOURCEA_EMAIL}</a>
        <a class="pe-btn pe-btn-ghost" href="{SOURCEA_URL}">{SOURCEA_URL}</a>
      </div>
    </div>
  </section>

  <footer class="pe-marketing-footer sa-footer">
    <p>SourceA · Runtime governance infrastructure · Hosted on AgentGo desktop stack · Portfolio lane — not AgentGo product</p>
    <p><a href="/">AgentGo home</a> · <a href="http://127.0.0.1:5180/sourcea/">Agent Run / SourceA</a></p>
  </footer>
</main>
<script src="/assets/agentic.js" defer></script>
</body>
</html>
"""


def agentrun_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <title>SourceA | Controlled agentic automation</title>
  <meta name="description" content="Done-for-you controlled agent loops with signed receipts. Policy at dispatch for teams shipping Cursor agents." />
  <meta name="theme-color" content="#0a1628" />
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&family=Inter:wght@400;500;600&display=swap" />
  <link rel="stylesheet" href="/assets/agentrun.css" />
  <link rel="stylesheet" href="/sourcea/sourcea.css" />
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml" />
</head>
<body class="ar-body sa-ar">

<header class="ar-header">
  <div class="ar-container ar-header-shell">
    <div class="ar-header-inner">
      <a class="ar-logo" href="/sourcea/" aria-label="SourceA">
        <span class="ar-logo-text">Source<span class="ar-logo-run">A</span></span>
      </a>
      <nav class="ar-nav" aria-label="Primary">
        <a href="/">← Agent Run</a>
        <a href="#solution">Platform</a>
        <a href="#pricing">Pricing</a>
        <a href="#proof">Proof</a>
      </nav>
      <a class="ar-btn ar-btn-primary ar-btn-sm" href="mailto:{SOURCEA_EMAIL}">Get Started</a>
    </div>
  </div>
</header>

<main id="main-content">
  <section class="ar-hero ar-hero-ref ar-reveal" id="top">
    <div class="ar-container ar-hero-ref-layout">
      <div class="ar-hero-ref-copy">
        <p class="ar-kicker">Controlled execution</p>
        <h1>Prove what your agents <span class="ar-hero-accent">executed last night.</span></h1>
        <p class="ar-hero-lead">Runtime governance infrastructure for platform engineers and agencies — policy before execution, signed receipts logged, replay on closeout.</p>
        <div class="ar-hero-actions">
          <a class="ar-btn ar-btn-primary" href="mailto:{SOURCEA_EMAIL}">Book discovery call<span class="ar-btn-arrow">→</span></a>
          <a class="ar-btn ar-btn-ghost" href="{GITHUB_BOOT}">sourcea-boot<span class="ar-btn-arrow ar-btn-arrow-dark">→</span></a>
        </div>
        <div class="ar-hero-trust">
          <div class="ar-trust-chip"><strong>Weeks</strong><span>not quarters to cash</span></div>
          <div class="ar-trust-chip"><strong>$3–10K</strong><span>DFY project band</span></div>
          <div class="ar-trust-chip"><strong>~$200/mo</strong><span>factory run cost</span></div>
        </div>
      </div>
    </div>
  </section>

  <section id="solution" class="ar-section ar-reveal">
    <div class="ar-container">
      <div class="ar-section-head ar-section-head-center">
        <p class="ar-kicker">The gap</p>
        <h2>Loops run. Governance stays on slides.</h2>
        <p>Temporal meets policy-as-wedge — orchestrator underneath, mechanical proof on top. Not L7 chat UI. Not compliance Copilot lane.</p>
      </div>
      <div class="ar-features-grid ar-stagger">
        <article class="ar-feature-card ar-reveal"><span class="ar-feature-num">01</span><h3>Factory observe</h3><p>Daily self-healing multi-agent ops with tier0 PASS.</p></article>
        <article class="ar-feature-card ar-reveal"><span class="ar-feature-num">02</span><h3>Policy at dispatch</h3><p>Pre-LLM gate — session gate · feasibility · cross-lane guard.</p></article>
        <article class="ar-feature-card ar-reveal"><span class="ar-feature-num">03</span><h3>Signed ledger</h3><p>Export bundle · weekly PDF/HTML for clients.</p></article>
        <article class="ar-feature-card ar-reveal"><span class="ar-feature-num">04</span><h3>Replay + tamper</h3><p>BLOCK → ALLOW → tamper-FAIL demo in one screen-share.</p></article>
      </div>
    </div>
  </section>

  <section id="proof" class="ar-section ar-section-muted ar-reveal">
    <div class="ar-container">
      <div class="ar-section-head ar-section-head-center">
        <p class="ar-kicker">>Verification</p>
        <h2>Every controlled turn leaves a receipt</h2>
      </div>
      <div class="sa-chain sa-chain-light">
        <span>request</span><span>→</span><span>policy eval</span><span>→</span><span>ALLOW/BLOCK</span><span>→</span>
        <span class="sa-pass">signed receipt</span><span>→</span><span>replay</span><span>→</span><span class="sa-fail">tamper-FAIL</span>
      </div>
    </div>
  </section>

  <section id="pricing" class="ar-section ar-reveal">
    <div class="ar-container">
      <div class="ar-section-head ar-section-head-center">
        <p class="ar-kicker">Asset B SKUs</p>
        <h2>Fixed outcome bands — no hourly glue</h2>
      </div>
      <div class="ar-pricing-grid ar-stagger">
        <article class="ar-price-card ar-reveal">
          <h3>Ops Health Audit</h3>
          <p class="ar-price">$750<small> one-time</small></p>
          <ul><li>48h spine audit</li><li>PDF-ready report</li></ul>
          <a class="ar-btn ar-btn-ghost ar-btn-sm" href="mailto:{SOURCEA_EMAIL}">Book audit</a>
        </article>
        <article class="ar-price-card is-featured ar-reveal">
          <span class="ar-price-badge">Fastest cash</span>
          <h3>Agent Loop Build</h3>
          <p class="ar-price">$3–10K<small> project</small></p>
          <ul><li>Outreach · ops · research</li><li>Handoff + replay demo</li></ul>
          <a class="ar-btn ar-btn-primary ar-btn-sm" href="mailto:{SOURCEA_EMAIL}">Start build</a>
        </article>
        <article class="ar-price-card ar-reveal">
          <h3>Retainer</h3>
          <p class="ar-price">$2–5K<small> / month</small></p>
          <ul><li>Weekly proof export</li><li>Approval-gated changes</li></ul>
          <a class="ar-btn ar-btn-ghost ar-btn-sm" href="mailto:{SOURCEA_EMAIL}">Retainer</a>
        </article>
      </div>
    </div>
  </section>

  <section class="ar-section ar-section-muted ar-reveal">
    <div class="ar-container ar-section-head ar-section-head-center">
      <h2>Subject: Can you prove what your agents executed last night?</h2>
      <p><a class="ar-btn ar-btn-primary" href="mailto:{SOURCEA_EMAIL}">{SOURCEA_EMAIL}</a></p>
      <p style="margin-top:1rem;font-size:0.9rem;opacity:0.8">Hosted on Agent Run desktop stack · SourceA portfolio — not GEO product</p>
      <p style="font-size:0.85rem"><a href="/">Agent Run home</a> · <a href="http://127.0.0.1:8080/sourcea/">AgentGo / SourceA</a></p>
    </div>
  </section>
</main>

<footer class="ar-site-footer">
  <div class="ar-container"><p>© SourceA · {SOURCEA_URL}</p></div>
</footer>
<script src="/assets/agentrun.js" defer></script>
</body>
</html>
"""


SOURCEA_CSS = """
/* SourceA overlays — AgentGo + Agent Run desktop routes */
.sa-page .sa-hero .pe-hero-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start; }
@media (max-width: 900px) { .sa-page .sa-hero .pe-hero-grid { grid-template-columns: 1fr; } }
.sa-fleet-panel {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(77, 159, 255, 0.25);
  border-radius: 14px;
  padding: 1.25rem;
  font-family: 'IBM Plex Mono', ui-monospace, monospace;
  font-size: 0.82rem;
}
.sa-panel-label { color: #8fa3bc; text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.7rem; margin-bottom: 0.75rem; }
.sa-roster { list-style: none; margin: 0; padding: 0; }
.sa-roster li { display: flex; justify-content: space-between; padding: 0.45rem 0; border-bottom: 1px solid rgba(255,255,255,0.06); }
.sa-roster code { color: #c5d4e8; }
.sa-pass { color: #34d399; font-weight: 700; font-size: 0.72rem; }
.sa-block, .sa-fail { color: #ff6b6b; font-weight: 700; font-size: 0.72rem; }
.sa-chain { display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 1.25rem 0; font-family: 'IBM Plex Mono', ui-monospace, monospace; font-size: 0.78rem; }
.sa-chain span { padding: 0.35rem 0.6rem; border-radius: 6px; border: 1px solid rgba(77,159,255,0.25); background: rgba(77,159,255,0.08); }
.sa-chain-light span { border-color: rgba(4,68,65,0.2); background: rgba(154,231,97,0.08); }
.sa-pillar-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1.5rem; }
.sa-pillar-grid article { padding: 1rem; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08); background: rgba(0,0,0,0.2); }
.sa-pillar-grid h3 { margin: 0 0 0.35rem; font-size: 1rem; }
.sa-pillar-grid p { margin: 0; font-size: 0.88rem; opacity: 0.85; }
.sa-price-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem; }
.sa-price { padding: 1.25rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); }
.sa-price.sa-featured { border-color: #4d9fff; box-shadow: 0 8px 32px rgba(77,159,255,0.15); }
.sa-amt { font-size: 1.75rem; font-weight: 800; margin: 0.5rem 0; color: #4d9fff; }
.sa-quote { margin-top: 1.5rem; padding: 1rem 1.25rem; border-left: 3px solid #4d9fff; font-style: italic; opacity: 0.9; }
.sa-footer { padding: 2rem; text-align: center; font-size: 0.85rem; opacity: 0.8; }
.sa-cta-band { text-align: center; }
@media (max-width: 768px) {
  .sa-pillar-grid, .sa-price-grid { grid-template-columns: 1fr; }
}
.sa-ar .ar-logo-run { color: #4d9fff; }
"""


def deploy_green_unified(dest_dir: Path) -> None:
    """Copy green-unified shell (all HTML subpages + CSS + JS)."""
    if not GREEN_UNIFIED.is_dir():
        raise SystemExit(f"FAIL: green-unified missing: {GREEN_UNIFIED}")
    dest_dir.mkdir(parents=True, exist_ok=True)
    for src in GREEN_UNIFIED.rglob("*"):
        if not src.is_file():
            continue
        if src.suffix not in {".html", ".css", ".js", ".svg", ".json", ".mp4"}:
            continue
        rel = src.relative_to(GREEN_UNIFIED)
        out = dest_dir / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)


def deploy(*, open_browser: bool = False) -> dict[str, str]:
    paths: dict[str, str] = {}
    if not AGENTGO.is_dir():
        raise SystemExit(f"FAIL: desktop app missing: {AGENTGO}")
    if not AGENTRUN.is_dir():
        raise SystemExit(f"FAIL: desktop app missing: {AGENTRUN}")

    # Agent Run — canonical green-unified landing
    ar_dest = AGENTRUN / "sourcea"
    deploy_green_unified(ar_dest)
    paths[AGENTRUN.name] = str(ar_dest / "index.html")

    # AgentGo — dark cinematic variant (different asset stack)
    go_dest = AGENTGO / "sourcea"
    go_dest.mkdir(parents=True, exist_ok=True)
    (go_dest / "index.html").write_text(agentgo_html(), encoding="utf-8")
    (go_dest / "sourcea.css").write_text(SOURCEA_CSS.strip() + "\n", encoding="utf-8")
    paths[AGENTGO.name] = str(go_dest / "index.html")

    # Sync canonical copies
    SINA.mkdir(parents=True, exist_ok=True)
    shutil.copy2(AGENTGO / "sourcea/index.html", SINA / "sourcea-agentgo-desktop-v1.html")
    shutil.copy2(AGENTRUN / "sourcea/index.html", SINA / "sourcea-agentrun-desktop-v1.html")
    shutil.copy2(AGENTRUN / "sourcea/sourcea.css", SINA / "sourcea-green-unified-v1.css")
    shutil.copy2(AGENTRUN / "sourcea/sourcea-motion.js", SINA / "sourcea-green-unified-motion-v1.js")

    if open_browser:
        import subprocess

        subprocess.run(["open", "http://127.0.0.1:8080/sourcea/"], check=False)
        subprocess.run(["open", "http://127.0.0.1:5180/sourcea/"], check=False)

    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--open", action="store_true", help="Open browser after deploy (servers must be running)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    paths = deploy(open_browser=args.open)
    if args.json:
        import json

        print(json.dumps({"ok": True, "paths": paths, "urls": {
            "agentgo": "http://127.0.0.1:8080/sourcea/",
            "agentrun": "http://127.0.0.1:5180/sourcea/",
        }}, indent=2))
    else:
        for k, v in paths.items():
            print(f"{k}: {v}")
        print("AgentGo  → http://127.0.0.1:8080/sourcea/")
        print("Agent Run → http://127.0.0.1:5180/sourcea/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
