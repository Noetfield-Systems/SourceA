#!/usr/bin/env python3
"""API Station live terminal — real process lines for founder task runs."""
from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

SINA = Path.home() / ".sina"
LOG_DIR = SINA / "api-station"
ACTIVE_LOG = LOG_DIR / "active-terminal.log"
ACTIVE_STATE = LOG_DIR / "active-terminal-state.json"

_lock = threading.Lock()
_ctx = threading.local()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_state(doc: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVE_STATE.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def _read_state() -> dict[str, Any]:
    if not ACTIVE_STATE.is_file():
        return {"running": False}
    try:
        return json.loads(ACTIVE_STATE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"running": False}


def active_emit(line: str) -> None:
    """Append one terminal line — safe from any thread during a session."""
    with _lock:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with ACTIVE_LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    sess = getattr(_ctx, "session", None)
    if sess is not None:
        sess.lines.append(line)


class TerminalSession:
    """Context manager for one API Station task run."""

    def __init__(self, *, app_id: str, task: str, tier: str = "light", label: str = "") -> None:
        self.app_id = app_id
        self.task = task
        self.tier = tier
        self.label = label or task
        self.lines: list[str] = []
        self.ok = False
        self.result: dict[str, Any] | None = None

    def emit(self, line: str) -> None:
        _ctx.session = self
        active_emit(line)

    def start(self) -> None:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        ACTIVE_LOG.write_text("", encoding="utf-8")
        _ctx.session = self
        _write_state(
            {
                "running": True,
                "at": _now(),
                "app_id": self.app_id,
                "task": self.task,
                "tier": self.tier,
                "label": self.label,
            }
        )
        self.emit(f"═══ API Station · {self.label} ({self.task}) · tier={self.tier} · {_now()} ═══")

    def finish(self, result: dict[str, Any]) -> dict[str, Any]:
        self.result = result
        self.ok = bool(result.get("ok", True))
        mark = "PASS" if self.ok else "FAIL"
        self.emit(f"═══ done · {mark} · {_now()} ═══")
        _ctx.session = None
        _write_state(
            {
                "running": False,
                "at": _now(),
                "app_id": self.app_id,
                "task": self.task,
                "tier": self.tier,
                "ok": self.ok,
                "terminal_lines": self.lines,
                "result": result,
            }
        )
        result["terminal_lines"] = self.lines
        result["terminal_log"] = str(ACTIVE_LOG)
        return result

    def log_error(self, exc: BaseException) -> None:
        self.emit(f"[ERROR] {type(exc).__name__}: {str(exc)[:400]}")


def format_result_lines(result: dict[str, Any]) -> list[str]:
    """Turn task result JSON into readable terminal lines."""
    lines: list[str] = []
    inner = result.get("result")
    if isinstance(inner, dict) and inner.get("result") and isinstance(inner["result"], dict):
        inner = inner["result"]
    if not isinstance(inner, dict):
        inner = result

    body = inner
    if "body" in inner and isinstance(inner["body"], dict):
        body = inner["body"]

    show = (body.get("for_founder") or {}).get("show_this")
    if show:
        lines.append(f"· {show}")

    summary = body.get("summary_line") or inner.get("summary_line")
    if summary:
        lines.append(f"· {summary}")

    steps = body.get("steps") or inner.get("steps")
    if isinstance(steps, list):
        for step in steps:
            if not isinstance(step, dict):
                continue
            name = step.get("step") or step.get("name") or step.get("id") or "step"
            ok = step.get("ok")
            mark = "PASS" if ok else "FAIL" if ok is False else "—"
            err = f" — {step.get('error')}" if step.get("error") else ""
            lines.append(f"  [{mark}] {name}{err}")

    for key in (
        "observatory_ok",
        "investigation_verdict",
        "loop_verdict",
        "tick_decision",
        "founder_routing_panel_line",
        "disclosure_line",
        "investigator_line",
        "judge_loop_line",
        "loop_specialist_line",
        "mcp_stack_line",
        "tool_pick_line",
        "anti_theater_line",
        "plans_unified_line",
        "phase0_line",
        "world_model_line",
    ):
        val = body.get(key)
        if val:
            lines.append(f"  {key}: {val}")

    if body.get("error") or inner.get("error"):
        lines.append(f"[ERROR] {body.get('error') or inner.get('error')}")

    if not lines:
        preview = json.dumps(body, indent=2)[:1200]
        lines.append("— result —")
        lines.extend(preview.splitlines()[:24])

    return lines


def terminal_tail(*, lines: int = 120) -> dict[str, Any]:
    state = _read_state()
    tail: list[str] = []
    if ACTIVE_LOG.is_file():
        try:
            tail = ACTIVE_LOG.read_text(encoding="utf-8").strip().splitlines()[-lines:]
        except OSError:
            pass
    return {
        "ok": True,
        "schema": "api-station-terminal-v1",
        "at": _now(),
        "running": bool(state.get("running")),
        "task": state.get("task"),
        "app_id": state.get("app_id"),
        "tier": state.get("tier"),
        "terminal_lines": tail,
        "line_count": len(tail),
        "log_path": str(ACTIVE_LOG),
        "finished_ok": state.get("ok") if not state.get("running") else None,
        "result": state.get("result") if not state.get("running") else None,
    }


def run_with_terminal(
    *,
    app_id: str,
    task: str,
    tier: str,
    label: str,
    runner: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    sess = TerminalSession(app_id=app_id, task=task, tier=tier, label=label)
    sess.start()
    try:
        sess.emit(f"→ execute {task}")
        raw = runner()
        if isinstance(raw, dict):
            for ln in format_result_lines(raw):
                sess.emit(ln)
        return sess.finish(raw if isinstance(raw, dict) else {"ok": True, "result": raw})
    except Exception as exc:
        sess.log_error(exc)
        return sess.finish({"ok": False, "error": str(exc)[:400], "task": task, "app_id": app_id})


def start_async_run(
    *,
    app_id: str,
    task: str,
    tier: str,
    label: str,
    runner: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    state = _read_state()
    if state.get("running"):
        return {
            "ok": True,
            "started": False,
            "running": True,
            "message": f"Already running {state.get('task')}",
            "terminal_lines": terminal_tail(lines=80).get("terminal_lines") or [],
        }

    def _job() -> None:
        run_with_terminal(app_id=app_id, task=task, tier=tier, label=label, runner=runner)

    threading.Thread(target=_job, daemon=True).start()
    return {
        "ok": True,
        "started": True,
        "running": True,
        "async": True,
        "task": task,
        "app_id": app_id,
        "tier": tier,
        "message": f"Started {task} — poll GET /api/api-station/terminal/v1",
        "terminal_lines": terminal_tail(lines=20).get("terminal_lines") or [],
    }
