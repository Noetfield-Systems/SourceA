#!/usr/bin/env python3
"""START Goal 1 Worker turn — runs Cursor agent CLI (loop actually executes).

Opening INBOX editor does NOT start the agent. This script does.

Hub Action only — founder never runs Terminal.
Law: GOAL_EXECUTION_ACTIVE_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INBOX_JSON = Path.home() / ".sina" / "worker-prompt-inbox-v1.json"
LOG = Path.home() / ".sina" / "goal1-worker-turn-runs.jsonl"
PROGRESS = Path.home() / ".sina" / "goal1-turn-progress-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _notify(title: str, msg: str) -> None:
    """macOS notification — must not leak osascript stderr into batch log."""
    try:
        safe = lambda s: s.replace("\\", "\\\\").replace('"', '\\"')[:200]
        script = (
            f'display notification "{safe(msg)}" with title "{safe(title)}"'
        )
        subprocess.run(
            ["osascript", "-e", script],
            check=False,
            timeout=5,
            capture_output=True,
            text=True,
        )
    except Exception:
        pass


def _load_inbox() -> dict:
    if not INBOX_JSON.is_file():
        return {"ok": False, "error": "no worker-prompt-inbox-v1.json — Hub Deliver INBOX first"}
    try:
        data = json.loads(INBOX_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": f"corrupt inbox: {exc}"}
    if not data.get("pending"):
        return {"ok": False, "error": "INBOX not pending — Hub Deliver healthy drain first"}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return {"ok": False, "error": "empty inbox prompt"}
    return {"ok": True, "data": data, "prompt": prompt}


def _agent_bin() -> str:
    from worker_chat_session_v1 import resolve_agent_bin  # noqa: WPS433

    return resolve_agent_bin()


def run_turn(
    *,
    dry_run: bool = False,
    timeout_sec: int = 300,
    auto_advance: bool = False,
    checkpoint: bool = False,
    quiet: bool = False,
) -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from active_now_v1 import heartbeat  # noqa: WPS433

    hb = heartbeat(caller="start_goal1_worker_turn")
    if not hb.get("ok"):
        return {"ok": False, "step": "active_now", **hb}

    from gatekeeper_v1 import run_gatekeeper  # noqa: WPS433

    gate = run_gatekeeper(role="act", engine="worker", caller="start_goal1_worker_turn")
    if not gate.get("safe_to_execute"):
        return {"ok": False, "step": "gatekeeper", **gate}

    loaded = _load_inbox()
    if not loaded.get("ok"):
        return loaded

    sys.path.insert(0, str(ROOT / "scripts"))
    from one_sa_per_turn_gate_v1 import guard_before_agent_turn  # noqa: WPS433

    data = loaded["data"]
    prompt = loaded["prompt"]
    from worker_inject_lib import heal_inbox_meta, write_turn_bind  # noqa: WPS433

    meta = heal_inbox_meta(data.get("meta") or {}, prompt)
    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "sa_id": meta.get("sa_id"),
            "queue_role": meta.get("queue_role"),
            "chars": len(prompt),
            "agent": _agent_bin(),
        }

    from duplicate_inject_guard_v1 import check_skip_inject  # noqa: WPS433

    skip = check_skip_inject(meta=meta, source="start_goal1_worker_turn")
    if skip.get("skip"):
        # Hub deliver + auto-run leaves INBOX pending — execute agent, do not re-inject.
        execute_ok = skip.get("reason") in (
            "INBOX_ALREADY_PENDING_SAME_TURN",
            "SA_ALREADY_IN_CURSOR_QUEUE_TURN_BIND",
        )
        if not execute_ok:
            return {
                "ok": False,
                "step": "duplicate_inject_guard",
                "blocked": True,
                "action": "SKIP_INJECT",
                "duplicate_guard": skip,
                "law": "NO_DUPLICATE_INJECT_LOCKED_v1.md",
            }

    bind = write_turn_bind(meta=meta, prompt=prompt)
    if not bind.get("ok"):
        return {"ok": False, "step": "turn_bind", **bind}
    gate = guard_before_agent_turn(expected_sa=str(meta.get("sa_id") or ""))
    if not gate.get("ok"):
        return {"ok": False, "step": "one_sa_gate", **gate}
    wrapper = f"""You are SourceA Worker — execute this INBOX turn fully in ONE run.

MANDATORY: os/chat-handoffs/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md

LAST LINES OF YOUR REPLY MUST BE EXACTLY THIS SHAPE (broker + orchestrator parse it):

```yaml
status: WORKER_ROUND_REPORT
round_type: {meta.get("queue_role") or "check"}
sa_focus: {meta.get("sa_id") or "sa-XXXX"}
validate:
  spine: PASS
  critical_bugs: 0
summary: one line
```

FORBIDDEN: `WORKER_ROUND_REPORT:` as parent key — use flat `status: WORKER_ROUND_REPORT` only.
FORBIDDEN: second sa_id · batch multiple sa · multiple WORKER_ROUND_REPORT blocks · registry_updated with more than one sa.
ONE SA ONLY THIS TURN: {meta.get("sa_id") or "sa-XXXX"} — then STOP.

--- INBOX TURN ---
{prompt}
--- END INBOX ---
"""

    sys.path.insert(0, str(ROOT / "scripts"))
    from one_sa_per_turn_gate_v1 import validate_agent_output  # noqa: WPS433

    from cursor_window_preflight_v1 import run_worker_chat_preflight  # noqa: WPS433

    preflight = run_worker_chat_preflight(caller="start_goal1_worker_turn")
    if not preflight.get("ok"):
        return {"ok": False, "step": "worker_chat_preflight", **preflight}

    if not quiet:
        _notify("Goal 1 Worker", f"Starting turn {meta.get('sa_id')} ({meta.get('queue_role')})…")

    from goal1_batch_log_v1 import log_agent_done, log_agent_start  # noqa: WPS433

    log_agent_start(
        sa_id=str(meta.get("sa_id") or "sa-XXXX"),
        queue_role=str(meta.get("queue_role") or ""),
        queue_pos=meta.get("queue_pos") or "",
        queue_total=meta.get("queue_total") or "",
    )

    try:
        from execution_event_log_v1 import append_event  # noqa: WPS433

        append_event(
            event="WORKER_STARTED",
            actor="headless_cli_worker",
            trace_id=str(meta.get("sa_id") or ""),
            data={
                "sa_id": meta.get("sa_id"),
                "queue_role": meta.get("queue_role"),
                "queue_pos": meta.get("queue_pos"),
            },
        )
    except Exception:
        pass

    PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS.write_text(
        json.dumps(
            {
                "status": "RUNNING",
                "at": _now(),
                "sa_id": meta.get("sa_id"),
                "queue_role": meta.get("queue_role"),
                "method": "cursor_agent_cli",
                "message": "Agent executing — Hub shows this after Refresh",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    chat_id = preflight.get("conversation_id")
    if not chat_id:
        from worker_chat_session_v1 import ensure_worker_chat_id  # noqa: WPS433

        chat_row = ensure_worker_chat_id(create_if_missing=True)
        chat_id = chat_row.get("conversation_id") if chat_row.get("ok") else None

    if chat_id:
        cmd = [_agent_bin(), "-p", "-f", "--resume", str(chat_id), "--output-format", "text", wrapper]
        method = "cursor_agent_cli_resume_worker_chat"
    else:
        cmd = [_agent_bin(), "-p", "-f", "--output-format", "text", wrapper]
        method = "cursor_agent_cli"
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout_sec,
        env={**dict(**__import__("os").environ)},
    )
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    row = {
        "at": _now(),
        "ok": proc.returncode == 0,
        "sa_id": meta.get("sa_id"),
        "queue_role": meta.get("queue_role"),
        "exit_code": proc.returncode,
        "output_chars": len(out),
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")

    broker_result = None
    if "WORKER_ROUND_REPORT" in out:
        sys.path.insert(0, str(ROOT / "scripts"))
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "broker", ROOT / "scripts" / "goal1_lane_broker.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        broker_result = mod.worker_submit(
            text=out,
            source="agent_cli",
            auto_advance=auto_advance,
            checkpoint=checkpoint,
        )

    broker_ok = bool((broker_result or {}).get("ok"))
    advance_ok = None
    if broker_result:
        if broker_result.get("auto_advance") or (broker_result.get("deliver") or {}).get("ok"):
            advance_ok = True
        elif broker_result.get("ok") is False:
            advance_ok = False
    report_ok = "WORKER_ROUND_REPORT" in out and broker_ok
    log_agent_done(
        exit_code=proc.returncode,
        broker_ok=broker_ok,
        advance_ok=advance_ok,
        report_ok=report_ok,
        chars=len(out),
    )

    _notify(
        "Goal 1 Worker",
        f"Turn done {meta.get('sa_id')} — check Hub / Brain broker poll",
    )

    PROGRESS.write_text(
        json.dumps(
            {
                "status": "DONE" if proc.returncode == 0 else "FAILED",
                "at": _now(),
                "sa_id": meta.get("sa_id"),
                "queue_role": meta.get("queue_role"),
                "exit_code": proc.returncode,
                "broker_ok": (broker_result or {}).get("ok"),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "ok": proc.returncode == 0,
        "started": True,
        "method": method,
        "worker_chat_id": chat_id,
        "sa_id": meta.get("sa_id"),
        "queue_role": meta.get("queue_role"),
        "exit_code": proc.returncode,
        "broker": broker_result,
        "advance_ok": advance_ok,
        "broker_ok": broker_ok,
        "output_preview": out[-2000:] if out else "",
        "message": (
            f"Worker turn in chat {chat_id} — open that Cursor tab to watch. "
            "Brain polls: python3 scripts/goal1_lane_broker.py brain-poll"
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Start Goal 1 Worker turn (agent CLI)")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--auto-advance", action="store_true", help="Broker auto-deliver next INBOX after report")
    p.add_argument("--quiet", action="store_true", help="Skip macOS notifications (loop mode)")
    args = p.parse_args()
    result = run_turn(
        dry_run=args.dry_run,
        timeout_sec=args.timeout,
        auto_advance=args.auto_advance,
        quiet=args.quiet,
    )
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
