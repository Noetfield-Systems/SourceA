#!/usr/bin/env python3
"""Forge Governance Kernel v4 — economy + legal arbitration + geopolitical layer.

Extends v3: nations as legal systems, treaties, sanctions, international court.
Receipt: ~/.sina/forge-governance-latest-v1.json
Law: brain-os/law/enforcement/SOURCEA_FORGE_GOVERNANCE_KERNEL_V4_LOCKED_v1.md
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
VIOLATIONS_LOG = SINA / "forge-governance-violations-v1.jsonl"
LATEST_RECEIPT = SINA / "forge-governance-latest-v1.json"
GOVERNANCE_VERSION = "v4"

GOVERNANCE_RULES = [
    "No agent may exceed assigned permissions",
    "No destructive system commands",
    "No memory overwrite without validation",
    "All deployments must pass firewall",
    "All patches must be verifiable",
    "Actions consume FORGE credits; violations incur penalties",
    "Rule conflicts MUST be resolved by arbitration, not first-deny",
    "Cross-border actions require active treaty or face international court",
]

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "planner": frozenset({"read_file", "list_files", "search_code", "search_semantic", "repo_index"}),
    "builder": frozenset({
        "read_file", "write_file", "patch_file", "apply_git_patch", "apply_patch",
        "list_files", "search_code", "search_semantic", "repo_index", "run_shell",
    }),
    "critic": frozenset({"read_file", "list_files", "search_code", "run_shell"}),
    "repair": frozenset({"read_file", "list_files", "search_code", "patch_file"}),
    "optimizer": frozenset({"read_file", "list_files", "search_code"}),
    "deployer": frozenset({"deploy"}),
    "admin": frozenset({
        "read_file", "write_file", "patch_file", "apply_git_patch", "apply_patch",
        "list_files", "search_code", "search_semantic", "repo_index", "run_shell", "deploy", "memory_write",
    }),
}

PROBATION_ALLOW = frozenset({"read_file", "list_files", "search_code"})
RESTRICTED_ALLOW = frozenset({"read_file", "list_files"})

LEVEL_PERMISSIONS: dict[str, frozenset[str]] = {
    "L1": frozenset({"read_file", "list_files", "search_code", "search_semantic", "repo_index"}),
    "L2": frozenset({"read_file", "list_files", "search_code", "patch_file"}),
    "L3": frozenset({"read_file", "write_file", "patch_file", "list_files", "search_code", "run_shell", "apply_git_patch"}),
    "SWARM": ROLE_PERMISSIONS["builder"],
}

HIGH_COST_ACTIONS = frozenset({"write_file", "patch_file", "apply_git_patch", "run_shell", "deploy"})

MEMORY_FORBIDDEN = re.compile(
    r"override_all_agents|delete_memory|reset_system|wipe_registry|forge-agent-registry-v1\.json",
    re.I,
)

SHELL_BANNED = re.compile(
    r"rm\s+-rf|shutdown|mkfs|:?\(\)\s*\{|:?\|:&\};:|curl\s+.*\|\s*sh|sudo\s+|chmod\s+777",
    re.I,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _get_agent(agent_id: str) -> dict[str, Any]:
    try:
        from forge_agent_registry_v1 import load_registry  # noqa: WPS433

        for a in load_registry().get("agents") or []:
            if a.get("id") == agent_id:
                return a
    except Exception:
        pass
    return {"id": agent_id, "role": "builder", "reputation": 0.5, "status": "active"}


def reputation_tier(reputation: float) -> str:
    if reputation >= 0.7:
        return "trusted"
    if reputation >= 0.4:
        return "standard"
    if reputation >= 0.25:
        return "probation"
    return "restricted"


def check_reputation_permissions(
    *,
    agent_id: str,
    agent_role: str,
    action_type: str,
) -> dict[str, Any]:
    agent = _get_agent(agent_id)
    rep = float(agent.get("reputation") or 0.5)
    tier = reputation_tier(rep)
    status = str(agent.get("status") or "active")

    if status == "disabled":
        return {"status": "DENY", "reason": "agent_disabled", "tier": tier}

    if tier == "restricted":
        if action_type not in RESTRICTED_ALLOW:
            return {"status": "DENY", "reason": f"restricted_tier:{rep}", "tier": tier}
    elif tier == "probation":
        if action_type not in PROBATION_ALLOW:
            return {"status": "DENY", "reason": f"probation_tier:{rep}", "tier": tier}
    elif tier == "standard":
        if action_type == "deploy":
            return {"status": "DENY", "reason": "deploy_requires_trusted_tier", "tier": tier}
        if action_type == "run_shell" and agent_role not in ("builder", "critic", "admin"):
            return {"status": "DENY", "reason": "run_shell_role_blocked", "tier": tier}

    return {"status": "ALLOW", "reason": "reputation_ok", "tier": tier, "reputation": rep}


def check_permission(*, agent_role: str, action_type: str, level: str = "") -> dict[str, Any]:
    role = (agent_role or "builder").lower()
    allowed = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["builder"])
    if level and level in LEVEL_PERMISSIONS:
        allowed = allowed | LEVEL_PERMISSIONS[level]
    if action_type in allowed:
        return {"status": "ALLOW", "reason": "role_ok"}
    return {"status": "DENY", "reason": f"action_not_allowed_for_role:{role}:{action_type}"}


def check_economy(*, agent_id: str, action_type: str, task_cost: float = 0.0, dry_run: bool = False) -> dict[str, Any]:
    if dry_run:
        return {"status": "ALLOW", "reason": "dry_run_skip_charge"}
    try:
        from forge_economy_v1 import action_cost, ensure_account  # noqa: WPS433

        acct = ensure_account(agent_id)
        required = action_cost(action_type) + max(0.0, float(task_cost or 0))
        balance = float(acct.get("balance") or 0)
        if balance < required * 1.05:
            return {"status": "DENY", "reason": "insufficient_credits", "balance": balance, "required": required}
        return {"status": "ALLOW", "reason": "credits_ok", "balance": balance, "estimated_cost": required}
    except Exception as exc:
        return {"status": "ALLOW", "reason": f"economy_fallback:{type(exc).__name__}"}


def validate_memory_write(*, payload: Any) -> dict[str, Any]:
    content = json.dumps(payload or {}, default=str)
    if MEMORY_FORBIDDEN.search(content):
        return {"status": "DENY", "reason": "memory_mutation_violation"}
    return {"status": "ALLOW", "reason": "memory_safe"}


def execution_firewall(*, action_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    if action_type == "run_shell":
        cmd = str(payload.get("cmd") or "")
        if SHELL_BANNED.search(cmd):
            return {"status": "DENY", "reason": "dangerous_shell_blocked"}
    if action_type == "deploy":
        if not payload.get("approved") and not payload.get("dry_run"):
            return {"status": "DENY", "reason": "deploy_requires_approval"}
    if action_type in ("write_file", "patch_file", "apply_git_patch", "apply_patch"):
        path = str(payload.get("path") or payload.get("diff") or "")[:500]
        if re.search(r"secrets\.env|/\.env\b|\.git/", path, re.I):
            return {"status": "DENY", "reason": "forbidden_path"}
    return {"status": "ALLOW", "reason": "execution_safe"}


def sync_agent_status_from_reputation(agent_id: str) -> None:
    """Dynamic role evolution — update status from reputation."""
    try:
        from forge_agent_registry_v1 import load_registry  # noqa: WPS433

        doc = load_registry()
        changed = False
        for agent in doc.get("agents") or []:
            if agent.get("id") != agent_id:
                continue
            rep = float(agent.get("reputation") or 0.5)
            tier = reputation_tier(rep)
            new_status = "active"
            if tier == "restricted":
                new_status = "restricted"
            elif tier == "probation":
                new_status = "probation"
            if agent.get("status") != new_status:
                agent["status"] = new_status
                changed = True
        if changed:
            from forge_agent_registry_v1 import _save  # noqa: WPS433

            _save(doc)
    except Exception:
        pass


def govern(
    *,
    agent_id: str,
    agent_role: str,
    action_type: str,
    payload: dict[str, Any] | None = None,
    task_id: str = "",
    level: str = "",
    task_cost: float = 0.0,
    dry_run: bool = False,
    charge_on_allow: bool = True,
    legal_review: bool = True,
) -> dict[str, Any]:
    """Core v4 decision engine — geo + ALLOW/DENY + economy + legal arbitration."""
    payload = dict(payload or {})

    geo_row: dict[str, Any] = {"status": "ALLOW", "reason": "geo_skip"}
    try:
        from forge_geopolitical_legal_v4 import (  # noqa: WPS433
            check_geopolitical,
            international_court,
            process_cross_border_violation,
        )

        geo_row = check_geopolitical(agent_id=agent_id, action_type=action_type, payload=payload)
        if geo_row.get("status") == "DENY" and geo_row.get("reason") == "sanction_active":
            return {
                "status": "DENY",
                "reason": "geo_sanction_active",
                "schema": "forge-governance-decision-v4",
                "version": GOVERNANCE_VERSION,
                "agent_id": agent_id,
                "action_type": action_type,
                "geo": geo_row,
                "at": _now(),
            }
        if geo_row.get("status") == "DENY" and legal_review and geo_row.get("geo", {}).get("cross_border"):
            geo_legal = process_cross_border_violation(
                agent_id=agent_id,
                agent_role=agent_role,
                action_type=action_type,
                payload=payload,
                dry_run=dry_run,
            )
            if geo_legal.get("governance_status") == "ALLOW":
                geo_row = {"status": "ALLOW", "reason": "international_court_acquittal", "geo": geo_row.get("geo")}
            else:
                return {
                    "status": "DENY",
                    "reason": str(geo_legal.get("judgment", {}).get("verdict") or "geo_denied"),
                    "schema": "forge-governance-decision-v4",
                    "version": GOVERNANCE_VERSION,
                    "agent_id": agent_id,
                    "action_type": action_type,
                    "geo": geo_row,
                    "geo_legal": geo_legal,
                    "at": _now(),
                }
    except Exception:
        pass

    rep_check = check_reputation_permissions(agent_id=agent_id, agent_role=agent_role, action_type=action_type)
    checks = [
        check_permission(agent_role=agent_role, action_type=action_type, level=level),
        rep_check,
        check_economy(agent_id=agent_id, action_type=action_type, task_cost=task_cost, dry_run=dry_run),
    ]
    if geo_row.get("status") == "ALLOW" and geo_row.get("reason") not in ("geo_skip",):
        checks.append({"status": "ALLOW", "reason": "geo_permitted", "geo": geo_row.get("geo")})
    elif geo_row.get("status") == "DENY":
        checks.append({"status": "DENY", "reason": geo_row.get("reason", "geo_denied"), "geo": geo_row.get("geo")})
    if action_type == "memory_write":
        checks.append(validate_memory_write(payload=payload))
    checks.append(execution_firewall(action_type=action_type, payload=payload))

    try:
        from forge_governance_legal_v3 import detect_rule_conflict, process_violation  # noqa: WPS433

        conflict = detect_rule_conflict(checks)
    except Exception:
        conflict = False
        process_violation = None  # type: ignore

    denies = [c for c in checks if c.get("status") == "DENY"]

    if conflict and legal_review and process_violation:
        primary_reason = str(denies[0].get("reason") if denies else "rule_conflict")
        legal = process_violation(
            agent_id=agent_id,
            agent_role=agent_role,
            action_type=action_type,
            payload=payload,
            violation=primary_reason,
            checks=checks,
            conflict=True,
            dry_run=dry_run,
        )
        status = legal.get("governance_status", "DENY")
        judgment = legal.get("judgment") or {}
        if status == "ALLOW":
            charge_row: dict[str, Any] = {}
            if charge_on_allow and not dry_run:
                try:
                    from forge_economy_v1 import charge_action  # noqa: WPS433

                    charge_row = charge_action(agent_id=agent_id, action_type=action_type, task_cost=task_cost)
                except Exception:
                    pass
            decision = {
                "status": "ALLOW",
                "reason": "legal_arbitration_acquittal",
                "schema": "forge-governance-decision-v4",
                "version": GOVERNANCE_VERSION,
                "agent_id": agent_id,
                "action_type": action_type,
                "reputation_tier": rep_check.get("tier"),
                "legal": legal,
                "judgment_verdict": judgment.get("verdict"),
                "economy": charge_row,
                "at": _now(),
            }
            SINA.mkdir(parents=True, exist_ok=True)
            LATEST_RECEIPT.write_text(json.dumps(decision, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return decision

        log_violation(
            agent_id=agent_id,
            agent_role=agent_role,
            action_type=action_type,
            reason=f"legal_guilty:{judgment.get('verdict')}",
            task_id=task_id,
            apply_penalty=not dry_run,
        )
        return {
            "status": "DENY",
            "reason": "legal_arbitration_guilty",
            "schema": "forge-governance-decision-v4",
            "version": GOVERNANCE_VERSION,
            "agent_id": agent_id,
            "action_type": action_type,
            "reputation_tier": rep_check.get("tier"),
            "legal": legal,
            "judgment_verdict": judgment.get("verdict"),
            "at": _now(),
        }

    for c in checks:
        if c.get("status") == "DENY":
            log_violation(
                agent_id=agent_id,
                agent_role=agent_role,
                action_type=action_type,
                reason=str(c.get("reason") or "denied"),
                task_id=task_id,
                apply_penalty=not dry_run,
            )
            sync_agent_status_from_reputation(agent_id)
            return {
                "status": "DENY",
                "reason": c.get("reason"),
                "schema": "forge-governance-decision-v4",
                "version": GOVERNANCE_VERSION,
                "agent_id": agent_id,
                "action_type": action_type,
                "reputation_tier": rep_check.get("tier"),
                "at": _now(),
            }

    charge_row: dict[str, Any] = {}
    if charge_on_allow and not dry_run:
        try:
            from forge_economy_v1 import charge_action, reward_agent  # noqa: WPS433

            charge_row = charge_action(agent_id=agent_id, action_type=action_type, task_cost=task_cost)
            if not charge_row.get("ok"):
                log_violation(
                    agent_id=agent_id,
                    agent_role=agent_role,
                    action_type=action_type,
                    reason="charge_failed",
                    task_id=task_id,
                    apply_penalty=False,
                )
                return {
                    "status": "DENY",
                    "reason": "insufficient_credits_at_charge",
                    "schema": "forge-governance-decision-v4",
                    "version": GOVERNANCE_VERSION,
                    "agent_id": agent_id,
                    "at": _now(),
                }
            if action_type in HIGH_COST_ACTIONS:
                reward_agent(agent_id=agent_id, amount=0.02, reason="high_cost_action_rebate")
        except Exception:
            pass

    decision = {
        "status": "ALLOW",
        "reason": "approved",
        "schema": "forge-governance-decision-v4",
        "version": GOVERNANCE_VERSION,
        "agent_id": agent_id,
        "action_type": action_type,
        "reputation_tier": rep_check.get("tier"),
        "economy": charge_row,
        "at": _now(),
    }
    SINA.mkdir(parents=True, exist_ok=True)
    LATEST_RECEIPT.write_text(json.dumps(decision, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return decision


def log_violation(
    *,
    agent_id: str,
    agent_role: str,
    action_type: str,
    reason: str,
    task_id: str = "",
    apply_penalty: bool = True,
) -> None:
    row = {
        "agent_id": agent_id,
        "agent_role": agent_role,
        "action_type": action_type,
        "reason": reason,
        "task_id": task_id,
        "version": GOVERNANCE_VERSION,
        "at": _now(),
    }
    if apply_penalty:
        try:
            from forge_economy_v1 import apply_violation_penalty  # noqa: WPS433
            from forge_agent_registry_v1 import update_reputation  # noqa: WPS433

            pen = apply_violation_penalty(agent_id=agent_id)
            row["penalty"] = pen
            update_reputation(agent_ids=[agent_id], success=False)
            sync_agent_status_from_reputation(agent_id)
        except Exception:
            pass
    SINA.mkdir(parents=True, exist_ok=True)
    with VIOLATIONS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def intercept_tool_execute(
    *,
    agent_id: str,
    agent_role: str,
    tool: str,
    args: dict[str, Any],
    execute_fn: Any,
    task_id: str = "",
    level: str = "",
    task_cost: float = 0.0,
    dry_run: bool = False,
    **execute_kw: Any,
) -> dict[str, Any]:
    decision = govern(
        agent_id=agent_id,
        agent_role=agent_role,
        action_type=tool,
        payload=args,
        task_id=task_id,
        level=level,
        task_cost=task_cost,
        dry_run=dry_run,
    )
    if decision.get("status") == "DENY":
        return {"ok": False, "error": "governance_denied", "governance": decision}
    return execute_fn(**execute_kw)


def list_violations(*, limit: int = 20) -> list[dict[str, Any]]:
    if not VIOLATIONS_LOG.is_file():
        return []
    lines = VIOLATIONS_LOG.read_text(encoding="utf-8").strip().splitlines()
    out: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out
