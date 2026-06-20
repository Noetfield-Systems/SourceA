#!/usr/bin/env python3
"""Thread Room L1 Scout — extract chat anchors · candidate THREAD arcs.

TRACE: SINA_THREAD_ROOM_DRAFT_v1.md L1 · Q-THREAD-ROOM-v1
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from judge_center_patterns_v1 import CHAT_ROLES  # noqa: E402
from thread_room_shared_v1 import (  # noqa: E402
    MEGACHAT_DEFAULT,
    THREAD_ARCS,
    THREAD_DIR,
    resolve_transcript,
    transcript_stats,
)

CASES_PATH = THREAD_DIR / "threads.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def scout_chats(chat_ids: list[str]) -> dict:
    packets: list[dict] = []
    for cid in chat_ids:
        path = resolve_transcript(cid)
        role = CHAT_ROLES.get(cid[:8], "unknown")
        arc = THREAD_ARCS.get(cid[:8], "THREAD-UNMAPPED")
        if not path:
            packets.append(
                {
                    "chat_id": cid,
                    "role": role,
                    "thread_arc": arc,
                    "transcript": None,
                    "tag": "UNMAPPED",
                    "note": "transcript missing",
                }
            )
            continue
        stats = transcript_stats(path)
        tag = "MEGACHAT" if stats["bytes"] > 500_000 else "CHAT"
        packets.append(
            {
                "chat_id": cid,
                "role": role,
                "thread_arc": arc,
                "transcript": str(path),
                "tag": tag,
                "stats": stats,
                "found": [f"FOUND — {path}"],
            }
        )

    case = {
        "schema": "thread-room-scout-v1",
        "scouted_at": _now(),
        "packets": packets,
        "megachat_count": sum(1 for p in packets if p.get("tag") == "MEGACHAT"),
        "unmapped_count": sum(1 for p in packets if p.get("tag") == "UNMAPPED"),
    }
    THREAD_DIR.mkdir(parents=True, exist_ok=True)
    with CASES_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(case, ensure_ascii=False) + "\n")
    (THREAD_DIR / "latest-scout-v1.json").write_text(
        json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return case


def main() -> int:
    ap = argparse.ArgumentParser(description="Thread Room L1 scout")
    ap.add_argument("--chats", default=",".join(MEGACHAT_DEFAULT))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    ids = [c.strip() for c in args.chats.split(",") if c.strip()]
    result = scout_chats(ids)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for p in result["packets"]:
            print(f"{p['chat_id']}: {p.get('thread_arc')} ({p.get('tag')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
