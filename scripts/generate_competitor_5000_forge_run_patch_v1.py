#!/usr/bin/env python3
"""Generate competitor-5000 Cloud Forge Run patch — batches 11-50 + pointer + pipeline + Dockerfile wire."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/portfolio-competitor-1000-manifest-v1.json"
ACTIVE = ROOT / "data/cloud-forge-run-queue-active-v1.json"
PIPELINE = ROOT / "data/cloud-forge-run-batch-pipeline-v1.json"
PATCH_RECEIPT = ROOT / "data/cloud-forge-run-competitor-5000-patch-v1.json"
DOCKERFILE = ROOT / "cloud/Dockerfile.fbe-runner"
DEPLOY_SCRIPT = ROOT / "scripts/deploy_fbe_railway_v1.py"

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

STACK_BATCHES: list[tuple[str, int, int]] = [
    ("sourcea", 1, 10),
    ("witnessbc", 11, 20),
    ("noetfield", 21, 30),
    ("trustfield", 31, 40),
    ("virlux", 41, 50),
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _registry_for_stack(stack: str) -> Path:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    key = stack.lower()
    for row in manifest.get("stacks") or []:
        if str(row.get("stack") or "").lower() == key:
            pack = Path(str(row.get("pack") or ""))
            reg = pack / "REGISTRY.json"
            if reg.is_file():
                return reg
    raise SystemExit(f"FAIL: registry not found for stack {stack}")


def generate_batch(
    *,
    batch_id: int,
    stack: str,
    registry_path: Path,
    offset: int,
    count: int = 100,
) -> dict[str, Any]:
    reg = json.loads(registry_path.read_text(encoding="utf-8"))
    backlog = [p for p in reg.get("plans") or [] if p.get("status") == "backlog"]
    slice_rows = backlog[offset : offset + count]
    if len(slice_rows) < count:
        raise SystemExit(
            f"FAIL batch {batch_id} {stack}: need {count} at offset {offset}, got {len(slice_rows)}"
        )

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
                "mac_role": "none — batch dispatch POST optional · read receipt after",
                "mac_executes_plan_body": False,
                "competitor": p.get("competitor"),
                "workstream": p.get("workstream"),
                "tier": tier,
                "cost_tier": cost,
                "cloud_action": (p.get("title") or "")[:220],
            }
        )

    first_cloud = f"CLOUD-SEC-{cloud_base + 1:03d}"
    last_cloud = f"CLOUD-SEC-{cloud_base + count:03d}"
    return {
        "schema": "secondary-cloud-forge-run-batch-v1",
        "version": "2.1.0",
        "batch_id": batch_id,
        "stack": stack,
        "locked": True,
        "edit_forbidden": True,
        "saved_at": _now(),
        "authority": "INCIDENT-038 v1.1 · competitor-5000 patch",
        "one_law": "1-10 Mac control only. 11-110 cloud secondary drain. Mac NEVER executes sa-mkt bodies.",
        "forbidden": ["Worker on Mac runs every plan", "RUN INBOX per sa-mkt on Mac", "hand-edit while locked"],
        "generator": "scripts/generate_competitor_5000_forge_run_patch_v1.py",
        "registry_path": str(registry_path),
        "registry_offset": offset,
        "registry_count": count,
        "supersedes_batch": batch_id - 1 if batch_id > 1 else None,
        "count": len(out),
        "summary": {
            "mac_control": 10,
            "cloud_forge": count,
            "batch_id": batch_id,
            "stack": stack,
            "maps_registry": f"{slice_rows[0]['id']} through {slice_rows[-1]['id']}",
            "cloud_sec_range": f"{first_cloud}..{last_cloud}",
        },
        "plans": out,
    }


def _batch_path(batch_id: int) -> Path:
    if batch_id == 1:
        return ROOT / "data/secondary-cloud-forge-run-batch-1-complete-locked-v1.json"
    return ROOT / f"data/secondary-cloud-forge-run-batch-{batch_id}-locked-v1.json"


def patch_dockerfile() -> dict[str, Any]:
    text = DOCKERFILE.read_text(encoding="utf-8")
    marker_start = "COPY data/secondary-cloud-forge-run-next-100-v1.json"
    marker_end = "COPY data/secondary-cloud-forge-run-batch-1-complete-locked-v1.json"
    glob_line = "COPY data/secondary-cloud-forge-run-batch-*.json data/"
    if glob_line in text:
        return {"ok": True, "skipped": True, "reason": "already_glob"}
    pattern = re.compile(
        r"COPY data/secondary-cloud-forge-run-batch-.*?\.json data/[^\n]*\n",
        re.MULTILINE,
    )
    if not pattern.search(text):
        return {"ok": False, "error": "dockerfile_batch_copy_block_not_found"}
    new_text = pattern.sub("", text)
    insert_after = marker_start
    if insert_after not in new_text:
        return {"ok": False, "error": "dockerfile_anchor_missing"}
    replacement = f"{insert_after} data/secondary-cloud-forge-run-next-100-v1.json\n{glob_line}\n"
    new_text = new_text.replace(
        f"{insert_after} data/secondary-cloud-forge-run-next-100-v1.json",
        replacement,
        1,
    )
    DOCKERFILE.write_text(new_text, encoding="utf-8")
    return {"ok": True, "dockerfile": str(DOCKERFILE), "glob_line": glob_line}


def patch_deploy_staging_list() -> dict[str, Any]:
    text = DEPLOY_SCRIPT.read_text(encoding="utf-8")
    needle = '"secondary-cloud-forge-run-batch-2-locked-v1.json",'
    glob_marker = "# competitor-5000 batch glob staging"
    if glob_marker in text:
        return {"ok": True, "skipped": True}
    if needle not in text:
        return {"ok": False, "error": "deploy_staging_anchor_missing"}
    block = '''    # competitor-5000 batch glob staging — batches 2-50 + archives via glob in _stage_deploy_context
'''
    new_text = text.replace(
        '    "secondary-cloud-forge-run-batch-2-locked-v1.json",\n'
        '    "secondary-cloud-forge-run-batch-3-locked-v1.json",\n'
        '    "secondary-cloud-forge-run-batch-4-locked-v1.json",\n'
        '    "secondary-cloud-forge-run-batch-5-locked-v1.json",\n'
        '    "secondary-cloud-forge-run-batch-6-locked-v1.json",\n'
        '    "secondary-cloud-forge-run-batch-7-locked-v1.json",\n'
        '    "secondary-cloud-forge-run-batch-8-locked-v1.json",\n'
        '    "secondary-cloud-forge-run-batch-9-locked-v1.json",\n'
        '    "secondary-cloud-forge-run-batch-10-locked-v1.json",\n',
        block,
        1,
    )
    if "glob_batch_files" not in new_text:
        anchor = "    for name in _STAGING_DATA_FILES:"
        inject = '''    glob_batch_files = sorted((ROOT / "data").glob("secondary-cloud-forge-run-batch-*.json"))
    for path in glob_batch_files:
        rel = f"data/{path.name}"
        if rel not in copied and path.is_file():
            _copy_file(path, STAGING / "data" / path.name)
            copied.append(rel)

'''
        new_text = new_text.replace(anchor, inject + anchor, 1)
    DEPLOY_SCRIPT.write_text(new_text, encoding="utf-8")
    return {"ok": True, "deploy_script": str(DEPLOY_SCRIPT)}


def build_patch(*, force: bool = False, activate_batch: int = 11) -> dict[str, Any]:
    generated: list[dict[str, Any]] = []
    skipped: list[int] = []

    for stack, lo, hi in STACK_BATCHES:
        reg = _registry_for_stack(stack)
        for batch_id in range(lo, hi + 1):
            if batch_id == 1:
                continue
            out_path = _batch_path(batch_id)
            if out_path.is_file() and not force:
                skipped.append(batch_id)
                continue
            if stack == "sourcea":
                if batch_id == 10:
                    offset, count = 990, 10
                else:
                    offset, count = (batch_id - 1) * 100, 100
            else:
                offset = (batch_id - lo) * 100
                count = 100
            doc = generate_batch(
                batch_id=batch_id,
                stack=stack,
                registry_path=reg,
                offset=offset,
                count=count,
            )
            out_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
            generated.append(
                {
                    "batch_id": batch_id,
                    "stack": stack,
                    "path": str(out_path),
                    "range": doc["summary"]["cloud_sec_range"],
                }
            )

    batches_meta: list[dict[str, Any]] = []
    for batch_id in range(1, 51):
        if batch_id == 1:
            path = "data/secondary-cloud-forge-run-batch-1-complete-locked-v1.json"
        else:
            path = f"data/secondary-cloud-forge-run-batch-{batch_id}-locked-v1.json"
        p = ROOT / path.replace("data/", "data/")
        if not p.is_file() and batch_id > 10:
            continue
        doc = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
        summary = doc.get("summary") or {}
        status = "COMPLETE" if batch_id < activate_batch else ("ACTIVE" if batch_id == activate_batch else "ready_locked")
        batches_meta.append(
            {
                "batch_id": batch_id,
                "status": status,
                "stack": doc.get("stack") or ("sourcea" if batch_id <= 10 else ""),
                "range": summary.get("cloud_sec_range") or "",
                "file": path,
            }
        )

    first_head = "CLOUD-SEC-1001"
    for row in batches_meta:
        if row["batch_id"] == activate_batch:
            bpath = ROOT / str(row["file"]).replace("data/", "data/")
            if bpath.is_file():
                doc = json.loads(bpath.read_text(encoding="utf-8"))
                first_head = (doc.get("summary") or {}).get("cloud_sec_range", "").split("..")[0] or first_head

    archives = {f"archive_batch{b}": f"data/secondary-cloud-forge-run-batch-{b}-locked-v1.json" for b in range(2, activate_batch)}
    archives["archive_batch1"] = "data/secondary-cloud-forge-run-batch-1-complete-locked-v1.json"
    nxt_id = activate_batch + 1
    nxt_path = f"data/secondary-cloud-forge-run-batch-{nxt_id}-locked-v1.json"
    ptr = {
        "schema": "cloud-forge-run-queue-active-v1",
        "version": "1.3.0",
        "batch_id": activate_batch,
        "locked": True,
        "saved_at": _now(),
        "queue_path": f"data/secondary-cloud-forge-run-batch-{activate_batch}-locked-v1.json",
        **archives,
        "drain_status": "competitor_5000_patch_armed",
        "registry_exhausted": False,
        "queue_batch_complete": False,
        "competitor_5000_patch": True,
        "phase_reset": {
            "cloud_forge_run_head": first_head,
            "cloud_forge_run_last_completed": None,
            "queue_batch_complete": False,
        },
        "next_batch": {
            "batch_id": nxt_id,
            "status": "ready_locked",
            "queue_path": nxt_path,
        },
        "cloud_workers_feed": {
            "machine": "scripts/cloud_workers_hub_v1.py",
            "control_plane": "data/cloud-workers-control-plane-v1.json",
            "auto_runtime": "data/cloud-auto-runtime-v1.json",
        },
        "proof_url": "https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/queue/v1",
    }
    ACTIVE.write_text(json.dumps(ptr, indent=2) + "\n", encoding="utf-8")

    pipe = {
        "schema": "cloud-forge-run-batch-pipeline-v1",
        "version": "1.3.0",
        "saved_at": _now(),
        "active_batch_id": activate_batch,
        "auto_handoff": True,
        "handoff_on": "swap_to_next_batch at batch end in run_auto_runtime_pack",
        "pattern": "full_pack max_advance 100 per trigger — CF cron */10",
        "competitor_5000_total": 5000,
        "stacks": 5,
        "batches_total": 50,
        "drain_status": "competitor_5000_patch_armed",
        "registry_exhausted": False,
        "batches": batches_meta,
    }
    PIPELINE.write_text(json.dumps(pipe, indent=2) + "\n", encoding="utf-8")

    docker = patch_dockerfile()
    deploy = patch_deploy_staging_list()

    receipt = {
        "schema": "cloud-forge-run-competitor-5000-patch-v1",
        "version": "1.0.0",
        "ok": True,
        "at": _now(),
        "generated_batches": generated,
        "skipped_existing": skipped,
        "active_batch_id": activate_batch,
        "head": first_head,
        "batches_on_disk": len(batches_meta),
        "dockerfile": docker,
        "deploy_script": deploy,
        "pointer": str(ACTIVE),
        "pipeline": str(PIPELINE),
        "for_founder": {
            "show_this": (
                f"Competitor-5000 patch ready · batch {activate_batch} armed · head {first_head} · "
                f"{len(generated)} new files · deploy Railway + CF cron */10"
            ),
        },
    }
    PATCH_RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--activate-batch", type=int, default=11)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = build_patch(force=args.force, activate_batch=args.activate_batch)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("for_founder", {}).get("show_this"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
