#!/usr/bin/env python3
"""Council strategic brief — founder verdict slice surfaced in hub payloads."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
BRIEF_DOC = "COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md"
BRIEF_ID = "STRATEGIC-SLICE-EVAL-L0-ENFORCE-v1"
SCHEMA = "council-strategic-brief-v1"
SSOT_TRUST_ORDER = "~/.sina + validators > hub Refresh > external chat"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _brief_path() -> Path:
    return SOURCE_A / BRIEF_DOC


def _load_eval_report(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        import json

        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def eval_comparison() -> dict:
    """Eval-1 structural vs Eval-1b behavioral — council brief machine slice."""
    v1 = _load_eval_report(Path.home() / ".sina" / "eval_packet_v1_report.json")
    v1b = _load_eval_report(Path.home() / ".sina" / "eval_packet_v1b_report.json")
    eval_gate_ok = False
    eval_gate_note = ""
    try:
        import sys

        scripts = Path(__file__).resolve().parent
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from runtime.dispatch_policy.policy_engine import eval_1b_gate_status

        eval_gate_ok, eval_gate_note = eval_1b_gate_status()
    except Exception as exc:  # noqa: BLE001
        eval_gate_note = str(exc)
    return {
        "registry_sa": "sa-0141",
        "prior_sa": "sa-0116",
        "doc_section": "Eval-1 vs Eval-1b — comparison (do not conflate)",
        "doc_path": BRIEF_DOC,
        "refreshed_at": _now(),
        "eval_1": {
            "id": "eval-1",
            "layer": "structural",
            "producer": "Eval-1",
            "live_llm": False,
            "metric": "readiness_score + gate_eligible",
            "threshold_pct": v1.get("threshold_pct", 80),
            "packet_win_pct": v1.get("packet_win_pct"),
            "task_count": v1.get("task_count"),
            "ok": v1.get("ok"),
            "generated_at": v1.get("generated_at"),
            "report_path": str(Path.home() / ".sina" / "eval_packet_v1_report.json"),
            "api": "/api/eval-packet-v1",
            "validator": "validate-eval-packet-v1.sh",
            "validators": ["validate-eval-packet-v1.sh"],
        },
        "eval_1b": {
            "id": "eval-1b",
            "layer": "behavioral",
            "producer": "Eval-1b",
            "mode": v1b.get("mode", "scaffold"),
            "scaffold_ok": v1b.get("scaffold_ok"),
            "scaffold_win_pct": v1b.get("scaffold_win_pct"),
            "live_ready": v1b.get("live_ready"),
            "live_pilot_win_pct": v1b.get("live_pilot_win_pct"),
            "live_pilot_count": v1b.get("live_pilot_count"),
            "metric": "scaffold composite + live pilot A/B",
            "threshold_pct": v1b.get("threshold_pct", 70),
            "ok": v1b.get("ok"),
            "generated_at": v1b.get("generated_at"),
            "report_path": str(Path.home() / ".sina" / "eval_packet_v1b_report.json"),
            "api": "/api/eval-packet-v1b",
            "validator": "validate-eval-packet-v1b.sh",
            "validators": [
                "validate-eval-packet-v1b.sh",
                "validate-eval-packet-v1b-grounding.sh",
                "validate-eval-packet-v1b-live.sh",
            ],
        },
        "comparison_table": [
            {
                "dimension": "Question",
                "eval_1": "Does assembled packet beat empty template on gate readiness?",
                "eval_1b": "Does packet context beat raw prompt on task outcome?",
            },
            {
                "dimension": "Live LLM",
                "eval_1": "Never — assembly / validate_packet only",
                "eval_1b": f"Scaffold: no · Live arm: OpenRouter (mode={v1b.get('mode', 'scaffold')})",
            },
            {
                "dimension": "Win metric",
                "eval_1": "readiness_score, gate_eligible",
                "eval_1b": "scaffold composite · live pilot A/B",
            },
            {
                "dimension": "Threshold",
                "eval_1": f"{v1.get('threshold_pct', 80)}% packet wins",
                "eval_1b": f"scaffold {v1b.get('threshold_pct', 70)}% · live pilots 80%",
            },
            {
                "dimension": "Dispatch gate",
                "eval_1": "Informational — sustains slice",
                "eval_1b": "eval_1b_gate_ok from policy_engine",
            },
        ],
        "relationship": (
            "Eval-1 proves packet assembly beats empty template without LLM. "
            "Eval-1b proves packet beats raw on task outcomes (scaffold proxy; live when credits)."
        ),
        "gate": {
            "eval_1b_gate_ok": eval_gate_ok,
            "eval_1b_gate_note": eval_gate_note,
            "dispatch_ready": False,
        },
        "summary_one_line": (
            f"Eval-1 structural {v1.get('packet_win_pct', '?')}% · "
            f"Eval-1b {v1b.get('mode', 'scaffold')} "
            f"{v1b.get('scaffold_win_pct') or v1b.get('packet_win_pct', '?')}% · "
            f"eval_1b_gate_ok={eval_gate_ok}"
        ),
    }


def load_brief_text(*, max_chars: int = 12000) -> str:
    path = _brief_path()
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n… [truncated — open full doc in hub]"


def strategic_brief_payload() -> dict:
    path = _brief_path()
    text = load_brief_text()
    workstreams = [
        {
            "id": "eval-1",
            "title": "Eval-1 sustain",
            "api": "/api/eval-packet-v1",
            "validator": "validate-eval-packet-v1.sh",
            "hub_jump": "eval-packet-panel",
        },
        {
            "id": "l0-l1",
            "title": "L0/L1 user + workspace signals",
            "api": "/api/user-workspace-signals-v1",
            "validator": "validate-user-workspace-signals-v1.sh",
            "hub_jump": "user-signals-panel",
        },
        {
            "id": "enforce-coverage",
            "title": "ENFORCE coverage + bypass map",
            "api": "/api/gate-receipts-v1",
            "validator": "validate-gate-receipts-v1.sh",
            "hub_jump": "gate-receipts-panel",
        },
        {
            "id": "eval-1b",
            "title": "Eval-1b behavioral proof",
            "api": "/api/eval-packet-v1b",
            "validator": "validate-eval-packet-v1b.sh",
            "hub_jump": "eval-1b-panel",
        },
        {
            "id": "rules-in-charge",
            "title": "Rules-in-charge loop",
            "api": "/api/agent-rules-in-charge-v1",
            "validator": "validate-agent-rules-in-charge-v1.sh",
            "hub_jump": "council-room",
        },
    ]
    return {
        "ok": bool(text),
        "schema": SCHEMA,
        "id": BRIEF_ID,
        "title": "Strategic slice — Eval-1 + L0/L1 + ENFORCE transparency",
        "verdict_one_line": (
            "GPT/Claude correct on architecture gaps; unreliable on ops state; "
            "silent on governance. Next: Eval-1 + L0/L1 + ENFORCE map — not new D-module."
        ),
        "doc_path": BRIEF_DOC,
        "doc_abs": str(path),
        "issued": "2026-05-27",
        "scope_agents": ["founder", "trustfield", "ai_dev_bridge_os"],
        "scope_lanes": ["TrustField", "Wire", "SourceA maintainer"],
        "deferred": ["L8 embeddings primary", "new D-modules", "C7 auto-dispatch", "event_bus"],
        "ssot_trust_order": SSOT_TRUST_ORDER,
        "workstreams": workstreams,
        "eval_comparison": eval_comparison(),
        "copy_block": (
            "STRATEGIC SLICE (LOCKED): Eval-1 structural + Eval-1b behavioral + L0/L1 + ENFORCE bypass map. "
            f"SSOT trust order: {SSOT_TRUST_ORDER}. "
            "NOT new D-module. Rules-in-charge every round. "
            f"Doc: {BRIEF_DOC}"
        ),
        "body_markdown": text,
        "body_chars": len(text),
        "built_at": _now(),
        "hub_tabs": ["council-room", "track", "command"],
        "track_card_ids": [
            "track-strategic-slice-v1",
            "track-trustfield-slice-v1",
            "track-wire-slice-v1",
        ],
        "related_docs": [
            "STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md",
            "ENFORCE_BYPASS_MAP_LOCKED_v1.md",
            "SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md",
            "WORLD_TARGET_MODEL_MAP_LOCKED_v5.md",
        ],
    }
