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
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SSOT = ROOT / "data/cloud-comprehension-bay-v1.json"
BAY_SLUG = "comprehension-loop-bay"

FOUNDER_ASKS = re.compile(r"\b(why|what|how|explain|understand|mean)\b", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _plain_block_reason(
    *,
    quality: dict,
    lang: dict,
    snapshot: dict | None,
    meaning_min: int,
) -> tuple[str, str, list[str]]:
    """Return (for_founder_why, agent_instruction, hints)."""
    hints: list[str] = []
    meaning = quality.get("meaning") or {}
    if meaning.get("score", 100) < meaning_min:
        hints.append("Explain in full sentences with because/so — not label chains.")
    for hit in lang.get("hits") or []:
        hints.append(str(hit.get("label") or hit.get("id") or "Use plain English"))
    if not hints:
        hints.append("Restate what the founder needs · explain why it matters for them · proof last.")

    system_notes: list[str] = []
    snap = snapshot or {}
    if snap.get("portfolio_line") and "RED" in str(snap["portfolio_line"]).upper():
        system_notes.append(
            "A product site check is still failing on disk — that may affect what agents say about email or launch."
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


def _run_single_attempt(
    *,
    draft: str,
    founder_message: str,
    system_snapshot: dict | None,
    bay_config: dict[str, Any],
) -> dict[str, Any]:
    import sys

    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))

    from founder_reply_translator_v1 import evaluate  # noqa: WPS433
    from agent_report_language_gate_v1 import scan_text as scan_language  # noqa: WPS433

    meaning_min = int(bay_config.get("meaning_min") or 65)
    relax_lang = bool(bay_config.get("relax_language_gate"))

    quality = evaluate(draft=draft, founder_message=founder_message)
    ship_text = quality.get("founder_text") or ""
    if not ship_text and relax_lang:
        preview = quality.get("translated_preview") or ""
        meaning = quality.get("meaning") or {}
        score = meaning.get("score")
        draft_lower = draft.lower()
        causal_draft = " because " in draft_lower or " until " in draft_lower or " which means " in draft_lower
        if (
            preview
            and score is not None
            and int(score) >= meaning_min
            and len(draft.strip()) >= 70
            and causal_draft
        ):
            ship_text = preview
    lang = scan_language(
        ship_text or draft,
        founder_asked_why=bool(FOUNDER_ASKS.search(founder_message or "")),
    )
    meaning = quality.get("meaning") or {}
    score = meaning.get("score")
    meaning_ok = score is not None and int(score) >= meaning_min

    if relax_lang and ship_text and meaning_ok:
        accepted = True
    else:
        accepted = bool(quality.get("ok")) and bool(ship_text) and meaning_ok

    if accepted:
        for_founder = {
            "show_this": ship_text or draft.strip(),
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
            quality=quality, lang=lang, snapshot=system_snapshot, meaning_min=meaning_min
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

    return {
        "variation_key": bay_config.get("variation_key"),
        "config_version": bay_config.get("config_version"),
        "verdict": verdict,
        "ok": accepted,
        "meaning_score": score,
        "meaning_min": meaning_min,
        "quality_verdict": quality.get("verdict"),
        "for_founder": for_founder,
        "for_agent": for_agent,
    }


def run_comprehension_bay(
    *,
    draft: str,
    founder_message: str = "",
    system_snapshot: dict | None = None,
    variation_key: str | None = None,
    config_override: dict | None = None,
    context_id: str = "",
) -> dict:
    import sys

    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))

    from agent_runtime_config_v1 import load_bay_config, load_variation_by_key  # noqa: WPS433

    bay_config = load_bay_config(
        BAY_SLUG,
        context_id=context_id,
        variation_key=variation_key,
        config_override=config_override,
    )

    attempts: list[dict[str, Any]] = []
    attempt = _run_single_attempt(
        draft=draft,
        founder_message=founder_message,
        system_snapshot=system_snapshot,
        bay_config=bay_config,
    )
    attempts.append(
        {
            "variation_key": attempt.get("variation_key"),
            "verdict": attempt.get("verdict"),
            "meaning_score": attempt.get("meaning_score"),
            "config_version": attempt.get("config_version"),
        }
    )

    escalated = False
    if (
        not attempt.get("ok")
        and bay_config.get("retry_on_blocked")
        and bay_config.get("fallback_variation")
    ):
        fallback_key = str(bay_config.get("fallback_variation"))
        fallback_config = load_variation_by_key(BAY_SLUG, fallback_key)
        fallback_attempt = _run_single_attempt(
            draft=draft,
            founder_message=founder_message,
            system_snapshot=system_snapshot,
            bay_config=fallback_config,
        )
        attempts.append(
            {
                "variation_key": fallback_attempt.get("variation_key"),
                "verdict": fallback_attempt.get("verdict"),
                "meaning_score": fallback_attempt.get("meaning_score"),
                "config_version": fallback_attempt.get("config_version"),
            }
        )
        if fallback_attempt.get("ok"):
            attempt = fallback_attempt
            escalated = True
        else:
            attempt = fallback_attempt

    accepted = bool(attempt.get("ok"))
    verdict = str(attempt.get("verdict") or ("ACCEPT" if accepted else "BLOCKED"))
    score = attempt.get("meaning_score")
    var_key = attempt.get("variation_key")
    cfg_ver = attempt.get("config_version")

    one_line = f"comprehension-bay · cloud · {verdict} · score={score} · cfg={cfg_ver}"
    if escalated:
        one_line += f" · escalated {var_key}"
    elif accepted:
        one_line += " · plain answer ready"
    else:
        one_line += " · blocked — rewrite"

    row = {
        "schema": "cloud-comprehension-bay-result-v1",
        "ok": accepted,
        "at": _now(),
        "bay_slug": BAY_SLUG,
        "factory_id": "comprehension-loop-factory-v1",
        "execution_plane": "headless_cloud",
        "verdict": verdict,
        "meaning_score": score,
        "quality_verdict": attempt.get("quality_verdict"),
        "config_version": cfg_ver,
        "variation_key": var_key,
        "attempts": attempts,
        "escalated": escalated,
        "for_founder": attempt.get("for_founder") or {},
        "for_agent": attempt.get("for_agent") or {},
        "system_snapshot_used": bool(system_snapshot),
        "one_line": one_line,
    }
    return row


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="FBE comprehension bay v1")
    ap.add_argument("--text", default="")
    ap.add_argument("--founder-message", default="")
    ap.add_argument("--snapshot-json", default="")
    ap.add_argument("--variation-key", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    snap = json.loads(args.snapshot_json) if args.snapshot_json.strip() else None
    row = run_comprehension_bay(
        draft=args.text,
        founder_message=args.founder_message,
        system_snapshot=snap,
        variation_key=args.variation_key or None,
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
