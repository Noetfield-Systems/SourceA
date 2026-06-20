#!/usr/bin/env python3
"""Agent executor daily duty card — founder reminder SSOT on disk.

Law: AGENT_EXECUTOR_DAILY_DUTY_CARD_LOCKED_v1.md
Writes/reads: ~/.sina/agent-executor-daily-duty-card-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD_PATH = Path.home() / ".sina" / "agent-executor-daily-duty-card-v1.json"
LOCKED_DOC = ROOT / "AGENT_EXECUTOR_DAILY_DUTY_CARD_LOCKED_v1.md"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_card() -> dict:
    if not CARD_PATH.is_file():
        return {}
    try:
        return json.loads(CARD_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def validate_card() -> dict:
    card = load_card()
    missing: list[str] = []
    if card.get("schema") != "agent-executor-daily-duty-card-v1":
        missing.append("schema")
    items = card.get("never_make_founder_repeat") or []
    if len(items) < 20:
        missing.append(f"never_make_founder_repeat count={len(items)}")
    if not LOCKED_DOC.is_file():
        missing.append("locked_doc missing on disk")
    ids = {x.get("id") for x in items if isinstance(x, dict)}
    for i in range(1, 24):
        want = f"D{i:02d}"
        if want not in ids:
            missing.append(f"missing {want}")
    ok = not missing
    return {
        "schema": "agent-daily-duty-card-validate-v1",
        "ok": ok,
        "at": _now(),
        "card_path": str(CARD_PATH),
        "locked_doc": str(LOCKED_DOC),
        "item_count": len(items),
        "missing": missing,
    }


def inject_slice(card: dict | None = None) -> dict:
    """Compact inject block for memory mirror / session gate."""
    c = card or load_card()
    if not c:
        return {}
    items = c.get("never_make_founder_repeat") or []
    bullets = [f"{x.get('id')}: {x.get('agent_duty')}" for x in items[:23] if isinstance(x, dict)]
    founder = c.get("founder_daily_three_taps") or []
    return {
        "read_first": str(CARD_PATH),
        "locked_doc": "AGENT_EXECUTOR_DAILY_DUTY_CARD_LOCKED_v1.md",
        "standing_order": "Founder must not re-remind — obey all D01–D23 every session",
        "founder_three_taps": founder,
        "never_repeat_top10": bullets[:10],
        "check_cart": c.get("check_cart_pointer"),
        "session_start": c.get("session_start_order") or [],
        "three_pipelines": "orientation | hospital | maze ONLY on founder word — session start = session gate only",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Agent executor daily duty card")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--inject", action="store_true", help="Print inject slice JSON")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.validate:
        out = validate_card()
        if args.json:
            print(json.dumps(out, indent=2, ensure_ascii=False))
        else:
            print(f"DAILY_CARD_VALIDATE ok={out['ok']} items={out['item_count']}")
            for m in out.get("missing") or []:
                print(f"  missing: {m}")
        return 0 if out["ok"] else 1

    if args.inject:
        out = inject_slice()
        if args.json:
            print(json.dumps(out, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0 if out else 1

    card = load_card()
    if args.json:
        print(json.dumps(card, indent=2, ensure_ascii=False))
    else:
        print(f"DAILY_CARD items={len(card.get('never_make_founder_repeat') or [])} path={CARD_PATH}")
    return 0 if card else 1


if __name__ == "__main__":
    raise SystemExit(main())
