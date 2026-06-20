#!/usr/bin/env python3
"""H1 Safety — fast ecosystem check for founder tap (<30s)."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "worker-hub-safety-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_h1_safety() -> dict:
    script = ROOT / "scripts" / "validate-ecosystem-safety-h1-fast-v1.sh"
    proc = subprocess.run(
        ["bash", str(script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=45,
    )
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    tail = ""
    for line in reversed(out.splitlines()):
        if line.startswith(("OK:", "FAIL:", "PASS:")):
            tail = line
            break
    row = {
        "ok": proc.returncode == 0,
        "schema": "worker-hub-safety-v1",
        "at": _now(),
        "message": f"Safety {'PASS' if proc.returncode == 0 else 'FAIL'}" + (f" · {tail}" if tail else ""),
        "tail": tail,
        "output": out[-4000:],
    }
    try:
        from sina_command_lib import kernel_k1_payload  # noqa: WPS433

        k1 = kernel_k1_payload()
        row["kernel_k1"] = {
            "verdict": k1.get("verdict"),
            "ok": k1.get("ok"),
            "founder_line": k1.get("founder_line"),
        }
        if k1.get("verdict"):
            row["message"] += f" · K1 {k1.get('verdict')}"
    except Exception as e:
        row["kernel_k1"] = {"ok": False, "verdict": "BLOCK", "error": str(e)}
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    try:
        from worker_hub_v1 import invalidate_worker_hub_cache, worker_hub_payload  # noqa: WPS433

        invalidate_worker_hub_cache()
        worker_hub_payload(skip_cache=True)
    except Exception:
        pass
    return row


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="H1 Safety fast check")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = run_h1_safety()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("message"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
