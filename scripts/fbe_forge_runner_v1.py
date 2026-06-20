#!/usr/bin/env python3
"""FBE forge runner — Factory 3 forge-bay (W5 headless)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SINA = Path.home() / ".sina"
BAY_JOBS = DATA / "fbe_bay_jobs_v1.json"
RECEIPT_PATH = SINA / "fbe-forge-run-receipt-v1.json"
PY = sys.executable

REFINERY_WRAPPERS: dict[str, str] = {
    "forge-orient-v1": "scripts/fbe/forge/fbe_forge_orient_v1.py",
    "forge-scaffold-v1": "scripts/fbe/forge/fbe_forge_scaffold_v1.py",
    "forge-inbox-gate-v1": "scripts/fbe/forge/fbe_forge_inbox_gate_v1.py",
}

ASSEMBLY_WRAPPERS: dict[str, str] = {
    "forge-deploy-pack-v1": "scripts/fbe/forge/fbe_forge_deploy_pack_v1.py",
    "forge-verify-job-v1": "scripts/fbe/forge/fbe_forge_verify_job_v1.py",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _run_step(node_id: str, wrapper: str, *, bay: str, tenant: str) -> dict[str, Any]:
    script = ROOT / wrapper
    cmd = [PY, str(script), "--bay", bay, "--tenant", tenant, "--json"]
    t0 = time.monotonic()
    try:
        out = subprocess.check_output(cmd, cwd=str(ROOT), stderr=subprocess.STDOUT, text=True, timeout=120)
        row = json.loads(out)
        return {
            "node_id": node_id,
            "ok": True,
            "executed": True,
            "step_ok": bool(row.get("ok")),
            "elapsed_sec": round(time.monotonic() - t0, 2),
        }
    except subprocess.CalledProcessError as e:
        step_ok = False
        try:
            step_ok = bool(json.loads(e.output or "{}").get("ok"))
        except json.JSONDecodeError:
            pass
        return {
            "node_id": node_id,
            "ok": True,
            "executed": True,
            "step_ok": step_ok,
            "exit": e.returncode,
            "tail": (e.output or "")[-400:],
        }
    except Exception as exc:
        return {"node_id": node_id, "ok": False, "executed": False, "error": str(exc)}


def run_forge(*, bay_slug: str = "forge-bay", tenant: str = "forge") -> dict:
    jobs = _read_json(BAY_JOBS)
    ref_pipeline = (jobs.get("pipelines") or {}).get("forge_refinery_w5") or {}
    asm_pipeline = (jobs.get("pipelines") or {}).get("forge_assembly_w5") or {}
    results: list[dict] = []
    executed = 0
    step_ok_count = 0

    for step in ref_pipeline.get("steps") or []:
        node_id = str(step.get("node") or "")
        wrapper = str(step.get("wrapper") or REFINERY_WRAPPERS.get(node_id, ""))
        if not wrapper:
            continue
        wrapper_path = wrapper if wrapper.startswith("scripts/") else f"scripts/fbe/forge/{wrapper}"
        row = _run_step(node_id, wrapper_path, bay=bay_slug, tenant=tenant)
        results.append({**row, "line": "refinery"})
        if row.get("executed"):
            executed += 1
        if row.get("step_ok"):
            step_ok_count += 1

    for step in asm_pipeline.get("steps") or []:
        node_id = str(step.get("node") or "")
        wrapper = str(step.get("wrapper") or ASSEMBLY_WRAPPERS.get(node_id, ""))
        if not wrapper:
            continue
        wrapper_path = wrapper if wrapper.startswith("scripts/") else f"scripts/fbe/forge/{wrapper}"
        row = _run_step(node_id, wrapper_path, bay=bay_slug, tenant=tenant)
        results.append({**row, "line": "assembly"})
        if row.get("executed"):
            executed += 1
        if row.get("step_ok"):
            step_ok_count += 1

    total = len((ref_pipeline.get("steps") or [])) + len((asm_pipeline.get("steps") or []))
    ok = executed == total and step_ok_count == total and total >= 5
    receipt = {
        "schema": "fbe-forge-run-receipt-v1",
        "ok": ok,
        "at": _now(),
        "wave": "W5",
        "bay_slug": bay_slug,
        "tenant": tenant,
        "template_id": "forge-app-factory-v1",
        "factory_id": "factory_3",
        "steps_total": total,
        "steps_executed": executed,
        "steps_ok": step_ok_count,
        "results": results,
        "deliveryMode": "prove_only",
        "execution_plane": "headless_w5",
        "proof_class": "G0-G3",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="forge-bay")
    ap.add_argument("--tenant", default="forge")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_forge(bay_slug=args.bay, tenant=args.tenant)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
