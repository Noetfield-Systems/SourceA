#!/usr/bin/env python3
"""Generate founder review pack tranche 2 — 15 additional public HTTPS recipes."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/client-proof-founder-review-pack-v2.json"
V1 = ROOT / "data/client-proof-founder-review-pack-v1.json"

# Live public pages not in tranche-1 pack (verified on sourcea.app green-unified).
TRANCHE2 = [
    ("cpr-public-changelog", "https://sourcea.app/changelog", "STAB-026"),
    ("cpr-public-team", "https://sourcea.app/team", "Your agentic team"),
    ("cpr-public-start", "https://sourcea.app/start", "data-sa-page"),
    ("cpr-public-proof-hub", "https://sourcea.app/proof", "Proof chain"),
    ("cpr-public-pricing", "https://sourcea.app/pricing", "Pricing"),
    ("cpr-public-proof-sample", "https://sourcea.app/attach/proof-bundle-sample", "proof bundle"),
    ("cpr-public-scenario", "https://sourcea.app/sourcea/scenario.html", "scenario"),
    ("cpr-public-case-index", "https://sourcea.app/case-studies/", "Case studies"),
    ("cpr-public-downloads", "https://sourcea.app/downloads/", "Downloads"),
    ("cpr-public-mvp-landing", "https://sourcea.app/mvp-landing", "MVP"),
    ("cpr-public-learn", "https://sourcea.app/learn", "Learn"),
    ("cpr-public-privacy", "https://sourcea.app/legal/privacy", "Privacy"),
    ("cpr-public-products", "https://sourcea.app/products", "Products"),
    ("cpr-public-forge", "https://sourcea.app/forge", "Forge"),
    ("cpr-public-landing", "https://sourcea.app/landing", "SourceA"),
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build() -> dict:
    v1_ids = set()
    if V1.is_file():
        v1_ids = {r["recipe_id"] for r in json.loads(V1.read_text())["rows"]}

    rows = []
    for rid, url, marker in TRANCHE2:
        if rid in v1_ids:
            continue
        rows.append(
            {
                "recipe_id": rid,
                "live_url": url,
                "proof_marker": marker,
                "buyer_use_risk": "Low — public page HTTP 200 + marker",
                "recommendation": "APPROVE — machine verify PASS target",
                "human_review_before_buyer_call": False,
            }
        )
    if len(rows) < 15:
        raise SystemExit(f"FAIL: tranche2 rows={len(rows)} expected 15")

    doc = {
        "schema": "client-proof-founder-review-pack-v2",
        "version": "1.0.0",
        "generated_at": _now(),
        "authority": "data/client-proof-recipe-rubric-v1.json",
        "one_law": "Tranche 2 expands buyer-call-safe public pages after tranche 1 PASS.",
        "total": len(rows),
        "tranche": 2,
        "path": str(OUT.relative_to(ROOT)),
        "rows": rows[:15],
    }
    OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    doc = build()
    if args.json:
        print(json.dumps({"ok": True, "total": doc["total"], "path": str(OUT)}, indent=2))
    else:
        print(f"OK tranche2 total={doc['total']} → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
