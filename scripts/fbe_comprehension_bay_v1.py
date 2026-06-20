#!/usr/bin/env python3
"""FBE comprehension bay — cloud worker analyzes agent output · plain founder result.

Runs on Railway FBE (headless). Mac Hub POSTs draft + optional system_snapshot only.
No Mac validators · no ~/.sina reads on cloud unless snapshot in body.

SSOT: data/cloud-comprehension-bay-v1.json
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SSOT = ROOT / "data/cloud-comprehension-bay-v1.json"

BENEFIT = re.compile(
    r"\b(you|your|for you|means|because|so |which means|blocked|ready|helps|matters)\b",
    re.I,
)
FOUNDER_ASKS = re.compile(r"\b(why|what|how|explain|understand|mean)\b", re.I)
MEANING_MIN = 65


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _plain_block_reason(*, quality: dict, lang: dict, snapshot: dict | None) -> tuple[str, str, list[str]]:
    """Return (for_founder_why, agent_instruction, hints)."""
    hints: list[str] = []
    meaning = quality.get("meaning") or {}
    if meaning.get("score", 100) < MEANING_MIN:
        hints.append("Explain in full sentences with because/so — not label chains.")
    for hit in lang.get("hits") or []:
        hints.append(str(hit.get("label") or hit.get("id") or "Use plain English"))
    if not hints:
        hints.append("Restate what the founder needs · explain why it matters for them · proof last.")

    system_notes: list[str] = []
    snap = snapshot or {}
    if snap.get("portfolio_line") and "RED" in str(snap["portfolio_line"]).upper():
        system_notes.append(
            "A product site check is still failing in the repository — that may affect what agents say about email or launch."
        )
    if snap.get("form_open", 0) > 0:
        system_notes.append(
            f"You have {snap['form_open']} open form decisions — cloud path may be waiting on those picks."
        )

    why = hints[0]
    if system_notes:
        why = system_notes[0] + " " + why

    agent = (
        "Rewrite in normal English (because/so). "
        + ("Also: " + system_notes[0] if system_notes else "")
        + " Do not send buzzword chains to the founder."
    )
    return why, agent.strip(), hints[:6]


def run_comprehension_bay(
    *,
    draft: str,
    founder_message: str = "",
    system_snapshot: dict | None = None,
) -> dict:
    import sys

    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))

    from founder_reply_translator_v1 import evaluate  # noqa: WPS433
    from agent_report_language_gate_v1 import scan_text as scan_language  # noqa: WPS433

    quality = evaluate(draft=draft, founder_message=founder_message)
    ship_text = quality.get("founder_text") or ""
    lang = scan_language(
        ship_text or draft,
        founder_asked_why=bool(FOUNDER_ASKS.search(founder_message or "")),
    )
    meaning = quality.get("meaning") or {}
    score = meaning.get("score")
    accepted = quality.get("ok") and bool(ship_text)

    if accepted:
        for_founder = {
            "show_this": ship_text,
            "blocked": False,
            "why": "",
        }
        for_agent = {
            "action": "ship",
            "instruction": "Cloud bay ACCEPT — use show_this for the founder.",
            "rewrite_hints": [],
        }
        verdict = "ACCEPT"
    else:
        why, agent_inst, hints = _plain_block_reason(
            quality=quality, lang=lang, snapshot=system_snapshot
        )
        for_founder = {
            "show_this": "",
            "blocked": True,
            "why": why,
        }
        for_agent = {
            "action": "rewrite",
            "instruction": agent_inst,
            "rewrite_hints": hints,
        }
        verdict = "BLOCKED"

    row = {
        "schema": "cloud-comprehension-bay-result-v1",
        "ok": accepted,
        "at": _now(),
        "bay_slug": "comprehension-loop-bay",
        "factory_id": "comprehension-loop-factory-v1",
        "execution_plane": "headless_cloud",
        "verdict": verdict,
        "meaning_score": score,
        "quality_verdict": quality.get("verdict"),
        "for_founder": for_founder,
        "for_agent": for_agent,
        "system_snapshot_used": bool(system_snapshot),
        "one_line": (
            f"comprehension-bay · cloud · {verdict} · score={score} · "
            + ("plain answer ready" if accepted else "blocked — rewrite")
        ),
    }
    return row


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="FBE comprehension bay v1")
    ap.add_argument("--text", default="")
    ap.add_argument("--founder-message", default="")
    ap.add_argument("--snapshot-json", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    snap = json.loads(args.snapshot_json) if args.snapshot_json.strip() else None
    row = run_comprehension_bay(
        draft=args.text,
        founder_message=args.founder_message,
        system_snapshot=snap,
    )
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        ff = row.get("for_founder") or {}
        print(row.get("one_line") or "")
        if ff.get("show_this"):
            print(ff["show_this"][:800])
        elif ff.get("why"):
            print("Blocked:", ff["why"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
