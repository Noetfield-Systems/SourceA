#!/usr/bin/env python3
"""Forge Terminal living reply contract — display_response + founder_language."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from forge_quality_gate_v1 import (  # noqa: E402
    _looks_like_json_blob,
    evaluate_quality_gate,
    response_for_display,
)


def run_reply_contract_tests() -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []

    json_resp = '{"goal":"x","risk":"low","summary":"bad"}'
    card = {
        "goal": "Summarize README for founder",
        "summary": "The README explains project scope in plain language.",
        "risk": "low",
    }
    display = response_for_display(response=json_resp, card=card)
    checks.append(("display swaps json for summary", not _looks_like_json_blob(display), display[:60]))
    checks.append(("display uses summary", "plain language" in display.lower(), display[:60]))

    gate = evaluate_quality_gate(
        run_id="ft-reply0000001",
        doc={
            "schema": "forge-terminal-run-v1",
            "run_id": "ft-reply0000001",
            "at": "2026-06-25T00:00:00Z",
            "founder_input": "Summarize README",
            "response": json_resp,
            "llm": {"ok": True, "provider": "gemini_direct", "model": "gemini-3.1-flash-lite"},
            "forge": {"workspace": "/tmp/ws"},
            "decision_card": card,
        },
        workspace_path="/tmp/ws",
        full_llm=True,
    )
    checks.append(("json fails founder_language", gate.get("verdict") != "PASS", gate.get("verdict") or ""))
    fl = next((x for x in gate.get("layers") or [] if x.get("id") == "founder_language"), {})
    checks.append(("founder_language layer fail", not fl.get("ok"), fl.get("note") or ""))

    prose = (
        "Bottom line\nThe README describes the project scope and main files clearly for the founder.\n\n"
        "What this means for you\nAgents can read README to understand workspace layout and goals.\n\n"
        "Blockers\nNone right now — no hard stop named in this paste.\n\n"
        "Next step\nOpen README and confirm the listed apps match your intent."
    )
    gate2 = evaluate_quality_gate(
        run_id="ft-reply0000002",
        doc={
            "schema": "forge-terminal-run-v1",
            "run_id": "ft-reply0000002",
            "at": "2026-06-25T00:00:00Z",
            "founder_input": "Summarize README purpose for this project",
            "response": prose,
            "llm": {"ok": True, "provider": "gemini_direct", "model": "gemini-3.1-flash-lite"},
            "forge": {"workspace": "/tmp/ws"},
            "decision_card": {
                "goal": "Summarize README purpose for this project",
                "risk": "low",
                "cursor_prompt": "Summarize README in plain English for the founder.",
                "summary": "README describes project scope and main files.",
                "decision": "pending",
                "cost_usd": 0.01,
            },
        },
        workspace_path="/tmp/ws",
        full_llm=True,
    )
    checks.append(("prose passes founder_language", gate2.get("verdict") == "PASS", gate2.get("verdict") or ""))

    return checks


def main() -> int:
    checks = run_reply_contract_tests()
    failed = 0
    for name, ok, detail in checks:
        if not ok:
            failed += 1
        extra = f" ({detail})" if detail and not ok else ""
        print(f"  {'PASS' if ok else 'FAIL'}  {name}{extra}")
    print(f"\n{len(checks) - failed}/{len(checks)} reply contract checks passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
