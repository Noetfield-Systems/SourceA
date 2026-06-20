#!/usr/bin/env python3
"""Mechanical entry gate — hash required law files before agent replies.

Law: BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP_LOCKED_v1.md
Writes: ~/.sina/cursor_entry_gate_receipt_v1.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # SourceA root
RECEIPT = Path.home() / ".sina" / "cursor_entry_gate_receipt_v1.json"

ROLE_FILES: dict[str, list[str]] = {
    "brain": [
        "brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md",
        "brain-os/entry/START_HERE_LOCKED_v1.md",
        "brain-os/entry/MANDATORY_READ_BY_ROLE_LOCKED_v1.md",
        "ARCHITECT_REPORT.yaml",
        "GLOBAL_BLOCKERS.json",
        "brain-os/incidents/SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md",
        "brain-os/incidents/SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md",
        "brain-os/system/WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md",
        "brain-os/enforcement/BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP_LOCKED_v1.md",
        "brain-os/plan-registry/SOURCEA-PRIORITY.md",
    ],
    "worker": [
        "brain-os/entry/START_HERE_LOCKED_v1.md",
        "ARCHITECT_REPORT.yaml",
        "GLOBAL_BLOCKERS.json",
        "brain-os/incidents/SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md",
        "brain-os/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md",
        "brain-os/system/WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md",
        "brain-os/enforcement/REGISTRY_DRAIN_RAIL_LOCKED_v1.md",
        "brain-os/plan-registry/SOURCEA-PRIORITY.md",
    ],
    "archive": [
        "brain-os/system/SINAAIDB_ARCHIVE_RETIREMENT_HANDOFF_LOCKED_v1.md",
        "brain-os/entry/START_HERE_LOCKED_v1.md",
    ],
}


def _sha8(path: Path) -> str:
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    return h[:8]


def run(role: str) -> int:
    if role not in ROLE_FILES:
        print(f"GATE_FAILED unknown_role={role}", file=sys.stderr)
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

    payload = {
        "gate_id": gate_id,
        "at": ts,
        "role": role,
        "workspace": str(ROOT),
        "gate_hash8": composite,
        "file_hashes": hashes,
        "reply_line1": f"GATE: {composite} | {ts} | gate_id={gate_id}",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    from prompt_feasibility_gate import check_session  # noqa: WPS433

    feas = check_session(role=role)
    payload["prompt_feasibility"] = feas

    if role == "worker":
        from worker_turn_lib import turn_open_block, open_turn, live_pick_id  # noqa: WPS433

        block = turn_open_block()
        if block:
            print(f"WORKER_TURN_BLOCKED {block.get('error')}", file=sys.stderr)
            return 1
        if feas.get("action") in ("STOP_INJECT",):
            print("FEASIBILITY_BLOCKED inject forbidden — OpenRouter/live-eval/impossible ACT", file=sys.stderr)
            print(json.dumps(feas, indent=2), file=sys.stderr)
            return 1
        from worker_inject_lib import inbox_status  # noqa: WPS433

        inbox = inbox_status()
        if inbox.get("pending"):
            sa = str((inbox.get("meta") or {}).get("sa_id") or "")
            if sa.startswith("sa-"):
                open_turn(sa_id=sa, path=str(ROOT / ".sina-loop/INBOX.md"))
        else:
            sa = live_pick_id()
            if sa:
                open_turn(sa_id=sa)
    elif role == "brain" and feas.get("blocked_count"):
        print("FEASIBILITY_WARN live_pick or queue blocked — fix before Worker inject", file=sys.stderr)
        print(json.dumps(feas, indent=2), file=sys.stderr)

    print("CURSOR_ENTRY_GATE ok")
    if feas.get("feasible"):
        print("FEASIBILITY_CHECK ok")
    else:
        print(f"FEASIBILITY_CHECK blocked count={feas.get('blocked_count')}")
    print(payload["reply_line1"])
    print(f"GATE_RECEIPT={RECEIPT}")
    print(json.dumps(payload))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Cursor entry gate — disk hash before reply")
    p.add_argument("--role", choices=sorted(ROLE_FILES), default="brain")
    args = p.parse_args()
    return run(args.role)


if __name__ == "__main__":
    raise SystemExit(main())
