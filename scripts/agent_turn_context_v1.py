#!/usr/bin/env python3
"""Shared turn context for API + CLI agents — disk memory, role law, report parse."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
ROUND_REPORT = Path.home() / ".sina" / "worker_round_report_v1.json"
API_RESULTS = Path.home() / ".sina" / "api-agent-results"
CC_RESULTS = Path.home() / ".sina" / "cc-agent-results"
ORCH_STATE = Path.home() / ".sina" / "healthy-drain-orchestrator-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def role_law_block(role: str) -> str:
    r = (role or "").lower()
    if "check" in r:
        return (
            "ROLE=CHECK (hard law):\n"
            "- Verify/gap-report ONLY. Zero implement. Zero closeout. Zero pick 30.\n"
            "- Run read-only validators if context provides commands.\n"
            "- status PASS only if verify criteria met; FAIL if broken; BLOCKED if cannot verify.\n"
            "- next_action must be exactly: act (same sa_id) OR NONE. Never ask the founder.\n"
        )
    if "verify" in r:
        return (
            "ROLE=VERIFY (hard law):\n"
            "- Run task .md validators only; SINA_FCB_FAST=1 if find_critical_bugs needed.\n"
            "- REGISTRY done ONLY via worker_verify_closeout_v1.sh + receipts/sa-XXXX-receipt.json.\n"
            "- Flow: validators → WORKER_ROUND_REPORT → goal1_lane_broker worker-submit → worker_verify_closeout_v1.sh.\n"
            "- NEVER edit REGISTRY.json status directly; NEVER restore done from YAML.\n"
            "- bash worker_verify_fast_v1.sh enforces receipt+broker gates (auto-reverts fake done).\n"
            "- next_action must be NONE after closeout.\n"
        )
    return (
        "ROLE=ACT (hard law):\n"
        "- Minimal diff for bound sa_id only. No closeout. No batch. No scope creep.\n"
        "- next_action must be verify (same sa_id) OR NONE.\n"
    )


def build_memory_block(*, sa_id: str, role: str, pos: int, total: int) -> str:
    """Disk session memory — agents must not pretend they have no context."""
    import sys

    sys.path.insert(0, str(SCRIPTS))
    from healthy_queue_ssot_lib import registry_status_for_sa  # noqa: WPS433

    lines = [
        "=== SESSION MEMORY (disk SSOT — do not ask founder) ===",
        f"bound_sa_id: {sa_id}",
        f"bound_role: {role}",
        f"queue_pos: {pos}/{total}",
        f"registry_status: {registry_status_for_sa(sa_id) or 'backlog'}",
        f"at: {_now()}",
    ]

    try:
        from worker_asf_directive_latch_v1 import directive_block  # noqa: WPS433

        block = directive_block()
        if block:
            lines.append(block.rstrip())
    except Exception:
        pass

    rr = _read_json(ROUND_REPORT)
    if rr:
        lines += [
            "last_round_report:",
            f"  sa_focus: {rr.get('sa_focus') or rr.get('sa_id')}",
            f"  status: {rr.get('status')}",
            f"  at: {rr.get('at')}",
            f"  summary: {(rr.get('summary') or '')[:200]}",
        ]

    orch = _read_json(ORCH_STATE)
    if orch:
        lines += [
            "orchestrator:",
            f"  status: {orch.get('status')}",
            f"  expected_sa: {orch.get('expected_sa')}",
            f"  expected_role: {orch.get('expected_role')}",
            f"  last_overnight_skip: {orch.get('last_overnight_skip')}",
        ]

    receipt = ROOT / "receipts" / f"{sa_id}-receipt.json"
    if receipt.is_file():
        try:
            rec = json.loads(receipt.read_text(encoding="utf-8"))
            lines += [f"receipt_on_disk: {rec.get('status')} agent={rec.get('agent')}"]
        except (OSError, json.JSONDecodeError):
            pass

    # Last API result for this sa
    if API_RESULTS.is_dir():
        hits = sorted(API_RESULTS.glob(f"{sa_id}-*"), key=lambda p: p.stat().st_mtime, reverse=True)
        if hits:
            lines.append(f"last_api_result: {hits[0].name}")

    if CC_RESULTS.is_dir():
        cc = CC_RESULTS / f"{sa_id}-result.json"
        if cc.is_file():
            try:
                cr = json.loads(cc.read_text(encoding="utf-8"))
                lines += [
                    "last_cli_result:",
                    f"  status: {cr.get('status')}",
                    f"  cost_usd: {cr.get('cost_usd')}",
                    f"  tools: {cr.get('tool_call_count')}",
                ]
            except (OSError, json.JSONDecodeError):
                pass

    try:
        gp = __import__("subprocess").run(
            [__import__("sys").executable, str(SCRIPTS / "goal-progress-v1.py")],
            capture_output=True,
            text=True,
            timeout=8,
            cwd=str(ROOT),
        )
        if gp.stdout:
            lines.append(f"goal_progress: {gp.stdout.strip().splitlines()[0]}")
    except Exception:
        pass

    lines.append("=== END SESSION MEMORY ===")
    return "\n".join(lines)


def parse_worker_round_report(text: str) -> dict:
    """Extract worker_round_report YAML block."""
    if not text:
        return {}
    m = re.search(
        r"worker_round_report:\s*\n((?:[ \t]+[^\n]+\n?)+)",
        text,
        re.IGNORECASE,
    )
    if not m:
        return {}
    out: dict = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip().split("#")[0].strip()
    return out


def validate_report(*, report: dict, sa_id: str, role: str) -> list[str]:
    """Return violation strings; empty = ok."""
    violations: list[str] = []
    if not report:
        return ["missing_worker_round_report"]
    rep_sa = str(report.get("sa_id") or report.get("sa_focus") or "").lower()
    if rep_sa and rep_sa != sa_id.lower():
        violations.append(f"sa_id_mismatch:{rep_sa}!={sa_id}")
    rep_role = str(report.get("role") or "").lower()
    if rep_role and role.lower() not in rep_role and rep_role not in role.lower():
        violations.append(f"role_mismatch:{rep_role}!={role}")
    status = str(report.get("status") or "").upper()
    if status not in ("PASS", "FAIL", "BLOCKED"):
        violations.append(f"invalid_status:{status or 'empty'}")
    na = str(report.get("next_action") or "").lower()
    if any(x in na for x in ("ask founder", "what should", "tell me", "your choice", "?")):
        violations.append("founder_question_forbidden")
    r = role.lower()
    if "check" in r and status == "PASS" and any(x in na for x in ("implement", "build", "fix", "act on")):
        if "act" not in na and "verify" not in na:
            violations.append("check_must_not_instruct_implement")
    return violations


def persist_round_report(*, sa_id: str, role: str, report: dict, source: str) -> dict:
    """Write ~/.sina/worker_round_report_v1.json for broker/orchestrator."""
    status = str(report.get("status") or "BLOCKED").upper()
    payload = {
        "status": "WORKER_ROUND_REPORT",
        "sa_focus": sa_id,
        "sa_id": sa_id,
        "round_type": role,
        "summary": report.get("summary") or "",
        "evidence": report.get("evidence") or "",
        "gaps": report.get("gaps") or "",
        "next_action": report.get("next_action") or "NONE",
        "turn_status": status,
        "source": source,
        "at": _now(),
    }
    ROUND_REPORT.parent.mkdir(parents=True, exist_ok=True)
    ROUND_REPORT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def normalize_status(report: dict, *, fallback: str = "BLOCKED") -> str:
    s = str(report.get("status") or report.get("turn_status") or fallback).upper()
    if s in ("PASS", "FAIL", "BLOCKED"):
        return s
    return fallback
