#!/usr/bin/env python3
"""Forge Quality Gate unit tests — one pass/fail fixture per layer + receipt schema."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from forge_quality_gate_v1 import (  # noqa: E402
    LAYER_ORDER,
    QUALITY_ENGINE_VERSION,
    SCHEMA,
    evaluate_quality_gate,
    execution_allowed,
    validate_receipt_schema,
)


def _base_doc(**overrides) -> dict:
    card = {
        "goal": "Build README summary for workspace",
        "risk": "low",
        "cursor_prompt": "Summarize README in plain English for the founder.",
        "summary": "The README describes a quality E2E test project with clear scope.",
        "decision": "pending",
        "cost_usd": 0.01,
        "founder_input": "Summarize README purpose for this project",
    }
    doc = {
        "schema": "forge-terminal-run-v1",
        "run_id": "ft-abc123456789",
        "at": "2026-06-25T00:00:00Z",
        "founder_input": "Summarize README purpose for this project",
        "response": "The README describes a quality E2E test project with clear scope.",
        "llm": {"ok": True, "provider": "gemini_direct", "model": "gemini-3.1-flash-lite"},
        "forge": {"workspace": "/tmp/ws"},
        "decision_card": card,
    }
    doc.update(overrides)
    if "decision_card" in overrides and overrides["decision_card"] is not None:
        doc["decision_card"] = {**card, **overrides["decision_card"]}
    return doc


def run_unit_tests() -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    checks.append(("engine version", QUALITY_ENGINE_VERSION == "1.1", QUALITY_ENGINE_VERSION))
    checks.append(("layer order frozen", len(LAYER_ORDER) == 11, str(len(LAYER_ORDER))))

    good = evaluate_quality_gate(
        run_id="ft-abc123456789",
        doc=_base_doc(),
        workspace_path="/tmp/ws",
        full_llm=True,
        eval_shadow=False,
    )
    ok_schema, err = validate_receipt_schema(good)
    checks.append(("receipt schema good", ok_schema, err))
    checks.append(("good doc PASS", good.get("verdict") == "PASS", good.get("verdict") or ""))
    checks.append(("11 layers", len(good.get("layers") or []) == 11, str(len(good.get("layers") or []))))

    # Per-layer fail fixtures
    fail_cases = [
        ("functional fail", _base_doc(response="ok", llm={"ok": False}), "functional"),
        ("founder_language json", _base_doc(response='{"goal":"x","risk":"low"}'), "founder_language"),
        ("model fail", _base_doc(llm={"ok": True, "provider": "", "model": ""}), "model_appropriate"),
        ("card fail", _base_doc(decision_card={"goal": "", "risk": "", "cursor_prompt": "", "summary": "", "decision": ""}), "decision_card_valid"),
        ("workspace fail", _base_doc(forge={}), "workspace_context_fit"),
    ]
    for name, doc, layer_id in fail_cases:
        gate = evaluate_quality_gate(
            run_id="ft-abc123456789",
            doc=doc,
            workspace_path="/tmp/ws" if layer_id != None and "workspace" not in name else None,
            full_llm=True,
        )
        if layer_id:
            ly = next((x for x in gate.get("layers") or [] if x.get("id") == layer_id), {})
            checks.append((name, not ly.get("ok"), ly.get("note") or ""))
        else:
            checks.append((name, gate.get("verdict") != "PASS", gate.get("verdict") or ""))

    thin = evaluate_quality_gate(
        run_id="ft-deadbeef1234",
        doc=_base_doc(response="x", founder_input="x"),
        workspace_path="/tmp/ws",
        full_llm=False,
    )
    checks.append(("thin blocked", not thin.get("execution_allowed"), thin.get("verdict") or ""))

    ok_exec, _ = execution_allowed({"run_id": "ft-abc123456789", "quality_gate": good})
    checks.append(("execution allowed helper", ok_exec, ""))

    return checks


def main() -> int:
    checks = run_unit_tests()
    failed = 0
    for name, ok, detail in checks:
        status = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        extra = f" ({detail})" if detail and not ok else ""
        print(f"  {status}  {name}{extra}")
    print(f"\n{len(checks) - failed}/{len(checks)} unit checks passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
