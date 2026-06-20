#!/usr/bin/env python3
"""Build SourceA-landing factories catalog from FBE disk SSOT."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "SourceA-landing" / "green-unified"
OUT_JSON = LANDING / "data" / "factories-catalog.json"
FACTORIES_DIR = LANDING / "factories"

sys.path.insert(0, str(ROOT / "scripts"))
from fbe.lib.factory_spec_v1 import catalog_payload  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


DETAIL_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{name} | Noetfield</title>
  <meta name="description" content="{tagline}" />
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&family=Inter:wght@400;500;600&display=swap" />
  <link rel="stylesheet" href="/assets/agentrun.css" />
  <link rel="stylesheet" href="/sourcea/sourcea.css" />
</head>
<body class="ar-body sa-v2 sa-agentic" data-sa-page="factory-{slug}">
<header class="ar-header sa-header">
  <div class="ar-container ar-header-shell">
    <div class="ar-header-inner">
      <a class="ar-logo" href="/sourcea/"><span class="ar-logo-text">Source<span class="ar-logo-run sa-logo-run">A</span></span></a>
      <nav class="ar-nav" id="ar-nav">
        <a href="/sourcea/factories/index.html">Factories</a>
        <a href="/sourcea/platform.html">Platform</a>
        <a href="mailto:hello@sourcea.com">Book demo</a>
      </nav>
    </div>
  </div>
</header>
<main id="main-content" class="ar-section">
  <div class="ar-container">
    <nav class="ar-breadcrumb"><a href="/sourcea/">Home</a> / <a href="/sourcea/factories/index.html">Factories</a> / <span>{name}</span></nav>
    <p class="ar-kicker">{tier_label} · {policy_pack_id}</p>
    <h1>{name}</h1>
    <p class="ar-lead">{tagline}</p>
    <div class="sa-factory-spec-grid" style="margin:2rem 0;display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(220px,1fr))">
      <article class="ar-feature-card"><h3>Inputs</h3><p><code>{inputs}</code></p></article>
      <article class="ar-feature-card"><h3>Operational nodes</h3><p><strong>{operational_nodes}</strong> compiled graph</p></article>
      <article class="ar-feature-card"><h3>Guaranteed output</h3><p>{guaranteed_output}</p></article>
      <article class="ar-feature-card"><h3>Maintenance</h3><p>${maintenance_fee_usd}/mo + compute</p></article>
    </div>
    <p><strong>Buyer:</strong> {buyer} · <strong>Status:</strong> {status} · <strong>Tier cap:</strong> {tier_cap_honest}</p>
    <div class="ar-hero-actions" style="margin-top:1.5rem">
      <a class="ar-btn ar-btn-primary sa-btn-glow" href="mailto:hello@sourcea.com?subject=Deploy%20{name_encoded}">{install_label}</a>
      <a class="ar-btn ar-btn-ghost" href="/sourcea/factories/index.html">All factories</a>
    </div>
    <div id="sa-sandbox-demo" data-factory-id="{factory_id}" data-kind="{kind}" style="margin-top:2rem;display:none">
      <pre class="sa-email-snippet" id="sa-demo-output">Running 30s sandbox demo…</pre>
    </div>
  </div>
</main>
<script src="/assets/agentrun.js" defer></script>
<script src="/sourcea/sourcea-factories-hub.js" defer></script>
</body>
</html>
"""


def build(*, write_html: bool = True) -> dict:
    cat = catalog_payload()
    items = []
    for item in cat.get("items") or []:
        items.append(
            {
                "id": item.get("catalog_id"),
                "factory_id": item.get("factory_id"),
                "name": item.get("name"),
                "tagline": item.get("tagline"),
                "buyer": item.get("buyer"),
                "tier": item.get("tier"),
                "kind": item.get("kind"),
                "hero": item.get("hero"),
                "href": f"/sourcea/factories/{item.get('website_slug')}.html",
                "website_slug": item.get("website_slug"),
                "inputs": item.get("inputs"),
                "operational_nodes": item.get("operational_nodes"),
                "guaranteed_output": item.get("guaranteed_output"),
                "maintenance_fee_usd": item.get("maintenance_fee_usd"),
                "demo_seconds": item.get("demo_seconds"),
                "policy_pack_id": item.get("policy_pack_id"),
                "install_label": item.get("install_label") or "Deploy",
                "status": item.get("status"),
                "tier_cap_honest": item.get("tier_cap_honest"),
            }
        )

    out = {
        "schema": "sourcea-factories-catalog-v1",
        "built_at": _now(),
        "platform": cat.get("platform"),
        "tagline": cat.get("tagline"),
        "hero_factory_id": cat.get("hero_factory_id"),
        "factories": items,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    if write_html:
        FACTORIES_DIR.mkdir(parents=True, exist_ok=True)
        for item in items:
            slug = item.get("website_slug") or "factory"
            html = DETAIL_TEMPLATE.format(
                name=item.get("name") or slug,
                name_encoded=(item.get("name") or slug).replace(" ", "%20"),
                tagline=item.get("tagline") or "",
                slug=slug,
                tier_label=item.get("tier") or "engine",
                policy_pack_id=item.get("policy_pack_id") or "trust_motor",
                inputs=item.get("inputs") or "",
                operational_nodes=item.get("operational_nodes") or 76,
                guaranteed_output=item.get("guaranteed_output") or "",
                maintenance_fee_usd=item.get("maintenance_fee_usd") or 0,
                buyer=item.get("buyer") or "",
                status=item.get("status") or "prove_only",
                tier_cap_honest=item.get("tier_cap_honest") or "",
                install_label=item.get("install_label") or "Deploy",
                factory_id=item.get("factory_id") or "",
                kind=item.get("kind") or "engine",
            )
            (FACTORIES_DIR / f"{slug}.html").write_text(html, encoding="utf-8")

    return {"ok": True, "path": str(OUT_JSON), "count": len(items)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-html", action="store_true")
    args = ap.parse_args()
    row = build(write_html=not args.no_html)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK: {row['path']} ({row['count']} factories)")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
