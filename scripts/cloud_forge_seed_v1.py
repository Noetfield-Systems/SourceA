#!/usr/bin/env python3
"""FORGE SEED — PLAN → BUILD → VALIDATE → RECEIPT for CLOUD-SEC autonomous cycles."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
STORE = "receipts/forge-seed"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_headless() -> bool:
    if str(os.environ.get("FBE_MODE", "")).lower() == "headless":
        return True
    if os.environ.get("FBE_HOME", "").strip() == "/app":
        return True
    return Path("/app/receipts").is_dir()


def artifact_dir(plan_id: str, *, root: Path | None = None) -> Path:
    base = root or ROOT
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in plan_id)
    return base / STORE / safe


def artifact_path(plan_id: str, *, root: Path | None = None) -> Path:
    return artifact_dir(plan_id, root=root) / "artifact-v1.json"


def validate_artifact(path: Path, *, plan_id: str) -> dict[str, Any]:
    """VALIDATE — file exists, schema, snippets, plan_id match."""
    if not path.is_file():
        return {"ok": False, "error": "artifact_missing", "artifact_path": str(path)}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": "artifact_parse_failed", "message": str(exc)[:120]}
    errors: list[str] = []
    if doc.get("schema") != "forge-seed-artifact-v1":
        errors.append("schema_mismatch")
    if str(doc.get("plan_id") or "") != plan_id:
        errors.append("plan_id_mismatch")
    snippets = doc.get("evidence_snippets") or []
    if not isinstance(snippets, list) or len(snippets) < 1:
        errors.append("snippets_empty")
    build = doc.get("build") or {}
    if not build.get("output_path"):
        errors.append("build_output_missing")
    ok = not errors
    return {
        "ok": ok,
        "validator_result": "PASS" if ok else "FAIL",
        "errors": errors,
        "artifact_path": str(path),
        "artifact_type": str(doc.get("artifact_type") or "forge_seed_build"),
        "snippet_count": len(snippets) if isinstance(snippets, list) else 0,
    }


def _build_artifact(plan: dict[str, Any], dispatch_receipt: dict[str, Any], *, root: Path) -> dict[str, Any]:
    """BUILD — write forge-seed artifact bundle from dispatch evidence."""
    plan_id = str(plan.get("id") or "")
    out_dir = artifact_dir(plan_id, root=root)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = artifact_path(plan_id, root=root)
    snippets = dispatch_receipt.get("evidence_snippets") or []
    build_md = out_dir / "build-output-v1.md"
    lines = [
        f"# FORGE SEED · {plan_id}",
        "",
        f"- **maps_registry:** {plan.get('maps_registry')}",
        f"- **competitor:** {plan.get('competitor')}",
        f"- **workstream:** {plan.get('workstream')}",
        f"- **tier:** {plan.get('tier')}",
        f"- **cloud_action:** {plan.get('cloud_action')}",
        "",
        "## Evidence snippets",
        "",
    ]
    for i, s in enumerate(snippets[:10], 1):
        lines.append(f"{i}. {s}")
    build_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    doc = {
        "schema": "forge-seed-artifact-v1",
        "version": "1.0.0",
        "at": _now(),
        "artifact_type": "forge_seed_build",
        "plan_id": plan_id,
        "maps_registry": plan.get("maps_registry"),
        "competitor": plan.get("competitor"),
        "workstream": plan.get("workstream"),
        "tier": plan.get("tier"),
        "cost_tier": plan.get("cost_tier"),
        "cloud_action": plan.get("cloud_action"),
        "source_url": dispatch_receipt.get("source_url"),
        "evidence_snippets": snippets,
        "dispatch_receipt_id": dispatch_receipt.get("receipt_id"),
        "dispatch_status": dispatch_receipt.get("status"),
        "build": {
            "output_path": str(build_md.relative_to(root)),
            "artifact_json": str(out_path.relative_to(root)),
            "bytes_md": build_md.stat().st_size,
        },
        "pipeline": ["PLAN", "BUILD", "VALIDATE", "RECEIPT"],
    }
    out_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def run_forge_seed_cycle(*, plan_id: str, dry_run: bool = False, root: Path | None = None) -> dict[str, Any]:
    """PLAN → BUILD → VALIDATE → RECEIPT — one CLOUD-SEC cycle with real artifact."""
    import sys

    base = root or ROOT
    sys.path.insert(0, str(SCRIPTS))
    from cloud_worker_dispatch_v1 import dispatch, load_plan  # noqa: WPS433

    plan = load_plan(plan_id)
    if not plan:
        return {"ok": False, "error": "plan_not_found", "plan_id": plan_id, "pipeline": "PLAN"}

    if dry_run:
        return {
            "ok": True,
            "schema": "cloud-forge-seed-v1",
            "plan_id": plan_id,
            "dry_run": True,
            "pipeline": ["PLAN"],
            "for_founder": {"show_this": f"DRY-RUN forge seed · {plan_id}"},
        }

    dispatch_receipt = dispatch(plan_id=plan_id, dry_run=False)
    if not dispatch_receipt.get("ok"):
        return {
            "ok": False,
            "schema": "cloud-forge-seed-v1",
            "plan_id": plan_id,
            "pipeline": ["PLAN", "BUILD"],
            "error": "dispatch_failed",
            "cloud_dispatch": dispatch_receipt,
        }

    artifact_doc = _build_artifact(plan, dispatch_receipt, root=base)
    ap = artifact_path(plan_id, root=base)
    validation = validate_artifact(ap, plan_id=plan_id)
    ok = bool(validation.get("ok")) and dispatch_receipt.get("status") == "PASS"

    rel_artifact = str(ap.relative_to(base))
    row = {
        "ok": ok,
        "schema": "cloud-forge-seed-v1",
        "at": _now(),
        "plan_id": plan_id,
        "maps_registry": plan.get("maps_registry"),
        "pipeline": ["PLAN", "BUILD", "VALIDATE", "RECEIPT"],
        "artifact_type": "forge_seed_build",
        "artifact_path": rel_artifact,
        "validator_result": validation.get("validator_result"),
        "validation": validation,
        "forge_seed_artifact": artifact_doc,
        "cloud_dispatch": dispatch_receipt,
        "dispatch_lane": "forge_seed",
        "for_founder": {
            "show_this": (
                f"{plan_id} · forge_seed · {validation.get('validator_result')} · "
                f"{rel_artifact} · {len(artifact_doc.get('evidence_snippets') or [])} snippets"
            ),
        },
    }
    return row


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="FORGE SEED cycle runner")
    ap.add_argument("--plan-id", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.validate_only:
        row = validate_artifact(artifact_path(args.plan_id), plan_id=args.plan_id)
    else:
        row = run_forge_seed_cycle(plan_id=args.plan_id, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("for_founder", {}).get("show_this") or row.get("error") or row.get("validator_result"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
