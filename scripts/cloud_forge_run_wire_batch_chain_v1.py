#!/usr/bin/env python3
"""Wire cloud-forge-run-queue-active-v1 next_batch chain through all locked batch files on disk."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = ROOT / "data/cloud-forge-run-queue-active-v1.json"
BATCH_GLOB = "data/secondary-cloud-forge-run-batch-{n}-locked-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def discover_batches() -> list[int]:
    out: list[int] = []
    for path in sorted((ROOT / "data").glob("secondary-cloud-forge-run-batch-*-locked-v1.json")):
        m = re.search(r"batch-(\d+)-", path.name)
        if m:
            out.append(int(m.group(1)))
    return sorted(out)


def batch_meta(batch_id: int) -> dict | None:
    path = ROOT / BATCH_GLOB.format(n=batch_id)
    if not path.is_file():
        return None
    doc = _read(path)
    summary = doc.get("summary") or {}
    return {
        "batch_id": batch_id,
        "status": "ready_locked",
        "queue_path": f"data/secondary-cloud-forge-run-batch-{batch_id}-locked-v1.json",
        "cloud_sec_range": summary.get("cloud_sec_range"),
    }


def wire(*, active_batch_id: int | None = None) -> dict:
    batches = discover_batches()
    if not batches:
        return {"ok": False, "error": "no_batches_on_disk"}

    ptr = _read(ACTIVE)
    bid = int(active_batch_id or ptr.get("batch_id") or batches[0])
    if bid not in batches:
        bid = max(b for b in batches if b <= bid) if any(b <= bid for b in batches) else batches[0]

    qpath = ROOT / BATCH_GLOB.format(n=bid)
    if not qpath.is_file():
        return {"ok": False, "error": "active_batch_file_missing", "batch_id": bid}

    doc = _read(qpath)
    cloud_plans = [p for p in (doc.get("plans") or []) if str(p.get("id", "")).startswith("CLOUD-SEC-")]
    first_head = str(cloud_plans[0].get("id")) if cloud_plans else ""

    idx = batches.index(bid)
    nxt = batches[idx + 1] if idx + 1 < len(batches) else None

    archives = {
        f"archive_batch{b}": BATCH_GLOB.format(n=b)
        for b in batches
        if b < bid and b != 1
    }
    if 1 in batches and bid > 1:
        complete = ROOT / "data/secondary-cloud-forge-run-batch-1-complete-locked-v1.json"
        legacy = ROOT / "data/secondary-cloud-forge-run-batch-1-locked-v1.json"
        if complete.is_file():
            archives["archive_batch1"] = "data/secondary-cloud-forge-run-batch-1-complete-locked-v1.json"
        elif legacy.is_file():
            archives["archive_batch1"] = "data/secondary-cloud-forge-run-batch-1-locked-v1.json"

    new_ptr = {
        "schema": "cloud-forge-run-queue-active-v1",
        "version": "1.1.0",
        "batch_id": bid,
        "locked": True,
        "saved_at": _now(),
        "queue_path": BATCH_GLOB.format(n=bid),
        **archives,
        "phase_reset": {
            "cloud_forge_run_head": first_head,
            "cloud_forge_run_last_completed": None,
            "queue_batch_complete": False,
        },
        "cloud_workers_feed": ptr.get("cloud_workers_feed")
        or {
            "machine": "scripts/cloud_workers_hub_v1.py",
            "control_plane": "data/cloud-workers-control-plane-v1.json",
            "auto_runtime": "data/cloud-auto-runtime-v1.json",
            "cockpit": "Cloud Workers.app :13027 — Proceed full-pack · no Worker Hub required",
        },
        "proof_url": ptr.get("proof_url")
        or "https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/queue/v1",
    }
    if nxt is not None:
        meta = batch_meta(nxt)
        if meta:
            new_ptr["next_batch"] = meta
    else:
        new_ptr.pop("next_batch", None)

    ACTIVE.write_text(json.dumps(new_ptr, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "schema": "cloud-forge-run-batch-chain-wire-v1",
        "active_batch_id": bid,
        "head": first_head,
        "next_batch": new_ptr.get("next_batch"),
        "batches_on_disk": batches,
        "pointer": str(ACTIVE),
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=0, help="Active batch id (default: keep pointer)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = wire(active_batch_id=args.batch or None)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("head") or row.get("error"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
