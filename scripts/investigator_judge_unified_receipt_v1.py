#!/usr/bin/env python3
"""Unified investigator + judge loop receipt for nerve routing."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
OUT = SINA / "investigator-judge-unified-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def build_unified_receipt(*, write: bool = True) -> dict:
    inv = _read(SINA / "investigator-circle-run-receipt-v1.json")
    judge = _read(SINA / "judge-loop-room-receipt-v1.json")
    inv_line = str(inv.get("investigator_line") or inv.get("founder_line") or "")
    judge_line = str(judge.get("judge_loop_line") or judge.get("founder_line") or "")
    ok = bool(inv.get("ok", True)) and bool(judge.get("ok", True))
    row = {
        "schema": "investigator-judge-unified-receipt-v1",
        "at": _now(),
        "ok": ok,
        "investigator": {"ok": inv.get("ok"), "at": inv.get("at"), "line": inv_line[:120]},
        "judge_loop": {"ok": judge.get("ok"), "at": judge.get("at"), "line": judge_line[:120]},
        "unified_line": f"investigator-judge · inv={'PASS' if inv.get('ok') else 'REVIEW'} · judge={'PASS' if judge.get('ok') else 'REVIEW'}",
        "law": "SOURCEA_INVESTIGATOR_JUDGE_LOOP_ROOM_LOCKED_v1.md",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Investigator + judge unified receipt")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = build_unified_receipt(write=True)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("unified_line"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
