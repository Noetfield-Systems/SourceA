#!/usr/bin/env python3
"""Cursor stop hook — post Worker YAML to broker."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        print("{}")
        return 0
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("{}")
        return 0

    chunks: list[str] = []
    for key in ("text", "response", "output", "last_message"):
        v = data.get(key)
        if isinstance(v, str):
            chunks.append(v)
    for m in data.get("transcript") or data.get("messages") or []:
        if isinstance(m, dict):
            chunks.append(str(m.get("text") or m.get("content") or ""))

    text = "\n".join(chunks)
    if "WORKER_ROUND_REPORT" not in text and "WORKER_ACK" not in text:
        print("{}")
        return 0

    import subprocess

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "goal1_lane_broker.py"), "worker-submit", "--stdin"],
        input=text.encode("utf-8"),
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    followup = ""
    if "WORKER_ROUND_REPORT" in text:
        followup = (
            "Broker logged WORKER_ROUND_REPORT. "
            "Brain: python3 scripts/brain_worker_broker_v1.py --poll"
        )
    print(json.dumps({"followup_message": followup} if followup else {}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
