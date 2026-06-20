"""Hub API — /api/graph-executor-v1"""
from __future__ import annotations

from pathlib import Path

from runtime.graph_executor.executor_engine import EXECUTOR_SSOT_PATH, run_graph_executor

SCHEMA = "graph-executor-v1"


def _clamp_founder_law(payload: dict) -> dict:
    """Hub graph layer — dispatch_ready stays false until founder spine Action (sa-0155)."""
    from runtime.dispatch_policy.policy_engine import orchestrator_dispatch_ready_payload  # noqa: WPS433

    out = dict(payload)
    orch = orchestrator_dispatch_ready_payload()
    out["dispatch_ready"] = False
    out["orchestrator_dispatch_ready"] = bool(orch.get("dispatch_ready"))
    out["dispatch_ready_blockers"] = list(orch.get("dispatch_ready_blockers") or [])
    out["eval_1b_gate_ok"] = bool(orch.get("eval_1b_gate_ok"))
    out["founder_spine_bridge_gate_ok"] = bool(orch.get("founder_spine_bridge_gate_ok"))
    out["founder_confirm_required"] = True
    if out.get("auto_dispatch"):
        out["auto_dispatch"] = False
    return out


def graph_executor_v1_payload(*, goal_tool_id: str = "pos-run", task_id: str = "") -> dict:
    if EXECUTOR_SSOT_PATH.is_file() and not task_id:
        try:
            import json

            cached = json.loads(EXECUTOR_SSOT_PATH.read_text(encoding="utf-8"))
            if cached.get("schema") == SCHEMA:
                return _clamp_founder_law({**cached, "from_disk": True})
        except (json.JSONDecodeError, OSError):
            pass
    return _clamp_founder_law(run_graph_executor(goal_tool_id=goal_tool_id, task_id=task_id))
