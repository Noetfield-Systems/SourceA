"""Hub model dispatch — single OpenRouter choke point (D15.1)."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

GATE_MODE_PREF_PATH = Path.home() / ".sina" / "gate_mode_v1.txt"
SHADOW_LOG = Path.home() / ".sina" / "gate_shadow_v1.jsonl"
ENFORCE_LOG = Path.home() / ".sina" / "gate_enforce_v1.jsonl"
GATE_SSOT_PATH = Path.home() / ".sina" / "model_dispatch_gate_v1.json"
GATE_SCHEMA = "model-dispatch-gate-v1"
_VALID_GATE_MODES = ("off", "shadow", "enforce")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_gate_mode(raw: str) -> str:
    m = (raw or "").strip().lower()
    if m not in _VALID_GATE_MODES:
        return "shadow"
    return m


def read_gate_mode_pref() -> str:
    """Founder SSOT: env SINA_GATE_MODE overrides ~/.sina/gate_mode_v1.txt."""
    env = os.environ.get("SINA_GATE_MODE", "").strip()
    if env:
        return _normalize_gate_mode(env)
    if GATE_MODE_PREF_PATH.is_file():
        return _normalize_gate_mode(GATE_MODE_PREF_PATH.read_text(encoding="utf-8"))
    return "shadow"


def persist_gate_mode_pref(mode: str) -> None:
    m = _normalize_gate_mode(mode)
    GATE_MODE_PREF_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_MODE_PREF_PATH.write_text(m + "\n", encoding="utf-8")


def current_gate_mode() -> str:
    return read_gate_mode_pref()


def enforce_synthesis_critic_drift_errors(
    synthesis_text: str,
    gate_mode: str | None = None,
    *,
    label: str = "SINA_GPT_CLAUDE_WTM_SYNTHESIS",
) -> list[str]:
    """sa-0020 — critic ENFORCE claims must match ~/.sina/gate_mode_v1.txt + dispatch-policy API."""
    mode = _normalize_gate_mode(gate_mode or current_gate_mode())
    errors: list[str] = []
    if mode == "shadow":
        if "| Gate mode | **enforce** |" in synthesis_text:
            errors.append(f"{label}: Live results Gate mode stale — disk={mode!r}")
        if "gate_mode_v1.txt` = enforce" in synthesis_text:
            errors.append(f"{label}: Claude table claims enforce current — disk={mode!r}")
        head = synthesis_text[:900]
        if "ENFORCE is live" in head and "shadow" not in head:
            errors.append(f"{label}: verdict claims ENFORCE live — disk={mode!r}")
    elif mode == "enforce":
        if "| Gate mode | **shadow** |" in synthesis_text:
            errors.append(f"{label}: Live results Gate mode stale — disk={mode!r}")
    if f"**{mode}**" not in synthesis_text and f"= {mode}" not in synthesis_text:
        errors.append(f"{label}: missing current gate_mode {mode!r} in synthesis")
    return errors


def _append_log(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_gate_ssot(*, row: dict, validation: dict) -> None:
    GATE_SSOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": GATE_SCHEMA,
        "generated_at": _now(),
        "path": str(GATE_SSOT_PATH),
        "latest": {
            **row,
            "readiness_score": validation.get("readiness_score"),
            "gate_eligible": validation.get("gate_eligible"),
            "missing_for_gate": validation.get("missing_for_gate"),
            "modes": ["off", "shadow", "enforce"],
            "current_mode": current_gate_mode(),
            "shadow_log": str(SHADOW_LOG),
            "enforce_log": str(ENFORCE_LOG),
            "choke_law": "assemble → validate_packet → dispatch (agent_loop planner first)",
        },
    }
    GATE_SSOT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def prepare_packet(*, task_id: str, repo_root: str = "", query_text: str = "") -> dict[str, Any]:
    from pre_llm.context_packet.schema import empty_packet_template, hydrate_from_disk_substrate, validate_packet  # noqa: WPS433

    if query_text.strip():
        try:
            from pre_llm.context_assembly.assembly_engine import run_context_assembly  # noqa: WPS433

            assembled = run_context_assembly(
                text=query_text,
                repo_root=repo_root or None,
                task_id=task_id or "dispatch-stub",
                force_refresh=False,
            )
            if assembled.get("ok") and assembled.get("packet"):
                pkt = assembled["packet"]
                check = assembled.get("validation") or validate_packet(pkt)
                pkt["readiness"] = {
                    **(pkt.get("readiness") or {}),
                    "score": check.get("readiness_score"),
                    "gate_eligible": check.get("gate_eligible"),
                    "missing_for_gate": check.get("missing_for_gate"),
                }
                return {"packet": pkt, "validation": check}
        except Exception:
            pass

    pkt = empty_packet_template(task_id=task_id or "dispatch-stub", repo_root=repo_root)
    pkt = hydrate_from_disk_substrate(pkt)
    check = validate_packet(pkt)
    pkt["readiness"] = {
        **(pkt.get("readiness") or {}),
        "score": check.get("readiness_score"),
        "gate_eligible": check.get("gate_eligible"),
        "missing_for_gate": check.get("missing_for_gate"),
    }
    return {"packet": pkt, "validation": check}


def gate_decision(validation: dict) -> dict[str, Any]:
    mode = current_gate_mode()
    eligible = bool(validation.get("gate_eligible"))
    if mode == "off":
        return {"allowed": True, "mode": mode, "reason": "gate_off", "gate_eligible": eligible}
    if mode == "shadow":
        return {"allowed": True, "mode": mode, "reason": "shadow_log_only", "gate_eligible": eligible}
    if mode == "enforce" and not eligible:
        return {
            "allowed": False,
            "mode": mode,
            "reason": "gate_eligible_false",
            "gate_eligible": eligible,
            "missing_for_gate": validation.get("missing_for_gate") or [],
        }
    return {"allowed": True, "mode": mode, "reason": "gate_pass", "gate_eligible": eligible}


def gate_status_payload(*, task_id: str = "", repo_root: str = "", query_text: str = "") -> dict[str, Any]:
    prep = prepare_packet(task_id=task_id or "gate-status", repo_root=repo_root, query_text=query_text)
    val = prep["validation"]
    decision = gate_decision(val)
    return {
        "ok": True,
        "schema": GATE_SCHEMA,
        "api": "/api/model-dispatch-gate-v1",
        "path": str(GATE_SSOT_PATH),
        "producer": "D15.1",
        "current_mode": current_gate_mode(),
        "decision": decision,
        "validation": val,
        "packet_readiness": prep["packet"].get("readiness"),
    }


def dispatch_chat(
    *,
    system: str,
    user: str,
    chat_fn: Callable[[str, str], tuple[bool, str]],
    task_id: str = "",
    repo_root: str = "",
    source: str = "hub",
) -> dict[str, Any]:
    """Shadow/enforce wrapper around a chat completion callable."""
    prep = prepare_packet(task_id=task_id, repo_root=repo_root, query_text=user)
    val = prep["validation"]
    decision = gate_decision(val)
    row = {
        "at": _now(),
        "source": source,
        "task_id": task_id,
        "readiness_score": val.get("readiness_score"),
        "gate_eligible": val.get("gate_eligible"),
        "missing_for_gate": val.get("missing_for_gate"),
        "mode": decision.get("mode"),
        "allowed": decision.get("allowed"),
        "reason": decision.get("reason"),
    }
    if decision.get("mode") == "shadow":
        _append_log(SHADOW_LOG, row)
    if decision.get("mode") == "enforce" and not decision.get("allowed"):
        _append_log(ENFORCE_LOG, row)
    _write_gate_ssot(row=row, validation=val)

    if not decision.get("allowed"):
        return {
            "ok": False,
            "blocked": True,
            "gate": decision,
            "validation": val,
            "message": "Model call blocked — packet not gate-eligible",
        }

    ok, raw = chat_fn(system, user)
    return {
        "ok": ok,
        "blocked": False,
        "gate": decision,
        "validation": val,
        "response": raw,
    }
