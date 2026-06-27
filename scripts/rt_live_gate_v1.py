#!/usr/bin/env python3
"""RT LIVE gate state + proof receipt (INCIDENT-027 / form Q-RT-LIVE YES)."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
GATE_PATH = SINA / "rt-live-gate-v1.json"
RECEIPT_PATH = SINA / "rt-live-gate-receipt-v1.json"
HUB = "http://127.0.0.1:13020"

# Law: cascade + hub-sync in seconds, not minutes (form Q-RT-LIVE)
HUB_SYNC_PASS_MS = 3000
CASCADE_PASS_MS = 45000


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _scripts_path() -> None:
    p = str(SCRIPTS)
    if p not in sys.path:
        sys.path.insert(0, p)


def receipt_pass() -> bool:
    """True when rt-live-gate-receipt-v1.json records gate PASS."""
    if not RECEIPT_PATH.is_file():
        return False
    try:
        rec = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
        return rec.get("gate") == "PASS"
    except Exception:
        return False


def sync_gate_state() -> dict:
    """Write ~/.sina/rt-live-gate-v1.json when form filled + RT LIVE gate open."""
    _scripts_path()
    from founder_p0_next_action_v1 import rt_live_gate_active  # noqa: WPS433
    from live_founder_decision_form_v1 import payload as live_form_payload  # noqa: WPS433

    form = live_form_payload()
    active = rt_live_gate_active()
    passed = receipt_pass()
    if active and passed:
        status = "pass"
        maintainer_p0 = ["FR-003", "phase_1_10_seal", "phase_3_resume"]
    elif active:
        status = "open"
        maintainer_p0 = ["cascade_seconds", "hub_sync_seconds", "FR-003"]
    else:
        status = "closed"
        maintainer_p0 = []
    row = {
        "schema": "rt-live-gate-v1",
        "updated_at": _now(),
        "gate": "RT-LIVE-GATE",
        "status": status,
        "form_edition": form.get("form_edition"),
        "asf_filled_at": form.get("asf_filled_at"),
        "maintainer_p0": maintainer_p0,
        "factory_background": True,
        "receipt_pass": passed,
        "law": "SOURCEA_LIVE_FOUNDER_DECISION_FORM_V2_ANSWERS_RECEIPT_2026-06-11_LOCKED_v1.md",
        "incident": "MAINT-REF-INCIDENT-027-001",
    }
    if active:
        SINA.mkdir(parents=True, exist_ok=True)
        GATE_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def _receipt_checksum(body: dict) -> str:
    stripped = {k: v for k, v in body.items() if k != "receipt_checksum"}
    raw = json.dumps(stripped, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _verify_receipt_checksum(rec: dict) -> bool:
    expected = rec.get("receipt_checksum")
    if not expected:
        return False
    return _receipt_checksum(rec) == expected


def _finalize_receipt(receipt: dict, *, gate_pass: bool) -> dict:
    """Write receipt with checksum; bind PASS receipts to governance spine."""
    _scripts_path()
    from governance_event_spine_v1 import append_event, find_by_event_id  # noqa: WPS433

    SINA.mkdir(parents=True, exist_ok=True)
    receipt = dict(receipt)
    receipt.pop("receipt_checksum", None)
    receipt.pop("spine_event_id", None)
    receipt.pop("spine_checksum", None)

    if gate_pass:
        receipt["receipt_checksum"] = _receipt_checksum(receipt)
        RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        spine_res = append_event(
            event_type="VALIDATOR_PASS",
            object_id="RT-LIVE-GATE",
            object_kind="system",
            agent_id="maintainer",
            law_id="LIVE_GOV_BP",
            skill_id="rt_live_gate_v1",
            validator_set=[
                "validate-universe-invariants-v1.sh",
                "validate-maintainer-scan-p0-v1.sh",
            ],
            affected_objects=["RT-LIVE-GATE", "command-data.json"],
            projection_targets=["hub", "monitor"],
            gate="RT_LIVE_GATE",
            proof=str(RECEIPT_PATH),
            payload={
                "gate": receipt.get("gate"),
                "hub_sync_wall_ms": receipt.get("hub_sync_wall_ms"),
                "cascade_wall_ms": receipt.get("cascade_wall_ms"),
                "reason": receipt.get("reason"),
            },
        )
        if spine_res.get("ok"):
            ev = spine_res["event"]
            receipt["spine_event_id"] = ev.get("event_id")
            receipt["spine_checksum"] = ev.get("checksum")

    receipt["receipt_checksum"] = _receipt_checksum(receipt)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def bind_receipt_to_spine() -> dict:
    """Upgrade existing PASS receipt with spine bind (no full re-prove)."""
    if not RECEIPT_PATH.is_file():
        return {"ok": False, "error": "no receipt"}
    rec = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    if rec.get("gate") != "PASS":
        return {"ok": False, "error": "receipt not PASS"}
    if rec.get("spine_event_id"):
        from governance_event_spine_v1 import find_by_event_id  # noqa: WPS433

        row = find_by_event_id(str(rec["spine_event_id"]))
        if row and _verify_receipt_checksum(rec):
            return {"ok": True, "receipt": rec, "already_bound": True}
    rec = _finalize_receipt(rec, gate_pass=True)
    return {"ok": True, "receipt": rec, "bound": True}


def _hub_sync_wall_ms() -> tuple[int, dict]:
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(f"{HUB}/api/hub-sync", timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        ms = int((time.monotonic() - t0) * 1000)
        return ms, {"ok": True, "generation_id": body.get("generation_id"), "ms": ms}
    except Exception as exc:
        ms = int((time.monotonic() - t0) * 1000)
        return ms, {"ok": False, "error": str(exc), "ms": ms}


def prove(*, reason: str = "maintainer_probe") -> dict:
    """Measure hub-sync + light cascade; write rt-live-gate-receipt-v1.json."""
    _scripts_path()
    from governance_propagation_cascade_v1 import cascade  # noqa: WPS433

    gate = sync_gate_state()
    hub_ms, hub_detail = _hub_sync_wall_ms()
    t0 = time.monotonic()
    cascade_row = cascade(reason=f"rt_live_gate:{reason}", strict_hub=False)
    cascade_ms = int((time.monotonic() - t0) * 1000)
    cascade_steps_ms = sum(int(s.get("ms") or 0) for s in cascade_row.get("steps") or [])

    hub_pass = hub_ms <= HUB_SYNC_PASS_MS and hub_detail.get("ok")
    cascade_pass = cascade_ms <= CASCADE_PASS_MS and bool(cascade_row.get("ok"))
    gate_pass = hub_pass and cascade_pass

    receipt = {
        "schema": "rt-live-gate-receipt-v1",
        "proved_at": _now(),
        "reason": reason,
        "gate": "PASS" if gate_pass else "FAIL",
        "hub_sync_wall_ms": hub_ms,
        "hub_sync_pass_ms": HUB_SYNC_PASS_MS,
        "cascade_wall_ms": cascade_ms,
        "cascade_steps_ms": cascade_steps_ms,
        "cascade_pass_ms": CASCADE_PASS_MS,
        "hub_sync_detail": hub_detail,
        "cascade_ok": cascade_row.get("ok"),
        "maintainer_p0_next": [
            "FR-003 wiring" if gate_pass else "fix cascade/hub-sync until gate PASS",
            "Phase 1.10 seal after gate PASS",
            "Phases 3-10 resume per Q-NEXT-WORK D",
        ],
        "incident": "MAINT-REF-INCIDENT-027-001",
    }
    if gate_pass:
        gate["status"] = "pass"
        receipt["gate_status"] = "pass"
    else:
        gate["status"] = "open"
        receipt["gate_status"] = "open"

    SINA.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")
    receipt = _finalize_receipt(receipt, gate_pass=gate_pass)
    return {"ok": gate_pass, "gate": gate, "receipt": receipt}


def generate_scan_brief() -> str:
    """JSON-only maintainer SCAN brief (INCIDENT-027 G4)."""
    _scripts_path()
    from live_founder_decision_form_v1 import payload as live_form_payload  # noqa: WPS433

    form = live_form_payload()
    prog_path = ROOT / "PROGRAM_PROGRESS.json"
    founder_open = ""
    if prog_path.is_file():
        todos = json.loads(prog_path.read_text(encoding="utf-8")).get("todos") or []
        for t in todos:
            if t.get("id") == "SYS-INTEGRITY-100":
                founder_open = str(t.get("founder_open") or "")
                break

    lines = [
        "MAINTAINER 2 SCAN (generated from disk JSON — not static template)",
        f"form_edition: {form.get('form_edition')} · v2_filled: {(form.get('v2_answers') or {}).get('filled')}",
        f"awaiting_founder_picks: {form.get('awaiting_founder_picks')}",
        f"form_headline: {form.get('form_headline')}",
        f"open_questions: {form.get('open_questions_count')}",
        f"PROGRAM_PROGRESS.founder_open: {founder_open}",
        "READ ORDER: form JSON → PROGRAM_PROGRESS → SESSION_LOG → form §4 → projection (LAG)",
        "BAN headline: sa-XXXX · Valid YES % · Cloud Forge Run · queue pos",
    ]
    if int(form.get("open_questions_count") or 0) > 0:
        lines.append(
            f"Maintainer P0: {form.get('open_questions_count')} open PICKs — M1 Canvas Pending confirmations · no drain hero"
        )
    elif (form.get("v2_answers") or {}).get("filled"):
        if RECEIPT_PATH.is_file():
            try:
                rec = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
                if rec.get("gate") == "PASS":
                    lines.append(
                        f"RT LIVE receipt PASS · hub_sync={rec.get('hub_sync_wall_ms')}ms · "
                        f"cascade={rec.get('cascade_wall_ms')}ms"
                    )
                    lines.append("Maintainer P0: FR-003 wiring · Phase 1.10 seal · Phase 3 resume (10.10 D)")
                else:
                    lines.append("Maintainer P0: RT LIVE gate proof + FR-003 · factory = background only")
            except Exception:
                lines.append("Maintainer P0: RT LIVE gate proof + FR-003 · factory = background only")
        else:
            lines.append("Maintainer P0: RT LIVE gate proof + FR-003 · factory = background only")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sync", action="store_true", help="Write rt-live-gate-v1.json")
    ap.add_argument("--prove", action="store_true", help="Run probe + write receipt")
    ap.add_argument("--scan-brief", action="store_true", help="Print JSON-derived SCAN brief")
    ap.add_argument("--bind-spine", action="store_true", help="Bind PASS receipt to governance spine")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.scan_brief:
        print(generate_scan_brief())
        return 0
    if args.bind_spine:
        out = bind_receipt_to_spine()
    elif args.prove:
        out = prove()
    elif args.sync:
        out = {"ok": True, "gate": sync_gate_state()}
    else:
        out = {"ok": True, "gate": sync_gate_state(), "receipt_path": str(RECEIPT_PATH)}
    if args.json or args.prove or args.sync:
        print(json.dumps(out, indent=2))
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
