#!/usr/bin/env python3
"""Forge Economy v1 — agent credit accounts (governance v2)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
ECONOMY_PATH = SINA / "forge-economy-v1.json"
DEFAULT_BALANCE = 100.0
NATION_TAX_RATE = 0.05

ACTION_COSTS: dict[str, float] = {
    "read_file": 0.05,
    "list_files": 0.02,
    "search_code": 0.08,
    "search_semantic": 0.12,
    "repo_index": 0.15,
    "patch_file": 0.4,
    "write_file": 0.5,
    "apply_git_patch": 0.45,
    "apply_patch": 0.45,
    "run_shell": 1.0,
    "deploy": 5.0,
    "memory_write": 0.2,
}

VIOLATION_PENALTY = 2.0


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load() -> dict[str, Any]:
    try:
        doc = json.loads(ECONOMY_PATH.read_text(encoding="utf-8"))
        if doc.get("accounts"):
            return doc
    except (OSError, json.JSONDecodeError):
        pass
    return {
        "schema": "forge-economy-v1",
        "currency": "FORGE_CREDITS",
        "nation_tax_rate": NATION_TAX_RATE,
        "accounts": {},
        "ledger": [],
        "at": _now(),
    }


def _save(doc: dict[str, Any]) -> None:
    doc["at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    ECONOMY_PATH.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ensure_account(agent_id: str) -> dict[str, Any]:
    doc = _load()
    accounts = doc.setdefault("accounts", {})
    if agent_id not in accounts:
        accounts[agent_id] = {
            "agent_id": agent_id,
            "balance": DEFAULT_BALANCE,
            "total_spent": 0.0,
            "total_earned": 0.0,
            "violations": 0,
        }
        _save(doc)
    return accounts[agent_id]


def action_cost(action_type: str) -> float:
    return float(ACTION_COSTS.get(action_type, 0.25))


def charge_action(*, agent_id: str, action_type: str, task_cost: float = 0.0) -> dict[str, Any]:
    """Debit credits for an action (includes optional task budget)."""
    doc = _load()
    acct = ensure_account(agent_id)
    cost = action_cost(action_type) + max(0.0, float(task_cost or 0))
    tax = round(cost * NATION_TAX_RATE, 4)
    total = round(cost + tax, 4)
    balance = float(acct.get("balance") or 0)
    if balance < total:
        return {"ok": False, "error": "insufficient_credits", "balance": balance, "required": total}
    acct["balance"] = round(balance - total, 4)
    acct["total_spent"] = round(float(acct.get("total_spent") or 0) + total, 4)
    doc["accounts"][agent_id] = acct
    entry = {
        "type": "debit",
        "agent_id": agent_id,
        "action": action_type,
        "cost": cost,
        "tax": tax,
        "total": total,
        "at": _now(),
    }
    doc.setdefault("ledger", []).append(entry)
    doc["ledger"] = doc["ledger"][-500:]
    _save(doc)
    return {"ok": True, "charged": total, "balance": acct["balance"], "tax": tax}


def reward_agent(*, agent_id: str, amount: float, reason: str = "task_success") -> dict[str, Any]:
    doc = _load()
    acct = ensure_account(agent_id)
    amt = max(0.0, float(amount))
    acct["balance"] = round(float(acct.get("balance") or 0) + amt, 4)
    acct["total_earned"] = round(float(acct.get("total_earned") or 0) + amt, 4)
    doc["accounts"][agent_id] = acct
    doc.setdefault("ledger", []).append({"type": "credit", "agent_id": agent_id, "amount": amt, "reason": reason, "at": _now()})
    doc["ledger"] = doc["ledger"][-500:]
    _save(doc)
    return {"ok": True, "balance": acct["balance"], "credited": amt}


def apply_violation_penalty(*, agent_id: str) -> dict[str, Any]:
    doc = _load()
    acct = ensure_account(agent_id)
    penalty = VIOLATION_PENALTY
    acct["balance"] = round(max(0.0, float(acct.get("balance") or 0) - penalty), 4)
    acct["violations"] = int(acct.get("violations") or 0) + 1
    doc["accounts"][agent_id] = acct
    doc.setdefault("ledger", []).append({"type": "penalty", "agent_id": agent_id, "amount": penalty, "at": _now()})
    doc["ledger"] = doc["ledger"][-500:]
    _save(doc)
    return {"ok": True, "penalty": penalty, "balance": acct["balance"]}


def load_economy() -> dict[str, Any]:
    return _load()
