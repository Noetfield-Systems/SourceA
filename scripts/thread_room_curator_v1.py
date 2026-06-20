#!/usr/bin/env python3
"""Thread Room L3 Curator — MERGE/SPLIT/DEFER plan · Form §THREAD row drafts.

TRACE: SINA_THREAD_ROOM_DRAFT_v1.md L3
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from thread_room_shared_v1 import THREAD_DIR  # noqa: E402

PENDING_FORM = THREAD_DIR / "pending-thread-form-rows.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_form_open_count() -> int:
    import subprocess

    raw = subprocess.check_output(
        [sys.executable, str(ROOT / "scripts/live_founder_decision_form_v1.py"), "--json"],
        text=True,
    )
    return int(json.loads(raw).get("open_questions_count") or 0)


def curate(thread_map: dict) -> dict:
    form_rows: list[dict] = []
    actions: list[dict] = []
    founder_lines: list[str] = []

    for arc in thread_map.get("arcs") or []:
        tid = arc.get("thread_arc") or "THREAD-?"
        chats = arc.get("chats") or []
        clock = arc.get("clock") or "T20"
        founder_lines.append(f"ARC {tid} ({clock}): {arc.get('founder_line')}")
        for c in chats:
            cid = c.get("chat_id", "?")
            role = c.get("role", "?")
            jv = c.get("judge_verdict", "UNJUDGED")
            founder_lines.append(f"  CHAT {cid} ({role}) · judge={jv} · map-only (Thread Room does not alarm)")
            if jv in ("ACTIVE_STALE", "BAD"):
                actions.append(
                    {
                        "action": "DEFER_TO_JUDGE",
                        "chat_id": cid,
                        "reason": f"Judge Center owns remediation — {jv}",
                    }
                )

        form_rows.append(
            {
                "id": f"§THREAD-{tid.replace('THREAD-', '')}",
                "thread_arc": tid,
                "clock": clock,
                "chat_ids": [c.get("chat_id") for c in chats],
                "pick_hint": f"§THREAD row draft — {tid} · {len(chats)} chats · T30 continuity",
                "reason": arc.get("founder_line"),
            }
        )

    for g in thread_map.get("gaps") or []:
        founder_lines.append(f"GAP: {g.get('type')} · {g.get('chat_id')}")

    case_id = f"TR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
    executive = (
        f"Thread Room batch {case_id}: {thread_map.get('arc_count', 0)} arcs · "
        f"{thread_map.get('gap_count', 0)} gaps · {len(form_rows)} §THREAD drafts. "
        f"Map only — RIGHT/STALE/BAD is Judge Center. Form open_count={_load_form_open_count()}."
    )

    result = {
        "schema": "thread-room-curator-v1",
        "case_id": case_id,
        "curated_at": _now(),
        "map_ref": thread_map.get("mapped_at"),
        "executive_summary": executive,
        "founder_continuity": founder_lines,
        "curator_actions": actions,
        "form_row_drafts": form_rows,
        "founder_pick_required": ["Q-THREAD-ROOM-v1 A"],
    }
    THREAD_DIR.mkdir(parents=True, exist_ok=True)
    (THREAD_DIR / "latest-curation-v1.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (THREAD_DIR / f"curation/{case_id}.json").parent.mkdir(parents=True, exist_ok=True)
    (THREAD_DIR / f"curation/{case_id}.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Thread Room L3 curator")
    ap.add_argument("--map", help="Cartographer JSON path")
    ap.add_argument("--latest", action="store_true")
    ap.add_argument("--write-form", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.latest:
        path = THREAD_DIR / "latest-map-v1.json"
    elif args.map:
        path = Path(args.map)
    else:
        print("FAIL: --map or --latest", file=sys.stderr)
        return 1
    thread_map = json.loads(path.read_text(encoding="utf-8"))
    result = curate(thread_map)
    if args.write_form and result.get("form_row_drafts"):
        with PENDING_FORM.open("a", encoding="utf-8") as fh:
            for row in result["form_row_drafts"]:
                fh.write(json.dumps({"case_id": result["case_id"], **row}, ensure_ascii=False) + "\n")
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(result["executive_summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
