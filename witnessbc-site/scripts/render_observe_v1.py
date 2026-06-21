#!/usr/bin/env python3
"""Render WitnessBC Observe lane — AI policy journalism desk with v12 commercial shell."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEED_DATA = ROOT / "data" / "observe-feed-v1.json"

sys.path.insert(0, str(ROOT / "scripts"))
from assemble_pages import (  # noqa: E402
    _apply_tokens,
    _load_partial,
    _nav_classes,
    _scripts_block,
    _site_tokens,
)

SITE_PAGES = (
    "index.html",
    "platform.html",
    "lifecycle.html",
    "proof.html",
    "compare.html",
    "policy.html",
    "pricing.html",
    "faq.html",
    "sources.html",
    "learn.html",
    "toolkits.html",
    "observe/index.html",
)


def _root_absolute_paths(html: str) -> str:
    html = re.sub(r'href="(?:\.\./)+assets/', 'href="/assets/', html)
    html = re.sub(r'src="(?:\.\./)+assets/', 'src="/assets/', html)
    html = html.replace('href="assets/', 'href="/assets/')
    html = html.replace('src="assets/', 'src="/assets/')
    for page in SITE_PAGES:
        html = re.sub(rf'href="(?:\.\./)+{re.escape(page)}', f'href="/{page}', html)
        html = html.replace(f'href="{page}"', f'href="/{page}"')
    html = re.sub(r'href="(?:\.\./)+observe/', 'href="/observe/', html)
    html = html.replace('href="observe/', 'href="/observe/')
    html = html.replace('data-live-demo-url="proof.html"', 'data-live-demo-url="/proof.html"')
    return html


def _assemble_subpage(
    *,
    body: str,
    title: str,
    description: str,
    canonical: str,
    breadcrumb: str,
    embed_feed_json: str = "",
) -> str:
    head = _load_partial("head.html")
    header = _load_partial("header.html")
    breadcrumb_tpl = _load_partial("breadcrumb.html")
    footer_tpl = _load_partial("footer.html")
    tokens = {**_site_tokens(), **_nav_classes("observe"), "BREADCRUMB_LABEL": breadcrumb, "OBSERVE_URL": "/observe/"}

    head_out = _apply_tokens(
        head.replace("{{TITLE}}", title)
        .replace("{{DESCRIPTION}}", description)
        .replace("{{CANONICAL}}", canonical)
        .replace("{{BODY_CLASS}}", "page-observe layout-ultra-v12"),
        tokens,
    )
    head_out = head_out.replace("</head>", '  <link rel="stylesheet" href="/assets/observe.css" />\n</head>')
    header_out = _apply_tokens(header, tokens)
    breadcrumb_out = _apply_tokens(breadcrumb_tpl, tokens)
    footer = _apply_tokens(
        footer_tpl.replace("{{SCRIPTS}}", _scripts_block(["observe-feed", "site"])),
        tokens,
    )
    body_out = _apply_tokens(body, tokens)
    if embed_feed_json:
        body_out += f'\n  <script type="application/json" id="wbcObserveFeed">{embed_feed_json}</script>\n'

    return _root_absolute_paths(head_out + header_out + breadcrumb_out + body_out + footer)


def _observe_hub_body() -> str:
    return """  <main id="main-content">
    <section class="page-hero">
      <div class="container">
        <p class="section-eyebrow">WitnessBC Observe</p>
        <h1>We observe and narrate AI policy truth.</h1>
        <p class="section-lead observe-hero-tagline">
          Witness means observer of truth in society. Observe covers
          <strong>AI policy</strong>, <strong>governance signals</strong>, and <strong>agentic startups</strong>
          — calm tone, documented sourcing, visible corrections.
        </p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="/observe/principles/">Editorial principles</a>
          <a class="btn btn-outline" href="/observe/corrections/">Corrections</a>
          <a class="btn btn-ghost" href="/">Witness AI platform →</a>
        </div>
      </div>
    </section>
    <section class="toolkit-section">
      <div class="container">
        <p class="section-eyebrow">Feed</p>
        <h2>Policy · governance · startups</h2>
        <div id="observeFeedFilters" class="observe-feed-filters" role="toolbar" aria-label="Filter by category"></div>
        <div id="observeFeedGrid" class="observe-feed-grid" aria-live="polite"></div>
        <aside class="observe-lane-bridge">
          <p class="section-eyebrow">Two lanes · one domain</p>
          <h3>Commercial + Observe</h3>
          <p class="section-lead">
            <strong>Witness AI</strong> sells runtime governance. <strong>Observe</strong> documents the AI society shift we witness.
          </p>
          <a class="btn btn-outline btn-sm" href="/toolkits.html">Accountability toolkits →</a>
        </aside>
      </div>
    </section>
  </main>
"""


def _principles_body() -> str:
    return """  <main id="main-content">
    <section class="page-hero">
      <div class="container">
        <p class="section-eyebrow">Observe · Editorial standards</p>
        <h1>Principles for AI policy reporting.</h1>
        <p class="section-lead">Documented sourcing on policy and governance, visible corrections, privacy-aware handling.</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="/observe/">← Observe feed</a>
          <a class="btn btn-outline" href="/observe/corrections/">Corrections</a>
        </div>
      </div>
    </section>
    <section class="toolkit-section">
      <div class="container observe-principles-grid">
        <article class="surface-card"><h2>1) Independence</h2><ul class="toolkit-list"><li>Editorial coverage — not vendor or regulator aligned.</li><li>Witness AI customers do not buy coverage or outcomes.</li></ul></article>
        <article class="surface-card"><h2>2) Sourcing</h2><ul class="toolkit-list"><li>Primary evidence: filings, model cards, policy docs.</li><li>Separate known vs alleged vs inferred.</li></ul></article>
        <article class="surface-card"><h2>3) Privacy-first</h2><ul class="toolkit-list"><li>De-identify when exposure risk exists.</li><li>Consent-first for sensitive AI deployment narratives.</li></ul></article>
        <article class="surface-card"><h2>4) Corrections</h2><ul class="toolkit-list"><li>Fix errors fast — especially policy citations.</li><li><a href="/observe/corrections/">/observe/corrections/</a></li></ul></article>
        <article class="surface-card" style="grid-column:1/-1"><h2>5) AI policy red lines</h2><ul class="toolkit-list"><li>No unverified leaks as fact.</li><li>No doxxing researchers or employees.</li><li>No legal advice — explain policy; route decisions to counsel.</li><li>No pay-to-publish startup coverage.</li></ul></article>
      </div>
    </section>
  </main>
"""


def _corrections_body() -> str:
    return """  <main id="main-content">
    <section class="page-hero">
      <div class="container">
        <p class="section-eyebrow">Observe · Accountability</p>
        <h1>Corrections and the public record.</h1>
        <p class="section-lead">When wrong, corrected. When facts change meaning on AI policy coverage, updated with a clear note.</p>
        <div class="hero-actions"><a class="btn btn-primary" href="#request">Request a correction</a></div>
      </div>
    </section>
    <section class="toolkit-section">
      <div class="container toolkit-grid-2">
        <article class="surface-card"><h2>What qualifies</h2><ul class="toolkit-list"><li>Factual errors on dates, quotes, regulatory citations.</li><li>Misleading framing beyond evidence.</li></ul></article>
        <article class="surface-card" id="request"><h2>Request a correction</h2>
          <form id="observeCorrectionsForm" class="observe-corrections-form">
            <input id="observe_c_url" type="url" placeholder="Article URL (required)" required />
            <textarea id="observe_c_what" rows="4" placeholder="What is incorrect"></textarea>
            <input id="observe_c_evidence" type="url" placeholder="Evidence link (optional)" />
            <button class="btn btn-primary" type="submit">Prepare email</button>
          </form>
        </article>
      </div>
    </section>
  </main>
"""


def render_all() -> dict:
    if not FEED_DATA.is_file():
        raise SystemExit(f"FAIL: missing {FEED_DATA}")
    feed_json = FEED_DATA.read_text(encoding="utf-8").strip()
    written: list[str] = []
    spec = [
        ("observe/index.html", _observe_hub_body(), "WitnessBC Observe — AI Policy · Governance · Startups",
         "AI policy news, governance signals, agentic startups. We observe and narrate.", "https://witnessbc.com/observe/", "Observe", True),
        ("observe/principles/index.html", _principles_body(), "Editorial Principles | WitnessBC Observe",
         "Standards for AI policy reporting.", "https://witnessbc.com/observe/principles/", "Principles", False),
        ("observe/corrections/index.html", _corrections_body(), "Corrections | WitnessBC Observe",
         "Corrections policy for Observe coverage.", "https://witnessbc.com/observe/corrections/", "Corrections", False),
    ]
    for rel, body, title, desc, canonical, crumb, embed in spec:
        out = ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            _assemble_subpage(body=body, title=title, description=desc, canonical=canonical, breadcrumb=crumb,
                              embed_feed_json=feed_json if embed else ""),
            encoding="utf-8",
        )
        written.append(rel)
    return {"ok": True, "written": written, "count": len(written)}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    result = render_all()
    print(json.dumps(result, indent=2) if args.json else f"OK: rendered {result['count']} Observe pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
