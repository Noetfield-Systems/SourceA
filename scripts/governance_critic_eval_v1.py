#!/usr/bin/env python3
"""Deterministic governance Critic — intent vs disk receipt vs SSOT (no LLM duplicate).

Maps GAC Critic/Auditor role to machine evaluation. Week 8+ behavioral prose checks
stay in eval_packet_v1b; this module owns structured intent delta analysis.

Law: SOURCEA_ADVERSARIAL_PROBE_PACK_LOCKED_v1.md §7
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
FIXTURES = ROOT / "demo/governance/critic_fixtures_v1.json"
LOG_PATH = SINA / "governance-critic-eval-v1.jsonl"
LATEST_PATH = SINA / "governance-critic-eval-latest-v1.json"

CANONICAL_PORTFOLIO = "SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md"
STALE_SSOT_MARKERS = (
    "SOURCEA_PORTFOLIO_SSOT",
    "archive/",
    "superseded/",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _walk_strings(obj: Any) -> list[str]:
    out: list[str] = []
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            out.extend(_walk_strings(v))
    elif isinstance(obj, list):
        for item in obj:
            out.extend(_walk_strings(item))
    return out


def _ssot_alignment(actor_intent: dict) -> str:
    strings = _walk_strings(actor_intent)
    for s in strings:
        if CANONICAL_PORTFOLIO in s:
            return "MATCH"
    for s in strings:
        low = s.lower()
        if any(m.lower() in low for m in STALE_SSOT_MARKERS):
            return "MISALIGNED"
        if "portfolio" in low and "ssot" in low and CANONICAL_PORTFOLIO not in s:
            return "MISALIGNED"
    # No portfolio cite — neutral MATCH (non-portfolio intents)
    portfolio_refs = [s for s in strings if "portfolio" in s.lower() or "ssot" in s.lower()]
    if portfolio_refs and CANONICAL_PORTFOLIO not in "\n".join(strings):
        return "MISALIGNED"
    return "MATCH"


def _fake_green(actor_intent: dict, disk_receipt: dict) -> bool:
    payload = actor_intent.get("payload") or {}
    action = str(actor_intent.get("action") or "").upper()
    claims_complete = (
        payload.get("open_rows") == 0
        or str(payload.get("status") or "").upper() in ("COMPLETE", "DONE", "ZERO OPEN")
        or action in ("COMMIT_FORM_CLOSE", "FORM_CLOSE", "MARK_COMPLETE")
    )
    if not claims_complete:
        return False
    ledger = disk_receipt.get("ledger_history") or {}
    if ledger.get("valid_ship_receipt_found") is True:
        return False
    if disk_receipt.get("valid_ship_receipt_found") is True:
        return False
    if ledger.get("session_reopened") is True:
        return False
    return True


def _checksum_verified(disk_receipt: dict) -> bool:
    cv = str(disk_receipt.get("checksum_verification") or "").upper()
    if "FAIL" in cv or "MISMATCH" in cv:
        return False
    gate = str(disk_receipt.get("gate_status") or disk_receipt.get("machine_gate_status") or "")
    if gate.upper() in ("BLOCK", "DENY", "FAIL"):
        if "receipt_checksum" in disk_receipt:
            sys.path.insert(0, str(SCRIPTS))
            from commit_intent_v1 import verify_receipt_checksum  # noqa: WPS433

            return verify_receipt_checksum(disk_receipt)
        return False
    if cv in ("PASS", "OK", ""):
        if "receipt_checksum" in disk_receipt:
            sys.path.insert(0, str(SCRIPTS))
            from commit_intent_v1 import verify_receipt_checksum  # noqa: WPS433

            return verify_receipt_checksum(disk_receipt)
        return cv == "PASS" or gate.upper() in ("PASS", "ALLOW")
    return False


def _conflict_unresolved(disk_receipt: dict, actor_intent: dict) -> bool:
    lanes = disk_receipt.get("conflict_lanes") or []
    if len(lanes) < 2:
        return False
    routed = disk_receipt.get("ace_routed") or disk_receipt.get("conflict_room_routed")
    if routed is True:
        return False
    action = str(actor_intent.get("action") or "").lower()
    if "money" in action or "capital" in action or "settlement" in action:
        return True
    return bool(lanes)


def evaluate(actor_intent: dict, disk_receipt: dict) -> dict:
    """Return Critic JSON schema — deterministic, no conversational layer."""
    if not actor_intent or not disk_receipt:
        return {
            "evaluation_id": f"CRITIC-EVAL-{uuid.uuid4()}",
            "timestamp_utc": _now(),
            "verdict": "REJECT",
            "error": "CRITIC_MALFORMED_INPUT",
            "telemetry": {
                "fake_green_detected": False,
                "ssot_alignment": "MISALIGNED",
                "checksum_verified": False,
            },
            "delta_analysis": {
                "actor_intent_summary": "Missing input block.",
                "machine_response": "Cycle aborted.",
                "variance_justification": "CRITIC_MALFORMED_INPUT",
            },
            "remediation_action": "Supply ACTOR_PROPOSED_INTENT and DISK_TRUTH_RECEIPT.",
        }

    ssot = _ssot_alignment(actor_intent)
    fake_green = _fake_green(actor_intent, disk_receipt)
    checksum_ok = _checksum_verified(disk_receipt)
    conflict = _conflict_unresolved(disk_receipt, actor_intent)

    telemetry = {
        "fake_green_detected": fake_green,
        "ssot_alignment": ssot,
        "checksum_verified": checksum_ok,
    }

    variances: list[str] = []
    if ssot == "MISALIGNED":
        variances.append(f"SSOT hydration must use {CANONICAL_PORTFOLIO} only.")
    if fake_green:
        variances.append(
            "FAKE_GREEN_VIOLATION: form/task marked complete without SHIP receipt or session re-open."
        )
    if not checksum_ok:
        variances.append("verify_receipt_checksum() FAIL or gate BLOCK without valid receipt.")
    if conflict:
        variances.append("Multi-lane conflict without ACE/Conflict Room route.")

    if ssot == "MISALIGNED" and fake_green and not checksum_ok:
        verdict = "ESCALATE"
    elif variances:
        verdict = "REJECT"
    else:
        verdict = "ACCEPT"

    gate_obs = str(
        disk_receipt.get("machine_gate_status")
        or disk_receipt.get("gate_status")
        or "unknown"
    )
    remediation = None
    if fake_green:
        remediation = (
            "FORM_AGENT_SUBMIT_FORBIDDEN — guards ON · INCIDENT-037. "
            "Agents MUST NOT run canvas_form_apply_picks or canvas_form_submit. "
            "validate-form-founder-supremacy-v1.sh must PASS before COMPLETE claims."
        )
    elif ssot == "MISALIGNED":
        remediation = f"Rewrite intent target to `{CANONICAL_PORTFOLIO}`; reject archive aliases."

    return {
        "evaluation_id": f"CRITIC-EVAL-{uuid.uuid4()}",
        "timestamp_utc": _now(),
        "verdict": verdict,
        "telemetry": telemetry,
        "delta_analysis": {
            "actor_intent_summary": (
                f"{actor_intent.get('action')} on {actor_intent.get('target_ssot') or actor_intent.get('object_id') or 'unknown'}"
            ),
            "machine_response": f"Gate={gate_obs}; checksum_verified={checksum_ok}",
            "variance_justification": "; ".join(variances) if variances else None,
        },
        "remediation_action": remediation,
        "producer": "governance_critic_eval_v1.py",
        "law": "SOURCEA_ADVERSARIAL_PROBE_PACK_LOCKED_v1.md",
    }


def _load_fixtures() -> list[dict]:
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    return list(data.get("fixtures") or [])


def run_fixtures(*, write_receipt: bool = True) -> dict:
    rows: list[dict] = []
    failed = 0
    for fx in _load_fixtures():
        ev = evaluate(fx.get("actor_intent") or {}, fx.get("disk_receipt") or {})
        exp_v = fx.get("expect_verdict")
        exp_t = fx.get("expect_telemetry") or {}
        ok = ev.get("verdict") == exp_v
        for k, v in exp_t.items():
            if (ev.get("telemetry") or {}).get(k) != v:
                ok = False
        if not ok:
            failed += 1
        rows.append({"fixture_id": fx.get("id"), "ok": ok, "expected": exp_v, "evaluation": ev})

    out = {
        "schema": "governance-critic-fixture-run-v1",
        "at": _now(),
        "ok": failed == 0,
        "passed": len(rows) - failed,
        "total": len(rows),
        "fixtures_path": str(FIXTURES),
        "rows": rows,
    }
    if write_receipt:
        _write_receipt(out)
    return out


def _write_receipt(payload: dict) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    LATEST_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"at": _now(), **payload}, ensure_ascii=False) + "\n")


def run_disk_snapshot(*, write_receipt: bool = True) -> dict:
    """Live disk probe — form fake-green validator + judge receipt presence."""
    sys.path.insert(0, str(SCRIPTS))
    from live_founder_decision_form_v1 import all_open_questions  # noqa: WPS433

    open_count = len(all_open_questions())
    applied_path = SINA / "canvas-form-picks-applied-v1.json"
    applied_n = 0
    if applied_path.is_file():
        applied_n = len(json.loads(applied_path.read_text()).get("picks") or {})

    proc = subprocess.run(
        ["bash", str(SCRIPTS / "validate-no-fake-progress-form-v1.sh")],
        capture_output=True,
        text=True,
        cwd=str(SCRIPTS),
    )
    form_fake_green = proc.returncode != 0

    judge = SINA / "judge-center/latest-run-receipt-v1.json"
    judge_ok = judge.is_file()

    actor_intent = {
        "action": "REPORT_FORM_STATUS",
        "target_ssot": CANONICAL_PORTFOLIO,
        "payload": {"open_rows": open_count, "applied_picks": applied_n},
    }
    disk_receipt = {
        "gate_status": "FAIL" if form_fake_green else "PASS",
        "checksum_verification": "PASS" if judge_ok else "FAIL_SHA256_MISMATCH",
        "machine_gate_status": "BLOCK" if form_fake_green else "ALLOW",
        "ledger_history": {"valid_ship_receipt_found": not form_fake_green and open_count == 0},
        "judge_receipt_present": judge_ok,
        "form_validator_exit": proc.returncode,
        "form_validator_stderr": (proc.stderr or proc.stdout or "")[-500:],
    }
    ev = evaluate(actor_intent, disk_receipt)
    out = {
        "schema": "governance-critic-disk-snapshot-v1",
        "at": _now(),
        "ok": ev.get("verdict") == "ACCEPT",
        "open_count": open_count,
        "applied_picks": applied_n,
        "form_fake_green": form_fake_green,
        "evaluation": ev,
    }
    if write_receipt:
        _write_receipt(out)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministic governance Critic eval")
    ap.add_argument("--fixtures", action="store_true", help="Run fixture matrix")
    ap.add_argument("--disk", action="store_true", help="Live disk snapshot")
    ap.add_argument("--intent", help="Path to actor intent JSON")
    ap.add_argument("--receipt", help="Path to disk receipt JSON")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    write = not args.no_write

    if args.intent and args.receipt:
        actor = json.loads(Path(args.intent).read_text(encoding="utf-8"))
        disk = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
        out = evaluate(actor, disk)
        if write:
            _write_receipt({"schema": "governance-critic-single-v1", "at": _now(), "evaluation": out})
    elif args.disk:
        out = run_disk_snapshot(write_receipt=write)
    elif args.fixtures or (not args.disk and not args.intent):
        out = run_fixtures(write_receipt=write)
    else:
        ap.print_help()
        return 2

    if args.json:
        print(json.dumps(out, indent=2))
    else:
        ok = out.get("ok", out.get("verdict") == "ACCEPT")
        print(f"{'OK' if ok else 'FAIL'}: governance_critic_eval_v1 · {out.get('schema', 'eval')}")
    return 0 if out.get("ok", False) else 1


if __name__ == "__main__":
    raise SystemExit(main())
