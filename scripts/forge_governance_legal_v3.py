#!/usr/bin/env python3
"""Forge Governance Legal Layer v3 — cases, judges, precedent, arbitration, appeals.

When rules conflict, the system judges instead of blindly enforcing.
Stores: ~/.sina/forge-governance-cases-v3.json
        ~/.sina/forge-governance-precedent-v3.json
        ~/.sina/forge-governance-judgment-latest-v3.json
Law: brain-os/law/enforcement/SOURCEA_FORGE_GOVERNANCE_KERNEL_V3_LOCKED_v1.md
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

SINA = Path.home() / ".sina"
CASES_STORE = SINA / "forge-governance-cases-v3.json"
PRECEDENT_STORE = SINA / "forge-governance-precedent-v3.json"
JUDGMENT_RECEIPT = SINA / "forge-governance-judgment-latest-v3.json"
SCHEMA = "forge-governance-legal-v3"
LEGAL_VERSION = "3.0.0"

JudgeType = Literal["constitutional", "economic", "security", "precedent"]
Verdict = Literal["GUILTY", "NOT_GUILTY", "PARTIAL"]
CaseStatus = Literal["open", "reviewing", "ruled", "appealed"]

CONSTITUTION_RULES = [
    "No agent may exceed assigned permissions",
    "No destructive system commands",
    "No memory overwrite without validation",
    "All deployments must pass firewall",
    "All patches must be verifiable",
    "Actions consume FORGE credits; violations incur penalties",
    "Low reputation restricts tools (probation mode)",
    "Rule conflicts MUST be resolved by arbitration, not first-deny",
]

JUDGE_TYPES: tuple[JudgeType, ...] = ("constitutional", "economic", "security", "precedent")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any) -> Any:
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return default


def _save_json(path: Path, data: Any) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_cases() -> dict[str, Any]:
    doc = _load_json(CASES_STORE, {"schema": SCHEMA, "cases": []})
    if not isinstance(doc.get("cases"), list):
        doc["cases"] = []
    return doc


def save_case(case: dict[str, Any]) -> dict[str, Any]:
    doc = load_cases()
    cases: list[dict[str, Any]] = doc["cases"]
    replaced = False
    for i, row in enumerate(cases):
        if row.get("id") == case.get("id"):
            cases[i] = case
            replaced = True
            break
    if not replaced:
        cases.append(case)
    doc["cases"] = cases[-500:]
    doc["updated_at"] = _now()
    _save_json(CASES_STORE, doc)
    return case


def load_case(case_id: str) -> dict[str, Any] | None:
    for row in load_cases().get("cases") or []:
        if row.get("id") == case_id:
            return row
    return None


def load_precedents() -> dict[str, Any]:
    doc = _load_json(PRECEDENT_STORE, {"schema": "forge-governance-precedent-v3", "precedents": []})
    if not isinstance(doc.get("precedents"), list):
        doc["precedents"] = []
    return doc


def add_precedent(*, case_summary: str, ruling: str, verdict: str, weight: float = 1.0) -> dict[str, Any]:
    doc = load_precedents()
    row = {
        "id": f"prec-{uuid.uuid4().hex[:10]}",
        "caseSummary": case_summary[:500],
        "ruling": ruling[:1000],
        "verdict": verdict,
        "weight": round(weight, 3),
        "at": _now(),
    }
    doc["precedents"] = (doc.get("precedents") or [])[-300:] + [row]
    doc["updated_at"] = _now()
    _save_json(PRECEDENT_STORE, doc)
    return row


def search_precedents(*, violation: str, action_type: str, limit: int = 5) -> list[dict[str, Any]]:
    needle = f"{violation} {action_type}".lower()
    scored: list[tuple[float, dict[str, Any]]] = []
    for p in load_precedents().get("precedents") or []:
        blob = f"{p.get('caseSummary', '')} {p.get('ruling', '')} {p.get('verdict', '')}".lower()
        score = 0.0
        for token in needle.split():
            if len(token) > 3 and token in blob:
                score += 1.0
        score *= float(p.get("weight") or 1.0)
        if score > 0:
            scored.append((score, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:limit]]


def collect_evidence(*, action_type: str, payload: dict[str, Any], checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"kind": "action", "action_type": action_type, "payload_keys": list((payload or {}).keys())[:20]},
        {"kind": "checks", "results": [{"status": c.get("status"), "reason": c.get("reason")} for c in checks]},
        {"kind": "constitution", "rules_count": len(CONSTITUTION_RULES)},
    ]


def create_case(
    *,
    action: dict[str, Any],
    agent_id: str,
    violation: str,
    checks: list[dict[str, Any]] | None = None,
    conflict: bool = False,
) -> dict[str, Any]:
    action_type = str(action.get("action_type") or "")
    payload = dict(action.get("payload") or {})
    case = {
        "id": f"case-{uuid.uuid4().hex[:10]}",
        "plaintiff": "governance_kernel",
        "defendant": agent_id,
        "action": action,
        "violation": violation,
        "evidence": collect_evidence(action_type=action_type, payload=payload, checks=checks or []),
        "status": "open",
        "conflict": conflict,
        "at": _now(),
    }
    return save_case(case)


def _judge_constitutional(legal_case: dict[str, Any]) -> dict[str, Any]:
    violation = str(legal_case.get("violation") or "")
    role_block = "action_not_allowed_for_role" in violation or "role_blocked" in violation
    tier_block = "probation_tier" in violation or "restricted_tier" in violation
    if legal_case.get("conflict") and tier_block and not role_block:
        return {"judge": "constitutional", "verdict": "PARTIAL", "reasoning": "Role permits; reputation restricts — partial fault"}
    if role_block or "dangerous_shell" in violation or "memory_mutation" in violation:
        return {"judge": "constitutional", "verdict": "GUILTY", "reasoning": "Constitutional rule violated"}
    if tier_block:
        return {"judge": "constitutional", "verdict": "GUILTY", "reasoning": "Reputation tier blocks action"}
    return {"judge": "constitutional", "verdict": "NOT_GUILTY", "reasoning": "No constitutional breach"}


def _judge_economic(legal_case: dict[str, Any]) -> dict[str, Any]:
    violation = str(legal_case.get("violation") or "")
    if "insufficient_credits" in violation or "charge_failed" in violation:
        return {"judge": "economic", "verdict": "GUILTY", "reasoning": "Insufficient FORGE credits"}
    if legal_case.get("conflict") and "credits_ok" in violation:
        return {"judge": "economic", "verdict": "NOT_GUILTY", "reasoning": "Economy permits; other layer conflicts"}
    return {"judge": "economic", "verdict": "NOT_GUILTY", "reasoning": "Economic impact acceptable"}


def _judge_security(legal_case: dict[str, Any]) -> dict[str, Any]:
    violation = str(legal_case.get("violation") or "")
    action = legal_case.get("action") or {}
    payload = action.get("payload") or {}
    if any(k in violation for k in ("dangerous_shell", "forbidden_path", "memory_mutation", "deploy_requires")):
        return {"judge": "security", "verdict": "GUILTY", "reasoning": "Security firewall triggered"}
    if str(action.get("action_type")) == "run_shell" and "rm" in str(payload.get("cmd") or ""):
        return {"judge": "security", "verdict": "GUILTY", "reasoning": "Destructive shell pattern"}
    return {"judge": "security", "verdict": "NOT_GUILTY", "reasoning": "No security threat detected"}


def _judge_precedent(legal_case: dict[str, Any]) -> dict[str, Any]:
    action = legal_case.get("action") or {}
    hits = search_precedents(
        violation=str(legal_case.get("violation") or ""),
        action_type=str(action.get("action_type") or ""),
    )
    if not hits:
        return {"judge": "precedent", "verdict": "PARTIAL", "reasoning": "No precedent — defer to panel majority"}
    top = hits[0]
    verdict = str(top.get("verdict") or "PARTIAL")
    if verdict not in ("GUILTY", "NOT_GUILTY", "PARTIAL"):
        verdict = "PARTIAL"
    return {
        "judge": "precedent",
        "verdict": verdict,
        "reasoning": f"Precedent {top.get('id')}: {top.get('ruling', '')[:120]}",
        "precedent_id": top.get("id"),
    }


def judge_case(legal_case: dict[str, Any], *, judge_type: JudgeType = "constitutional", dry_run: bool = True) -> dict[str, Any]:
    """Judge a case — deterministic stubs on Mac (no LLM required)."""
    dispatch = {
        "constitutional": _judge_constitutional,
        "economic": _judge_economic,
        "security": _judge_security,
        "precedent": _judge_precedent,
    }
    fn = dispatch.get(judge_type, _judge_constitutional)
    row = fn(legal_case)
    row["dry_run"] = dry_run
    row["at"] = _now()
    return row


def spawn_judges(count: int = 3) -> list[JudgeType]:
    base: list[JudgeType] = ["constitutional", "economic", "security"]
    if count >= 4:
        base.append("precedent")
    while len(base) < count:
        base.append("constitutional")
    return base[:count]


def _verdict_score(verdict: str) -> int:
    return {"GUILTY": 1, "PARTIAL": 0, "NOT_GUILTY": -1}.get(verdict, 0)


def aggregate_rulings(rulings: list[dict[str, Any]]) -> dict[str, Any]:
    if not rulings:
        return {"verdict": "GUILTY", "score": 1, "split": False}
    scores = [_verdict_score(str(r.get("verdict") or "PARTIAL")) for r in rulings]
    total = sum(scores)
    split = len({r.get("verdict") for r in rulings}) > 1
    if total > 0:
        verdict: Verdict = "GUILTY"
    elif total < 0:
        verdict = "NOT_GUILTY"
    else:
        verdict = "PARTIAL"
    return {"verdict": verdict, "score": total, "split": split, "panel_size": len(rulings)}


def constitutional_court(legal_case: dict[str, Any], rulings: list[dict[str, Any]]) -> dict[str, Any]:
    """Top layer — resolves judge disagreement."""
    agg = aggregate_rulings(rulings)
    if not agg.get("split"):
        return {"escalated": False, "verdict": agg.get("verdict"), "reasoning": "Panel unanimous"}
    cc = judge_case(legal_case, judge_type="constitutional", dry_run=True)
    prec = judge_case(legal_case, judge_type="precedent", dry_run=True)
    # Constitutional court weights constitution + precedent over economy
    score = _verdict_score(str(cc.get("verdict"))) * 2 + _verdict_score(str(prec.get("verdict")))
    if score > 0:
        verdict: Verdict = "GUILTY"
    elif score < 0:
        verdict = "NOT_GUILTY"
    else:
        verdict = "PARTIAL"
    return {
        "escalated": True,
        "verdict": verdict,
        "reasoning": "Constitutional court resolved split panel",
        "constitutional_ruling": cc,
        "precedent_ruling": prec,
    }


def resolve_conflict(aggregated: dict[str, Any], precedent_influence: list[dict[str, Any]]) -> dict[str, Any]:
    verdict = str(aggregated.get("verdict") or "GUILTY")
    if precedent_influence and verdict == "PARTIAL":
        pv = str(precedent_influence[0].get("verdict") or "")
        if pv in ("GUILTY", "NOT_GUILTY"):
            verdict = pv
    credit_fine = 2.0 if verdict == "GUILTY" else (0.5 if verdict == "PARTIAL" else 0.0)
    rep_impact = -0.15 if verdict == "GUILTY" else (-0.05 if verdict == "PARTIAL" else 0.05)
    perm: list[str] = []
    if verdict == "GUILTY":
        perm.append("restrict_high_cost_actions")
    elif verdict == "NOT_GUILTY":
        perm.append("restore_standard_permissions")
    return {
        "verdict": verdict,
        "penalty": {
            "creditFine": credit_fine,
            "reputationImpact": rep_impact,
            "permissionChange": perm,
        },
    }


def arbitrate(
    legal_case: dict[str, Any],
    judge_results: list[dict[str, Any]] | None = None,
    *,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Arbitration core — aggregate judges + precedent → judgment."""
    legal_case = dict(legal_case)
    legal_case["status"] = "reviewing"
    save_case(legal_case)

    if judge_results is None:
        types = spawn_judges(4 if legal_case.get("conflict") else 3)
        judge_results = [judge_case(legal_case, judge_type=jt, dry_run=dry_run) for jt in types]

    aggregated = aggregate_rulings(judge_results)
    court = None
    if aggregated.get("split"):
        court = constitutional_court(legal_case, judge_results)
        aggregated["verdict"] = court.get("verdict")

    action = legal_case.get("action") or {}
    precedents = search_precedents(
        violation=str(legal_case.get("violation") or ""),
        action_type=str(action.get("action_type") or ""),
    )
    resolved = resolve_conflict(aggregated, precedents)

    precedent_row = add_precedent(
        case_summary=f"{legal_case.get('violation')} · {action.get('action_type')}",
        ruling=resolved.get("verdict", ""),
        verdict=str(resolved.get("verdict") or "PARTIAL"),
        weight=1.2 if legal_case.get("conflict") else 1.0,
    )

    judgment = {
        "schema": "forge-governance-judgment-v3",
        "version": LEGAL_VERSION,
        "caseId": legal_case.get("id"),
        "verdict": resolved.get("verdict"),
        "penalty": resolved.get("penalty"),
        "reasoning": "; ".join(r.get("reasoning", "")[:80] for r in judge_results[:4]),
        "precedentId": precedent_row.get("id"),
        "judge_results": judge_results,
        "constitutional_court": court,
        "precedent_influence": [p.get("id") for p in precedents[:3]],
        "dry_run": dry_run,
        "at": _now(),
    }

    legal_case["status"] = "ruled"
    legal_case["judgment"] = judgment
    save_case(legal_case)

    SINA.mkdir(parents=True, exist_ok=True)
    JUDGMENT_RECEIPT.write_text(json.dumps(judgment, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return judgment


def enforce_judgment(judgment: dict[str, Any], *, agent_id: str, dry_run: bool = True) -> dict[str, Any]:
    """Apply ruling penalties to agent wallet + reputation."""
    penalty = judgment.get("penalty") or {}
    verdict = str(judgment.get("verdict") or "GUILTY")
    out: dict[str, Any] = {"ok": True, "verdict": verdict, "agent_id": agent_id, "dry_run": dry_run}

    if dry_run:
        out["stub"] = True
        return out

    try:
        from forge_economy_v1 import apply_violation_penalty, reward_agent  # noqa: WPS433
        from forge_agent_registry_v1 import update_reputation  # noqa: WPS433
        from forge_governance_kernel_v1 import sync_agent_status_from_reputation  # noqa: WPS433

        fine = float(penalty.get("creditFine") or 0)
        if fine > 0 and verdict in ("GUILTY", "PARTIAL"):
            out["penalty_applied"] = apply_violation_penalty(agent_id=agent_id)
        if verdict == "NOT_GUILTY":
            reward_agent(agent_id=agent_id, amount=0.25, reason="legal_acquittal")
            update_reputation(agent_ids=[agent_id], success=True)
        elif verdict == "GUILTY":
            update_reputation(agent_ids=[agent_id], success=False)
        else:
            update_reputation(agent_ids=[agent_id], success=False)
        sync_agent_status_from_reputation(agent_id)
    except Exception as exc:
        out["ok"] = False
        out["error"] = str(exc)
    return out


def process_violation(
    *,
    agent_id: str,
    agent_role: str,
    action_type: str,
    payload: dict[str, Any],
    violation: str,
    checks: list[dict[str, Any]],
    conflict: bool = False,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Full legal flow: case → judges → arbitrate → enforce."""
    action = {"action_type": action_type, "payload": payload, "agent_role": agent_role}
    legal_case = create_case(action=action, agent_id=agent_id, violation=violation, checks=checks, conflict=conflict)
    judgment = arbitrate(legal_case, dry_run=dry_run)
    enforcement = enforce_judgment(judgment, agent_id=agent_id, dry_run=dry_run)
    allow = str(judgment.get("verdict")) == "NOT_GUILTY"
    return {
        "ok": True,
        "schema": SCHEMA,
        "version": LEGAL_VERSION,
        "case": legal_case,
        "judgment": judgment,
        "enforcement": enforcement,
        "governance_status": "ALLOW" if allow else "DENY",
        "at": _now(),
    }


def appeal(case_id: str, *, agent_id: str, dry_run: bool = True) -> dict[str, Any]:
    """Agent challenges a ruling — requires reputation ≥ 0.6."""
    case = load_case(case_id)
    if not case:
        return {"ok": False, "error": "case_not_found", "case_id": case_id}

    try:
        from forge_governance_kernel_v1 import _get_agent, reputation_tier  # noqa: WPS433

        agent = _get_agent(agent_id)
        rep = float(agent.get("reputation") or 0.5)
    except Exception:
        rep = 0.5

    if rep < 0.6:
        return {"ok": False, "error": "DENIED", "reason": "appeal_requires_trust_0.6", "reputation": rep}

    case["status"] = "appealed"
    save_case(case)
    types = spawn_judges(5)
    rulings = [judge_case(case, judge_type=jt, dry_run=dry_run) for jt in types]
    judgment = arbitrate(case, rulings, dry_run=dry_run)
    enforcement = enforce_judgment(judgment, agent_id=agent_id, dry_run=dry_run)
    allow = str(judgment.get("verdict")) == "NOT_GUILTY"
    return {
        "ok": True,
        "schema": SCHEMA,
        "appeal": True,
        "case_id": case_id,
        "judgment": judgment,
        "enforcement": enforcement,
        "governance_status": "ALLOW" if allow else "DENY",
        "at": _now(),
    }


def detect_rule_conflict(checks: list[dict[str, Any]]) -> bool:
    statuses = {c.get("status") for c in checks}
    return "ALLOW" in statuses and "DENY" in statuses
