#!/usr/bin/env python3
"""Agentic conduct gate — INCIDENT-026/027 machine limits for Cursor agents.

Law: SOURCEA_AGENTIC_ENFORCEMENT_STACK_LOCKED_v2.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from governance_paths_v1 import AUTHORITY_INDEX, COMMERCIAL_SSOT, GOVERNANCE_ENTRY, NO_FAKE_PROGRESS
SINA = Path.home() / ".sina"

FORBIDDEN_SHELLS = frozenset(
    {
        "build-sina-command-panel.py",
        "validate-anti-staleness-bundle-v1.sh",
        "validate-sourcea-e2e-full-v1.sh",
        "validate-sourcea-e2e-standard-v1.sh",
        "validate-live-prompt-feed-e2e-v1.sh",
    }
)

BRAIN_FORBIDDEN = frozenset(
    {
        "build-sina-command-panel.py",
        "validate-anti-staleness-bundle-v1.sh",
        "validate-sourcea-e2e-full-v1.sh",
        "validate-sourcea-e2e-standard-v1.sh",
        "validate-e2e-fast-ladder-v1.sh",
        "validate-live-prompt-feed-e2e-v1.sh",
    }
)

READ_ORDER = [
    ("form_json", SINA / "live-founder-decision-form-v1.json"),
    ("commercial_ssot", COMMERCIAL_SSOT),
    ("governance_entry", GOVERNANCE_ENTRY),
    ("program_progress", ROOT / "PROGRAM_PROGRESS.json"),
]

ROLE_LIMITS = {
    "brain": {"max_shell_seconds": 90, "max_reply_seconds": 30},
    "governance": {"max_shell_seconds": 120, "max_reply_seconds": 60},
    "worker": {"max_shell_seconds": 300, "max_reply_seconds": 45},
    "any": {"max_shell_seconds": 120, "max_reply_seconds": 60},
}


def _load_brain_forbidden() -> list[str]:
    p = SINA / "brain-current-action-v1.json"
    if not p.is_file():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    out: list[str] = []
    for key in ("forbidden_commands", "forbidden_brain_e2e"):
        val = data.get(key)
        if isinstance(val, str) and val:
            out.append(val)
        elif isinstance(val, list):
            out.extend(str(x) for x in val)
    intent = data.get("brain_intent") or {}
    fc = intent.get("forbidden_commands")
    if isinstance(fc, list):
        out.extend(str(x) for x in fc)
    return out


def evaluate(*, role: str = "any", task_text: str = "") -> dict:
    warnings: list[str] = []
    violations: list[str] = []
    role = role if role in ROLE_LIMITS else "any"
    limits = ROLE_LIMITS[role]

    # Read order presence
    read_order_ok = True
    missing_reads: list[str] = []
    for name, path in READ_ORDER:
        if not path.is_file():
            missing_reads.append(name)
            read_order_ok = False
    if missing_reads and role in ("governance", "brain"):
        warnings.append(f"read_order_missing:{','.join(missing_reads)}")

    # Task text scan
    task_lower = (task_text or "").lower()
    forbidden_set = BRAIN_FORBIDDEN if role == "brain" else FORBIDDEN_SHELLS
    for frag in forbidden_set:
        if frag in task_lower:
            msg = f"forbidden_shell:{frag}"
            if role == "brain":
                violations.append(msg)
            else:
                warnings.append(msg)

    if "&&" in task_text and task_text.count("validate-") >= 2:
        warnings.append("validator_chain_pattern:&&")

    # MAC LAW machine enforce — forbidden shell / Mac-body work (031)
    if task_text.strip():
        try:
            from mac_law_machine_enforce_v1 import scan_agent_text  # noqa: WPS433

            ml = scan_agent_text(task_text)
            for hit in ml.get("hits") or []:
                hid = hit.get("id") or "mac_law"
                because = str(hit.get("because") or "")[:96]
                violations.append(f"mac_law_machine:{hid}:{because}")
        except Exception as exc:
            warnings.append(f"mac_law_machine_scan_error:{exc}")

    if "g7" in task_lower and "--heal" in task_lower and "--scan" not in task_lower:
        warnings.append("g7_heal_without_scan")

    # Founder close-line (INCIDENT-028 — fail-closed on operator instructions)
    if task_text.strip():
        try:
            from founder_close_line_gate_v1 import scan_text as scan_close_line  # noqa: WPS433

            cl = scan_close_line(task_text)
            for hit in cl.get("hits") or []:
                violations.append(f"founder_close_line:{hit['id']}:{hit['label']}")
        except Exception as exc:
            warnings.append(f"founder_close_line_scan_error:{exc}")

    brain_disk = _load_brain_forbidden()
    for frag in brain_disk:
        if frag and frag in task_lower and role == "brain":
            violations.append(f"brain_disk_forbidden:{frag}")

    # UI FIRST CHECK — no UI edit without ack (026 zero-exception law)
    if task_text.strip() and role in ("brain", "worker", "governance", "maintainer", "any"):
        ui_markers = (
            ".html",
            ".css",
            ".js",
            ".tsx",
            ".jsx",
            ".vue",
            "index.html",
            "form/index",
            "worker-hub",
            "canvas.tsx",
            "redesign",
            "polish ui",
            "upgrade ui",
            "hub form",
        )
        ack_markers = (
            "ui_upgrade_first_check",
            "first check",
            "first_check",
            "--ack",
            "ui-upgrade-first-check",
            "up-0",
            "up checklist",
            "ui upgrade:",
            "up checklist:",
        )
        if any(m in task_lower for m in ui_markers):
            if not any(m in task_lower for m in ack_markers):
                violations.append("ui_edit_without_first_check:run classifier + --ack before any UI edit")

    # NO INVITATION — founder-no-agent-invitation flag (stable system · guards only)
    no_invite_flag = SINA / "founder-no-agent-invitation-v1.flag"
    if task_text.strip() and no_invite_flag.is_file():
        invite_markers = (
            "one next tap",
            "hard refresh",
            "submit when ready",
            "tap here",
            "open http://",
            "visit http://",
            "go to http://",
        )
        if any(m in task_lower for m in invite_markers):
            violations.append("founder_invitation_forbidden:no invitation in agent output — guards only")

    # ZERO UI DRIFT — founder-zero-ui-drift flag (no tolerance for skip/downgrade)
    zero_drift_flag = SINA / "founder-zero-ui-drift-v1.flag"
    if task_text.strip() and zero_drift_flag.is_file():
        drift_markers = (
            "skip first check",
            "skip ui check",
            "without ledger",
            "ui drift ok",
            "downgrade ui",
            "ignore baseline",
            "bypass pre_write",
            "no ack needed",
        )
        if any(m in task_lower for m in drift_markers):
            violations.append("ui_zero_drift_forbidden:no UI drift · no upgrade drift — FIRST CHECK mandatory")

    # CLOUD COMPREHENSION BAY — Hub POST → Railway FBE (030) · no Mac validators
    if task_text.strip():
        try:
            from cloud_comprehension_bay_client_v1 import analyze_via_cloud  # noqa: WPS433

            comp = analyze_via_cloud(
                draft=task_text,
                founder_message=task_lower[:500],
                write_receipt=False,
            )
            if not comp.get("ok"):
                fa = comp.get("for_agent") or {}
                inst = str(fa.get("instruction") or "Rewrite in plain English for the founder.")
                violations.append(f"comprehension_cloud:BLOCKED:{inst[:96]}")
        except Exception as exc:
            warnings.append(f"comprehension_cloud_bay_error:{exc}")

    # MAIN PROBLEM — PREPARE not report when flag active (029)
    mp_flag = SINA / "main-problem-trigger-active-v1.flag"
    if mp_flag.is_file() and task_text.strip():
        words = len(task_text.split())
        has_work = "python3 scripts/" in task_text or "receipts/" in task_text
        report_markers = ("## summary", "test plan", "validator dump", "all pass", "todo list")
        tl = task_text.lower()
        if words > 120 and not has_work:
            violations.append("main_problem_report_theater:PREPARE mode active — execute next_action not long report")
        elif any(m in tl for m in report_markers) and not has_work:
            warnings.append("main_problem_prepare_hint:short reply · execute next_action from receipt")

    # G7 receipt freshness hint
    g7_receipt = SINA / "governance-self-heal-receipt-v1.json"
    g7_hint = g7_receipt.is_file()

    ok = len(violations) == 0
    return {
        "schema": "agentic-conduct-gate-v1",
        "ok": ok,
        "role": role,
        "limits": limits,
        "read_order_ok": read_order_ok,
        "missing_reads": missing_reads,
        "warnings": warnings,
        "violations": violations,
        "forbidden_shells": sorted(forbidden_set),
        "law": "SOURCEA_AGENTIC_ENFORCEMENT_STACK_LOCKED_v2.md",
        "g7_receipt_present": g7_hint,
        "incidents": ["026", "027", "028", "016", "037"],
        "ui_first_check_mandatory": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Agentic conduct gate v1")
    ap.add_argument("--role", default="any", choices=["any", "brain", "worker", "governance", "archive"])
    ap.add_argument("--task-text", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = evaluate(role=args.role, task_text=args.task_text or "")
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"CONDUCT ok={result['ok']} warnings={len(result['warnings'])} violations={len(result['violations'])}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
