#!/usr/bin/env python3
"""Exa technical_velocity fetch — optional P2 research worker (structured notes only).

Returns ingestion-shaped notes for technical_velocity signal — never raw HTML dumps.
Live Exa when EXA_API_KEY is set; otherwise dry-run from checklist metadata.

Law: data/outbound-factory-salvage-spec-v1.json · data/outbound-ingestion-schema-v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "data" / "outbound-research-checklist-v1.json"
EXA_API = "https://api.exa.ai/search"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _structured_note(*, title: str, text: str, source_url: str = "", published_at: str | None = None) -> dict:
    return {
        "title": title[:200],
        "text": text[:2000],
        "source_url": source_url[:500],
        "published_at": published_at,
    }


def _dry_run_notes(account_id: str, meta: dict) -> list[dict]:
    company = str(meta.get("company_name") or account_id)
    role = str(meta.get("executive_role") or "executive")
    query_hint = f"{company} {role} product velocity AI engineering blog changelog"
    return [
        _structured_note(
            title=f"{company} technical velocity (dry-run)",
            text=(
                f"Optional Exa P2 worker — structured notes only. "
                f"Query hint: {query_hint}. Set EXA_API_KEY for live search."
            ),
            source_url="",
        )
    ]


def _exa_live_notes(query: str, *, api_key: str, num_results: int = 3) -> list[dict]:
    payload = json.dumps(
        {
            "query": query,
            "numResults": num_results,
            "type": "auto",
            "contents": {"text": {"maxCharacters": 800}},
        }
    ).encode()
    req = urllib.request.Request(
        EXA_API,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        body = json.loads(resp.read().decode())
    notes: list[dict] = []
    for row in body.get("results") or []:
        notes.append(
            _structured_note(
                title=str(row.get("title") or "result"),
                text=str(row.get("text") or row.get("snippet") or "")[:2000],
                source_url=str(row.get("url") or ""),
                published_at=str(row.get("publishedDate") or "") or None,
            )
        )
    return notes


def fetch_technical_velocity(*, account_id: str, live: bool | None = None) -> dict:
    """U055 — return structured technical_velocity notes for research checklist."""
    data = _read(CHECKLIST)
    acct = (data.get("accounts") or {}).get(account_id)
    if not acct:
        return {
            "ok": False,
            "schema": "exa-velocity-fetch-v1",
            "account_id": account_id,
            "error": "unknown account",
            "upgrade": "U055",
        }
    meta = acct.get("target_metadata") or {}
    company = str(meta.get("company_name") or account_id)
    role = str(meta.get("executive_role") or "")
    api_key = str(os.environ.get("EXA_API_KEY") or "").strip()
    use_live = live if live is not None else bool(api_key)
    mode = "live" if use_live and api_key else "dry_run"
    query = f"{company} {role} product launch engineering blog technical velocity".strip()

    notes: list[dict]
    warning: str | None = None
    if mode == "live":
        try:
            notes = _exa_live_notes(query, api_key=api_key)
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError) as exc:
            mode = "dry_run"
            warning = str(exc)
            notes = _dry_run_notes(account_id, meta)
    else:
        notes = _dry_run_notes(account_id, meta)

    return {
        "ok": True,
        "schema": "exa-velocity-fetch-v1",
        "at": _now(),
        "account_id": account_id,
        "signal": "technical_velocity",
        "mode": mode,
        "query": query,
        "structured_notes": notes,
        "raw_html": False,
        "human_confirmed": False,
        "ingestion_shape": {
            "text": notes[0]["text"] if notes else "",
            "source_url": notes[0].get("source_url") or "",
            "human_confirmed": False,
        },
        "warning": warning,
        "upgrade": "U055",
        "law": "Structured JSON only — no raw HTML dumps",
    }


def validate_exa_velocity_acceptance() -> dict:
    """U055 acceptance — returns structured notes only (no raw HTML)."""
    row = fetch_technical_velocity(account_id="fundmore", live=False)
    notes = row.get("structured_notes") or []
    forbidden_keys = {"html", "raw_html_body", "html_dump", "raw_dump"}
    note_keys = {k for n in notes for k in (n.keys() if isinstance(n, dict) else [])}
    has_shape = (
        row.get("ok")
        and row.get("signal") == "technical_velocity"
        and row.get("raw_html") is False
        and isinstance(notes, list)
        and notes
        and all(isinstance(n, dict) and "text" in n and "title" in n for n in notes)
        and not (forbidden_keys & note_keys)
        and row.get("ingestion_shape", {}).get("human_confirmed") is False
    )
    return {
        "ok": has_shape,
        "upgrade": "U055",
        "mode": row.get("mode"),
        "note_count": len(notes),
        "sample_title": notes[0].get("title") if notes else None,
        "acceptance": "Returns structured notes only",
        "check": "python3 scripts/exa_velocity_fetch_v1.py --check-structured-notes --json",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Exa technical_velocity fetch — structured notes only")
    ap.add_argument("--account", help="Checklist account id (e.g. fundmore)")
    ap.add_argument("--live", action="store_true", help="Force live Exa when EXA_API_KEY set")
    ap.add_argument("--dry-run", action="store_true", help="Force dry-run structured notes")
    ap.add_argument("--check-structured-notes", action="store_true", help="U055 acceptance")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.check_structured_notes:
        row = validate_exa_velocity_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_structured_notes:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if not args.account:
        ap.error("--account required unless --check-structured-notes")
    live = False if args.dry_run else (True if args.live else None)
    row = fetch_technical_velocity(account_id=args.account, live=live)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("mode"), len(row.get("structured_notes") or []), row.get("ok"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
