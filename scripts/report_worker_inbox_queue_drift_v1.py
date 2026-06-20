#!/usr/bin/env python3
"""Report drift: worker-prompt-inbox meta vs healthy-queue-state (w1-26).

TRACE: AUTO-TRACE-WORKER-INBOX-DRIFT-v1.0 · agent Auto
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

INBOX = Path.home() / ".sina" / "worker-prompt-inbox-v1.json"
QUEUE_STATE = Path.home() / ".sina" / "healthy-queue-state-v1.json"
QUEUE_HOME = Path.home() / ".sina" / "healthy-queue-30-active.json"


def main() -> int:
    from worker_inject_lib import inbox_status, parse_prompt_bind_sa  # noqa: WPS433

    inbox = inbox_status()
    meta = inbox.get("meta") or {}
    prompt_text = inbox.get("prompt") or inbox.get("preview") or ""
    if not prompt_text and INBOX.is_file():
        try:
            prompt_text = json.loads(INBOX.read_text(encoding="utf-8")).get("prompt") or ""
        except (OSError, json.JSONDecodeError):
            prompt_text = ""
    prompt_sa = parse_prompt_bind_sa(prompt_text)
    meta_sa = str(meta.get("sa_id") or "")

    qpos = qrole = None
    head_sa = ""
    if QUEUE_STATE.is_file():
        try:
            st = json.loads(QUEUE_STATE.read_text(encoding="utf-8"))
            qpos = st.get("next_pos")
        except (OSError, json.JSONDecodeError):
            pass
    if qpos and QUEUE_HOME.is_file():
        try:
            qdoc = json.loads(QUEUE_HOME.read_text(encoding="utf-8"))
            items = qdoc.get("queue") or []
            idx = int(qpos) - 1
            if 0 <= idx < len(items):
                head_sa = str(items[idx].get("sa_id") or "")
                qrole = items[idx].get("queue_role")
        except (OSError, json.JSONDecodeError, ValueError):
            pass

    drift = []
    if prompt_sa and meta_sa and prompt_sa != meta_sa:
        drift.append(f"meta_sa={meta_sa} != prompt_bind={prompt_sa}")
    if meta.get("queue_pos") and qpos and int(meta["queue_pos"]) != int(qpos):
        drift.append(f"meta_queue_pos={meta.get('queue_pos')} != state_next_pos={qpos}")
    if head_sa and meta_sa and head_sa != meta_sa:
        drift.append(f"meta_sa={meta_sa} != queue_head={head_sa} at pos={qpos}")
    if head_sa and prompt_sa and head_sa != prompt_sa:
        drift.append(f"prompt_bind={prompt_sa} != queue_head={head_sa}")

    row = {
        "ok": True,
        "schema": "worker-inbox-queue-drift-v1",
        "inbox_pending": inbox.get("pending"),
        "meta_sa": meta_sa,
        "prompt_bind_sa": prompt_sa,
        "queue_pos_meta": meta.get("queue_pos"),
        "queue_state_next_pos": qpos,
        "queue_head_sa": head_sa,
        "queue_head_role": qrole,
        "drift": drift,
        "aligned": not drift,
    }
    print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
