#!/usr/bin/env python3
"""Second independent critic — T2 merge authority (MACHINE_LOOPS §2 + §3)."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts" / "proof" / "adversarial-critic-second-latest-v1.json"
CANON_VERSION = "FOUNDER_CANON_v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def critique() -> dict[str, Any]:
    """Independent second pass — cross-check primary critic + receipt chain + validation."""
    primary = _read(ROOT / "receipts/proof/adversarial-critic-latest-v1.json")
    validation = _read(ROOT / "receipts/proof/machine-validation-latest-v1.json")
    chain = _read(ROOT / "receipts/proof/receipt-chain-audit-latest-v1.json")
    merge = _read(ROOT / "receipts/proof/machine-merge-gate-latest-v1.json")

    findings: list[dict[str, str]] = []

    if not primary:
        findings.append({"check": "primary_missing", "severity": "P1", "detail": "no primary critic receipt"})
    elif primary.get("verdict") == "REJECT":
        findings.append({"check": "primary_reject", "severity": "P0", "detail": "primary critic REJECT"})

    if validation and not validation.get("ok"):
        findings.append({"check": "validation", "severity": "P0", "detail": "machine validation not ok"})

    if chain and not chain.get("ok"):
        findings.append({"check": "receipt_chain", "severity": "P0", "detail": "HMAC receipt chain broken"})

    # Second critic must disagree-stress: if primary APPROVE but validation steps empty, flag
    steps = validation.get("steps") if isinstance(validation.get("steps"), list) else []
    if primary.get("verdict") == "APPROVE" and validation.get("ok") and not steps:
        findings.append({"check": "thin_validation", "severity": "P2", "detail": "APPROVE on thin validation evidence"})

    # Cross-check: primary and second should not both rubber-stamp without chain audit
    if primary.get("verdict") == "APPROVE" and not chain:
        findings.append({"check": "no_chain_audit", "severity": "P1", "detail": "APPROVE without receipt chain audit"})

    p0 = [f for f in findings if f.get("severity") == "P0"]
    if p0:
        verdict = "REJECT"
    elif findings:
        verdict = "UNCERTAIN"
    elif primary.get("verdict") == "APPROVE":
        verdict = "APPROVE"
    else:
        verdict = primary.get("verdict", "UNCERTAIN")

    doc = {
        "schema": "adversarial-critic-second-v1",
        "version": "1.0.0",
        "canon_version": CANON_VERSION,
        "at": _now(),
        "ok": verdict == "APPROVE",
        "verdict": verdict,
        "actor": "independent_second_critic",
        "primary_verdict": primary.get("verdict"),
        "findings": findings,
        "merge_tier_gate": merge.get("tier"),
        "report_line": f"critic_second {verdict} · {len(findings)} findings",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = critique()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("verdict") == "APPROVE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
