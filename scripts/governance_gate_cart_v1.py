#!/usr/bin/env python3
"""Governance gate cart — unified PASS/FAIL for all machine gates (session tier).

Writes: ~/.sina/governance-gate-cart-v1.json
Law: AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md · GOVERNANCE_DRIFT_ENGINE_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "governance-gate-cart-v1.json"

GATES = (
    ("brain_ssot", ["bash", "scripts/validate-brain-not-command-data-ssot-v1.sh"], 120),
    ("cascade", ["bash", "scripts/validate-founder-input-cascade-v1.sh"], 120),
    ("anti_staleness_vocab", ["bash", "scripts/validate-anti-staleness-vocabulary-gate-v1.sh"], 360),
    ("zero_drift", ["bash", "scripts/validate-governance-zero-drift-live-wire-v1.sh"], 180),
    ("sascip", ["bash", "scripts/validate-stranger-agent-safety-live-wire-v1.sh"], 120),
    ("full_stack_fix_plan", ["bash", "scripts/validate-full-stack-100-fix-plan-v1.sh"], 120),
    ("agent_behavior_settings", ["bash", "scripts/validate-agent-behavior-settings-v1.sh"], 120),
    ("ui_first_check_mandatory", ["bash", "scripts/validate-ui-first-check-mandatory-all-agents-v1.sh"], 180),
    ("ui_zero_drift", ["bash", "scripts/validate-ui-zero-drift-v1.sh"], 240),
    ("founder_no_invitation", ["bash", "scripts/validate-founder-no-invitation-v1.sh"], 60),
    ("anti_theater_validator_loop", ["bash", "scripts/validate-anti-theater-validator-loop-v1.sh"], 600),
    ("factory_cost_intelligence", ["bash", "scripts/validate-factory-cost-intelligence-v1.sh"], 120),
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _json_ok(stdout: str) -> bool | None:
    text = (stdout or "").strip()
    if not text or "{" not in text:
        return None
    for candidate in (text, text[text.find("{") :]):
        try:
            payload = json.loads(candidate)
            if isinstance(payload, dict) and "ok" in payload:
                return bool(payload.get("ok"))
        except json.JSONDecodeError:
            continue
    return None


def _run(cmd: list[str], *, timeout: int = 120) -> dict:
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        tail = (proc.stdout or proc.stderr or "").strip().splitlines()
        row = {
            "ok": proc.returncode == 0,
            "exit": proc.returncode,
            "tail": tail[-1][:200] if tail else f"exit {proc.returncode}",
        }
        if "--json" in cmd:
            parsed_ok = _json_ok(proc.stdout or "")
            if parsed_ok is not None:
                row["ok"] = parsed_ok
        return row
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit": -1, "tail": "timeout"}
    except OSError as exc:
        return {"ok": False, "exit": -1, "tail": str(exc)}


def _py_gate(name: str, script: str, *args: str, timeout: int = 90) -> dict:
    row = _run([sys.executable, str(SCRIPTS / script), *args, "--json"], timeout=timeout)
    row["id"] = name
    return row


def run_cart(*, tier: str = "session", write: bool = True) -> dict:
    rows: list[dict] = []
    for gate_item in GATES:
        if len(gate_item) == 3:
            gate_id, cmd, gate_timeout = gate_item
        else:
            gate_id, cmd = gate_item
            gate_timeout = 120
        if tier == "fast" and gate_id in ("anti_staleness_vocab",):
            continue
        r = _run(cmd, timeout=gate_timeout)
        r["id"] = gate_id
        rows.append(r)

    rows.append(_py_gate("governance_center", "governance_center_run_v1.py", "--tier", "fast", timeout=240))
    rows.append(_py_gate("nerve", "agent_nerve_system_v1.py"))
    rows.append(_py_gate("zero_drift_wire", "governance_zero_drift_live_wire_v1.py", "--role", "worker", "--tier", "session"))

    if tier == "full":
        for pipe in ("orientation", "hospital", "maze"):
            r = _run(
                [sys.executable, str(SCRIPTS / "agent_three_pipelines_router_v1.py"), pipe, "--role", "worker", "--json"],
                timeout=180,
            )
            r["id"] = f"pipeline_{pipe}"
            rows.append(r)

    exec_plane: dict = {}
    comm_plane: dict = {}
    try:
        sys.path.insert(0, str(SCRIPTS))
        from execution_plane_honesty_v1 import assess_commercial_readiness, assess_execution_plane  # noqa: WPS433

        exec_plane = assess_execution_plane()
        comm_plane = assess_commercial_readiness()
        for check_id, check_ok in (exec_plane.get("checks") or {}).items():
            rows.append(
                {
                    "id": f"execution_{check_id}",
                    "ok": bool(check_ok),
                    "exit": 0 if check_ok else 1,
                    "tail": exec_plane.get("execution_honesty_line", "")[:120],
                    "plane": "execution",
                }
            )
        for gate_id, gate_ok in (comm_plane.get("gates") or {}).items():
            rows.append(
                {
                    "id": f"commercial_{gate_id}",
                    "ok": bool(gate_ok),
                    "exit": 0 if gate_ok else 1,
                    "tail": comm_plane.get("commercial_readiness_line", "")[:120],
                    "plane": "commercial",
                }
            )
    except Exception as exc:
        rows.append({"id": "execution_plane", "ok": False, "exit": -1, "tail": str(exc)[:120]})

    passed = sum(1 for r in rows if r.get("ok"))
    total = len(rows)
    gov_rows = [r for r in rows if not r.get("plane")]
    comm_rows = [r for r in rows if r.get("plane") == "commercial"]
    gov_passed = sum(1 for r in gov_rows if r.get("ok"))
    gov_total = len(gov_rows)
    gov_ok = gov_passed == gov_total if gov_rows else True
    exec_ok = bool(exec_plane.get("ok")) if exec_plane else True
    comm_failed = [r for r in comm_rows if not r.get("ok")]
    founder_commercial_block: dict | None = None
    if comm_failed and exec_ok and gov_ok:
        only_send = all(str(r.get("id") or "") == "commercial_w3_send_ready" for r in comm_failed)
        if only_send:
            founder_commercial_block = {
                "gate_id": "commercial_w3_send_ready",
                "owner": "founder",
                "reason": "L3 confirm_sent — agents never send email",
                "founder_action": "Hub commercial L3 · ocree:confirm_sent",
                "ready_pct": comm_plane.get("ready_pct"),
                "documented_at": _now(),
                "law": "OUTBOUND_EXECUTION_HARDENING_PLAN_LOCKED_v1.md",
            }
    comm_ok = all(r.get("ok") for r in comm_rows) if comm_rows else True
    cart_acceptance_ok = bool(gov_ok and exec_ok and (comm_ok or founder_commercial_block))
    ok = gov_ok and passed == total
    line = f"gate-cart · {passed}/{total} PASS · tier={tier}" + ("" if ok else " · REVIEW")
    if founder_commercial_block:
        line += " · founder_block=w3_send_ready"
    if cart_acceptance_ok and not ok:
        line += " · F054_OK"
    if exec_plane:
        line += f" · {exec_plane.get('execution_honesty_line', '')[:48]}"

    receipt = {
        "schema": "governance-gate-cart-v1",
        "at": _now(),
        "tier": tier,
        "ok": ok,
        "cart_acceptance_ok": cart_acceptance_ok,
        "governance_ok": gov_ok,
        "governance_gates": {"passed": gov_passed, "total": gov_total},
        "execution_plane_ok": exec_ok,
        "commercial_ready_pct": comm_plane.get("ready_pct"),
        "founder_commercial_block": founder_commercial_block,
        "passed": passed,
        "total": total,
        "cart_line": line,
        "gates": rows,
        "execution_plane": exec_plane,
        "commercial_plane": comm_plane,
        "law": "AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Governance gate cart — unified machine gate PASS/FAIL")
    ap.add_argument("--tier", choices=("fast", "session", "full"), default="session")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    row = run_cart(tier=args.tier, write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["cart_line"])
        for g in row["gates"]:
            if not g.get("ok"):
                print(f"  FAIL · {g.get('id')} · {g.get('tail')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
