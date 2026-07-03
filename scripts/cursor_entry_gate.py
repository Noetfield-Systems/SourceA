#!/usr/bin/env python3
"""Mechanical entry gate — hash required law files before agent replies.

Law: BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP_LOCKED_v1.md
Writes: ~/.sina/cursor_entry_gate_receipt_v1.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = Path.home() / ".sina" / "cursor_entry_gate_receipt_v1.json"


def _check_wire_age(path: Path, *, max_sec: int, label: str) -> dict:
    if not path.is_file():
        return {"ok": False, "label": label, "error": "missing"}
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
        at = str(row.get("at") or "")
        if not at:
            return {"ok": False, "label": label, "error": "no_at"}
        dt = datetime.fromisoformat(at.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - dt).total_seconds()
        return {"ok": age <= max_sec, "label": label, "age_sec": int(age), "max_sec": max_sec}
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {"ok": False, "label": label, "error": str(exc)}


ROLE_FILES: dict[str, list[str]] = {
    "brain": [
        "ACTIVE_NOW.md",
        "brain-os/laws/ACTIVE_NOW_HEARTBEAT_LOCKED_v1.md",
        "brain-os/laws/SOURCEA_EXECUTION_LAW_LOCKED_v1.md",
        "brain-os/laws/FOUNDER_BUSY_OPERATING_MODEL_LOCKED_v1.md",
        "brain-os/laws/SOURCEA_INVARIANT_GATEKEEPER_BLUEPRINT_LOCKED_v1.md",
        "brain-os/system/GOAL_HIERARCHY_LOCKED_v1.md",
        "brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md",
        "brain-os/law/entry/START_HERE_LOCKED_v1.md",
        "brain-os/law/entry/MANDATORY_READ_BY_ROLE_LOCKED_v1.md",
        "brain-os/incidents/SINA_GOAL_HIERARCHY_ENFORCEMENT_INCIDENT_LOCKED_v1.md",
        "ARCHITECT_REPORT.yaml",
        "GLOBAL_BLOCKERS.json",
        "brain-os/incidents/SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md",
        "brain-os/incidents/SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md",
        "brain-os/incidents/SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md",
        "brain-os/system/WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md",
        "brain-os/law/enforcement/BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP_LOCKED_v1.md",
        "brain-os/law/enforcement/SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md",
        "brain-os/plan-registry/SOURCEA-PRIORITY.md",
    ],
    "worker": [
        "ACTIVE_NOW.md",
        "brain-os/laws/ACTIVE_NOW_HEARTBEAT_LOCKED_v1.md",
        "brain-os/laws/SOURCEA_EXECUTION_LAW_LOCKED_v1.md",
        "brain-os/laws/FOUNDER_BUSY_OPERATING_MODEL_LOCKED_v1.md",
        "brain-os/laws/SOURCEA_INVARIANT_GATEKEEPER_BLUEPRINT_LOCKED_v1.md",
        "brain-os/system/GOAL_HIERARCHY_LOCKED_v1.md",
        "brain-os/law/entry/START_HERE_LOCKED_v1.md",
        "ARCHITECT_REPORT.yaml",
        "GLOBAL_BLOCKERS.json",
        "brain-os/incidents/SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md",
        "brain-os/law/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md",
        "brain-os/system/WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md",
        "brain-os/law/enforcement/REGISTRY_DRAIN_RAIL_LOCKED_v1.md",
        "brain-os/law/enforcement/AGENT_VERBS_SAVE_WORK_EDIT_LOCKED_v1.md",
        "brain-os/law/enforcement/WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md",
        "brain-os/law/enforcement/SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md",
        "brain-os/incidents/SINA_GOAL1_AUTORUN_BROKER_STALE_RECEIPT_INCIDENT_LOCKED_v1.md",
        "brain-os/plan-registry/SOURCEA-PRIORITY.md",
    ],
    "archive": [
        "brain-os/system/SINAAIDB_ARCHIVE_RETIREMENT_HANDOFF_LOCKED_v1.md",
        "brain-os/law/entry/START_HERE_LOCKED_v1.md",
    ],
}


def _sha8(path: Path) -> str:
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    return h[:8]


def run(role: str, *, scan_text: str = "") -> int:
    if role not in ROLE_FILES:
        print(f"GATE_FAILED unknown_role={role}", file=sys.stderr)
        return 1

    sys.path.insert(0, str(ROOT / "scripts"))
    from active_now_v1 import heartbeat  # noqa: WPS433

    hb = heartbeat(caller=f"cursor_entry_gate:{role}", task_text=scan_text)
    if not hb.get("ok") or not hb.get("heartbeat"):
        print("GATE_FAILED active_now or execution_law", file=sys.stderr)
        if hb.get("message"):
            print(hb.get("message"), file=sys.stderr)
        print(json.dumps(hb, indent=2), file=sys.stderr)
        return 1

    missing: list[str] = []
    hashes: dict[str, str] = {}
    for rel in ROLE_FILES[role]:
        p = ROOT / rel
        if not p.is_file():
            missing.append(rel)
            continue
        hashes[rel] = _sha8(p)

    if missing:
        print(f"GATE_FAILED missing={','.join(missing)}", file=sys.stderr)
        return 1

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    gate_id = f"gate-{ts.replace(':', '').replace('-', '')}-{role}"
    composite = hashlib.sha256("".join(hashes[k] for k in sorted(hashes)).encode()).hexdigest()[:8]

    founder_class = "ASF_QUESTION"
    factory_now_line = ""
    if scan_text:
        from factory_control_v1 import classify_founder_message  # noqa: WPS433

        founder_class = classify_founder_message(scan_text)
    try:
        from factory_control_v1 import format_line, load_factory_now  # noqa: WPS433

        factory_now_line = format_line(load_factory_now())
    except Exception:
        factory_now_line = "factory-now · unavailable"

    payload = {
        "gate_id": gate_id,
        "at": ts,
        "role": role,
        "workspace": str(ROOT),
        "gate_hash8": composite,
        "file_hashes": hashes,
        "founder_class": founder_class,
        "factory_now_line": factory_now_line,
        "active_now": {
            "hash8": hb.get("hash8"),
            "current_sa_id": hb.get("current_sa_id"),
            "current_goal": hb.get("current_goal"),
        },
        "reply_line1": f"GATE: {composite} | {ts} | gate_id={gate_id} | founder_class={founder_class}",
        "reply_line2": factory_now_line,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    wire_fresh: dict = {"ok": True, "skipped": True}
    sina = Path.home() / ".sina"
    if role in ("governance", "commercial", "brief"):
        wp = sina / "l1-agent-pipeline-wire-v1.json"
        wire_fresh = _check_wire_age(wp, max_sec=120, label="l1_pipeline")
        if not wire_fresh.get("ok"):
            print(f"GATE_FAILED stale {wire_fresh.get('label')}", file=sys.stderr)
            return 1
    if role in ("worker", "archive", "maintainer", "brain"):
        wp = sina / "governance-brain-wire-v1.json"
        wire_fresh = _check_wire_age(wp, max_sec=300, label="brain_wire")
        if not wire_fresh.get("ok") and role in ("worker", "brain"):
            print(f"GATE_FAILED stale {wire_fresh.get('label')}", file=sys.stderr)
            return 1
    payload["wire_freshness"] = wire_fresh
    RECEIPT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    # UI FIRST CHECK — all roles · form · app · website · hub · canvas (026 zero exception)
    ui_fc_path = sina / "ui-upgrade-first-check-receipt-v1.json"
    ui_fc_ok = False
    if ui_fc_path.is_file():
        try:
            ui_fc_row = json.loads(ui_fc_path.read_text(encoding="utf-8"))
            ui_fc_ok = bool(ui_fc_row.get("wire_ok"))
            payload["ui_upgrade_first_check"] = {
                "ok": ui_fc_ok,
                "line": (ui_fc_row.get("line") or "")[:120],
            }
        except (OSError, json.JSONDecodeError):
            payload["ui_upgrade_first_check"] = {"ok": False, "error": "parse_error"}
    else:
        payload["ui_upgrade_first_check"] = {"ok": False, "error": "receipt_missing"}
    if not ui_fc_ok:
        print("GATE_FAILED ui_upgrade_first_check wire_ok=false — run ui_upgrade_first_check_v1.py --wire", file=sys.stderr)
        RECEIPT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return 1
    RECEIPT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    from prompt_feasibility_gate import check_session  # noqa: WPS433

    feas = check_session(role=role)
    payload["prompt_feasibility"] = feas

    if founder_class == "ASF_STOP":
        print("GATE_FAILED founder_class=ASF_STOP — run stop_goal1_auto_run before any drain", file=sys.stderr)
        print(json.dumps({"founder_class": founder_class, "factory_now_line": factory_now_line}, indent=2), file=sys.stderr)
        return 1

    if role == "worker":
        from worker_turn_lib import turn_open_block, open_turn, live_pick_id  # noqa: WPS433
        from authority_enforce_p1_lib import check_prompt_pick_authority  # noqa: WPS433

        if scan_text:
            from worker_scope_guard_v1 import check_fat_request  # noqa: WPS433
            from founder_close_line_gate_v1 import scan_text as scan_close_line  # noqa: WPS433
            from founder_input_cascade_v1 import cascade_founder_input  # noqa: WPS433

            cascade = cascade_founder_input(scan_text, source=f"cursor_entry_gate:{role}")
            payload["founder_input_cascade"] = {
                "ok": cascade.get("ok"),
                "ms": cascade.get("ms"),
                "failed": (cascade.get("verify") or {}).get("failed"),
            }
            if not cascade.get("ok"):
                print("GATE_WARN founder_input_cascade incomplete — layers may be stale", file=sys.stderr)

            cl = scan_close_line(scan_text)
            if cl.get("hits"):
                print("GATE_FAILED founder_close_line INCIDENT-028", file=sys.stderr)
                print(json.dumps(cl, indent=2), file=sys.stderr)
                return 1

            fat = check_fat_request(scan_text)
            if fat:
                print(f"WORKER_FAT_TASK_BLOCKED {fat.get('reason')}", file=sys.stderr)
                print(json.dumps(fat, indent=2), file=sys.stderr)
                return 1
            breach = check_prompt_pick_authority(
                text=scan_text,
                source="composer_paste",
            )
            if not breach.get("ok"):
                print(f"AUTHORITY_BREACH {breach.get('error')}", file=sys.stderr)
                print(json.dumps(breach, indent=2), file=sys.stderr)
                return 1

        if feas.get("action") in ("STOP_INJECT",):
            print("FEASIBILITY_BLOCKED inject forbidden — OpenRouter/live-eval/impossible ACT", file=sys.stderr)
            print(json.dumps(feas, indent=2), file=sys.stderr)
            return 1
        from worker_factory_evidence_gate_v1 import run_factory_gate  # noqa: WPS433

        fg = run_factory_gate(caller="cursor_entry_gate", role="worker", require_inbox=False)
        if not fg.get("ok"):
            print("WORKER_FACTORY_GATE_BLOCKED", file=sys.stderr)
            print(json.dumps(fg, indent=2), file=sys.stderr)
            return 1
        try:
            wg = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "worker_execution_gate_v1.py"),
                 "--role", "worker", "--task", scan_text[:200] if scan_text else "worker-entry",
                 "--skip-session", "--json"],
                cwd=str(ROOT), capture_output=True, text=True, timeout=120,
            )
            if wg.returncode != 0:
                print("WORKER_EXECUTION_GATE_BLOCKED", file=sys.stderr)
                print(wg.stdout or wg.stderr, file=sys.stderr)
                return 1
        except (subprocess.TimeoutExpired, OSError) as exc:
            print(f"WORKER_EXECUTION_GATE_ERROR {exc}", file=sys.stderr)
            return 1
        from worker_inject_lib import inbox_status  # noqa: WPS433

        inbox = inbox_status()
        if inbox.get("pending"):
            sa = str((inbox.get("meta") or {}).get("sa_id") or inbox.get("sa_id") or "")
            if sa.startswith("sa-") and sa not in ("sa-TEST",):
                block = turn_open_block()
                if block and str(block.get("open_sa") or "") != sa:
                    print(f"WORKER_TURN_BLOCKED {block.get('error')}", file=sys.stderr)
                    return 1
                open_turn(sa_id=sa, path=str(ROOT / ".sina-loop/INBOX.md"))
    elif role == "brain" and feas.get("blocked_count"):
        print("FEASIBILITY_WARN live_pick or queue blocked — fix before Worker inject", file=sys.stderr)
        print(json.dumps(feas, indent=2), file=sys.stderr)

    print("CURSOR_ENTRY_GATE ok")
    if feas.get("feasible"):
        print("FEASIBILITY_CHECK ok")
    else:
        print(f"FEASIBILITY_CHECK blocked count={feas.get('blocked_count')}")
    print(payload["reply_line1"])
    if payload.get("reply_line2"):
        print(payload["reply_line2"])
    print(f"GATE_RECEIPT={RECEIPT}")
    print(json.dumps(payload))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Cursor entry gate — disk hash before reply")
    p.add_argument("--role", choices=sorted(ROLE_FILES), default="brain")
    p.add_argument(
        "--scan-text",
        default="",
        help="Worker only: scan composer paste for advisor pick-breach patterns",
    )
    args = p.parse_args()
    return run(args.role, scan_text=args.scan_text or "")


if __name__ == "__main__":
    raise SystemExit(main())
