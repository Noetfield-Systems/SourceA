#!/usr/bin/env python3
"""Adversarial critic receipt — APPROVE | REJECT | UNCERTAIN (MACHINE_LOOPS §3)."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts" / "proof" / "adversarial-critic-latest-v1.json"
CANON_VERSION = "FOUNDER_CANON_v1"

PROSE_PROOF = re.compile(
    r"\b(should work|looks good|probably|I think|config live|trust me)\b", re.I
)
SELF_VERIFY = re.compile(r"\b(I verified|I checked|confirmed working)\b", re.I)
L5_TOUCH = re.compile(
    r"(GOVERNED_AUTORUN|validate-trigger-registry|\.agent-policy/|FORBIDDEN_MARKERS)", re.I
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _git_diff_stat() -> str:
    try:
        return subprocess.check_output(
            ["git", "diff", "--stat", "HEAD~1..HEAD"],
            cwd=str(ROOT),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()[:2000]
    except subprocess.CalledProcessError:
        try:
            return subprocess.check_output(
                ["git", "diff", "--stat"],
                cwd=str(ROOT),
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()[:2000]
        except subprocess.CalledProcessError:
            return ""


def critique(*, target_receipt: Path | None = None) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    worker = _read(target_receipt or ROOT / "receipts/proof/worker-execution-gate-latest-v1.json")
    validation = _read(ROOT / "receipts/proof/machine-validation-latest-v1.json")
    diff = _git_diff_stat()

    if worker and not worker.get("ok"):
        findings.append({"check": "worker_gate", "severity": "P0", "detail": "worker gate not ok"})
    if validation and not validation.get("ok"):
        findings.append({"check": "machine_validation", "severity": "P0", "detail": "validation not ok"})

    blob = json.dumps(worker) + diff
    if PROSE_PROOF.search(blob):
        findings.append({"check": "prose_as_proof", "severity": "P1", "detail": "prose-as-proof language detected"})
    if SELF_VERIFY.search(blob):
        findings.append({"check": "self_verification", "severity": "P1", "detail": "self-verification claim without external probe"})
    if L5_TOUCH.search(diff) and "validate" not in diff.lower():
        findings.append({"check": "l5_touch", "severity": "P0", "detail": "L5-class path in diff — founder gate required"})

    if not worker.get("op_key") and worker:
        findings.append({"check": "idempotency", "severity": "P2", "detail": "missing op_key on worker receipt"})

    p0 = [f for f in findings if f.get("severity") == "P0"]
    p1 = [f for f in findings if f.get("severity") == "P1"]

    if p0:
        verdict = "REJECT"
    elif p1:
        verdict = "UNCERTAIN"
    else:
        verdict = "APPROVE"

    doc = {
        "schema": "adversarial-critic-v1",
        "version": "1.0.0",
        "canon_version": CANON_VERSION,
        "at": _now(),
        "ok": verdict == "APPROVE",
        "verdict": verdict,
        "findings": findings,
        "evidence": {"diff_stat_lines": len(diff.splitlines()), "worker_ok": worker.get("ok")},
        "report_line": f"critic {verdict} · {len(findings)} findings",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--receipt", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    target = Path(args.receipt) if args.receipt else None
    row = critique(target_receipt=target)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("verdict") == "APPROVE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
