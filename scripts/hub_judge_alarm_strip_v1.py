#!/usr/bin/env python3
"""Hub Judge Alarm strip P0–P3 — disk JSON from Judge Center + Form Office."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

JUDGE_DIR = Path.home() / ".sina/judge-center"
OUT_PATH = JUDGE_DIR / "latest-alarm-strip-v1.json"
SCHEMA = "hub-judge-alarm-strip-v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def build_strip(*, refresh_judge: bool = False) -> dict:
    if refresh_judge:
        import subprocess
        import sys

        root = Path(__file__).resolve().parents[1]
        chats = "58148ac9,6245d9dd,e54ddfa8,74f5ccab,3369d11c,a53f3fa1"
        subprocess.run(
            [sys.executable, str(root / "scripts/judge_center_run_v1.py"), "--chats", chats, "--json"],
            check=False,
            capture_output=True,
        )

    resolution = _read_json(JUDGE_DIR / "latest-resolution-v1.json")
    ts = (resolution.get("summary") or {}).get("temporal_summary") or {}
    active = list(ts.get("active_stale") or [])
    bad = list(ts.get("bad") or [])
    past = list(ts.get("past_stale_only") or [])
    trusted = list(ts.get("trusted") or []) + list((resolution.get("summary") or {}).get("right") or [])

    form: dict = {}
    try:
        import sys

        root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root / "scripts"))
        from live_founder_decision_form_v1 import payload as form_payload  # noqa: WPS433

        form = form_payload()
    except Exception:
        form = {}

    open_count = int(form.get("open_questions_count") or 0)
    picks_required = list(resolution.get("founder_pick_required") or [])

    p0_items: list[dict] = []
    for cid in active:
        p0_items.append({"id": cid, "tag": "ACTIVE_STALE", "label": f"Chat {cid[:8]} — wrong today"})
    for cid in bad:
        p0_items.append({"id": cid, "tag": "BAD", "label": f"Chat {cid[:8]} — BAD conduct"})

    p1_items: list[dict] = []
    if open_count > 0:
        p1_items.append(
            {
                "id": "FORM_OPEN",
                "tag": "NEEDS_PICK",
                "label": f"M1 Canvas — {open_count} open PICK(s)",
                "count": open_count,
            }
        )
    for pid in picks_required[:6]:
        p1_items.append({"id": pid, "tag": "JUDGE_PICK", "label": f"Judge draft: {pid}"})

    p2_items = [
        {"id": cid, "tag": "PAST_STALE_ONLY", "label": f"Chat {cid[:8]} — archaeology only · trust recent"}
        for cid in past
    ]

    p3_items: list[dict] = []
    if not p0_items and not p1_items:
        p3_items.append(
            {
                "id": "ALL_CLEAR",
                "tag": "OK",
                "label": resolution.get("executive_resolution") or "No active stale · trust recent windows",
            }
        )
    for cid in trusted:
        p3_items.append({"id": cid, "tag": "TRUSTED", "label": f"Chat {cid[:8]} — trusted"})

    levels = [
        {
            "level": "P0",
            "severity": "critical",
            "title": "Active wrong today",
            "count": len(p0_items),
            "items": p0_items,
            "tone": "red" if p0_items else "muted",
        },
        {
            "level": "P1",
            "severity": "founder_action",
            "title": "Form PICK / judge drafts",
            "count": len(p1_items),
            "items": p1_items,
            "tone": "amber" if p1_items else "muted",
        },
        {
            "level": "P2",
            "severity": "archaeology",
            "title": "Past stale only — trust recent",
            "count": len(p2_items),
            "items": p2_items[:8],
            "tone": "blue" if p2_items else "muted",
        },
        {
            "level": "P3",
            "severity": "info",
            "title": "Clear / trusted",
            "count": len(p3_items),
            "items": p3_items[:4],
            "tone": "green",
        },
    ]

    headline = "ALL CLEAR"
    tone = "green"
    if p0_items:
        headline = f"P0 — {len(p0_items)} active alarm(s)"
        tone = "red"
    elif p1_items:
        headline = f"P1 — {open_count} form fork(s) open"
        tone = "amber"
    elif p2_items:
        headline = f"P2 — {len(p2_items)} past-stale · recent clean"
        tone = "blue"

    row = {
        "ok": True,
        "schema": SCHEMA,
        "built_at": _now(),
        "headline": headline,
        "tone": tone,
        "case_id": resolution.get("case_id"),
        "executive_resolution": resolution.get("executive_resolution"),
        "levels": levels,
        "summary": {
            "active_stale": len(active),
            "bad": len(bad),
            "past_stale_only": len(past),
            "trusted": len(trusted),
            "form_open": open_count,
        },
        "sources": {
            "resolution": str(JUDGE_DIR / "latest-resolution-v1.json"),
            "form": str(Path.home() / ".sina/live-founder-decision-form-v1.json"),
        },
        "law": "CROSS_CHAT_TRUTH_ALARM_FORM_OFFICIAL_2026-06-12_LOCKED_v1.md",
    }
    return row


def write_strip(**kwargs) -> dict:
    row = build_strip(**kwargs)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    row["path"] = str(OUT_PATH)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Build hub judge alarm strip P0–P3")
    ap.add_argument("--refresh-judge", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = write_strip(refresh_judge=args.refresh_judge)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK: hub_judge_alarm_strip_v1 · {row['headline']} · {row.get('path')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
