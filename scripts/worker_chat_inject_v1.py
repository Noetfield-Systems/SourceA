#!/usr/bin/env python3
"""Inject into SourceA Worker chat via agent --resume — never clipboard/Brain hijack.

Law: brain-os/laws/WORKER_CHAT_INJECT_LOCKED_v1.md
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
INBOX_MD = ROOT / ".sina-loop" / "INBOX.md"
LOG = Path.home() / ".sina" / "worker-chat-inject-v1.jsonl"
DEFAULT_POP_SLEEP_SEC = 2.0


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _agent_bin() -> str:
    return shutil.which("agent") or "agent"


def _log(row: dict) -> None:
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({**row, "at": _now()}) + "\n")
    except OSError:
        pass


def _chat_id() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from worker_chat_session_v1 import ensure_worker_chat_id  # noqa: WPS433

    return ensure_worker_chat_id(create_if_missing=True)


def pop_worker_editor_window(*, caller: str = "worker_chat_inject", sleep_sec: float = DEFAULT_POP_SLEEP_SEC) -> dict:
    """Foreground Worker UI before inject: Cursor app + INBOX editor + agent --resume chat."""
    sys.path.insert(0, str(SCRIPTS))
    from cursor_window_preflight_v1 import cursor_focus_steal_disabled  # noqa: WPS433

    if cursor_focus_steal_disabled():
        row = _chat_id()
        cid = row.get("conversation_id") if row.get("ok") else None
        out = {
            "ok": True,
            "skipped": True,
            "focus_steal_skipped": True,
            "reason": "cursor_focus_steal_disabled",
            "caller": caller,
            "method": "pop_worker_editor_window",
            "conversation_id": cid,
        }
        _log(out)
        return out
    row = _chat_id()
    if not row.get("ok"):
        return {"ok": False, "step": "worker_chat_id", "error": row.get("error"), "caller": caller}
    chat_id = row["conversation_id"]
    try:
        # 1) Foreground Cursor (not -g — must pop window in front of Brain/Cowork)
        subprocess.run(["open", "-a", "Cursor"], capture_output=True, timeout=15, check=False)
        time.sleep(0.4)
        # 2) Open Worker INBOX editor tab in foreground (visible anchor for Worker lane)
        if INBOX_MD.is_file():
            subprocess.run(
                ["open", "-a", "Cursor", str(INBOX_MD.resolve())],
                capture_output=True,
                timeout=15,
                check=False,
            )
            time.sleep(0.4)
        # 3) Resume dedicated Worker chat session (not last-active Brain tab)
        subprocess.Popen(
            [_agent_bin(), "--resume", str(chat_id)],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        # 4) AppleScript activate — ensure Cursor window stack is on top
        subprocess.run(
            ["osascript", "-e", 'tell application "Cursor" to activate'],
            capture_output=True,
            timeout=10,
            check=False,
        )
        delay = max(1.0, min(float(sleep_sec), 5.0))
        time.sleep(delay)
        out = {
            "ok": True,
            "method": "pop_worker_editor_window",
            "conversation_id": chat_id,
            "inbox_editor": str(INBOX_MD) if INBOX_MD.is_file() else None,
            "caller": caller,
            "sleep_sec": delay,
        }
        _log(out)
        return out
    except Exception as exc:
        err = {"ok": False, "error": str(exc), "caller": caller, "conversation_id": chat_id}
        _log(err)
        return err


def focus_worker_chat(*, caller: str = "worker_chat_inject", sleep_sec: float = DEFAULT_POP_SLEEP_SEC) -> dict:
    """Alias — always pop Worker editor window before inject/execute."""
    return pop_worker_editor_window(caller=caller, sleep_sec=sleep_sec)


def inject_into_worker_chat(
    text: str,
    *,
    caller: str = "worker_chat_inject",
    execute: bool = False,
    timeout_sec: int = 1800,
) -> dict:
    """Target Worker chat by ID. execute=True runs agent -p -f in that session only."""
    focus = focus_worker_chat(caller=caller)
    if not focus.get("ok"):
        return focus

    chat_id = focus["conversation_id"]
    body = (text or "").strip()
    if not body:
        return {**focus, "injected": False, "reason": "empty_body"}

    if not execute:
        return {
            **focus,
            "injected": True,
            "execute": False,
            "message": "Worker chat focused — prompt logged; run_turn executes via agent --resume",
            "chars": len(body),
        }

    cmd = [_agent_bin(), "-p", "-f", "--resume", str(chat_id), "--output-format", "text", body]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        out = {
            "ok": proc.returncode == 0,
            "injected": True,
            "execute": True,
            "method": "agent_resume_execute",
            "conversation_id": chat_id,
            "caller": caller,
            "exit_code": proc.returncode,
            "output_chars": len((proc.stdout or "") + (proc.stderr or "")),
        }
        _log(out)
        return out
    except Exception as exc:
        err = {"ok": False, "error": str(exc), "caller": caller, "conversation_id": chat_id}
        _log(err)
        return err


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Worker chat inject via agent --resume")
    p.add_argument("--focus", action="store_true")
    p.add_argument("--inject", metavar="TEXT")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--caller", default="cli")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.focus:
        row = focus_worker_chat(caller=args.caller)
    elif args.inject is not None:
        row = inject_into_worker_chat(args.inject, caller=args.caller, execute=args.execute)
    else:
        row = _chat_id()
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
