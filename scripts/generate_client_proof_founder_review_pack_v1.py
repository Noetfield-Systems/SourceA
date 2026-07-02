#!/usr/bin/env python3
"""Generate 15-recipe founder review pack — revenue unlock before queue expansion."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "client-proof-recipe-queue-v1.json"
OUT = ROOT / "data" / "client-proof-founder-review-pack-v1.json"
SINA_RECEIPT = Path.home() / ".sina" / "client-proof-founder-review-pack-v1.json"

MARKER_HINTS: dict[str, str] = {
    "cpr-eval-boot": 'data-sa-page="sourcea-boot-eval" · pip install sourcea-boot',
    "cpr-contract-operating-brain": "validate-sourcea-contract-pages-e2e PASS · /operating-brain-install",
    "cpr-contract-aivg": "validate-sourcea-contract-pages-e2e PASS · /ai-value-governance",
    "cpr-contract-eacp": "validate-sourcea-contract-pages-e2e PASS · /enterprise-ai-control-plane",
    "cpr-live-receipt": "ok=true or verdict field in /sourcea/proof/live JSON",
    "cpr-forge-terminal": "Forge Terminal · data-sa-proof-cta",
    "cpr-free-job-intake": "data-sa-page=\"proof-sandbox\" · sa-sandbox-intake-form · mvp-intake e2e POST/read-back",
    "cpr-railway-observer": "Railway queue API ok=true · execution_plane headless_cloud",
    "cpr-supabase-rows": "cloud_forge_run_supabase_v1.py --query --count total > 0",
    "cpr-proof-export-loop": "Proof export · retainer",
    "cpr-agency-onepager": "Agency overview · proof",
    "cpr-procurement-pack": "Procurement · ISO",
    "cpr-pureflow-case": "PureFlow · 48-hour",
    "cpr-agentgo-case": "AgentGo · agency",
    "cpr-brain-chat": "Brain worker health HTTP 200",
}

RISK: dict[str, str] = {
    "cpr-eval-boot": "Medium — prospect laptop pip path must match live eval copy",
    "cpr-contract-operating-brain": "Low — contract E2E locked; proof strip on page",
    "cpr-contract-aivg": "Low — regional mirror; hreflang must stay wired",
    "cpr-contract-eacp": "Low — UK mirror; demo panel read-only",
    "cpr-live-receipt": "Low — buyer-proof hotfix PASS on both hosts",
    "cpr-forge-terminal": "Medium — terminal ALLOW/BLOCK beat needs live walkthrough",
    "cpr-free-job-intake": "Medium — intake form → MVP worker path must work on call",
    "cpr-railway-observer": "Low — infra receipt; not buyer-facing URL alone",
    "cpr-supabase-rows": "Medium — no public URL; show row count delta only",
    "cpr-proof-export-loop": "Low — marketing loop page",
    "cpr-agency-onepager": "Low — attach PDF/HTML outbound",
    "cpr-procurement-pack": "Low — regulated buyer pack",
    "cpr-pureflow-case": "Medium — case study claims need founder comfort",
    "cpr-agentgo-case": "Medium — case study claims need founder comfort",
    "cpr-brain-chat": "Medium — answer quality varies; disk-backed not guaranteed every Q",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _marker(row: dict[str, Any]) -> str:
    pid = str(row.get("plan_id") or "")
    if pid in MARKER_HINTS:
        return MARKER_HINTS[pid]
    verify = str(row.get("verify") or "")
    markers = re.findall(r'--marker\s+"([^"]+)"', verify)
    if markers:
        return " · ".join(markers[:3])
    if "assert" in verify:
        return verify.split("assert", 1)[-1][:120].strip()
    return str(row.get("done_when") or "")[:120]


def _recommendation(row: dict[str, Any]) -> str:
    return "APPROVE — machine verify PASS target"


def _live_url(row: dict[str, Any]) -> str:
    artifact = str(row.get("proof_artifact") or "")
    if artifact.startswith("http"):
        return artifact
    return artifact


def build() -> dict[str, Any]:
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    proven = [r for r in (queue.get("items") or []) if r.get("proven")]
    if len(proven) != 15:
        raise SystemExit(f"FAIL: expected 15 proven recipes, got {len(proven)}")

    rows = []
    for r in proven:
        rows.append(
            {
                "recipe_id": r.get("plan_id"),
                "live_url": _live_url(r),
                "proof_marker": _marker(r),
                "buyer_use_risk": RISK.get(str(r.get("plan_id") or ""), "Medium — review verify command"),
                "recommendation": _recommendation(r),
                "human_review_before_buyer_call": bool(r.get("human_review_before_buyer_call")),
            }
        )

    human_first = sorted(rows, key=lambda x: (not x["human_review_before_buyer_call"], x["recipe_id"]))
    doc = {
        "schema": "client-proof-founder-review-pack-v1",
        "version": "1.0.0",
        "generated_at": _now(),
        "authority": "data/client-proof-recipe-rubric-v1.json",
        "one_law": "Founder approves proven recipes before buyer calls — queue expansion waits on this pack.",
        "total": len(human_first),
        "human_review_count": sum(1 for x in human_first if x["human_review_before_buyer_call"]),
        "path": str(OUT.relative_to(ROOT)),
        "rows": human_first,
    }
    OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    SINA_RECEIPT.write_text(json.dumps({"ok": True, "at": doc["generated_at"], "path": str(OUT)}, indent=2) + "\n")
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    doc = build()
    if args.json:
        print(json.dumps({"ok": True, "path": str(OUT), "total": doc["total"]}, indent=2))
    else:
        print(f"OK founder-review-pack total={doc['total']} → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
