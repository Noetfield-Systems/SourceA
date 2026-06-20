"""Hub surface for ENFORCE/SHADOW gate receipts + bypass map."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE_A = Path(__file__).resolve().parents[1]
BYPASS_DOC = "brain-os/law/enforcement/law/enforcement/ENFORCE_BYPASS_MAP_LOCKED_v1.md"
ENFORCE_LOG = Path.home() / ".sina" / "gate_enforce_v1.jsonl"
SHADOW_LOG = Path.home() / ".sina" / "gate_shadow_v1.jsonl"

BYPASS_ROUTES = [
    {"route": "agent_loop planner", "enforce": True, "note": "Primary choke — gate_eligible"},
    {
        "route": "Hub Advisor / loop_advisor",
        "enforce": False,
        "note": "Partial — vault OpenRouter; enforce:false = not planner-gated (doc: Partial)",
    },
    {
        "route": "Intelligence circle live agents",
        "enforce": False,
        "note": "Partial — per-agent session; not packet-gated today",
    },
    {"route": "Cursor IDE", "enforce": False, "note": "Direct model — outside hub"},
    {"route": "Spine / execution_router", "enforce": False, "note": "dispatch_ready false — human confirm"},
    {"route": "Refresh / build scripts", "enforce": False, "note": "Local validators only"},
    {"route": "SEMEJ browser chain", "enforce": False, "note": "External Chrome AIs — compare only"},
    {"route": "Pre-LLM D1–D16 assembly", "enforce": False, "note": "No LLM ingress"},
]


def _tail_jsonl(path: Path, n: int = 12) -> list[dict]:
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    out: list[dict] = []
    for line in lines[-n:]:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _model_dispatch_surface() -> dict[str, Any]:
    try:
        import model_dispatch  # noqa: WPS433

        status = model_dispatch.gate_status_payload()
        ssot: dict[str, Any] = {}
        if model_dispatch.GATE_SSOT_PATH.is_file():
            ssot = json.loads(model_dispatch.GATE_SSOT_PATH.read_text(encoding="utf-8"))
        latest = ssot.get("latest") or {}
        decision = status.get("decision") or {}
        readiness = status.get("packet_readiness") or {}
        return {
            "ok": bool(status.get("ok")),
            "schema": model_dispatch.GATE_SCHEMA,
            "path": str(model_dispatch.GATE_SSOT_PATH),
            "producer": "model_dispatch.py",
            "current_mode": status.get("current_mode"),
            "decision": decision,
            "gate_eligible": readiness.get("gate_eligible"),
            "readiness_score": readiness.get("score"),
            "reason": decision.get("reason"),
            "ssot_generated_at": ssot.get("generated_at"),
            "ssot_latest": latest,
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "producer": "model_dispatch.py"}


def gate_receipts_hub_payload() -> dict[str, Any]:
    try:
        import model_dispatch  # noqa: WPS433

        mode = model_dispatch.current_gate_mode()
    except Exception:
        mode = "unknown"
    enforce = _tail_jsonl(ENFORCE_LOG)
    shadow = _tail_jsonl(SHADOW_LOG)
    blocked = sum(1 for r in enforce if not r.get("allowed"))
    md = _model_dispatch_surface()
    return {
        "ok": True,
        "schema": "gate-receipts-hub-v1",
        "api": "/api/gate-receipts-v1",
        "current_mode": mode,
        "enforce_log": str(ENFORCE_LOG),
        "shadow_log": str(SHADOW_LOG),
        "enforce_count": len(enforce),
        "shadow_count": len(shadow),
        "enforce_blocked": blocked,
        "enforce_recent": enforce,
        "shadow_recent": shadow[-6:],
        "model_dispatch": md,
        "coverage_note": (
            "ENFORCE blocks agent_loop planner when gate_eligible false; see bypass map · "
            f"model_dispatch: mode={md.get('current_mode')} reason={md.get('reason')} "
            f"eligible={md.get('gate_eligible')} score={md.get('readiness_score')}"
        ),
        "bypass_doc": BYPASS_DOC,
        "bypass_doc_abs": str(SOURCE_A / BYPASS_DOC),
        "bypass_routes": BYPASS_ROUTES,
    }
