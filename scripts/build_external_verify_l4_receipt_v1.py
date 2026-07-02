#!/usr/bin/env python3
"""Build L4 external-verify receipt from founder_proof_15 (body hashes required)."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def build_receipt(
    *,
    founder_proof: dict[str, Any],
    run_id: str,
    sha: str,
    run_url: str,
    trigger_source: str = "",
    deploy_run_id: str = "",
    deploy_run_url: str = "",
) -> dict[str, Any]:
    rows = founder_proof.get("rows") or []
    checks: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        pf = row.get("public_fetch") if isinstance(row.get("public_fetch"), dict) else {}
        if not pf and isinstance(row.get("regional_redirect_fetch"), dict):
            pf = row["regional_redirect_fetch"]
        checks.append(
            {
                "recipe_id": row.get("recipe_id"),
                "url": row.get("live_url"),
                "verdict": row.get("verdict"),
                "http_status": pf.get("http_code"),
                "body_sha256": pf.get("body_sha256_full") or pf.get("body_sha256_prefix"),
                "body_bytes": pf.get("body_bytes"),
                "defect": row.get("defect") or (row.get("defects") or [""])[0],
            }
        )
    passed = int(founder_proof.get("passed") or 0)
    total = int(founder_proof.get("total") or len(rows))
    proof_ok = bool(founder_proof.get("ok")) and passed == total and total == 15
    chain = trigger_source == "deploy_workflow_run_chain"
    return {
        "schema": "external-verify-l4-receipt-v1",
        "version": "1.0.0",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "law": "L4 buyer surfaces — founder_proof_15 with body_sha256",
        "github_run_id": run_id,
        "github_sha": sha,
        "run_url": run_url,
        "workflow": "external-verify.yml",
        "runner": "github_actions",
        "trigger_source": trigger_source or "push",
        "platform_native": {
            "item": "PN-001-workflow_run_chain",
            "deploy_run_id": deploy_run_id or None,
            "deploy_run_url": deploy_run_url or None,
            "chain_active": chain,
            "retired_hand_roll": [
                "publish_sourcea_landing run_founder_proof_verify min_seconds=60 sleep",
                "manual timing guess between deploy complete and external verify",
            ],
        },
        "ok": proof_ok,
        "founder_proof_15": founder_proof,
        "checks": checks,
        "report_line": (
            f"external-verify-l4 {'PASS' if proof_ok else 'FAIL'} · "
            f"15-recipe={passed}/{total} · run={run_id}"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--founder-proof", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    proof = json.loads(Path(args.founder_proof).read_text(encoding="utf-8"))
    row = build_receipt(
        founder_proof=proof,
        run_id=os.environ.get("GITHUB_RUN_ID", ""),
        sha=os.environ.get("GITHUB_SHA", ""),
        run_url=os.environ.get("GITHUB_RUN_URL", ""),
        trigger_source=os.environ.get("VERIFY_TRIGGER_SOURCE", ""),
        deploy_run_id=os.environ.get("DEPLOY_RUN_ID", ""),
        deploy_run_url=os.environ.get("DEPLOY_RUN_URL", ""),
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
