#!/usr/bin/env python3
"""Cloud CI hook — public HTTPS founder proof after Pages publish.

LAW: Wait >=60s after last publish receipt, then run 15-recipe verify.
Local dist verification is INVALID as PASS.
Receipt: ~/.sina/client-proof-founder-review-verify-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLISH_RECEIPT = Path.home() / ".sina/sourcea-landing-publish-receipt-v1.json"
VERIFY_RECEIPT = Path.home() / ".sina/client-proof-founder-review-verify-v1.json"
VERIFY_SCRIPT = ROOT / "scripts/verify_client_proof_founder_review_v1.py"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _publish_age_seconds() -> int | None:
    if not PUBLISH_RECEIPT.is_file():
        return None
    try:
        doc = json.loads(PUBLISH_RECEIPT.read_text(encoding="utf-8"))
        at = str(doc.get("at") or "")
        published = datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return int((datetime.now(timezone.utc) - published).total_seconds())
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        return None


def run(*, min_seconds: int = 60, write_receipt: bool = True) -> dict:
    elapsed = _publish_age_seconds()
    if elapsed is not None and elapsed < min_seconds:
        wait_for = min_seconds - elapsed
        time.sleep(wait_for)
        elapsed = min_seconds

    cmd = [sys.executable, str(VERIFY_SCRIPT), "--json", "--min-seconds-after-deploy", str(min_seconds)]
    if write_receipt:
        cmd.append("--write-receipt")
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    try:
        verify = json.loads(proc.stdout)
    except json.JSONDecodeError:
        verify = {"ok": False, "error": (proc.stderr or proc.stdout)[-400:]}

    row = {
        "schema": "founder-proof-post-publish-v1",
        "at": _now(),
        "min_seconds_after_deploy": min_seconds,
        "publish_elapsed_seconds": elapsed,
        "verify_ok": bool(verify.get("ok")) and proc.returncode == 0,
        "passed": verify.get("passed"),
        "total": verify.get("total"),
        "verify_receipt": str(VERIFY_RECEIPT),
        "verify_law": verify.get("verify_law"),
    }
    if not row["verify_ok"]:
        row["error"] = verify.get("error") or verify.get("defect") or "founder verify HOLD"
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min-seconds-after-deploy", type=int, default=60)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write-receipt", action="store_true")
    args = ap.parse_args()
    row = run(min_seconds=args.min_seconds_after_deploy, write_receipt=not args.no_write_receipt)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"verify_ok={row['verify_ok']} passed={row.get('passed')}/{row.get('total')}")
    return 0 if row.get("verify_ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
