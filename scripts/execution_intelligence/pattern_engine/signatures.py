"""Fingerprints for commands, errors, and outputs (observe only)."""
from __future__ import annotations

import hashlib
import re


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())[:500]


def command_signature(input_command: str) -> str:
    cmd = _norm(input_command)
    if not cmd:
        return "cmd:empty"
    return f"cmd:{hashlib.sha256(cmd.encode()).hexdigest()[:12]}"


def error_fingerprint(stderr: str, exit_code: int, error_signature: str = "") -> str:
    if error_signature:
        return f"err:{_norm(error_signature)[:120]}"
    lines = [ln.strip() for ln in (stderr or "").splitlines() if ln.strip()]
    if lines:
        return f"err:{_norm(lines[-1])[:120]}"
    return f"err:exit_{exit_code}"


def output_fingerprint(stdout: str) -> str:
    text = _norm(stdout)
    if not text:
        return "out:empty"
    # Stable tail — engines often repeat headers
    tail = text[-240:] if len(text) > 240 else text
    return f"out:{hashlib.sha256(tail.encode()).hexdigest()[:12]}"


def action_key(record: dict) -> str:
    return (record.get("action_id") or record.get("producer") or "unknown").strip()


def record_fingerprint(record: dict) -> str:
    status = record.get("status") or "unknown"
    cmd = command_signature(record.get("input_command") or "")
    if status == "success":
        return f"{cmd}|{output_fingerprint(record.get('stdout') or '')}"
    return f"{cmd}|{error_fingerprint(record.get('stderr') or '', record.get('exit_code') or 1, record.get('error_signature') or '')}"
