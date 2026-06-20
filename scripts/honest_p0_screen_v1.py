#!/usr/bin/env python3
"""One honest P0 screen — ZONE A only (no command-data museum).

Law: SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md · INCIDENT-033
Output: ~/.sina/honest-p0-screen-v1.json + founder text block
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
OUT = SINA / "honest-p0-screen-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _run_json(script: str, *args: str, timeout: int = 25) -> dict:
    path = SCRIPTS / script
    if not path.is_file():
        return {"ok": False, "error": f"missing {script}"}
    try:
        proc = subprocess.run(
            [sys.executable, str(path), *args],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if proc.stdout.strip():
            return json.loads(proc.stdout)
        return {"ok": False, "error": (proc.stderr or "")[:200]}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _drift_flags(*, factory: dict, queue_pos: int, queue_total: int, queue_sa: str, inbox: dict) -> list[str]:
    flags: list[str] = []
    if not factory.get("queue_sa"):
        flags.append("factory-now.queue_sa empty")
    inbox_sa = (inbox.get("meta") or {}).get("sa_id") or inbox.get("sa_id") or ""
    if inbox_sa and queue_sa and inbox_sa != queue_sa:
        flags.append(f"inbox_sa {inbox_sa} != queue_sa {queue_sa}")
    if inbox_sa in ("sa-0000", "") and queue_sa and queue_sa != "sa-0000":
        flags.append(f"stale inbox head {inbox_sa or 'empty'}")
    if queue_total and (queue_pos < 1 or queue_pos > queue_total):
        flags.append(f"queue cursor {queue_pos}/{queue_total} out of range")
    if factory.get("dual_proof_ok") is False:
        flags.append("dual_proof false")
    if factory.get("kill_flag"):
        flags.append("FREEZE ON")
    if factory.get("poison_stall"):
        flags.append("poison_stall")
    return flags


def build_screen(*, sync_truth: bool = True) -> dict:
    if sync_truth:
        _run_json("run_inbox_disk_truth_v1.py", "--json")

    factory = _read(SINA / "factory-now-v1.json")
    inbox = _read(SINA / "worker-prompt-inbox-v1.json")
    truth = _read(SINA / "run-inbox-disk-truth-v1.json")
    museum = {}

    sys.path.insert(0, str(SCRIPTS))
    from healthy_queue_ssot_lib import load_healthy_queue, healthy_queue_state_path  # noqa: E402

    _, q = load_healthy_queue()
    items = q.get("queue") or []
    state = _read(healthy_queue_state_path())
    pos = int(state.get("next_pos") or 1)
    total = len(items)
    head = items[pos - 1] if items and 0 < pos <= total else {}
    queue_sa = str(head.get("sa_id") or "")
    queue_role = str(head.get("queue_role") or "check")

    form = _run_json("live_founder_decision_form_v1.py", "--json")
    brain = _run_json("brain_validate_goal1_v1.py", "--json")
    progress = (brain.get("progress_honest") or {}) if brain.get("ok") else {}

    drift = _drift_flags(
        factory=factory,
        queue_pos=pos,
        queue_total=total,
        queue_sa=queue_sa,
        inbox=inbox,
    )
    honest_ok = len(drift) == 0 and bool(queue_sa) and total > 0

    p0_action = f"RUN INBOX — {queue_sa} {queue_role.upper()}" if queue_sa else "HEAL QUEUE — empty or drifted"
    if drift:
        p0_action = f"FIX DRIFT then RUN INBOX — {queue_sa or '?'} {queue_role.upper()}"

    screen = {
        "schema": "honest-p0-screen-v1",
        "at": _now(),
        "zone": "A",
        "law": "SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md",
        "honest_ok": honest_ok,
        "drift_flags": drift,
        "p0": {
            "id": "STRATEGIC-SLICE",
            "north_star": "Factory REGISTRY drain — Valid YES only",
            "next_action": p0_action,
            "progress": f"{progress.get('valid_yes', factory.get('valid_yes', '?'))}/1000 ({progress.get('pct', '?')}%)",
            "factory_line": factory.get("line") or "",
        },
        "factory": {
            "valid_yes": factory.get("valid_yes"),
            "mode": factory.get("mode"),
            "freeze": bool(factory.get("kill_flag")),
            "dual_proof": factory.get("dual_proof_ok"),
            "broker": factory.get("broker_status"),
            "orchestrator": factory.get("orchestrator_status"),
        },
        "queue": {
            "pos": pos,
            "total": total,
            "sa_id": queue_sa,
            "role": queue_role,
            "title": (head.get("sa_title") or head.get("title") or "")[:80],
            "phase_strict": bool(q.get("phase_strict")),
        },
        "inbox": {
            "pending": bool(inbox.get("pending")),
            "sa_id": (inbox.get("meta") or {}).get("sa_id") or inbox.get("sa_id"),
            "chars": inbox.get("chars"),
        },
        "form": {
            "open_count": form.get("open_questions_count") if form.get("ok") else form.get("second_form", {}).get("open_remaining_count"),
            "clear": (form.get("open_questions_count") or 0) == 0 if form.get("ok") else None,
        },
        "zones": {
            "A_daily": "factory-now · truth bundle · worker-hub API · RUN INBOX",
            "B_heavy": "/machines/ · H2 pending · Judge weekly",
            "C_retired": "Command deleted — Hub H1 / + H2 /machines/ only",
        },
        "forbidden_ssot": "command-data monolith — retired",
    }
    return screen


def format_text(screen: dict) -> str:
    drift = screen.get("drift_flags") or []
    q = screen.get("queue") or {}
    p0 = screen.get("p0") or {}
    f = screen.get("factory") or {}
    lines = [
        "═ SOURCE A · HONEST P0 (ZONE A) ═",
        f"at: {screen.get('at')} · honest_ok: {screen.get('honest_ok')}",
        "",
        f"P0 NEXT: {p0.get('next_action')}",
        f"PROGRESS: {p0.get('progress')} · {f.get('mode')} · freeze={f.get('freeze')}",
        f"QUEUE: {q.get('pos')}/{q.get('total')} · {q.get('sa_id')} · {str(q.get('role') or '').upper()}",
    ]
    if q.get("title"):
        lines.append(f"TASK: {q.get('title')}")
    form = screen.get("form") or {}
    lines.append(f"FORM: open={form.get('open_count')} clear={form.get('clear')}")
    inbox = screen.get("inbox") or {}
    lines.append(f"INBOX: pending={inbox.get('pending')} sa={inbox.get('sa_id')}")
    if drift:
        lines.append("")
        lines.append("DRIFT (fix before trust):")
        for d in drift:
            lines.append(f"  · {d}")
    lines.append("")
    lines.append(f"MUSEUM (browse only): {screen.get('zones', {}).get('C_museum')}")
    lines.append("═ END P0 ═")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="One honest P0 screen — Zone A")
    p.add_argument("--json", action="store_true")
    p.add_argument("--no-sync", action="store_true")
    args = p.parse_args()

    screen = build_screen(sync_truth=not args.no_sync)
    SINA.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(screen, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(screen, indent=2))
    else:
        print(format_text(screen))
    return 0 if screen.get("honest_ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
