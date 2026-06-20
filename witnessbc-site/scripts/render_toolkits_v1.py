#!/usr/bin/env python3
"""Render WitnessBC toolkit subpages (free templates + training hub) with v12 shell."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTIALS = ROOT / "partials"
DATA = ROOT / "data" / "toolkits-v1.json"

# Import token helpers from assemble_pages
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
)


def _root_absolute_paths(html: str) -> str:
    """Nested toolkit pages must use root-absolute asset + nav URLs."""
    html = re.sub(r'href="(?:\.\./)+assets/', 'href="/assets/', html)
    html = re.sub(r'src="(?:\.\./)+assets/', 'src="/assets/', html)
    html = html.replace('href="assets/', 'href="/assets/')
    html = html.replace('src="assets/', 'src="/assets/')

    for page in SITE_PAGES:
        html = re.sub(rf'href="(?:\.\./)+{re.escape(page)}', f'href="/{page}', html)
        html = html.replace(f'href="{page}"', f'href="/{page}"')
        html = re.sub(rf'href="{re.escape(page)}#', f'href="/{page}#', html)

    html = re.sub(r'href="(?:\.\./)+toolkits/', 'href="/toolkits/', html)
    html = html.replace('href="toolkits/', 'href="/toolkits/')
    html = html.replace('href="/toolkits.html#quickstart"', 'href="/toolkits.html#quickstart"')
    html = html.replace('href="../"', 'href="/toolkits/training/"')
    html = html.replace('data-live-demo-url="proof.html"', 'data-live-demo-url="/proof.html"')
    return html


def _free_body(page: dict) -> str:
    slug = page["slug"]
    title = page["title"]
    intro = page["intro"]
    tpl = page.get("template_text", "")
    tpl_label = page.get("template_label", "Copy template")
    price = page.get("price", 19)
    stripe_key = page["stripe_key"]

    return f"""  <main id="main-content">
    <section class="page-hero page-hero-toolkit">
      <div class="container">
        <p class="section-eyebrow">Toolkits · Free</p>
        <h1>{title}</h1>
        <p class="section-lead">{intro} <strong>Education only — not legal advice.</strong></p>
        <div class="hero-actions toolkit-actions">
          <a class="btn btn-ghost" href="/toolkits.html">← Back to Toolkits</a>
          <button class="btn btn-primary" type="button" data-buy="{stripe_key}">Buy Pro (${price})</button>
          <a class="btn btn-outline" href="/toolkits/training/">Training</a>
        </div>
      </div>
    </section>

    <section class="toolkit-section">
      <div class="container toolkit-grid-2">
        <article class="surface-card">
          <h2>What this is (and what it is not)</h2>
          <ul class="toolkit-list">
            <li><strong>For:</strong> repeatable publishing discipline — sources, limits, correction-ready notes.</li>
            <li><strong>Not for:</strong> case handling, case review, outcome services, or emergency/legal guidance.</li>
            <li><strong>Privacy-first:</strong> do not put sensitive personal data into public drafts or forms.</li>
          </ul>
        </article>
        <article class="surface-card">
          <h2>Minimum standard (5 minutes)</h2>
          <ul class="toolkit-list">
            <li>Each claim is a single sentence.</li>
            <li>Each claim links to at least one source with a <strong>Source ID</strong> and <strong>date accessed</strong>.</li>
            <li>Write one <strong>Limits</strong> line per claim (what you cannot prove).</li>
            <li>Separate evidence from interpretation.</li>
            <li>Include a correction path before publishing.</li>
          </ul>
        </article>
      </div>
    </section>

    <section class="toolkit-section" id="template">
      <div class="container">
        <article class="surface-card toolkit-template-card">
          <div class="toolkit-template-head">
            <h2>{tpl_label}</h2>
            <p class="meta">Paste into Notes / Google Docs / Notion.</p>
            <button class="btn btn-outline btn-sm" type="button" id="copyTpl" data-target="tpl-{slug}">Copy template</button>
          </div>
          <textarea id="tpl-{slug}" class="toolkit-textarea" aria-label="{title} template" spellcheck="false">{tpl}</textarea>
        </article>
      </div>
    </section>

    <section class="toolkit-section toolkit-cta-band">
      <div class="container toolkit-cta-inner">
        <div>
          <h2>Upgrade for repeat use</h2>
          <p class="section-lead">Pro packs are printable PDF workflows — same discipline, built for reuse.</p>
        </div>
        <div class="hero-actions">
          <button class="btn btn-primary" type="button" data-buy="{stripe_key}">Buy Pro (${price})</button>
          <a class="btn btn-outline" href="/toolkits.html#bundles">View bundles</a>
        </div>
      </div>
    </section>
  </main>
"""


def _training_hub_body(data: dict) -> str:
    courses = data.get("training") or []
    cards = []
    for c in courses:
        cards.append(
            f"""        <article class="toolkit-product-card surface-card">
          <div class="toolkit-product-head">
            <h3>{c['name']}</h3>
            <p class="toolkit-tagline">{c['tagline']}</p>
          </div>
          <p class="toolkit-product-desc">{c['desc']}</p>
          <div class="toolkit-product-foot">
            <span class="toolkit-price">${c['price']}</span>
            <div class="toolkit-product-actions">
              <a class="btn btn-ghost btn-sm" href="/{c['outline_path'].lstrip('/')}">View outline</a>
              <button class="btn btn-primary btn-sm" type="button" data-buy="{c['stripe_key']}">Buy course</button>
            </div>
          </div>
        </article>"""
        )
    cards_html = "\n".join(cards)

    return f"""  <main id="main-content">
    <section class="page-hero page-hero-toolkit">
      <div class="container">
        <p class="section-eyebrow">Toolkits · Training</p>
        <h1>Async training for accountable, privacy-first publishing</h1>
        <p class="section-lead">Two short courses designed to reduce repeat mistakes. <strong>Education only — not legal advice.</strong> No case review. No outcomes sold.</p>
        <div class="hero-actions toolkit-actions">
          <a class="btn btn-ghost" href="/toolkits.html">← Back to Toolkits</a>
          <a class="btn btn-outline" href="/toolkits.html#all">Free templates first</a>
        </div>
      </div>
    </section>

    <section class="toolkit-section">
      <div class="container toolkit-grid-2">
        <article class="surface-card">
          <h2>Recommended path</h2>
          <p><strong>Path A — Privacy-first:</strong> Privacy-First Publishing → Privacy pack Pro.</p>
          <p><strong>Path B — Evidence discipline:</strong> Evidence Literacy 101 → Sourcing pack Pro.</p>
        </article>
        <article class="surface-card">
          <h2>What you get</h2>
          <ul class="toolkit-list">
            <li>Self-paced async modules</li>
            <li>Drills + checklists aligned to free templates</li>
            <li>Education only — not individualized advice</li>
          </ul>
        </article>
      </div>
    </section>

    <section class="toolkit-section" id="courses">
      <div class="container">
        <h2 class="section-title">Courses</h2>
        <div class="toolkit-product-grid">
{cards_html}
        </div>
      </div>
    </section>
  </main>
"""


def _training_outline_body(course: dict) -> str:
    return f"""  <main id="main-content">
    <section class="page-hero page-hero-toolkit">
      <div class="container">
        <p class="section-eyebrow">Training outline</p>
        <h1>{course['name']}</h1>
        <p class="section-lead">{course['tagline']}. <strong>Education only — not legal advice.</strong></p>
        <div class="hero-actions toolkit-actions">
          <a class="btn btn-ghost" href="/toolkits/training/">← All training</a>
          <button class="btn btn-primary" type="button" data-buy="{course['stripe_key']}">Buy course (${course['price']})</button>
        </div>
      </div>
    </section>

    <section class="toolkit-section">
      <div class="container toolkit-grid-2">
        <article class="surface-card">
          <h2>Who this is for</h2>
          <p>{course['desc']}</p>
        </article>
        <article class="surface-card">
          <h2>Boundaries</h2>
          <ul class="toolkit-list">
            <li>No case review or individualized legal advice</li>
            <li>No outcomes sold — education only</li>
            <li>Do not send sensitive personal data</li>
          </ul>
        </article>
      </div>
    </section>

    <section class="toolkit-section">
      <div class="container">
        <article class="surface-card">
          <h2>Outline (summary)</h2>
          <ul class="toolkit-list">
            <li>Module 1 — Minimum standard checklist</li>
            <li>Module 2 — Common failure modes + fixes</li>
            <li>Module 3 — Repeatable workflow sheets</li>
            <li>Module 4 — Corrections + privacy integration</li>
          </ul>
          <p class="meta" style="margin-top:1rem">Full syllabus ships with purchase. Prefer templates first? Start with <a href="/toolkits.html#all">free toolkits</a>.</p>
        </article>
      </div>
    </section>
  </main>
"""



def _sandbox_body(data: dict) -> str:
    sandbox = data.get("sandbox") or {}
    pages = data.get("free_pages") or []
    options = "\n".join(
        f'            <option value="{p["slug"]}">{p["title"]}</option>' for p in pages
    )
    intro = sandbox.get("intro") or "Try templates in your browser — free forever."
    honesty = sandbox.get("honesty") or "browser_local_only"
    return f"""  <main id="main-content">
    <section class="page-hero page-hero-toolkit">
      <div class="container">
        <p class="section-eyebrow">Toolkits · Sandbox · Freemium</p>
        <h1>Client sandbox — try templates free</h1>
        <p class="section-lead">{intro} <strong>Education only — not legal advice.</strong></p>
        <div class="toolkit-freemium-status" data-freemium-active="true" role="status">
          <span class="toolkit-pill toolkit-pill-live">Freemium active</span>
          <span class="toolkit-pill">{honesty}</span>
        </div>
        <div class="hero-actions toolkit-actions">
          <a class="btn btn-ghost" href="/toolkits.html">← Toolkits hub</a>
          <a class="btn btn-outline" href="/toolkits/free/sourcing/">Start free — Source Log</a>
        </div>
      </div>
    </section>

    <section class="toolkit-section" id="sandbox">
      <div class="container">
        <article class="surface-card toolkit-sandbox-card">
          <div class="toolkit-sandbox-toolbar">
            <label for="sandbox-select">Template</label>
            <select id="sandbox-select" class="toolkit-sandbox-select" aria-label="Choose template">
{options}
            </select>
            <button class="btn btn-outline btn-sm" type="button" id="sandbox-copy">Copy</button>
            <button class="btn btn-ghost btn-sm" type="button" id="sandbox-reset">Reset</button>
          </div>
          <p id="sandbox-status" class="meta toolkit-sandbox-status">Sandbox · loading…</p>
          <textarea id="sandbox-editor" class="toolkit-textarea toolkit-sandbox-editor" spellcheck="false" aria-label="Sandbox editor"></textarea>
        </article>
      </div>
    </section>
  </main>
"""

def _assemble_subpage(
    *,
    body: str,
    title: str,
    description: str,
    canonical: str,
    nav_active: str = "toolkits",
) -> str:
    head = _load_partial("head.html")
    header = _load_partial("header.html")
    breadcrumb_tpl = _load_partial("breadcrumb.html")
    footer_tpl = _load_partial("footer.html")

    tokens = {**_site_tokens(), **_nav_classes(nav_active), "BREADCRUMB_LABEL": "Toolkits"}
    tokens["TOOLKITS_URL"] = "/toolkits.html"

    head_out = _apply_tokens(
        head.replace("{{TITLE}}", title)
        .replace("{{DESCRIPTION}}", description)
        .replace("{{CANONICAL}}", canonical)
        .replace("{{BODY_CLASS}}", "page-toolkits layout-ultra-v12"),
        tokens,
    )
    head_out = head_out.replace("</head>", '  <link rel="stylesheet" href="/assets/toolkits.css" />\n</head>')

    header_out = _apply_tokens(header, tokens)
    breadcrumb_out = _apply_tokens(breadcrumb_tpl, tokens)
    footer = _apply_tokens(
        footer_tpl.replace(
            "{{SCRIPTS}}",
            _scripts_block(["toolkits", "site"]),
        ),
        tokens,
    )
    body_out = _apply_tokens(body, tokens)
    return _root_absolute_paths(head_out + header_out + breadcrumb_out + body_out + footer)


def render_all() -> dict:
    if not DATA.is_file():
        raise SystemExit(f"FAIL: missing {DATA}")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    written: list[str] = []

    for page in data.get("free_pages") or []:
        slug = page["slug"]
        out_dir = ROOT / "toolkits" / "free" / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        canonical = f"https://witnessbc.com/toolkits/free/{slug}/"
        html = _assemble_subpage(
            body=_free_body(page),
            title=f"{page['title']} – WitnessBC Toolkits",
            description=page["intro"],
            canonical=canonical,
        )
        out_path = out_dir / "index.html"
        out_path.write_text(html, encoding="utf-8")
        written.append(str(out_path.relative_to(ROOT)))

    # Sandbox (freemium · browser-local)
    sandbox_dir = ROOT / "toolkits" / "sandbox"
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    sandbox_html = _assemble_subpage(
        body=_sandbox_body(data),
        title="Toolkit Sandbox (Free) – WitnessBC",
        description=(data.get("sandbox") or {}).get("intro", "Free toolkit sandbox."),
        canonical="https://witnessbc.com/toolkits/sandbox/",
    )
    sandbox_html = sandbox_html.replace(
        _root_absolute_paths(_scripts_block(["toolkits", "site"])),
        _root_absolute_paths(_scripts_block(["toolkits", "toolkits-sandbox", "site"])),
    )
    (sandbox_dir / "index.html").write_text(sandbox_html, encoding="utf-8")
    written.append("toolkits/sandbox/index.html")

    # Training hub
    train_dir = ROOT / "toolkits" / "training"
    train_dir.mkdir(parents=True, exist_ok=True)
    train_html = _assemble_subpage(
        body=_training_hub_body(data),
        title="Training – WitnessBC Toolkits",
        description="Async training for accountable, privacy-first publishing. Education only.",
        canonical="https://witnessbc.com/toolkits/training/",
    )
    (train_dir / "index.html").write_text(train_html, encoding="utf-8")
    written.append("toolkits/training/index.html")

    for course in data.get("training") or []:
        outline_slug = course["outline_path"].rstrip("/").split("/")[-1]
        out_dir = train_dir / outline_slug
        out_dir.mkdir(parents=True, exist_ok=True)
        html = _assemble_subpage(
            body=_training_outline_body(course),
            title=f"{course['name']} – WitnessBC Training",
            description=course["desc"],
            canonical=f"https://witnessbc.com/toolkits/training/{outline_slug}/",
        )
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        written.append(f"toolkits/training/{outline_slug}/index.html")

    return {"ok": True, "written": written, "count": len(written)}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    result = render_all()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"OK: rendered {result['count']} toolkit subpages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
