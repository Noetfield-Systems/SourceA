#!/usr/bin/env python3
"""Copilot governance demo gate — rule P-001 only (no factory queue)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "brain-os/demo/governance_demo_policy_v1.json"


def load_policy(path: Path | None = None) -> dict:
    p = path or POLICY_PATH
    return json.loads(p.read_text(encoding="utf-8"))


def evaluate(intent: dict, policy: dict | None = None) -> dict:
    pol = policy or load_policy()
    rules = pol.get("rules") or []
    p001 = next((r for r in rules if r.get("id") == "P-001"), None)
    if not p001:
        return {
            "safe_to_execute": False,
            "rule_id": "",
            "reason": "P-001 policy missing",
        }

    deny = p001.get("deny_when") or {}
    if intent.get("intent") != deny.get("intent"):
        return {
            "safe_to_execute": True,
            "rule_id": "P-001",
            "reason": "not a copilot policy change intent",
        }

    missing = deny.get("missing_field") or ""
    risk = deny.get("risk")
    if risk and intent.get("risk") == risk and missing and not intent.get(missing):
        return {
            "safe_to_execute": False,
            "rule_id": "P-001",
            "reason": f"high-risk enable requires {missing}",
            "policy_id": intent.get("policy_id"),
        }

    return {
        "safe_to_execute": True,
        "rule_id": "P-001",
        "reason": "approval_ref present or risk not high",
        "policy_id": intent.get("policy_id"),
    }


def main() -> int:
    import argparse
    import sys

    ap = argparse.ArgumentParser(description="Governance demo gate — P-001")
    ap.add_argument("--intent", required=True, help="Intent JSON file")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    intent = json.loads(Path(args.intent).read_text(encoding="utf-8"))
    row = evaluate(intent)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        status = "PASS" if row.get("safe_to_execute") else "DENY"
        print(f"{status}: {row.get('reason')} (rule {row.get('rule_id')})")
    return 0 if row.get("safe_to_execute") else 1


if __name__ == "__main__":
    raise SystemExit(main())
