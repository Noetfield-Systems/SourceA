#!/usr/bin/env python3
"""Dry-run factory job — LangGraph gate + receipt (no Temporal server)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPIKE = Path(__file__).resolve().parents[1]
if str(SPIKE) not in sys.path:
    sys.path.insert(0, str(SPIKE))

from factory_runtime_spike.activities_v1 import run_dry_factory_job  # noqa: E402
from factory_runtime_spike.types_v1 import PUREFLOW_FIXTURE, JobInput, new_job_id, utc_now  # noqa: E402

SINA_RECEIPT = Path.home() / ".sina" / "factory-runtime-spike-receipt-v1.json"


def _fixture(name: str) -> JobInput:
    if name == "pureflow":
        return PUREFLOW_FIXTURE
    if name == "bad":
        return JobInput(
            job_id=new_job_id(),
            factory_id="web-product-factory-v1",
            prompt="too short",
            vertical="test",
            audience="test",
            proof_artifact="None",
        )
    raise SystemExit(f"unknown fixture: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Factory runtime spike dry-run")
    parser.add_argument("--fixture", choices=["pureflow", "bad"], default="pureflow")
    parser.add_argument("--embed", choices=["langgraph", "maf", "advisor"], default="langgraph")
    parser.add_argument("--prompt", default="")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--receipt-path", default=str(SINA_RECEIPT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    if args.prompt.strip():
        job = JobInput(
            job_id=new_job_id(),
            factory_id="web-product-factory-v1",
            prompt=args.prompt.strip(),
            vertical="custom",
            audience="custom",
            proof_artifact="Service Report",
        )
    else:
        job = _fixture(args.fixture)

    try:
        if args.embed == "advisor":
            sys.path.insert(0, str(ROOT / "scripts"))
            from forge_advisor_orchestrator_v1 import run_advisor  # noqa: WPS433
            from factory_runtime_spike.langgraph_gate_v1 import run_advisor_gate  # noqa: E402

            adv = run_advisor(
                goal=args.prompt.strip() or job.prompt,
                workspace_path=str(ROOT),
                dry_run=True,
                max_steps=2,
            )
            bridge = run_advisor_gate(adv)
            row = {
                "ok": bridge.get("gate_verdict") == "PASS",
                "verdict": bridge.get("gate_verdict"),
                "embed": "advisor",
                "advisor": adv,
                "bridge": bridge,
                "at": utc_now(),
            }
            if not args.no_write:
                path = Path(args.receipt_path).expanduser()
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
                row["receipt_path"] = str(path)
            print(json.dumps(row, indent=2))
            return 0 if row.get("ok") else 1
        receipt = run_dry_factory_job(job, embed=args.embed)
    except ImportError as exc:
        err = {
            "ok": False,
            "error": "missing_dependency",
            "detail": str(exc),
            "hint": "pip install -r apps/factory-runtime-spike/requirements.txt",
        }
        print(json.dumps(err, indent=2))
        return 1

    ok = receipt.get("policy_passed") is True and receipt.get("status") == "COMPLETED"
    row = {
        "ok": ok,
        "verdict": receipt.get("gate_verdict"),
        "status": receipt.get("status"),
        "job_id": receipt.get("job_id"),
        "embed": args.embed,
        "runtime_embed": receipt.get("runtime_embed"),
        "nodes_executed": receipt.get("nodes_executed"),
        "receipt": receipt,
        "at": utc_now(),
    }

    if not args.no_write:
        path = Path(args.receipt_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(path)

    print(json.dumps(row, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
