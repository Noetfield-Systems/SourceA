#!/usr/bin/env python3
"""RUN THE LOOP + trace: narrate gates → spawn if READY → return in <30s (no poll).

Default "run the loop": trace gates then spawn. Loop runs on disk in background.
Law: BRAIN_UNIFIED_RULES_LOCKED_v1.md §1
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "brain-run-loop-trace-v1.json"
MAX_SEC = 30


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--turns", type=int, default=10)
    p.add_argument("--phrase", default="run the loop")
    args = p.parse_args()
    sys.path.insert(0, str(SCRIPTS))
    from active_now_v1 import heartbeat  # noqa: WPS433

    hb = heartbeat(caller="brain_run_loop_trace")
    if not hb.get("ok"):
        print(json.dumps({"ok": False, "step": "active_now", **hb}, indent=2))
        return 1
    t0 = time.monotonic()

    spec = importlib.util.spec_from_file_location("bw", SCRIPTS / "brain_watch_loop_v1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    watch = mod.watch_loop(founder_phrase=args.phrase)
    timing = watch.get("timing_enforcement") or {}

    narration: list[str] = []
    for s in watch.get("steps") or []:
        narration.append(
            f"Step {s.get('n')} [{s.get('gate')}] {s.get('decision')} "
            f"({s.get('elapsed_sec')}s/{s.get('limit_sec')}s): {s.get('reason')}"
        )

    activate_step = next((s for s in watch.get("steps") or [] if s.get("gate") == "ACTIVATE"), {})
    inject_step = next((s for s in watch.get("steps") or [] if s.get("gate") == "INJECT"), {})
    act_dec = activate_step.get("decision")
    spawn_row: dict = {"attempted": False, "ok": False}

    if act_dec == "READY":
        spawn_row["attempted"] = True
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "brain_run_loop_v1.py"), "--turns", str(min(max(1, args.turns), 30))],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=20,
        )
        try:
            spawn_row = json.loads(proc.stdout) if proc.stdout.strip() else {"ok": False, "raw": proc.stderr}
        except json.JSONDecodeError:
            spawn_row = {"ok": False, "raw": (proc.stdout or proc.stderr or "")[:2000]}
        spawn_row["attempted"] = True
        narration.append(
            f"Step 10 [SPAWN] {'PASS' if spawn_row.get('ok') else 'FAIL'}: "
            f"brain_run_loop_v1.py pid={spawn_row.get('pid')} log={spawn_row.get('log_path')}"
        )
    elif act_dec == "RUNNING":
        narration.append(f"Step 10 [SPAWN] SKIP: executor already RUNNING")
        spawn_row = {"attempted": False, "skipped": "already_running", "busy_pid": activate_step.get("result", {}).get("busy_pid")}
    else:
        narration.append(f"Step 10 [SPAWN] BLOCK: activate decision={act_dec} — {activate_step.get('reason')}")

    inbox_path = SINA / "worker-prompt-inbox-v1.json"
    inbox_md = ROOT / ".sina-loop" / "INBOX.md"
    inj = inject_step.get("result") or {}
    elapsed = round(time.monotonic() - t0, 1)

    if spawn_row.get("ok"):
        final = (
            f"Loop STARTED pid={spawn_row.get('pid')} — headless agent -p -f runs Worker queue. "
            f"Worker chat empty. Watch {spawn_row.get('log_path')}. INBOX sa={inj.get('sa_id')} role={inj.get('queue_role')}."
        )
    elif act_dec == "RUNNING":
        final = f"Loop already running — no spawn. Watch ~/.sina/goal1-worker-batch-latest.log"
    elif act_dec == "READY" and spawn_row.get("attempted"):
        final = f"Spawn FAILED: {spawn_row.get('error') or spawn_row.get('message') or spawn_row}"
    else:
        final = f"Loop NOT started — gate blocked at ACTIVATE ({act_dec}). Fix: {activate_step.get('reason')}"

    out = {
        "status": "BRAIN_RUN_LOOP_TRACE",
        "at": _now(),
        "elapsed_sec": elapsed,
        "timing_enforcement": timing,
        "founder_prompt": args.phrase,
        "narration": narration,
        "final_answer": final,
        "who_runs_loop": "goal1_run_loop_v1.py → start_goal1_worker_turn_v1.py → agent -p -f (NOT Brain chat)",
        "injection": {
            "inbox_json": str(inbox_path),
            "inbox_md": str(inbox_md),
            "sa_id": inj.get("sa_id"),
            "queue_role": inj.get("queue_role"),
            "queue": inj.get("queue"),
            "pending": inj.get("pending"),
        },
        "which_chat": "Headless: no Cursor chat. Manual lane: SourceA Worker chat + run inbox.",
        "spawn": spawn_row,
        "chain": watch.get("chain"),
        "enforcement_note": "Steps 1-9 trace; step 10 spawn if READY; Brain reply ends; loop continues on disk",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print(f"status: {out['status']}")
    print(f"elapsed_sec: {elapsed}")
    print("narration:")
    for line in narration:
        print(f"  - {line}")
    print(f"who_runs_loop: {out['who_runs_loop']}")
    print(f"injection: {out['injection']}")
    print(f"which_chat: {out['which_chat']}")
    print(f"final_answer: {final}")
    return 0 if (spawn_row.get("ok") or act_dec == "RUNNING") else 1


if __name__ == "__main__":
    raise SystemExit(main())
