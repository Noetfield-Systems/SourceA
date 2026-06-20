#!/usr/bin/env python3
"""Founder reply quality loop — translate technical drafts; ship only if meaningful.

Flow: technical draft → translate → meaning score → SHIP founder text or REJECT + hints.
Agents rewrite until ok — no parrot reaches founder.

Law: data/agent-report-language-standard-v1.json
Receipt: ~/.sina/founder-reply-quality-v1.json
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "founder-reply-quality-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_loop(*, draft: str, founder_message: str = "", write_receipt: bool = False) -> dict:
    from founder_reply_translator_v1 import evaluate  # noqa: WPS433

    row = evaluate(draft=draft, founder_message=founder_message)
    out = {
        "schema": "founder-reply-quality-loop-v1",
        "at": _now(),
        "ok": row.get("ok"),
        "verdict": row.get("verdict"),
        "founder_text": row.get("founder_text") or "",
        "meaning_score": (row.get("meaning") or {}).get("score"),
        "rewrite_hints": row.get("rewrite_hints") or [],
        "translate_notes": row.get("translate_notes") or [],
        "founder_line": _founder_line(row),
        "agent_line": _agent_line(row),
        "detail": row,
    }
    if write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def _founder_line(row: dict) -> str:
    if row.get("ok"):
        v = row.get("verdict")
        if v == "SHIP_TRANSLATED":
            return "Reply cleared for founder (translated to plain language)."
        return "Reply cleared for founder."
    return "Reply blocked — agent must rewrite in plain language."


def _agent_line(row: dict) -> str:
    if row.get("ok"):
        return "Use founder_text from loop output."
    hints = row.get("rewrite_hints") or []
    return "REJECT: " + (hints[0] if hints else "rewrite for understanding and benefit")


def main() -> int:
    ap = argparse.ArgumentParser(description="Founder reply quality loop v1")
    ap.add_argument("--text", default="")
    ap.add_argument("--founder-message", default="")
    ap.add_argument("--file")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    body = args.text
    if args.file:
        body = Path(args.file).read_text(encoding="utf-8", errors="replace")
    row = run_loop(
        draft=body,
        founder_message=args.founder_message,
        write_receipt=args.write_receipt,
    )
    if args.json:
        # Slim JSON for gates — omit nested detail unless --verbose
        slim = {k: v for k, v in row.items() if k != "detail"}
        print(json.dumps(slim, indent=2, ensure_ascii=False))
    else:
        print(f"LOOP ok={row['ok']} verdict={row.get('verdict')} score={row.get('meaning_score')}")
        print(row.get("founder_line") or "")
        print(row.get("agent_line") or "")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
