#!/usr/bin/env python3
"""Machine merge gate — T0/T1 merge authority per MACHINE_LOOPS §2."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts" / "proof" / "machine-merge-gate-latest-v1.json"
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


def _changed_files() -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", "origin/main...HEAD"],
            cwd=str(ROOT),
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return [l.strip() for l in out.splitlines() if l.strip()]
    except subprocess.CalledProcessError:
        try:
            out = subprocess.check_output(
                ["git", "diff", "--name-only", "HEAD~1..HEAD"],
                cwd=str(ROOT),
                text=True,
                stderr=subprocess.DEVNULL,
            )
            return [l.strip() for l in out.splitlines() if l.strip()]
        except subprocess.CalledProcessError:
            return []


def _tier_for_files(files: list[str]) -> str:
    t3_prefixes = (".agent-policy/", "data/trigger-registry", "docs/GOVERNED_AUTORUN", "docs/FOUNDER_CANON")
    t2_prefixes = (".github/workflows/", "package.json", "requirements", "wrangler.toml")
    t0_prefixes = ("docs/", "receipts/proof/", "tests/", "scripts/validate-", ".md")
    for f in files:
        if any(f.startswith(p) for p in t3_prefixes):
            return "T3"
    for f in files:
        if any(p in f for p in t2_prefixes):
            return "T2"
    for f in files:
        if not any(f.startswith(p) or f.endswith(p.replace("scripts/validate-", ".sh")) for p in t0_prefixes):
            if f.startswith("scripts/") or f.startswith("data/") or f.startswith("cloud/"):
                return "T1"
    return "T0"


def evaluate(*, tier: str = "") -> dict[str, Any]:
    files = _changed_files()
    inferred = _tier_for_files(files) if files else "T0"
    tier = tier or inferred

    validation = _read(ROOT / "receipts/proof/machine-validation-latest-v1.json")
    critic = _read(ROOT / "receipts/proof/adversarial-critic-latest-v1.json")
    adv = _read(ROOT / "receipts/proof/adversarial-critique-latest-v1.json")

    critic2 = _read(ROOT / "receipts/proof/adversarial-critic-second-latest-v1.json")
    chain = _read(ROOT / "receipts/proof/receipt-chain-audit-latest-v1.json")

    criteria = {
        "external_ci_proxy": bool(validation.get("ok")),
        "receipt_schema_valid": validation.get("schema") == "machine-validation-v1",
        "critic_verdict": critic.get("verdict", "MISSING"),
        "critic_second_verdict": critic2.get("verdict", "MISSING"),
        "receipt_chain_ok": bool(chain.get("ok")),
        "adversarial_gate": bool(adv.get("ok")),
        "canon_version_present": True,
    }

    ok = False
    reason = ""
    if tier == "T3":
        ok = False
        reason = "T3 requires founder merge — never auto"
    elif tier in ("T0", "T1"):
        ok = (
            criteria["external_ci_proxy"]
            and criteria["adversarial_gate"]
            and criteria["critic_verdict"] in ("APPROVE", "MISSING")
        )
        if tier == "T1" and criteria["critic_verdict"] != "APPROVE":
            ok = False
            reason = "T1 requires critic APPROVE"
        if ok:
            reason = f"machine merge authorized for {tier}"
    elif tier == "T2":
        ok = (
            criteria["external_ci_proxy"]
            and criteria["adversarial_gate"]
            and criteria["critic_verdict"] == "APPROVE"
            and criteria["critic_second_verdict"] == "APPROVE"
            and criteria["receipt_chain_ok"]
        )
        reason = (
            "machine merge authorized for T2"
            if ok
            else "T2 requires primary+second critic APPROVE + receipt chain green"
        )
    else:
        ok = False
        reason = f"unknown tier {tier}"

    doc = {
        "schema": "machine-merge-gate-v1",
        "version": "1.0.0",
        "canon_version": CANON_VERSION,
        "at": _now(),
        "ok": ok,
        "tier": tier,
        "inferred_tier": inferred,
        "files_sample": files[:20],
        "criteria": criteria,
        "reason": reason,
        "report_line": f"merge_gate {'PASS' if ok else 'BLOCK'} · {tier} · {reason}",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tier", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = evaluate(tier=args.tier)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
