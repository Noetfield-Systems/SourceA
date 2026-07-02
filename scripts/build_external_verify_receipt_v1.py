#!/usr/bin/env python3
"""Assemble external-verify receipt for truth_log + disk (L4)."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def build_receipt(
    *,
    autorun: dict[str, Any],
    founder_proof: dict[str, Any],
    determinism: dict[str, Any] | None = None,
    github_run_id: str,
    github_sha: str,
    run_url: str,
    conclusion: str,
) -> dict[str, Any]:
    autorun_ok = bool(autorun.get("ok"))
    proof_ok = bool(founder_proof.get("ok"))
    det = determinism or {}
    det_ok = bool(det.get("ok")) if det else True
    checks = []
    for rec in founder_proof.get("rows") or founder_proof.get("recipes") or []:
        if isinstance(rec, dict):
            checks.append(
                {
                    "recipe_id": rec.get("id") or rec.get("recipe_id"),
                    "url": rec.get("url"),
                    "verdict": rec.get("verdict") or ("PASS" if rec.get("ok") else "FAIL"),
                    "http_status": rec.get("http_code") or rec.get("http_status"),
                    "body_sha256": rec.get("body_sha256") or rec.get("sha256"),
                }
            )
    return {
        "schema": "external-verify-receipt-v1",
        "version": "1.1.0",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "law": "GOVERNED_AUTORUN_LAWS_v3 L4+L13 — external verify + determinism gate",
        "github_run_id": github_run_id,
        "github_sha": github_sha,
        "run_url": run_url,
        "conclusion": conclusion,
        "workflow": "external-verify.yml",
        "runner": "github_actions",
        "ok": autorun_ok and proof_ok and det_ok,
        "autorun_verify": autorun,
        "founder_proof_15": founder_proof,
        "determinism_gate": det or None,
        "checks": checks,
        "report_line": (
            f"external-verify {'PASS' if autorun_ok and proof_ok and det_ok else 'FAIL'} · "
            f"autorun={'PASS' if autorun_ok else 'FAIL'} · "
            f"determinism={'PASS' if det_ok else 'FAIL'} · "
            f"15-recipe={founder_proof.get('passed', '?')}/{founder_proof.get('total', '?')} · "
            f"run={github_run_id}"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--autorun", required=True)
    ap.add_argument("--founder-proof", required=True)
    ap.add_argument("--determinism", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    autorun = json.loads(Path(args.autorun).read_text(encoding="utf-8"))
    proof = json.loads(Path(args.founder_proof).read_text(encoding="utf-8"))
    det = {}
    if args.determinism and Path(args.determinism).is_file():
        det = json.loads(Path(args.determinism).read_text(encoding="utf-8"))
    row = build_receipt(
        autorun=autorun,
        founder_proof=proof,
        determinism=det or None,
        github_run_id=os.environ.get("GITHUB_RUN_ID", ""),
        github_sha=os.environ.get("GITHUB_SHA", ""),
        run_url=os.environ.get("GITHUB_RUN_URL", ""),
        conclusion=os.environ.get("GITHUB_RUN_CONCLUSION", "unknown"),
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
