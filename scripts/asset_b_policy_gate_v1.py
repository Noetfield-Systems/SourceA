#!/usr/bin/env python3
"""Asset B buyer policy gate — evaluates demo intents against policy pack JSON.

Law: docs/SOURCEA_ASSET_B_POLICY_PACK_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/asset-b-policy-pack-v1.json"
PACK_DIR = ROOT / "docs/asset-b-policy-pack"

POLICY_FILES = {
    "outreach": PACK_DIR / "outreach_loop_v1.json",
    "ops": PACK_DIR / "ops_spend_v1.json",
    "creative": PACK_DIR / "creative_publish_v1.json",
}


def _is_null(value: object) -> bool:
    return value is None or value == ""


def _eval_condition(when: str, intent: dict) -> bool:
    text = when.strip()
    for op in ("==", "!="):
        if op not in text:
            continue
        left, right = [part.strip() for part in text.split(op, 1)]
        actual = intent.get(left)
        if right == "null":
            is_null = _is_null(actual)
            return is_null if op == "==" else not is_null
        if right == "true":
            truthy = actual is True
            return truthy if op == "==" else not truthy
        if right == "false":
            falsy = actual is False or _is_null(actual)
            return falsy if op == "==" else not falsy
        expected = right.strip("'\"")
        match = actual == expected
        return match if op == "==" else not match

    for op in (">=", "<=", ">", "<"):
        if op not in text:
            continue
        left, right = [part.strip() for part in text.split(op, 1)]
        actual = float(intent.get(left) or 0)
        bound = float(right)
        if op == ">":
            return actual > bound
        if op == ">=":
            return actual >= bound
        if op == "<":
            return actual < bound
        return actual <= bound

    raise ValueError(f"unsupported condition: {when}")


def load_policy(policy_key: str) -> dict:
    path = POLICY_FILES.get(policy_key)
    if not path or not path.is_file():
        raise FileNotFoundError(f"policy missing: {policy_key}")
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(intent: dict, policy: dict) -> dict:
    if intent.get("intent") and intent.get("intent") != policy.get("intent"):
        return {
            "safe_to_execute": False,
            "rule_id": policy.get("policy_id"),
            "reason": f"intent mismatch: expected {policy.get('intent')}",
            "policy_id": policy.get("policy_id"),
        }

    for rule in policy.get("rules") or []:
        when = str(rule.get("when") or "")
        if not when:
            continue
        if not _eval_condition(when, intent):
            continue
        effect = str(rule.get("effect") or "").lower()
        if effect == "deny":
            return {
                "safe_to_execute": False,
                "rule_id": policy.get("policy_id"),
                "reason": rule.get("reason") or "policy deny",
                "policy_id": policy.get("policy_id"),
                "effect": "deny",
            }
        return {
            "safe_to_execute": True,
            "rule_id": policy.get("policy_id"),
            "reason": "policy allow",
            "policy_id": policy.get("policy_id"),
            "effect": "allow",
            "receipt": rule.get("receipt") or {},
        }

    return {
        "safe_to_execute": False,
        "rule_id": policy.get("policy_id"),
        "reason": "no matching policy rule",
        "policy_id": policy.get("policy_id"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Asset B policy gate")
    ap.add_argument("--policy", choices=tuple(POLICY_FILES), required=True)
    ap.add_argument("--intent", required=True, help="Intent JSON path")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    intent_path = Path(args.intent)
    if not intent_path.is_file():
        print(json.dumps({"ok": False, "error": f"intent missing: {intent_path}"}))
        return 1

    intent = json.loads(intent_path.read_text(encoding="utf-8"))
    policy = load_policy(args.policy)
    row = evaluate(intent, policy)
    out = {"ok": True, "policy": args.policy, "gate": row, "intent_path": str(intent_path)}
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        status = "PASS" if row.get("safe_to_execute") else "DENY"
        print(f"{status}: {row.get('reason')} ({row.get('policy_id')})")
    return 0 if row.get("safe_to_execute") else 1


if __name__ == "__main__":
    raise SystemExit(main())
