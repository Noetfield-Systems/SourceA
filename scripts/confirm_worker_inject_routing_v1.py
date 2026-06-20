#!/usr/bin/env python3
"""Verify next Worker inject targets ~/.sina/worker-chat-marker-v1.json — not Brain."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
MARKER = Path.home() / ".sina" / "worker-chat-marker-v1.json"
RECEIPT = Path.home() / ".sina" / "worker-inject-routing-v1.json"


def confirm(*, pop: bool = False) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    if not MARKER.is_file():
        return {"ok": False, "error": "worker_chat_marker_missing"}
    marker = json.loads(MARKER.read_text(encoding="utf-8"))
    chat_id = marker.get("conversation_id")
    if not chat_id:
        return {"ok": False, "error": "no_conversation_id"}

    pop_row = None
    if pop:
        from worker_chat_inject_v1 import pop_worker_editor_window  # noqa: WPS433

        pop_row = pop_worker_editor_window(caller="confirm_worker_inject_routing")

    row = {
        "ok": True,
        "schema": "worker-inject-routing-v1",
        "next_inject_target": chat_id,
        "marker": str(MARKER),
        "method": "agent_resume_only",
        "brain_chat_clean": str(Path.home() / ".sina/brain-chat-routing-clean-v1.json"),
        "pop": pop_row,
        "verified_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--pop", action="store_true", help="Pop Worker editor before confirm")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = confirm(pop=args.pop)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
