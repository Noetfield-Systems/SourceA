#!/usr/bin/env python3
"""U070 — post-send reply tracking manual row · ~/.sina/outbound-replies-v1.jsonl."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
OUTBOUND = SINA / "outbound"
REPLIES = SINA / "outbound-replies-v1.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _normalize_yn(val: str) -> str:
    t = str(val or "").strip().upper()
    if t in ("Y", "YES", "TRUE", "1"):
        return "Y"
    if t in ("N", "NO", "FALSE", "0"):
        return "N"
    raise SystemExit("reply must be Y or N")


def read_replies(*, account_id: str = "") -> list[dict]:
    if not REPLIES.is_file():
        return []
    rows: list[dict] = []
    aid = str(account_id or "").strip()
    try:
        for line in REPLIES.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if aid and row.get("account_id") != aid:
                continue
            rows.append(row)
    except OSError:
        return []
    return rows


def latest_reply_by_account() -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for row in read_replies():
        aid = str(row.get("account_id") or "")
        if aid:
            latest[aid] = row
    return latest


def log_reply(account_id: str, reply_yn: str, *, note: str = "", logged_by: str = "founder") -> dict:
    """Append manual founder reply row Y/N — agents never auto-log replies."""
    aid = str(account_id or "").strip()
    if not aid:
        return {"ok": False, "error": "account_id required", "upgrade": "U070"}
    yn = _normalize_yn(reply_yn)
    pack_path = OUTBOUND / f"w3-canada-{aid}" / "pack.json"
    pack = _read_json(pack_path)
    row = {
        "schema": "outbound-reply-row-v1",
        "upgrade": "U070",
        "at": _now(),
        "account_id": aid,
        "reply_yn": yn,
        "replied": yn == "Y",
        "reply_rate_pct": 100 if yn == "Y" else 0,
        "note": note or None,
        "logged_by": logged_by,
        "to": pack.get("to"),
        "sent_at": pack.get("sent_at"),
        "subject": pack.get("subject"),
        "company": pack.get("company"),
    }
    REPLIES.parent.mkdir(parents=True, exist_ok=True)
    with REPLIES.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    return {"ok": True, "row": row, "path": str(REPLIES)}


def validate_reply_log_acceptance() -> dict:
    """U070 acceptance — founder logs reply Y/N to outbound-replies-v1.jsonl."""
    y = log_reply("fundmore", "Y", note="U070 acceptance Y")
    n = log_reply("ocree", "N", note="U070 acceptance N")
    latest = latest_reply_by_account()
    ok = (
        REPLIES.is_file()
        and latest.get("fundmore", {}).get("reply_yn") == "Y"
        and latest.get("ocree", {}).get("reply_yn") == "N"
        and y.get("ok")
        and n.get("ok")
    )
    return {
        "ok": ok,
        "upgrade": "U070",
        "path": str(REPLIES),
        "latest": {
            "fundmore": latest.get("fundmore", {}).get("reply_yn"),
            "ocree": latest.get("ocree", {}).get("reply_yn"),
        },
        "acceptance": "Founder logs reply Y/N",
        "check": "python3 scripts/outbound_reply_log_v1.py --check-reply-log --json",
        "command": "python3 scripts/outbound_reply_log_v1.py --log fundmore Y --note 'got reply'",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Outbound post-send reply log (founder manual)")
    ap.add_argument("--log", nargs=2, metavar=("ACCOUNT", "Y|N"), help="Log founder reply Y/N")
    ap.add_argument("--list", action="store_true", help="List reply rows")
    ap.add_argument("--account", default="", help="Filter --list by account_id")
    ap.add_argument("--note", default="")
    ap.add_argument("--check-reply-log", action="store_true", help="U070 acceptance")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.check_reply_log:
        row = validate_reply_log_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_reply_log:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.list:
        rows = read_replies(account_id=args.account)
        if args.json:
            print(json.dumps({"ok": True, "rows": rows, "path": str(REPLIES)}, indent=2))
        else:
            for r in rows:
                print(f"{r.get('at')} {r.get('account_id')} reply={r.get('reply_yn')} note={r.get('note')}")
        return 0
    if args.log:
        aid, yn = args.log
        row = log_reply(aid, yn, note=args.note)
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(f"OK: {aid} reply={row['row']['reply_yn']}" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
