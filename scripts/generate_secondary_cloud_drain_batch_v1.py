#!/usr/bin/env python3
"""Generate locked cloud drain queue batch N (10 MAC-CTL + 100 CLOUD-SEC)."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os/plan-registry/sourcea-competitor-1000/REGISTRY.json"
ACTIVE_POINTER = ROOT / "data/cloud-drain-queue-active-v1.json"
BATCH1_ARCHIVE = ROOT / "data/secondary-cloud-drain-batch-1-complete-locked-v1.json"
LEGACY = ROOT / "data/secondary-cloud-drain-next-100-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


MAC_TITLES = [
    ("CHECK", "Read mac-law + federated-run receipts · cloud worker URL glance only"),
    ("ACT", "Hub POST dispatch dry-run · read cloud receipt (no Mac body)"),
    ("VERIFY", "Read brain-cloud pulse receipt · cloud executed not Mac"),
    ("VOCAB", "Read mac-worker-vs-factory vocabulary SSOT · confirm cloud executes factory body"),
    ("DISPATCH", "Hub POST dry-run /api/cloud-worker/dispatch/v1 · read dispatch receipt only"),
    ("SECRETS", "Confirm secrets path ~/.sourcea-secrets only · no repo env · glance"),
    ("FORGE_RCPT", "Read forge/federated cloud receipts · portfolio-competitor manifest glance"),
    ("LOOP_TICK", "Read loop-specialist tick receipt · cloud tick not Mac motor"),
    ("ADAPTER", "Read fbe-cloud-adapter receipt — Mac glance only"),
    ("FREEZE", "Read factory-now FREEZE + mac-law lock receipts · no fbe_motor_delegate on Mac"),
]


def generate_batch(*, batch_id: int, offset: int, count: int = 100, lock: bool = True) -> dict:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    backlog = [p for p in reg.get("plans") or [] if p.get("status") == "backlog"]
    slice_rows = backlog[offset : offset + count]
    if len(slice_rows) < count:
        raise SystemExit(f"FAIL: need {count} backlog rows at offset {offset}, got {len(slice_rows)}")

    mac_base = (batch_id - 1) * 10
    cloud_base = (batch_id - 1) * 100
    out: list[dict] = []

    for i, (verb, title) in enumerate(MAC_TITLES, 1):
        mac_n = mac_base + i
        out.append(
            {
                "n": i,
                "id": f"MAC-CTL-{mac_n:03d}",
                "bind": f"W-CLOUD-{mac_n:03d}" if i <= 3 else None,
                "plane": "mac_control",
                "batch_id": batch_id,
                "mac_role": "observe · optional Hub dispatch POST · read receipt only — no validate-* on Mac",
                "mac_build_forbidden": True,
                "mac_executes_plan_body": False,
                "title": f"Mac control {verb} (batch {batch_id}): {title}",
            }
        )

    for j, p in enumerate(slice_rows, 11):
        cloud_n = cloud_base + (j - 10)
        tier = str(p.get("tier") or "T2")
        cost = "free" if tier in ("T0", "T3") else "openrouter_cap"
        out.append(
            {
                "n": j,
                "id": f"CLOUD-SEC-{cloud_n:03d}",
                "maps_registry": p["id"],
                "plane": "cloud_forge",
                "batch_id": batch_id,
                "mac_role": "none — batch dispatch POST optional · read receipt after",
                "mac_executes_plan_body": False,
                "stack": "sourcea",
                "competitor": p.get("competitor"),
                "workstream": p.get("workstream"),
                "tier": tier,
                "cost_tier": cost,
                "cloud_action": (p.get("title") or "")[:220],
            }
        )

    first_cloud = f"CLOUD-SEC-{cloud_base + 1:03d}"
    last_cloud = f"CLOUD-SEC-{cloud_base + count:03d}"
    maps_lo = slice_rows[0]["id"]
    maps_hi = slice_rows[-1]["id"]

    return {
        "schema": "secondary-cloud-drain-batch-v1",
        "version": "2.0.0",
        "batch_id": batch_id,
        "locked": lock,
        "edit_forbidden": lock,
        "saved_at": _now(),
        "authority": "INCIDENT-038 v1.1 · batch-2 handoff",
        "one_law": "1-10 Mac control only. 11-110 cloud secondary drain. Mac NEVER executes sa-mkt bodies.",
        "forbidden": ["Worker on Mac runs every plan", "RUN INBOX per sa-mkt on Mac", "hand-edit while locked"],
        "incident_ref": "brain-os/incidents/SINA_AGENT_WORKER_FACTORY_PLANE_CONFLATION_INCIDENT_038_LOCKED_v1.md",
        "generator": "scripts/generate_secondary_cloud_drain_batch_v1.py",
        "registry_offset": offset,
        "registry_count": count,
        "supersedes_batch": batch_id - 1 if batch_id > 1 else None,
        "count": len(out),
        "summary": {
            "mac_control": 10,
            "cloud_forge": count,
            "batch_id": batch_id,
            "maps_registry": f"{maps_lo} through {maps_hi}",
            "cloud_sec_range": f"{first_cloud}..{last_cloud}",
        },
        "plans": out,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=2)
    ap.add_argument("--offset", type=int, default=90)
    ap.add_argument("--count", type=int, default=100)
    ap.add_argument("--lock", action="store_true", default=True)
    ap.add_argument("--activate", action="store_true", default=True)
    ap.add_argument("--archive-batch1", action="store_true", default=True)
    args = ap.parse_args()

    out_path = ROOT / f"data/secondary-cloud-drain-batch-{args.batch}-locked-v1.json"
    doc = generate_batch(batch_id=args.batch, offset=args.offset, count=args.count, lock=args.lock)
    out_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    if args.archive_batch1 and LEGACY.is_file() and not BATCH1_ARCHIVE.is_file():
        shutil.copy2(LEGACY, BATCH1_ARCHIVE)
        arch = json.loads(BATCH1_ARCHIVE.read_text(encoding="utf-8"))
        arch["batch_id"] = 1
        arch["batch_status"] = "complete"
        arch["completed_at"] = _now()
        arch["locked"] = True
        BATCH1_ARCHIVE.write_text(json.dumps(arch, indent=2) + "\n", encoding="utf-8")

    first_cloud = doc["summary"]["cloud_sec_range"].split("..")[0]
    ptr = {
        "schema": "cloud-drain-queue-active-v1",
        "version": "1.0.0",
        "batch_id": args.batch,
        "locked": True,
        "saved_at": _now(),
        "queue_path": f"data/secondary-cloud-drain-batch-{args.batch}-locked-v1.json",
        "archive_batch1": "data/secondary-cloud-drain-batch-1-complete-locked-v1.json",
        "phase_reset": {
            "cloud_drain_head": first_cloud,
            "cloud_drain_last_completed": None,
            "queue_batch_complete": False,
        },
        "cloud_workers_feed": {
            "machine": "scripts/cloud_workers_hub_v1.py",
            "control_plane": "data/cloud-workers-control-plane-v1.json",
            "auto_runtime": "data/cloud-drain-auto-runtime-v1.json",
        },
    }
    if args.activate:
        ACTIVE_POINTER.write_text(json.dumps(ptr, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"ok": True, "batch": args.batch, "path": str(out_path), "head": first_cloud, "pointer": str(ACTIVE_POINTER)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
