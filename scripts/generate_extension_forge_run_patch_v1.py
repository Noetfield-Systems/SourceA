#!/usr/bin/env python3
"""Wave 2 extension patch — remaining noetfield-1000 + mono-1000 plans → batches 51+ for Railway."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/portfolio-extension-wave2-manifest-v1.json"
ACTIVE = ROOT / "data/cloud-forge-run-queue-active-v1.json"
PIPELINE = ROOT / "data/cloud-forge-run-batch-pipeline-v1.json"
PATCH_RECEIPT = ROOT / "data/cloud-forge-run-extension-wave2-patch-v1.json"

MAC_TITLES = [
    ("CHECK", "Read mac-law + federated-run receipts · cloud worker URL glance only"),
    ("ACT", "Hub POST dispatch dry-run · read cloud receipt (no Mac body)"),
    ("VERIFY", "Read brain-cloud pulse receipt · cloud executed not Mac"),
    ("VOCAB", "Read mac-worker-vs-factory vocabulary SSOT · confirm cloud executes factory body"),
    ("DISPATCH", "Hub POST dry-run /api/cloud-worker/dispatch/v1 · read dispatch receipt only"),
    ("SECRETS", "Confirm secrets path ~/.sourcea-secrets only · no repo env · glance"),
    ("FORGE_RCPT", "Read forge/federated cloud receipts · portfolio-extension manifest glance"),
    ("LOOP_TICK", "Read loop-specialist tick receipt · cloud tick not Mac motor"),
    ("ADAPTER", "Read fbe-cloud-adapter receipt — Mac glance only"),
    ("FREEZE", "Read factory-now FREEZE + mac-law lock receipts · no fbe_motor_delegate on Mac"),
]

BATCH_SIZE = 100


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _batch_path(batch_id: int) -> Path:
    return ROOT / f"data/secondary-cloud-forge-run-batch-{batch_id}-locked-v1.json"


def _registry_path(row: dict[str, Any]) -> Path:
    pack = Path(str(row.get("pack") or ""))
    reg = pack / "REGISTRY.json"
    if not reg.is_file():
        raise SystemExit(f"FAIL: registry missing for {row.get('stack')}: {reg}")
    return reg


def generate_batch(
    *,
    batch_id: int,
    stack: str,
    library: str,
    registry_path: Path,
    slice_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    count = len(slice_rows)
    mac_base = (batch_id - 1) * 10
    cloud_base = (batch_id - 1) * 100
    out: list[dict[str, Any]] = []

    for i, (verb, title) in enumerate(MAC_TITLES, 1):
        mac_n = mac_base + i
        out.append(
            {
                "n": i,
                "id": f"MAC-CTL-{mac_n:03d}",
                "bind": f"W-CLOUD-{mac_n:03d}" if i <= 3 else None,
                "plane": "mac_control",
                "batch_id": batch_id,
                "stack": stack,
                "library": library,
                "mac_role": "observe · optional Hub dispatch POST · read receipt only — no validate-* on Mac",
                "mac_build_forbidden": True,
                "mac_executes_plan_body": False,
                "title": f"Mac control {verb} (batch {batch_id} · {stack}): {title}",
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
                "stack": stack,
                "library": library,
                "mac_role": "none — batch dispatch POST optional · read receipt after",
                "mac_executes_plan_body": False,
                "workstream": p.get("phase") or p.get("workstream"),
                "tier": tier,
                "cost_tier": cost,
                "cloud_action": (p.get("title") or p.get("agent_prompt") or "")[:220],
            }
        )

    first_cloud = f"CLOUD-SEC-{cloud_base + 1:03d}"
    last_cloud = f"CLOUD-SEC-{cloud_base + count:03d}"
    return {
        "schema": "secondary-cloud-forge-run-batch-v1",
        "version": "2.2.0",
        "batch_id": batch_id,
        "stack": stack,
        "library": library,
        "locked": True,
        "edit_forbidden": True,
        "saved_at": _now(),
        "authority": "extension-wave2 · remaining no-asf libraries",
        "one_law": "1-10 Mac control only. 11+ cloud secondary drain. Mac NEVER executes plan bodies.",
        "forbidden": ["Worker on Mac runs every plan", "RUN INBOX per plan on Mac", "hand-edit while locked"],
        "generator": "scripts/generate_extension_forge_run_patch_v1.py",
        "registry_path": str(registry_path),
        "registry_count": count,
        "supersedes_batch": batch_id - 1 if batch_id > 1 else None,
        "count": len(out),
        "summary": {
            "mac_control": 10,
            "cloud_forge": count,
            "batch_id": batch_id,
            "stack": stack,
            "library": library,
            "maps_registry": f"{slice_rows[0]['id']} through {slice_rows[-1]['id']}",
            "cloud_sec_range": f"{first_cloud}..{last_cloud}",
        },
        "plans": out,
    }


def _backlog_slice(registry_path: Path, offset: int, limit: int) -> list[dict[str, Any]]:
    reg = json.loads(registry_path.read_text(encoding="utf-8"))
    backlog = [p for p in reg.get("plans") or [] if p.get("status") == "backlog"]
    return backlog[offset : offset + limit]


def build_patch(*, force: bool = False, activate_batch: int | None = None) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    start_batch = int(manifest.get("batch_start") or 51)
    batch_id = start_batch
    generated: list[dict[str, Any]] = []
    skipped: list[int] = []
    source_slices: list[dict[str, Any]] = []

    for src in manifest.get("sources") or []:
        stack = str(src.get("stack") or "")
        library = str(src.get("library") or "")
        reg_path = _registry_path(src)
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
        backlog = [p for p in reg.get("plans") or [] if p.get("status") == "backlog"]
        offset = 0
        while offset < len(backlog):
            chunk = backlog[offset : offset + BATCH_SIZE]
            if not chunk:
                break
            out_path = _batch_path(batch_id)
            if out_path.is_file() and not force:
                skipped.append(batch_id)
                batch_id += 1
                offset += len(chunk)
                continue
            doc = generate_batch(
                batch_id=batch_id,
                stack=stack,
                library=library,
                registry_path=reg_path,
                slice_rows=chunk,
            )
            doc["registry_offset"] = offset
            out_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
            generated.append(
                {
                    "batch_id": batch_id,
                    "stack": stack,
                    "library": library,
                    "path": str(out_path),
                    "range": doc["summary"]["cloud_sec_range"],
                    "count": len(chunk),
                }
            )
            source_slices.append(
                {
                    "stack": stack,
                    "library": library,
                    "batch_id": batch_id,
                    "maps_registry": doc["summary"]["maps_registry"],
                }
            )
            batch_id += 1
            offset += len(chunk)

    last_batch = batch_id - 1
    if last_batch < start_batch:
        raise SystemExit("FAIL: no extension batches generated — all sources empty?")

    act = int(activate_batch or start_batch)
    batches_meta: list[dict[str, Any]] = []
    for bid in range(1, last_batch + 1):
        if bid == 1:
            path = "data/secondary-cloud-forge-run-batch-1-complete-locked-v1.json"
        else:
            path = f"data/secondary-cloud-forge-run-batch-{bid}-locked-v1.json"
        p = ROOT / path.replace("data/", "data/")
        if not p.is_file():
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        summary = doc.get("summary") or {}
        if bid < act:
            status = "COMPLETE"
        elif bid == act:
            status = "ACTIVE"
        else:
            status = "ready_locked"
        batches_meta.append(
            {
                "batch_id": bid,
                "status": status,
                "stack": doc.get("stack") or "",
                "library": doc.get("library") or "",
                "range": summary.get("cloud_sec_range") or "",
                "file": path,
            }
        )

    act_path = ROOT / f"data/secondary-cloud-forge-run-batch-{act}-locked-v1.json"
    act_doc = json.loads(act_path.read_text(encoding="utf-8"))
    first_head = (act_doc.get("summary") or {}).get("cloud_sec_range", "").split("..")[0] or "CLOUD-SEC-5001"

    archives = {
        f"archive_batch{b}": f"data/secondary-cloud-forge-run-batch-{b}-locked-v1.json"
        for b in range(2, act)
    }
    archives["archive_batch1"] = "data/secondary-cloud-forge-run-batch-1-complete-locked-v1.json"

    nxt_id = act + 1
    nxt_path = f"data/secondary-cloud-forge-run-batch-{nxt_id}-locked-v1.json"
    ptr: dict[str, Any] = {
        "schema": "cloud-forge-run-queue-active-v1",
        "version": "1.4.0",
        "batch_id": act,
        "locked": True,
        "saved_at": _now(),
        "queue_path": f"data/secondary-cloud-forge-run-batch-{act}-locked-v1.json",
        **archives,
        "drain_status": "extension_wave2_patch_armed",
        "registry_exhausted": False,
        "queue_batch_complete": False,
        "extension_wave2_patch": True,
        "competitor_5000_patch": True,
        "phase_reset": {
            "cloud_forge_run_head": first_head,
            "cloud_forge_run_last_completed": "CLOUD-SEC-5000",
            "queue_batch_complete": False,
        },
        "cloud_workers_feed": {
            "machine": "scripts/cloud_workers_hub_v1.py",
            "control_plane": "data/cloud-workers-control-plane-v1.json",
            "auto_runtime": "data/cloud-auto-runtime-v1.json",
        },
        "proof_url": "https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/queue/v1",
    }
    if (ROOT / nxt_path.replace("data/", "data/")).is_file():
        nxt_doc = json.loads((ROOT / nxt_path.replace("data/", "data/")).read_text(encoding="utf-8"))
        ptr["next_batch"] = {
            "batch_id": nxt_id,
            "status": "ready_locked",
            "queue_path": nxt_path,
            "cloud_sec_range": (nxt_doc.get("summary") or {}).get("cloud_sec_range"),
        }
    ptr["manifest"] = str(MANIFEST)
    ACTIVE.write_text(json.dumps(ptr, indent=2) + "\n", encoding="utf-8")

    ext_total = sum(g["count"] for g in generated)
    noetfield_batches = [g for g in generated if g["stack"] == "noetfield"]
    noetfield_plans = sum(g["count"] for g in noetfield_batches)

    pipe = {
        "schema": "cloud-forge-run-batch-pipeline-v1",
        "version": "1.4.0",
        "saved_at": _now(),
        "active_batch_id": act,
        "auto_handoff": True,
        "handoff_on": "swap_to_next_batch at batch end in run_auto_runtime_pack",
        "pattern": "full_pack max_advance 100 per trigger — CF cron */10",
        "competitor_5000_total": 5000,
        "extension_wave2_total": ext_total,
        "extension_wave2_batches": len(generated),
        "stacks": 7,
        "batches_total": last_batch,
        "drain_status": "extension_wave2_patch_armed",
        "registry_exhausted": False,
        "batches": batches_meta,
        "extension_manifest": str(MANIFEST),
    }
    PIPELINE.write_text(json.dumps(pipe, indent=2) + "\n", encoding="utf-8")

    receipt = {
        "schema": "cloud-forge-run-extension-wave2-patch-v1",
        "version": "1.0.0",
        "ok": True,
        "at": _now(),
        "generated_batches": generated,
        "skipped_existing": skipped,
        "active_batch_id": act,
        "head": first_head,
        "last_batch_id": last_batch,
        "noetfield_plans_in_patch": noetfield_plans,
        "noetfield_batches": len(noetfield_batches),
        "extension_plan_total": ext_total,
        "pointer": str(ACTIVE),
        "pipeline": str(PIPELINE),
        "source_slices": source_slices,
        "for_founder": {
            "show_this": (
                f"Wave-2 patch ready · {noetfield_plans} Noetfield + mono plans · "
                f"batches {start_batch}-{last_batch} · head {first_head} · deploy Railway"
            ),
        },
    }
    PATCH_RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--activate-batch", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    act = args.activate_batch if args.activate_batch > 0 else None
    row = build_patch(force=args.force, activate_batch=act)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("for_founder", {}).get("show_this"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
