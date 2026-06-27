#!/usr/bin/env python3
"""Chat Unify smart router — intent → machine + agent team + ROI model.

SSOT: data/chat-unify-smart-router-v1.json
Receipts: ~/.sina/chat-unify-engine/routing/
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ROUTER_SSOT = ROOT / "data" / "chat-unify-smart-router-v1.json"
FORGE_ROUTER = ROOT / "data" / "forge-mvp-router-rules-v0.1.json"
COST_ROUTER = ROOT / "data" / "cursor-cost-intelligence-routing-v1.json"
ROUTING_DIR = Path.home() / ".sina" / "chat-unify-engine" / "routing"
ROUTER_VERSION = "1.0.0"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return row if isinstance(row, dict) else {}


def load_router_ssot() -> dict[str, Any]:
    return _load_json(ROUTER_SSOT)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _score_intent(text: str, spec: dict[str, Any]) -> float:
    t = _normalize(text)
    if not t:
        return 0.0
    score = 0.0
    for kw in spec.get("keywords") or []:
        k = str(kw).lower()
        if k in t:
            score += 2.5 if len(k) > 6 else 1.5
        if t.startswith(k) or t.endswith(k):
            score += 0.5
    return score


def classify_intent(text: str, *, ssot: dict[str, Any] | None = None) -> tuple[str, float, dict[str, Any]]:
    doc = ssot or load_router_ssot()
    intents = doc.get("intents") if isinstance(doc.get("intents"), dict) else {}
    scores: list[tuple[str, float, dict[str, Any]]] = []
    for name, spec in intents.items():
        if not isinstance(spec, dict):
            continue
        s = _score_intent(text, spec)
        if s > 0:
            scores.append((name, s, spec))
    scores.sort(key=lambda x: x[1], reverse=True)
    if not scores:
        default = intents.get("chat") if isinstance(intents.get("chat"), dict) else {}
        return "chat", 0.35, default
    best_name, best_score, best_spec = scores[0]
    total = sum(s for _, s, _ in scores) or 1.0
    confidence = min(0.98, round(best_score / total, 2))
    return best_name, confidence, best_spec


def _complexity_team(text: str, ssot: dict[str, Any]) -> list[str] | None:
    boost = ssot.get("complexity_boost") if isinstance(ssot.get("complexity_boost"), dict) else {}
    min_chars = int(boost.get("min_chars_multi") or 420)
    min_lines = int(boost.get("min_lines_multi") or 12)
    lines = [ln for ln in (text or "").splitlines() if ln.strip()]
    if len(text) >= min_chars and len(lines) >= min_lines:
        team = boost.get("multi_agents")
        if isinstance(team, list) and team:
            return [str(a) for a in team]
    return None


def _pick_model(work_tier: str, task_kind: str = "") -> dict[str, str]:
    role = work_tier or "bulk"
    try:
        from model_dispatch import resolve_sourcea_model  # noqa: WPS433

        resolved = resolve_sourcea_model(product="chat_unify", role=role, preserve_explicit=True)
        return {
            "model_id": str(resolved.get("model_id") or "gpt-4o"),
            "provider": str(resolved.get("provider") or "auto"),
            "api_model": str(resolved.get("api_model") or resolved.get("model_id") or "gpt-4o"),
            "work_tier": role,
        }
    except Exception:
        return {"model_id": "gpt-4o", "provider": "openai", "api_model": "gpt-4o", "work_tier": role}


def _machine_row(machine_id: str) -> dict[str, Any]:
    try:
        from chat_unify_engine_v1 import MACHINES  # noqa: WPS433
    except Exception:
        MACHINES = []
    for m in MACHINES:
        if m.get("id") == machine_id:
            return dict(m)
    return {"id": machine_id, "label": machine_id}


def _write_receipt(row: dict[str, Any]) -> str:
    ROUTING_DIR.mkdir(parents=True, exist_ok=True)
    rid = str(row.get("route_id") or uuid.uuid4().hex[:12])
    path = ROUTING_DIR / f"{rid}.json"
    row["receipt_at"] = _now()
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return str(path)


def route_request(
    text: str,
    *,
    workspace_path: str | None = None,
    explicit_agent: str | None = None,
    explicit_machine: str | None = None,
    save_receipt: bool = True,
) -> dict[str, Any]:
    """Return routing decision for founder text."""
    ssot = load_router_ssot()
    forge_rules = _load_json(FORGE_ROUTER)
    intent, confidence, spec = classify_intent(text, ssot=ssot)
    if spec.get("force_multi"):
        agent_team = list(spec.get("agents") or ["planner", "builder", "verifier"])
    else:
        complexity_team = _complexity_team(text, ssot)
        if complexity_team:
            intent = "multi"
            confidence = max(confidence, 0.72)
            agent_team = complexity_team
        else:
            agent_team = list(spec.get("agents") or ["builder"])

    if explicit_agent and explicit_agent not in ("auto", "smart"):
        agent_team = [explicit_agent]
    machine_id = explicit_machine or str(spec.get("machine") or "living-chat")
    work_tier = str(spec.get("work_tier") or "bulk")
    task_kind = str(spec.get("task_kind") or "")
    tier_map = ssot.get("tier_to_forge_role") if isinstance(ssot.get("tier_to_forge_role"), dict) else {}
    forge_role = str(tier_map.get(work_tier) or work_tier)
    model_row = _pick_model(forge_role, task_kind)

    task_lanes = forge_rules.get("route_by_task_kind") if isinstance(forge_rules.get("route_by_task_kind"), dict) else {}
    mvp_lane = str(task_lanes.get(task_kind) or "")

    primary_agent = agent_team[0] if agent_team else "builder"
    use_multi = len(agent_team) > 1
    route_id = f"cu-route-{uuid.uuid4().hex[:10]}"

    reasons = [
        f"intent={intent} ({confidence:.0%})",
        f"machine={machine_id}",
        f"team={'→'.join(agent_team)}",
        f"model={model_row['model_id']} ({forge_role})",
    ]
    if mvp_lane:
        reasons.append(f"mvp_lane={mvp_lane}")

    row: dict[str, Any] = {
        "ok": True,
        "schema": "chat-unify-smart-route-v1",
        "version": ROUTER_VERSION,
        "route_id": route_id,
        "at": _now(),
        "intent": intent,
        "confidence": confidence,
        "machine": _machine_row(machine_id),
        "machine_tab": machine_id,
        "agent_team": agent_team,
        "primary_agent": primary_agent,
        "use_multi_agent": use_multi,
        "work_tier": forge_role,
        "task_kind": task_kind,
        "mvp_lane": mvp_lane or None,
        "model_id": model_row["model_id"],
        "provider": model_row["provider"],
        "api_model": model_row.get("api_model"),
        "reasoning": " · ".join(reasons),
        "sources": list(ssot.get("authority") or [])[:6],
        "workspace_path": workspace_path,
        "text_preview": (text or "")[:160],
    }
    if save_receipt:
        row["receipt_path"] = _write_receipt(row)
    return row


def explain_route(route: dict[str, Any]) -> str:
    m = route.get("machine") or {}
    team = route.get("agent_team") or []
    return (
        f"Smart route · {route.get('intent')} · open **{m.get('label', route.get('machine_tab'))}** · "
        f"team: {' → '.join(team)} · model: {route.get('model_id')}"
    )
