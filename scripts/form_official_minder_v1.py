#!/usr/bin/env python3
"""FORM_OFFICIAL minder — rows stay until founder fills · cap 100 urgent remind · else Brain builds.

Receipt: ~/.sina/form-official-minder-v1.json
Law: ASF 2026-06-19 — gather complete · no new chat forks · build focus under cap
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
RECEIPT = SINA / "form-official-minder-v1.json"
EXTRACTION = SINA / "live-founder-decision-form-extraction-v1.json"
LIVE_FORM = SINA / "live-founder-decision-form-v1.json"
FORM_CAP = 100
WARN_AT = 90


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _live_open_count() -> int:
    if LIVE_FORM.is_file():
        try:
            return int(json.loads(LIVE_FORM.read_text(encoding="utf-8")).get("open_questions_count") or 0)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
    return 0


def _load_counts() -> dict:
    gathered = 0
    fresh = 0
    if EXTRACTION.is_file():
        try:
            d = json.loads(EXTRACTION.read_text(encoding="utf-8"))
            gathered = int(d.get("total_count") or len(d.get("rows") or []))
            fresh = int(d.get("fresh_count") or 0)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
    open_count = _live_open_count()
    if open_count <= 0 and fresh <= 0 and gathered > 0:
        open_count = fresh or gathered
    return {
        "open_count": open_count,
        "gathered_count": gathered,
        "fresh_count": fresh if fresh else open_count,
    }


def minder(*, write: bool = True) -> dict:
    c = _load_counts()
    open_count = c["open_count"]
    gathered = c["gathered_count"]
    fresh = c["fresh_count"]

    if open_count >= FORM_CAP:
        mode = "cap_critical"
        brain_focus = "remind_founder_fill_only"
        founder_line = (
            f"FORM FULL ({open_count}/{FORM_CAP}) open PICKs — fill M1 Canvas NOW · "
            f"Brain pauses new gathers · {gathered} on canvas"
        )
        gather_new_rows = False
    elif open_count >= WARN_AT:
        mode = "cap_warn"
        brain_focus = "build_plans_and_light_remind"
        founder_line = f"Form {open_count}/{FORM_CAP} open — fill soon · {gathered} gathered on canvas"
        gather_new_rows = False
    elif fresh > 0 or open_count > 0:
        mode = "build_focus"
        brain_focus = "build_plans_rows_stay_on_form"
        founder_line = (
            f"Form {open_count} open PICKs stay until you fill · {gathered} gathered · "
            "Brain builds — fill when ready"
        )
        gather_new_rows = open_count < FORM_CAP
    else:
        mode = "all_picked"
        brain_focus = "build_execute"
        founder_line = f"Form clear · {gathered} gathered · Brain execute"
        gather_new_rows = True

    out = {
        "ok": True,
        "schema": "form-official-minder-v1",
        "at": _now(),
        "form_cap": FORM_CAP,
        "warn_at": WARN_AT,
        "open_count": open_count,
        "gathered_count": gathered,
        "fresh_count": fresh,
        "mode": mode,
        "brain_focus": brain_focus,
        "founder_minder_line": founder_line,
        "gather_new_rows_allowed": gather_new_rows,
        "policy": {
            "rows_stay": "All gathered rows remain on FORM_OFFICIAL until founder PICK",
            "under_cap": "Brain focuses on build plans — do not re-ask in chat",
            "at_cap": "Urgent founder remind — stop new gathers",
        },
        "hub_action": "FORM_OFFICIAL (M1 Canvas)",
        "hub_url": "http://127.0.0.1:13020/form/",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        out["receipt_path"] = str(RECEIPT)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="FORM_OFFICIAL minder cap 100")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    row = minder(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["founder_minder_line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
