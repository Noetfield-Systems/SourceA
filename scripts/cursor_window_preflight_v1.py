#!/usr/bin/env python3
"""AUTO-RUN window preflight — foreground Worker chat before inject (never Brain).

Law: brain-os/laws/AUTO_RUN_WINDOW_PREFLIGHT_LOCKED_v1.md
ASF: open -a Cursor · sleep 1 · agent --resume Worker chat id · osascript activate
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

LOG = Path.home() / ".sina" / "cursor-window-preflight-v1.jsonl"
FOCUS_STEAL_DISABLED_FLAG = Path.home() / ".sina" / "cursor-focus-steal-disabled-v1.flag"
DEFAULT_SLEEP_SEC = 2.0
# ASF Worker chat — never last-active Brain tab
DEFAULT_WORKER_CHAT_ID = "e54ddfa8-531b-40de-8443-d8167f80a614"


def cursor_focus_steal_disabled() -> bool:
    """Founder research mode — skip open/activate/agent resume so Chrome stays front."""
    env = os.environ.get("SINA_CURSOR_FOCUS_STEAL", "").strip().lower()
    if env in ("0", "false", "no", "off", "disabled"):
        return True
    if env in ("1", "true", "yes", "on", "enabled"):
        return False
    return FOCUS_STEAL_DISABLED_FLAG.is_file()


def set_cursor_focus_steal_disabled(*, disabled: bool, caller: str = "cli") -> dict:
    FOCUS_STEAL_DISABLED_FLAG.parent.mkdir(parents=True, exist_ok=True)
    if disabled:
        FOCUS_STEAL_DISABLED_FLAG.write_text(
            json.dumps({"at": _now(), "caller": caller, "reason": "founder_research_mode"}, indent=2) + "\n",
            encoding="utf-8",
        )
    elif FOCUS_STEAL_DISABLED_FLAG.is_file():
        FOCUS_STEAL_DISABLED_FLAG.unlink()
    row = {
        "ok": True,
        "disabled": disabled,
        "caller": caller,
        "flag": str(FOCUS_STEAL_DISABLED_FLAG),
        "research_mode": disabled,
    }
    _append_log({**row, "at": _now(), "step": "focus_steal_toggle"})
    return row


def toggle_cursor_focus_steal_disabled(*, caller: str = "toggle") -> dict:
    return set_cursor_focus_steal_disabled(disabled=not cursor_focus_steal_disabled(), caller=caller)


def _focus_steal_skipped(caller: str, *, target: str = "unknown") -> dict:
    row = {
        "at": _now(),
        "ok": True,
        "caller": caller,
        "focus_steal_skipped": True,
        "research_mode": True,
        "step": "focus_steal_skipped",
        "target": target,
        "flag": str(FOCUS_STEAL_DISABLED_FLAG),
    }
    _append_log(row)
    return row


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _agent_bin() -> str:
    from worker_chat_session_v1 import resolve_agent_bin  # noqa: WPS433

    return resolve_agent_bin()


def _resolve_worker_chat_id() -> str:
    marker = Path.home() / ".sina" / "worker-chat-marker-v1.json"
    if marker.is_file():
        try:
            row = json.loads(marker.read_text(encoding="utf-8"))
            cid = str(row.get("conversation_id") or "").strip()
            if cid:
                return cid
        except (OSError, json.JSONDecodeError):
            pass
    return DEFAULT_WORKER_CHAT_ID


def run_worker_chat_preflight(
    *,
    caller: str = "unknown",
    sleep_sec: float = 1.0,
) -> dict:
    """Focus SourceA Worker chat — NOT Brain last-active tab."""
    if cursor_focus_steal_disabled():
        return _focus_steal_skipped(caller, target="sourcea_worker")
    chat_id = _resolve_worker_chat_id()
    root = Path(__file__).resolve().parents[1]
    try:
        proc = subprocess.run(
            ["open", "-a", "Cursor"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "open failed").strip()
            row = {
                "at": _now(),
                "ok": False,
                "caller": caller,
                "error": err,
                "step": "open_cursor",
                "conversation_id": chat_id,
            }
            _append_log(row)
            return row

        delay = max(1.0, min(float(sleep_sec), 3.0))
        time.sleep(delay)

        subprocess.Popen(
            [_agent_bin(), "--resume", str(chat_id)],
            cwd=str(root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        osa = f'''
        tell application "Cursor" to activate
        delay 0.3
        '''
        subprocess.run(
            ["osascript", "-e", osa],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        row = {
            "at": _now(),
            "ok": True,
            "caller": caller,
            "sleep_sec": delay,
            "step": "worker_chat_preflight_complete",
            "method": "open_cursor_agent_resume_osascript",
            "conversation_id": chat_id,
            "target": "sourcea_worker",
        }
        _append_log(row)
        return row
    except Exception as exc:
        row = {
            "at": _now(),
            "ok": False,
            "caller": caller,
            "error": str(exc),
            "conversation_id": chat_id,
        }
        _append_log(row)
        return row


def run_cursor_window_preflight(
    *,
    caller: str = "unknown",
    sleep_sec: float = DEFAULT_SLEEP_SEC,
    target: str = "brain",
) -> dict:
    """Activate Cursor. target=worker uses Worker chat id (ASF — never Brain hijack)."""
    if cursor_focus_steal_disabled():
        return _focus_steal_skipped(caller, target=(target or "brain"))
    if (target or "").strip().lower() in ("worker", "sourcea_worker", "goal1"):
        return run_worker_chat_preflight(caller=caller, sleep_sec=max(1.0, sleep_sec))
    try:
        proc = subprocess.run(
            ["open", "-a", "Cursor"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "open failed").strip()
            row = {
                "at": _now(),
                "ok": False,
                "caller": caller,
                "error": err,
                "step": "open_cursor",
            }
            _append_log(row)
            return row
        delay = max(0.5, min(float(sleep_sec), 3.0))
        time.sleep(delay)
        row = {
            "at": _now(),
            "ok": True,
            "caller": caller,
            "sleep_sec": delay,
            "step": "preflight_complete",
            "target": "brain",
        }
        _append_log(row)
        return row
    except Exception as exc:
        row = {"at": _now(), "ok": False, "caller": caller, "error": str(exc)}
        _append_log(row)
        return row


def _append_log(row: dict) -> None:
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        pass


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Cursor window preflight for AUTO-RUN")
    p.add_argument("--caller", default="cli")
    p.add_argument("--sleep", type=float, default=DEFAULT_SLEEP_SEC)
    p.add_argument("--worker", action="store_true", help="Focus Worker chat id (ASF default for inject)")
    p.add_argument("--status", action="store_true", help="Print research-mode / focus-steal status")
    p.add_argument("--disable-steal", action="store_true", help="Enable Chrome research mode (stop Cursor pop)")
    p.add_argument("--enable-steal", action="store_true", help="Resume auto-run Cursor foreground")
    args = p.parse_args()
    if args.status:
        print(
            json.dumps(
                {
                    "research_mode": cursor_focus_steal_disabled(),
                    "flag": str(FOCUS_STEAL_DISABLED_FLAG),
                    "flag_exists": FOCUS_STEAL_DISABLED_FLAG.is_file(),
                },
                indent=2,
            )
        )
        return 0
    if args.disable_steal:
        print(json.dumps(set_cursor_focus_steal_disabled(disabled=True, caller="cli"), indent=2))
        return 0
    if args.enable_steal:
        print(json.dumps(set_cursor_focus_steal_disabled(disabled=False, caller="cli"), indent=2))
        return 0
    if args.worker:
        row = run_worker_chat_preflight(caller=args.caller, sleep_sec=args.sleep)
    else:
        row = run_cursor_window_preflight(caller=args.caller, sleep_sec=args.sleep)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
