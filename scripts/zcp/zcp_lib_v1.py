#!/usr/bin/env python3
"""ZCP lib v1 — parser · prompt builder · validator · router (Python mirror of @forge/zcp)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

ZCP_SCHEMA = "zcp-message-v1"
ZCP_VERSION = "1.0.0"
ZCPType = Literal["TASK", "FIX", "CRITIC"]
TaskComplexity = Literal["low", "medium", "high"]

TASK_ACTIONS = frozenset({"patch", "analyze", "generate", "repair"})
LINE_RANGE = re.compile(r"^[0-9]+(-[0-9]+)?$")

SYSTEM_HEADER = (
    "You are operating under ZCP (Zero-Context Protocol).\n"
    "RULES:\n"
    "- no explanations\n"
    "- no reasoning text\n"
    "- output JSON only\n"
    "- minimal file edits only\n"
    "- no architectural expansion\n"
    "- no chat history\n"
    "- at most one file_ref per execution"
)

STATION_BY_ACTION = {
    "patch": "claude_code",
    "repair": "claude_code",
    "generate": "openrouter_bulk",
    "analyze": "gemini_context",
}

STATION_BY_COMPLEXITY = {
    "low": "openrouter_bulk",
    "medium": "gemini_context",
    "high": "claude_code",
}


@dataclass
class ZCPRunResult:
    status: str
    mode: ZCPType
    prompt: str
    envelope: dict[str, Any]
    route: str
    validation_errors: list[str] = field(default_factory=list)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _try_json(raw: str) -> Any | None:
    text = raw.strip()
    if not text.startswith("{"):
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _envelope(zcp_type: ZCPType, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": ZCP_SCHEMA,
        "version": ZCP_VERSION,
        "saved_at": _now(),
        "type": zcp_type,
        "payload": payload,
    }


def _parse_kv(body: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in body.split("\n"):
        m = re.match(r"^\s*([a-z_]+)\s*:\s*(.+)$", line, re.I)
        if m:
            out[m.group(1).lower()] = m.group(2).strip()
    return out


def _parse_fix_body(body: str) -> dict[str, Any]:
    kv = _parse_kv(body)
    target = kv.get("target") or kv.get("file_ref") or ""
    issue = kv.get("issue") or next((l.strip() for l in body.split("\n") if l.strip() and ":" not in l), "")
    row: dict[str, Any] = {"target": target, "issue": issue}
    if kv.get("snippet"):
        row["snippet"] = kv["snippet"]
    return row


def _parse_critic_body(body: str) -> dict[str, Any]:
    checkpoints: list[str] = []
    subject = ""
    in_cp = False
    for line in body.split("\n"):
        if re.match(r"^CHECKPOINTS:", line.strip(), re.I):
            in_cp = True
            continue
        bullet = re.match(r"^\s*-\s+(.+)$", line)
        if bullet:
            checkpoints.append(bullet.group(1).strip())
        elif in_cp and line.strip():
            checkpoints.append(line.strip())
        elif line.strip() and not subject and not re.match(r"^CHECKPOINTS:", line, re.I):
            subject = line.strip()
    kv = _parse_kv(body)
    return {
        "subject": kv.get("subject") or subject or "review implementation",
        "checkpoints": checkpoints or [subject or "review implementation"],
        "file_ref": kv.get("file_ref"),
    }


def _parse_task_body(body: str) -> dict[str, Any]:
    parsed = _try_json(body)
    if isinstance(parsed, dict) and parsed.get("task_id") and parsed.get("action") and parsed.get("goal"):
        return parsed
    kv = _parse_kv(body)
    return {
        "task_id": kv.get("task_id") or f"zcp-{int(datetime.now(timezone.utc).timestamp())}",
        "action": kv.get("action") or "patch",
        "file_ref": kv.get("file_ref") or kv.get("target"),
        "goal": kv.get("goal") or body.strip()[:280],
        "input": kv.get("input"),
        "range": kv.get("range"),
    }


def parse_zcp(input_text: str) -> tuple[ZCPType, dict[str, Any]]:
    raw = input_text.strip()
    upper = raw.upper()
    parsed = _try_json(raw)
    if isinstance(parsed, dict) and parsed.get("schema") == ZCP_SCHEMA and parsed.get("type"):
        zcp_type = str(parsed["type"]).upper()
        if zcp_type in ("TASK", "FIX", "CRITIC"):
            return zcp_type, parsed  # type: ignore[return-value]
    if isinstance(parsed, dict):
        if parsed.get("target") and parsed.get("issue"):
            return "FIX", _envelope("FIX", parsed)
        if parsed.get("subject") and parsed.get("checkpoints"):
            return "CRITIC", _envelope("CRITIC", parsed)
        if parsed.get("task_id") and parsed.get("action") and parsed.get("goal"):
            return "TASK", _envelope("TASK", parsed)
    if upper.startswith("FIX:"):
        body = raw.split(":", 1)[1].strip()
        return "FIX", _envelope("FIX", _parse_fix_body(body))
    if upper.startswith("CRITIC:"):
        body = raw.split(":", 1)[1].strip()
        return "CRITIC", _envelope("CRITIC", _parse_critic_body(body))
    return "TASK", _envelope("TASK", _parse_task_body(raw))


def validate_envelope(envelope: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if envelope.get("schema") != ZCP_SCHEMA:
        errors.append("schema must be zcp-message-v1")
    zcp_type = envelope.get("type")
    payload = envelope.get("payload") or {}
    if not isinstance(payload, dict):
        return errors + ["payload must be object"]
    if zcp_type == "TASK":
        if not str(payload.get("task_id") or "").strip():
            errors.append("task_id required")
        if str(payload.get("action") or "") not in TASK_ACTIONS:
            errors.append(f"invalid action: {payload.get('action')}")
        if not str(payload.get("goal") or "").strip():
            errors.append("goal required")
    elif zcp_type == "FIX":
        if not str(payload.get("target") or "").strip():
            errors.append("target required")
        if not str(payload.get("issue") or "").strip():
            errors.append("issue required")
    elif zcp_type == "CRITIC":
        if not str(payload.get("subject") or "").strip():
            errors.append("subject required")
        if not payload.get("checkpoints"):
            errors.append("checkpoints required")
    return errors


def route_station(envelope: dict[str, Any], complexity: TaskComplexity = "medium") -> str:
    zcp_type = envelope.get("type")
    if zcp_type == "CRITIC":
        return "gpt_control"
    if zcp_type == "FIX":
        return "claude_code"
    payload = envelope.get("payload") or {}
    if payload.get("station"):
        return str(payload["station"])
    action = str(payload.get("action") or "patch")
    return STATION_BY_ACTION.get(action) or STATION_BY_COMPLEXITY.get(complexity, "gemini_context")


def build_prompt(envelope: dict[str, Any]) -> str:
    zcp_type = envelope.get("type")
    payload_text = json.dumps(envelope.get("payload") or {}, indent=2)
    if zcp_type == "TASK":
        return "\n".join(
            [
                "SYSTEM MODE: ZCP EXECUTION",
                SYSTEM_HEADER,
                "OUTPUT FORMAT:",
                '{"status":"ok|fail","result":"string","confidence":0.0,"files_changed":[]}',
                "TASK:",
                payload_text,
            ]
        )
    if zcp_type == "FIX":
        return "\n".join(
            [
                "ZCP_MODE: FIX",
                "OUTPUT: PATCH ONLY — JSON with status + patch",
                "NO TEXT OUTSIDE JSON",
                "TASK:",
                payload_text,
            ]
        )
    return "\n".join(
        [
            "ZCP_MODE: CRITIC",
            "OUTPUT: JSON SCORE ONLY — gate not designer",
            "NO PATCHES · NO PLANS",
            "TASK:",
            payload_text,
        ]
    )


def run_executor(input_text: str, complexity: TaskComplexity = "medium") -> ZCPRunResult:
    mode, envelope = parse_zcp(input_text)
    if envelope.get("schema") != ZCP_SCHEMA:
        envelope = envelope if envelope.get("type") else _envelope(mode, envelope.get("payload", envelope))
    errors = validate_envelope(envelope)
    route = route_station(envelope, complexity)
    prompt = build_prompt(envelope)
    return ZCPRunResult(
        status="ok" if not errors else "fail",
        mode=mode,
        prompt=prompt,
        envelope=envelope,
        route=route,
        validation_errors=errors,
    )


def task_id_from_envelope(envelope: dict[str, Any]) -> str:
    payload = envelope.get("payload") or {}
    if isinstance(payload, dict) and payload.get("task_id"):
        return str(payload["task_id"])
    zcp_type = str(envelope.get("type") or "task").lower()
    return f"zcp-{zcp_type}-{int(datetime.now(timezone.utc).timestamp())}"


def critic_validate(output: dict[str, Any]) -> dict[str, Any]:
    risks = output.get("risk") or []
    drift = int(output.get("drift_score") or 0)
    return {
        "valid": len(risks) == 0,
        "score": 10 if not risks else max(0, 10 - drift),
        "issues": list(risks),
        "gate_pass": drift <= 6 and len(risks) == 0,
    }
