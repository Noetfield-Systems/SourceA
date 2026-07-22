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
LOCKED_DOC = ROOT / "brain-os/law/enforcement/AGENT_EXECUTOR_DAILY_DUTY_CARD_LOCKED_v1.md"


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
    if len(items) < 26:
        missing.append(f"never_make_founder_repeat count={len(items)}")
    if not LOCKED_DOC.is_file():
        missing.append("locked_doc missing on disk")
    ids = {x.get("id") for x in items if isinstance(x, dict)}
    for i in range(1, 27):
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
    bullets: list[str] = []
    for x in items[:26]:
        if not isinstance(x, dict):
            continue
        duty = str(x.get("agent_duty") or "")
        if x.get("id") == "D01":
            duty = (
                "After law change: wire W1–W10 on ship window / cloud CI only — "
                "never Mac founder chat pre-reply marathon (INCIDENT-039 · INCIDENT-040)"
            )
        bullets.append(f"{x.get('id')}: {duty}")
    founder = c.get("founder_daily_three_taps") or []
    session_start: list[str] = []
    for line in c.get("session_start_order") or []:
        s = str(line)
        if "W4" in s and "W10" in s:
            session_start.append(
                "Read ~/.sina/agent-law-wire-checkcart-v1.json — ship window / cloud CI only "
                "(INCIDENT-039: not Mac pre-reply validator marathon)"
            )
        else:
            session_start.append(s)
    return {
        "read_first": str(CARD_PATH),
        "locked_doc": "brain-os/law/enforcement/AGENT_EXECUTOR_DAILY_DUTY_CARD_LOCKED_v1.md",
        "standing_order": "Founder must not re-remind — obey all D01–D26 every session",
        "founder_three_taps": founder,
        "never_repeat_top10": bullets[:10],
        "check_cart": c.get("check_cart_pointer"),
        "session_start": session_start,
        "three_pipelines": "orientation | hospital | maze ONLY on founder word — session start = session gate only",
        "incident_039_override": "Mac founder session: reply <30s · proof=Read receipts · no W1–W10 bash before chat",
    }


def sync_e2e_duties() -> dict:
    """Append D24–D26 to duty card if missing."""
    card = load_card()
    if not card:
        return {"ok": False, "error": "no card"}
    items = list(card.get("never_make_founder_repeat") or [])
    ids = {x.get("id") for x in items if isinstance(x, dict)}
    additions = [
        {
            "id": "D24",
            "founder_said": "Agents re-run E2E without reading last report",
            "agent_duty": "Before any E2E: python3 scripts/sourcea_e2e_run_v1.py --read-last --json",
            "proof": "~/.sina/sourcea-e2e-last-report-v1.json",
        },
        {
            "id": "D25",
            "founder_said": "E2E proof lost in /tmp",
            "agent_duty": "After E2E: sourcea_e2e_run_v1.py --write-report — logs in ~/.sina/e2e-logs/",
            "proof": "validate-sourcea-e2e-report-discipline-v1.sh",
        },
        {
            "id": "D26",
            "founder_said": "No weekly E2E checklist",
            "agent_duty": "Sunday ship window: --cadence weekly --write-report or cloud CI",
            "proof": "~/.sina/sourcea-e2e-weekly-checklist-receipt-v1.json",
        },
    ]
    added = 0
    for row in additions:
        if row["id"] not in ids:
            items.append(row)
            added += 1
    card["never_make_founder_repeat"] = items
    card["updated_at"] = _now()
    order = list(card.get("session_start_order") or [])
    e2e_line = "python3 scripts/sourcea_e2e_run_v1.py --read-last --json — before any E2E"
    if e2e_line not in order:
        order.insert(2, e2e_line)
        card["session_start_order"] = order
    CARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    CARD_PATH.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "added": added, "item_count": len(items), "path": str(CARD_PATH)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Agent executor daily duty card")
    ap.add_argument("--sync-e2e-duties", action="store_true", help="Append D24-D26 to ~/.sina duty card")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--inject", action="store_true", help="Print inject slice JSON")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.sync_e2e_duties:
        out = sync_e2e_duties()
        if args.json:
            print(json.dumps(out, indent=2, ensure_ascii=False))
        else:
            print(f"DAILY_CARD_SYNC_E2E ok={out.get('ok')} added={out.get('added')}")
        return 0 if out.get("ok") else 1

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
