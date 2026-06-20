#!/usr/bin/env python3
"""Detect Worker/healthy-drain prompts misdelivered to Brain chat — refuse execution.

Law: SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKER_SIGNALS = (
    "[GOAL1_HEALTHY_DRAIN",
    "WORKER_ROUND_REPORT",
    "HEALTHY DRAIN — queue",
    "AUTOLOOP ACTIVE (Goal 1 REGISTRY drain",
    "THIS TURN — CHECK ONLY",
    "THIS TURN — ACT ONLY",
    "VERIFY + CLOSEOUT — `sa-",
    "cursor_entry_gate.py --role worker",
    "WORKER INBOX PENDING",
    "SourceA Worker — execute fully",
    "REGISTRY bind: sa-",
)

BRAIN_OK_SIGNALS = (
    "status: BRAIN_ACK",
    "INPUT CLASS: EXTERNAL_CRITIC",
    "[SINA_LOOP",
    "you are brain",
    "routing only",
)


def is_worker_prompt(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    if any(s.lower() in t.lower() for s in BRAIN_OK_SIGNALS):
        return False
    hits = sum(1 for s in WORKER_SIGNALS if s in t)
    if "[GOAL1_HEALTHY_DRAIN" in t:
        return True
    if hits >= 2:
        return True
    if re.search(r"HEALTHY DRAIN — queue \d+/\d+", t) and "role=" in t:
        return True
    return False


def refuse_payload(*, preview: str = "") -> dict:
    return {
        "ok": True,
        "lane": "brain",
        "worker_misdelivery": True,
        "action": "REFUSE_EXECUTE",
        "reply_status": "BRAIN_REFUSE_WORKER_PROMPT",
        "message": (
            "Worker/healthy-drain prompt detected in Brain chat — Brain does NOT execute. "
            "Open SourceA Worker chat or read ~/.sina/worker-prompt-inbox-v1.json"
        ),
        "founder_headsup": (
            "Goal 1 loop turn is for SourceA Worker only. Stay in or switch to Worker chat. "
            "Brain will route only — never run validators or implement here."
        ),
        "inbox_json": str(Path.home() / ".sina" / "worker-prompt-inbox-v1.json"),
        "inbox_md": str(Path.home() / "Desktop" / "SourceA" / ".sina-loop" / "INBOX.md"),
        "preview": (preview or "")[:200],
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def check_text(text: str) -> dict:
    if is_worker_prompt(text):
        return refuse_payload(preview=text[:200])
    return {"ok": True, "lane": "brain", "worker_misdelivery": False, "action": "PROCEED"}


def write_loop_headsup(*, queue_pos: int, queue_total: int, role: str, sa_id: str) -> dict:
    """Executor calls before autoloop inject — ASF sees heads-up in hub state file."""
    path = Path.home() / ".sina" / "worker-loop-headsup-v1.json"
    payload = {
        "active": True,
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "message": (
            f"GOAL1 loop {queue_pos}/{queue_total} · {role} · {sa_id} — "
            "switch to SourceA Worker chat now. Brain will not execute this turn."
        ),
        "queue_pos": queue_pos,
        "queue_total": queue_total,
        "queue_role": role,
        "sa_id": sa_id,
        "founder_action": "Open SourceA Worker chat → say run inbox or read INBOX.md",
        "brain_action": "REFUSE if prompt appears in Brain chat",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Brain lane guard — refuse Worker prompts in Brain")
    p.add_argument("--stdin", action="store_true")
    p.add_argument("--text", default="")
    p.add_argument("--headsup", action="store_true")
    p.add_argument("--pos", type=int, default=1)
    p.add_argument("--total", type=int, default=30)
    p.add_argument("--role", default="check")
    p.add_argument("--sa", default="")
    args = p.parse_args()

    if args.headsup:
        print(json.dumps(write_loop_headsup(
            queue_pos=args.pos, queue_total=args.total, role=args.role, sa_id=args.sa
        ), indent=2))
        return 0

    text = sys.stdin.read() if args.stdin else args.text
    print(json.dumps(check_text(text), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
