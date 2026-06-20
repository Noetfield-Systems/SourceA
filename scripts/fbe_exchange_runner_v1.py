#!/usr/bin/env python3
"""FBE exchange runner — Factory 2 trustfield-bay (W4 headless)."""
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
RECEIPT_PATH = SINA / "fbe-exchange-run-receipt-v1.json"
PY = sys.executable

REFINERY_WRAPPERS: dict[str, str] = {
    "creed-orient-v1": "scripts/fbe/exchange/fbe_exchange_orient_v1.py",
    "creed-session-v1": "scripts/fbe/exchange/fbe_exchange_session_v1.py",
    "exchange-match-floor-v1": "scripts/fbe/exchange/fbe_exchange_match_floor_v1.py",
    "exchange-asset-fidelity-v1": "scripts/fbe/exchange/fbe_exchange_asset_fidelity_v1.py",
    "factory-verify-v1": "scripts/fbe/exchange/fbe_exchange_verify_job_v1.py",
    "exchange-dealer-bridge-v1": "scripts/fbe/exchange/fbe_exchange_dealer_bridge_v1.py",
}

ASSEMBLY_WRAPPERS: dict[str, str] = {
    "church-orient-v1": "scripts/fbe/assembly/fbe_assembly_orient_v1.py",
    "church-boundary-v1": "scripts/fbe/assembly/fbe_assembly_boundary_v1.py",
    "church-policy-v1": "scripts/fbe/assembly/fbe_assembly_policy_v1.py",
    "exchange-voice-perimeter-v1": "scripts/fbe/assembly/fbe_assembly_voice_perimeter_v1.py",
    "church-intake-v1": "scripts/fbe/assembly/fbe_assembly_intake_v1.py",
    "church-market-fidelity-v1": "scripts/fbe/assembly/fbe_assembly_market_fidelity_v1.py",
    "church-verify-v1": "scripts/fbe/assembly/fbe_assembly_verify_v1.py",
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
        out = subprocess.check_output(cmd, cwd=str(ROOT), stderr=subprocess.STDOUT, text=True, timeout=300)
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


def run_exchange(*, bay_slug: str = "trustfield-bay", tenant: str = "trustfield") -> dict:
    jobs = _read_json(BAY_JOBS)
    ref_pipeline = (jobs.get("pipelines") or {}).get("exchange_refinery_w4") or {}
    asm_pipeline = (jobs.get("pipelines") or {}).get("exchange_assembly_w4") or {}
    results: list[dict] = []
    executed = 0

    for step in ref_pipeline.get("steps") or []:
        node_id = str(step.get("node") or "")
        wrapper = str(step.get("wrapper") or REFINERY_WRAPPERS.get(node_id, ""))
        if not wrapper:
            continue
        wrapper_path = f"scripts/fbe/exchange/{wrapper}" if not wrapper.startswith("scripts/") else wrapper
        row = _run_step(node_id, wrapper_path, bay=bay_slug, tenant=tenant)
        results.append({**row, "line": "refinery"})
        if row.get("executed"):
            executed += 1

    for step in asm_pipeline.get("steps") or []:
        node_id = str(step.get("node") or "")
        wrapper = str(step.get("wrapper") or ASSEMBLY_WRAPPERS.get(node_id, ""))
        if not wrapper:
            continue
        wrapper_path = wrapper if wrapper.startswith("scripts/") else f"scripts/fbe/assembly/{wrapper}"
        row = _run_step(node_id, wrapper_path, bay=bay_slug, tenant=tenant)
        results.append({**row, "line": "assembly"})
        if row.get("executed"):
            executed += 1

    total = len((ref_pipeline.get("steps") or [])) + len((asm_pipeline.get("steps") or []))
    step_ok_count = sum(1 for r in results if r.get("step_ok"))
    ok = executed == total and step_ok_count >= total and total >= 13
    receipt = {
        "schema": "fbe-exchange-run-receipt-v1",
        "ok": ok,
        "at": _now(),
        "wave": "W4",
        "bay_slug": bay_slug,
        "tenant": tenant,
        "template_id": "exchange-factory-v1",
        "factory_id": "factory_2",
        "steps_total": total,
        "steps_executed": executed,
        "results": results,
        "deliveryMode": "prove_only",
        "execution_plane": "headless_w4",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="trustfield-bay")
    ap.add_argument("--tenant", default="trustfield")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_exchange(bay_slug=args.bay, tenant=args.tenant)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
