#!/usr/bin/env python3
"""Regenerate ACTIVE_NOW blocker/queue lines from factory-now SSOT (AS-08)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = ROOT / "ACTIVE_NOW.md"
RESUME_FOOTER_MARKER = "**Resume law"


def _scripts_path() -> None:
    p = str(ROOT / "scripts")
    if p not in sys.path:
        sys.path.insert(0, p)


def sync_active_now(*, dry_run: bool = False) -> dict:
    _scripts_path()
    from factory_control_v1 import load_factory_now  # noqa: WPS433

    fn = load_factory_now()
    if not ACTIVE.is_file():
        return {"ok": False, "error": "ACTIVE_NOW.md missing"}

    text = ACTIVE.read_text(encoding="utf-8")
    queue_sa = str(fn.get("queue_sa") or "?")
    mode = str(fn.get("mode") or "FREEZE")
    kill = bool(fn.get("kill_flag"))
    line = str(fn.get("line") or format_line_from(fn))
    goal1_idle = (
        int(fn.get("valid_yes") or 0) >= 1000
        and int(fn.get("backlog") or 0) == 0
        and bool(fn.get("dual_proof_ok"))
        and not str(fn.get("queue_sa") or "").strip()
    )

    queue_line = (
        f"**Current Queue:** `~/.sina/healthy-queue-30-active.json` · "
        f"factory-now queue `{queue_sa}` · **Goal 1 idle**"
        if goal1_idle
        else f"**Current Queue:** `~/.sina/healthy-queue-30-active.json` · factory-now queue `{queue_sa}`"
    )
    from factory_control_v1 import load_resume_token  # noqa: WPS433

    resume = load_resume_token()
    active = not kill and mode != "FREEZE" and bool(resume)
    if goal1_idle:
        blocker_line = (
            f"**Current Blocker:** Goal 1 complete · queue idle · AUTO-RUN FREEZE · `{line}` · "
            f"commercial P0 · ASF: resume drain or name Cycle 4 pack for next factory drain"
        )
        sprint_line = "**Current Sprint:** Goal 1 honest complete · commercial flywheel · Hub advisory"
    elif active:
        max_t = resume.get("max_turns") if resume else "?"
        blocker_line = (
            f"**Current Blocker:** ACTIVE — resume token live · drain spawn allowed · "
            f"max {max_t} turns · mode {mode} · `{line}`"
        )
        sprint_line = "**Current Sprint:** s5 commercial drain — cycle-2 P2 · OpenRouter enforce active"
    elif kill or mode == "FREEZE":
        blocker_line = (
            f"**Current Blocker:** FREEZE — kill flag ON · mode {mode} · `{line}` · "
            f"ASF: resume drain — max N — receipt required"
        )
        sprint_line = "**Current Sprint:** Paused — all engines off · no spend"
    else:
        blocker_line = (
            f"**Current Blocker:** {mode} — kill flag OFF · `{line}` · "
            f"bounded resume token required · guards only · machine gate blocks drain without receipt"
        )
        sprint_line = "**Current Sprint:** Paused — bounded resume required before drain"

    from worker_drain_lib import healthy_queue_status  # noqa: WPS433

    queue = healthy_queue_status()
    q_sa = str(queue.get("sa_id") or queue_sa)
    q_role = str(queue.get("queue_role") or "?").lower()
    q_pos = queue.get("queue_pos")
    q_total = queue.get("queue_total")
    if goal1_idle:
        sa_id_line = "**Current sa_id:** `idle` · Goal 1 complete"
    elif q_sa and q_sa not in ("?", "—", "-"):
        pos_bit = f" · pos `{q_pos}/{q_total}`" if q_pos and q_total else ""
        sa_id_line = f"**Current sa_id:** `{q_sa}` · `{q_role}`{pos_bit}"
    else:
        sa_id_line = f"**Current sa_id:** `{queue_sa}` · factory-now queue"

    out = text
    out = re.sub(r"\*\*Current Sprint:\*\*[^\n]*", sprint_line, out, count=1)
    out = re.sub(r"\*\*Current Queue:\*\*[^\n]*", queue_line, out, count=1)
    if re.search(r"\*\*Current sa_id:\*\*", out):
        out = re.sub(r"\*\*Current sa_id:\*\*[^\n]*", sa_id_line, out, count=1)
    out = re.sub(r"\*\*Current Blocker:\*\*[^\n]*", blocker_line, out, count=1)

    if RESUME_FOOTER_MARKER not in out:
        return {"ok": False, "error": "resume law footer missing — manual ASF edit required"}

    changed = out != text
    if changed and not dry_run:
        ACTIVE.write_text(out, encoding="utf-8")

    return {
        "ok": True,
        "changed": changed,
        "queue_sa": queue_sa,
        "mode": mode,
        "kill_flag": kill,
        "resume_active": active,
        "blocker_line": blocker_line,
        "sprint_line": sprint_line,
        "current_sa_id": q_sa if not goal1_idle else "",
        "sa_id_line": sa_id_line,
    }


def format_line_from(fn: dict) -> str:
    return (
        f"factory-now · Valid YES {fn.get('valid_yes', '?')} · "
        f"brain {fn.get('brain_vy', '?')} · "
        f"dual_proof {fn.get('dual_proof_ok', '?')} · "
        f"mode {fn.get('mode', '?')} · "
        f"queue {fn.get('queue_sa', '?')}"
    )


def main() -> int:
    import argparse
    import json

    p = argparse.ArgumentParser(description="Sync ACTIVE_NOW from factory-now")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = sync_active_now(dry_run=args.dry_run)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
