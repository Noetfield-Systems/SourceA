#!/usr/bin/env python3
"""Backfill missing batch CLOUD-SEC rows → forge-seed receipt + Supabase (retry until ack)."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT_DIR = ROOT / "receipts" / "cloud-forge-run"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_missing(*, batch_id: int, reconcile_path: Path | None) -> list[str]:
    path = reconcile_path or ROOT / f"data/cloud-forge-batch-{batch_id}-supabase-reconcile-v1.json"
    if path.is_file():
        doc = json.loads(path.read_text(encoding="utf-8"))
        return list(doc.get("missing_ids") or [])
    sys.path.insert(0, str(ROOT / "scripts"))
    from cloud_forge_run_supabase_v1 import batch_plan_ids_from_doc, count_batch_in_supabase  # noqa: WPS433

    batch_path = ROOT / f"data/secondary-cloud-forge-run-batch-{batch_id}-locked-v1.json"
    doc = json.loads(batch_path.read_text(encoding="utf-8"))
    plan_ids = batch_plan_ids_from_doc(doc)
    sb = count_batch_in_supabase(plan_ids=plan_ids)
    return list(sb.get("missing") or [])


def _railway_artifact(*, plan_id: str, base_url: str) -> dict[str, Any] | None:
    url = f"{base_url.rstrip('/')}/api/cloud-forge-run/evidence-audit/v1?plan_id={urllib.parse.quote(plan_id)}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            detail = json.loads(resp.read().decode("utf-8", errors="replace"))
        art = detail.get("artifact") if isinstance(detail.get("artifact"), dict) else None
        return art if detail.get("ok") and art else None
    except (urllib.error.HTTPError, OSError, json.JSONDecodeError):
        return None


def backfill(
    *,
    batch_id: int,
    railway_url: str = "https://sourcea-fbe-runner-production.up.railway.app",
    reconcile_path: Path | None = None,
) -> dict[str, Any]:
    import os

    os.environ["CLOUD_FORGE_RUN_SUPABASE_ALLOW_MAC"] = "1"
    sys.path.insert(0, str(ROOT / "scripts"))
    from cloud_forge_run_supabase_v1 import (  # noqa: WPS433
        batch_sink_invariant,
        ensure_env,
        persist_shipped_row,
        row_from_ship,
        upsert_row_with_retry,
    )
    from cloud_forge_seed_v1 import run_forge_seed_cycle  # noqa: WPS433

    ensure_env()
    missing = _load_missing(batch_id=batch_id, reconcile_path=reconcile_path)
    results: list[dict[str, Any]] = []
    backfilled = 0
    for plan_id in missing:
        source = "railway_receipt"
        artifact_doc = _railway_artifact(plan_id=plan_id, base_url=railway_url)
        cycle_row: dict[str, Any] | None = None
        if artifact_doc:
            cycle_row = {
                "ok": True,
                "plan_id": plan_id,
                "at": artifact_doc.get("at") or _now(),
                "validator_result": "PASS",
                "artifact_path": f"receipts/forge-seed/{plan_id}/artifact-v1.json",
                "forge_seed_artifact": artifact_doc,
            }
        else:
            source = "forge_seed_replay"
            seed = run_forge_seed_cycle(plan_id=plan_id, dry_run=False, root=ROOT)
            if not seed.get("ok"):
                results.append({"plan_id": plan_id, "ok": False, "source": source, "error": seed.get("failure_class") or seed.get("error") or "seed_failed", "seed": seed})
                continue
            artifact_doc = seed.get("forge_seed_artifact") if isinstance(seed.get("forge_seed_artifact"), dict) else {}
            cycle_row = seed
        sb = persist_shipped_row(cycle_row, artifact_doc=artifact_doc)
        if not sb.get("ok"):
            ship_row = row_from_ship(plan_id=plan_id, cycle_row=cycle_row, plan=None, artifact_doc=artifact_doc or {})
            sb = upsert_row_with_retry(ship_row)
        ok = bool(sb.get("ok"))
        if ok:
            backfilled += 1
        results.append({"plan_id": plan_id, "ok": ok, "source": source, "supabase": sb})

    invariant = batch_sink_invariant(batch_id=batch_id, railway_url=railway_url)
    row = {
        "ok": invariant.get("ok"),
        "schema": "cloud-forge-batch-supabase-backfill-v1",
        "at": _now(),
        "batch_id": batch_id,
        "requested": len(missing),
        "backfilled": backfilled,
        "failed": len(missing) - backfilled,
        "invariant": invariant,
        "results": results,
        "root_cause": "batching_bug",
        "root_cause_detail": (
            "100-row pack advanced queue head without requiring Supabase ack; "
            "persist_shipped_row failures were logged but did not block advance_on_pass"
        ),
    }
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    out = RECEIPT_DIR / f"batch-{batch_id}-supabase-backfill-receipt-v1.json"
    out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    row["artifact_path"] = str(out)
    SINA.mkdir(parents=True, exist_ok=True)
    (SINA / f"cloud-forge-batch-{batch_id}-supabase-backfill-receipt-v1.json").write_text(
        json.dumps({"ok": row["ok"], "at": row["at"], "path": str(out)}, indent=2) + "\n"
    )
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--batch-id", type=int, default=77)
    ap.add_argument("--reconcile", type=Path)
    ap.add_argument("--railway-url", default="https://sourcea-fbe-runner-production.up.railway.app")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = backfill(batch_id=args.batch_id, railway_url=args.railway_url, reconcile_path=args.reconcile)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"OK backfill batch {row['batch_id']}: {row['backfilled']}/{row['requested']} · "
            f"invariant={row['invariant'].get('verdict')}"
        )
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
