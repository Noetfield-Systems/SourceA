#!/usr/bin/env python3
"""Reconcile portfolio products — case studies · platform SKUs · plan packs · auto-conflict."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCEA_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = SOURCEA_ROOT / "data/sourcea-products-catalog-v1.json"
RECEIPT_PATH = SOURCEA_ROOT / "data/sourcea-products-reconcile-receipt-v1.json"
AGENTGO_MASTER = SOURCEA_ROOT / "brain-os/plan-registry/AGENTGO_CASE_STUDY_6000_MASTER_v1.json"
PORTFOLIO_MASTER = SOURCEA_ROOT / "brain-os/plan-registry/PORTFOLIO_NEXT_6000_MASTER_v1.json"

CANONICAL_PRODUCTS = [
    {
        "id": "pureflow-case-study",
        "slug": "pureflow",
        "kind": "case_study",
        "rank": 1,
        "title": "PureFlow",
        "subtitle": "Case study #1 · Local trades acquisition",
        "buyer": "Pool & spa operators · local service businesses",
        "proof": "Live site + visit reports · 48-hour acquisition path",
        "url": "/sourcea/case-studies/pureflow",
        "live_url": "https://pureflow.sourcea.app/",
        "status": "shipped",
        "tier": "T1",
    },
    {
        "id": "agentgo-case-study",
        "slug": "agentgo",
        "kind": "case_study",
        "rank": 2,
        "title": "AgentGo",
        "subtitle": "Case study #2 · Factory-scale GEO surface",
        "buyer": "SaaS & marketing leaders · agency CTOs",
        "proof": "1,259 HTML pages · dual deploy · Wil L3 separation",
        "url": "/sourcea/case-studies/agentgo",
        "live_url": None,
        "status": "shipped",
        "tier": "T1",
        "metrics": {"html_pages": 1259, "research_topics": 592, "compare_pages": 83},
    },
    {
        "id": "asset-b-loop-build",
        "slug": "asset-b",
        "kind": "service",
        "rank": 3,
        "title": "Asset B · Agent Loop Build",
        "subtitle": "Fixed-scope controlled automation",
        "buyer": "Revenue agencies · platform teams",
        "proof": "Signed receipt · cross-lane guard · replay demo",
        "url": "/sourcea/offer",
        "price_band": "$3–10K",
        "status": "active",
        "tier": "T1",
    },
    {
        "id": "prompt-forge",
        "slug": "prompt-forge",
        "kind": "platform",
        "rank": 10,
        "title": "Prompt Forge",
        "subtitle": "Founder language → bounded mission",
        "buyer": "Founders · operators",
        "proof": "scoped prompt pipeline logged",
        "url": "/sourcea/forge/",
        "status": "active",
        "tier": "T2",
    },
    {
        "id": "chat-unify",
        "slug": "chat-unify",
        "kind": "platform",
        "rank": 11,
        "title": "Chat Unify",
        "subtitle": "Verify · audit · unify AI sessions",
        "buyer": "Power users · compliance teams",
        "proof": "Mac app · session truth gate",
        "url": "/downloads/chat-unify-mac-v1.dmg",
        "status": "active",
        "tier": "T2",
    },
    {
        "id": "cloud-workers",
        "slug": "cloud-workers",
        "kind": "platform",
        "rank": 12,
        "title": "Cloud Workers",
        "subtitle": "Factory proceed · OpenRouter on cloud",
        "buyer": "Engineering · factory operators",
        "proof": "Railway full-pack · receipt per tick",
        "url": "/sourcea/platform#cloud-workers",
        "status": "active",
        "tier": "T2",
    },
    {
        "id": "proof-loops",
        "slug": "loops",
        "kind": "platform",
        "rank": 13,
        "title": "Scoped loops",
        "subtitle": "Outreach · ops · research",
        "buyer": "Growth · ops teams",
        "proof": "Six loops · live scenario",
        "url": "/sourcea/loops/",
        "status": "active",
        "tier": "T2",
    },
    {
        "id": "sourcea-boot",
        "slug": "sourcea-boot",
        "kind": "eval",
        "rank": 5,
        "title": "sourcea-boot",
        "subtitle": "Self-serve gate eval",
        "buyer": "Platform engineers",
        "proof": "PASS/BLOCK before you buy",
        "url": "https://github.com/Noetfield-Systems/sourcea-boot",
        "status": "active",
        "tier": "T0",
    },
    {
        "id": "brain-public-chat",
        "slug": "brain-chat",
        "kind": "platform",
        "rank": 4,
        "title": "Brain · Public chat",
        "subtitle": "OpenRouter routing on sourcea.app",
        "buyer": "All visitors",
        "proof": "Live chat · proof chips · honest offline",
        "url": "/sourcea/scenario",
        "status": "active",
        "tier": "T1",
        "api": "/api/brain/chat/v1",
    },
]


def _load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _plan_pack_rows() -> list[dict]:
    rows = []
    ag = _load_json(AGENTGO_MASTER)
    if ag:
        rows.append(
            {
                "id": "agentgo-case-study-6000",
                "kind": "plan_pack",
                "title": "AgentGo case study 6000",
                "count": ag.get("plan_count", 6000),
                "schema_version": ag.get("schema_version"),
                "smart_tier": ag.get("smart_tier"),
                "pick": "bash scripts/plan-no-asf-run.sh pick-agentgo 3",
                "law": "docs/AGENTGO_SA4_CASE_STUDY_6000_PLANS_LOCKED_v1.md",
            }
        )
    pf = _load_json(PORTFOLIO_MASTER)
    if pf:
        rows.append(
            {
                "id": "portfolio-next-6000",
                "kind": "plan_pack",
                "title": "Portfolio next 6000",
                "count": pf.get("plan_count"),
                "schema_version": pf.get("schema_version"),
                "pick": "bash scripts/plan-no-asf-run.sh pick-next 3",
                "law": "docs/PORTFOLIO_UPGRADE_PLANS_CANONICAL_LOCKED_v1.md",
            }
        )
    return rows


def reconcile(*, write: bool = True) -> dict:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    by_slug: dict[str, dict] = {}
    conflicts: list[dict] = []

    for product in CANONICAL_PRODUCTS:
        slug = product["slug"]
        if slug in by_slug:
            prev = by_slug[slug]
            winner = product if product.get("rank", 99) < prev.get("rank", 99) else prev
            loser = prev if winner is product else product
            conflicts.append(
                {
                    "slug": slug,
                    "resolved_to": winner["id"],
                    "dropped": loser["id"],
                    "reason": "lower_rank_wins",
                }
            )
            by_slug[slug] = winner
        else:
            by_slug[slug] = product

    products = sorted(by_slug.values(), key=lambda p: (p.get("rank", 99), p["id"]))
    plan_packs = _plan_pack_rows()

    catalog = {
        "schema": "sourcea-products-catalog-v1",
        "version": "1.0.0",
        "generated_at": now,
        "product_count": len(products),
        "case_studies": [p for p in products if p["kind"] == "case_study"],
        "platform": [p for p in products if p["kind"] == "platform"],
        "services": [p for p in products if p["kind"] == "service"],
        "eval": [p for p in products if p["kind"] == "eval"],
        "products": products,
        "plan_packs": plan_packs,
        "conflicts_resolved": len(conflicts),
    }

    receipt = {
        "schema": "sourcea-products-reconcile-receipt-v1",
        "version": "1.0.0",
        "reconciled_at": now,
        "ok": True,
        "product_count": len(products),
        "conflicts": conflicts,
        "plan_packs": [p["id"] for p in plan_packs],
    }

    if write:
        CATALOG_PATH.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
        RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        landing_copy = SOURCEA_ROOT / "SourceA-landing/green-unified/data/sourcea-products-catalog-v1.json"
        landing_copy.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

    return {"catalog": catalog, "receipt": receipt}


def main() -> int:
    out = reconcile(write=True)
    print(json.dumps(out["receipt"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
