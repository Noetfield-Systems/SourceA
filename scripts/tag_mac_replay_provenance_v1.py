#!/usr/bin/env python3
"""Tag Supabase rows with origin=mac_replay where Railway artifact is absent — provenance only."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _patch_origin(*, plan_id: str, origin: str, cfg: dict[str, str]) -> dict[str, Any]:
    params = urllib.parse.urlencode({"plan_id": f"eq.{plan_id}"})
    url = f"{cfg['url'].rstrip('/')}/rest/v1/{cfg['table']}?{params}"
    payload = json.dumps({"origin": origin, "updated_at": _now()}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "apikey": cfg["key"],
            "Authorization": f"Bearer {cfg['key']}",
            "Prefer": "return=minimal",
        },
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return {"ok": 200 <= resp.status < 300, "plan_id": plan_id, "status": resp.status}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "plan_id": plan_id, "status": exc.code, "error": exc.read().decode("utf-8", errors="replace")[:200]}
    except Exception as exc:
        return {"ok": False, "plan_id": plan_id, "error": str(exc)[:200]}


def tag_mac_replay(*, batch_id: int, railway_url: str, dry_run: bool = False) -> dict[str, Any]:
    os.environ["CLOUD_FORGE_RUN_SUPABASE_ALLOW_MAC"] = "1"
    sys.path.insert(0, str(ROOT / "scripts"))
    from cloud_forge_run_supabase_v1 import (  # noqa: WPS433
        _supabase_cfg,
        apply_migration_if_missing,
        apply_origin_migration,
        batch_plan_ids_from_doc,
        count_batch_in_supabase,
        count_batch_on_railway,
        ensure_env,
        table_probe,
    )

    ensure_env()
    probe = table_probe()
    if not probe.get("exists"):
        apply_migration_if_missing()
    apply_origin_migration()
    batch_path = ROOT / f"data/secondary-cloud-forge-run-batch-{batch_id}-locked-v1.json"
    plan_ids = batch_plan_ids_from_doc(json.loads(batch_path.read_text(encoding="utf-8")))
    sb = count_batch_in_supabase(plan_ids=plan_ids)
    rw = count_batch_on_railway(plan_ids=plan_ids, base_url=railway_url)
    railway_present = set(rw.get("present") or [])
    sb_present = set(sb.get("present") or [])
    mac_candidates = sorted(sb_present - railway_present)
    cfg = _supabase_cfg()
    tagged: list[dict[str, Any]] = []
    if not dry_run:
        for pid in mac_candidates:
            tagged.append(_patch_origin(plan_id=pid, origin="mac_replay", cfg=cfg))
    from cloud_forge_run_supabase_v1 import batch_sink_invariant  # noqa: WPS433

    invariant = batch_sink_invariant(batch_id=batch_id, railway_url=railway_url)
    row = {
        "ok": invariant.get("ok"),
        "schema": "cloud-forge-mac-replay-provenance-v1",
        "at": _now(),
        "batch_id": batch_id,
        "mac_candidates": mac_candidates,
        "tagged": tagged if not dry_run else [],
        "dry_run": dry_run,
        "invariant": invariant,
    }
    out = ROOT / "receipts" / "cloud-forge-run" / f"batch-{batch_id}-mac-replay-provenance-v1.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    SINA.mkdir(parents=True, exist_ok=True)
    (SINA / f"cloud-forge-batch-{batch_id}-mac-replay-provenance-v1.json").write_text(
        json.dumps({"ok": row["ok"], "at": row["at"], "path": str(out)}, indent=2) + "\n"
    )
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--batch-id", type=int, default=77)
    ap.add_argument("--railway-url", default="https://sourcea-fbe-runner-production.up.railway.app")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = tag_mac_replay(batch_id=args.batch_id, railway_url=args.railway_url, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"mac_replay candidates={len(row['mac_candidates'])} "
            f"invariant={row['invariant'].get('verdict')}"
        )
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
