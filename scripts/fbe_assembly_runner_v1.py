#!/usr/bin/env python3
"""FBE assembly runner — Factory 1 Line B wired + planned W6 pipelines."""
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
RECEIPT_PATH = SINA / "fbe-assembly-run-receipt-v1.json"
PY = sys.executable

STEP_WRAPPERS: dict[str, str] = {
    "church-orient-v1": "scripts/fbe/assembly/fbe_assembly_orient_v1.py",
    "church-architect-v1": "scripts/fbe/assembly/fbe_assembly_architect_v1.py",
    "church-boundary-v1": "scripts/fbe/assembly/fbe_assembly_boundary_v1.py",
    "church-rules-v1": "scripts/fbe/assembly/fbe_assembly_rules_v1.py",
    "church-definition-v1": "scripts/fbe/assembly/fbe_assembly_definition_v1.py",
    "church-neutrality-v1": "scripts/fbe/assembly/fbe_assembly_neutrality_v1.py",
    "church-isolation-v1": "scripts/fbe/assembly/fbe_assembly_isolation_v1.py",
    "church-policy-v1": "scripts/fbe/assembly/fbe_assembly_policy_v1.py",
    "church-dealer-letter-v1": "scripts/fbe/assembly/fbe_assembly_dealer_letter_v1.py",
    "church-intake-v1": "scripts/fbe/assembly/fbe_assembly_intake_v1.py",
    "church-market-fidelity-v1": "scripts/fbe/assembly/fbe_assembly_market_fidelity_v1.py",
    "church-verify-v1": "scripts/fbe/assembly/fbe_assembly_verify_v1.py",
    "church-scaffold-v1": "scripts/fbe/assembly/fbe_assembly_scaffold_v1.py",
    "church-merge-v1": "scripts/fbe/assembly/fbe_assembly_merge_v1.py",
    "church-brand-unity-v1": "scripts/fbe/assembly/fbe_assembly_brand_unity_v1.py",
    "church-narrative-v1": "scripts/fbe/assembly/fbe_assembly_narrative_v1.py",
    "church-forbidden-v1": "scripts/fbe/assembly/fbe_assembly_forbidden_v1.py",
    "church-demo-v1": "scripts/fbe/assembly/fbe_assembly_demo_v1.py",
    "church-gtm-v1": "scripts/fbe/assembly/fbe_assembly_gtm_v1.py",
    "church-deploy-v1": "scripts/fbe/assembly/fbe_assembly_deploy_v1.py",
    "church-domain-v1": "scripts/fbe/assembly/fbe_assembly_domain_v1.py",
    "church-live-smoke-v1": "scripts/fbe/assembly/fbe_assembly_live_smoke_v1.py",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _run_step(node_id: str, *, bay: str, tenant: str) -> dict[str, Any]:
    wrapper = STEP_WRAPPERS.get(node_id)
    if not wrapper:
        return {"node_id": node_id, "ok": False, "error": "no wrapper"}
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
            "church_ok": bool(row.get("ok")),
            "elapsed_sec": round(time.monotonic() - t0, 2),
        }
    except subprocess.CalledProcessError as e:
        tail = (e.output or "")[-400:]
        church_ok = False
        try:
            church_ok = bool(json.loads(e.output or "{}").get("ok"))
        except json.JSONDecodeError:
            pass
        return {
            "node_id": node_id,
            "ok": True,
            "executed": True,
            "church_ok": church_ok,
            "exit": e.returncode,
            "tail": tail,
        }
    except Exception as exc:
        return {"node_id": node_id, "ok": False, "executed": False, "error": str(exc)}


def run_bay(
    *,
    bay_slug: str = "sample-bay",
    tenant: str = "wil_ai_design_partner",
    pipeline_id: str = "assembly_first_bay_w3",
) -> dict:
    jobs = _read_json(BAY_JOBS)
    pipeline = (jobs.get("pipelines") or {}).get(pipeline_id) or {}
    steps = pipeline.get("steps") or []
    results: list[dict] = []
    church_ok_count = 0
    for step in steps:
        node_id = str(step.get("node") or "")
        if not node_id:
            continue
        row = _run_step(node_id, bay=bay_slug, tenant=tenant)
        results.append(row)
        if row.get("church_ok"):
            church_ok_count += 1

    executed = sum(1 for r in results if r.get("executed"))
    min_steps = 10 if pipeline_id == "assembly_planned_w6" else 12
    ok = executed == len(steps) and len(steps) >= min_steps
    wave = "W6" if pipeline_id == "assembly_planned_w6" else "W3"
    receipt = {
        "schema": "fbe-assembly-run-receipt-v1",
        "ok": ok,
        "at": _now(),
        "wave": wave,
        "bay_slug": bay_slug,
        "tenant": tenant,
        "pipeline": pipeline_id,
        "steps_total": len(steps),
        "steps_executed": executed,
        "church_ok_count": church_ok_count,
        "results": results,
        "deliveryMode": "prove_only",
        "execution_plane": "headless_w6" if wave == "W6" else "headless_w3",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="sample-bay")
    ap.add_argument("--tenant", default="wil_ai_design_partner")
    ap.add_argument("--pipeline", default="assembly_first_bay_w3")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_bay(bay_slug=args.bay, tenant=args.tenant, pipeline_id=args.pipeline)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
