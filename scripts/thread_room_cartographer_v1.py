#!/usr/bin/env python3
"""Thread Room L2 Cartographer — T30/T20 map · gaps · judge cross-link.

TRACE: SINA_THREAD_ROOM_DRAFT_v1.md L2
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from thread_room_shared_v1 import THREAD_DIR  # noqa: E402

JUDGE_LATEST = Path.home() / ".sina/judge-center/latest-resolution-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _judge_verdicts() -> dict[str, str]:
    if not JUDGE_LATEST.is_file():
        return {}
    try:
        data = json.loads(JUDGE_LATEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    out: dict[str, str] = {}
    ts = (data.get("summary") or {}).get("temporal_summary") or {}
    for cid in ts.get("past_stale_only") or []:
        out[cid[:8]] = "PAST_STALE_ONLY"
    for cid in ts.get("active_stale") or []:
        out[cid[:8]] = "ACTIVE_STALE"
    for cid in ts.get("trusted") or []:
        out[cid[:8]] = "TRUSTED"
    for cid in ts.get("bad") or []:
        out[cid[:8]] = "BAD"
    return out


def cartograph(scout: dict) -> dict:
    judge = _judge_verdicts()
    arcs: dict[str, list] = {}
    gaps: list[dict] = []
    for p in scout.get("packets") or []:
        arc = p.get("thread_arc") or "THREAD-UNMAPPED"
        cid = p.get("chat_id", "")[:8]
        row = {
            "chat_id": p.get("chat_id"),
            "role": p.get("role"),
            "tag": p.get("tag"),
            "judge_verdict": judge.get(cid, "UNJUDGED"),
            "stats": p.get("stats"),
            "transcript": p.get("transcript"),
        }
        arcs.setdefault(arc, []).append(row)
        if p.get("tag") == "UNMAPPED":
            gaps.append({"type": "missing_transcript", "chat_id": p.get("chat_id")})
        if arc == "THREAD-UNMAPPED":
            gaps.append({"type": "unmapped_arc", "chat_id": p.get("chat_id")})

    continuity = []
    for arc, chats in sorted(arcs.items()):
        megachats = [c for c in chats if c.get("tag") == "MEGACHAT"]
        continuity.append(
            {
                "thread_arc": arc,
                "chat_count": len(chats),
                "megachat_count": len(megachats),
                "clock": "T30" if megachats else "T20",
                "chats": chats,
                "founder_line": (
                    f"{arc}: {len(chats)} chat(s) mapped — "
                    f"{len(megachats)} megachat(s) · nothing lost if transcript logged"
                ),
            }
        )

    result = {
        "schema": "thread-room-cartographer-v1",
        "mapped_at": _now(),
        "scout_ref": scout.get("scouted_at"),
        "judge_ref": str(JUDGE_LATEST) if JUDGE_LATEST.is_file() else None,
        "arcs": continuity,
        "gaps": gaps,
        "arc_count": len(continuity),
        "gap_count": len(gaps),
    }
    THREAD_DIR.mkdir(parents=True, exist_ok=True)
    (THREAD_DIR / "latest-map-v1.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Thread Room L2 cartographer")
    ap.add_argument("--packet", help="Scout JSON path")
    ap.add_argument("--latest", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.latest:
        path = THREAD_DIR / "latest-scout-v1.json"
    elif args.packet:
        path = Path(args.packet)
    else:
        print("FAIL: --packet or --latest", file=sys.stderr)
        return 1
    scout = json.loads(path.read_text(encoding="utf-8"))
    result = cartograph(scout)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for a in result["arcs"]:
            print(f"{a['thread_arc']}: {a['chat_count']} chats · {a['clock']}")
        print(f"gaps={result['gap_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
