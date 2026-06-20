#!/usr/bin/env python3
"""Judge Loop Room — verdict on loop health · route REPORT to specialists.

Law: docs/SOURCEA_INVESTIGATOR_JUDGE_LOOP_ROOM_LOCKED_v1.md
Receipt: ~/.sina/judge-loop/latest-verdict-v1.json
Complements judge_center_bench (chat) — this judges loop receipts only.
execution_authority: false
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
JUDGE_LOOP_DIR = SINA / "judge-loop"
RECEIPT = JUDGE_LOOP_DIR / "latest-verdict-v1.json"
INVESTIGATION = SINA / "loop-health-investigation-receipt-v1.json"
LOOP_VERDICTS = frozenset(
    {"LOOP_HEALTHY", "LOOP_DEGRADED", "DISPATCH_BLOCKED", "PROMPT_STALE"}
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _loop_verdict(
    *,
    investigation: dict,
    specialist: dict,
    obs: dict,
) -> str:
    inv_v = str(investigation.get("investigation_verdict") or "YELLOW")
    tick = str(specialist.get("tick_decision") or "")
    freeze = obs.get("freeze") or {}

    if freeze.get("prompt_blocked_by_freeze") or tick == "compose_blocked":
        return "DISPATCH_BLOCKED"
    if inv_v == "RED":
        return "LOOP_DEGRADED"
    blockers = specialist.get("block_reasons") or []
    if "auto_dispatch_disabled" in blockers and int(
        (obs.get("commercial") or {}).get("commercial_red_count") or 0
    ) > 0:
        return "PROMPT_STALE"
    if inv_v == "YELLOW":
        return "LOOP_DEGRADED"
    if tick in ("observe_only", "dispatch_ready", "dispatch_done", "idle"):
        return "LOOP_HEALTHY"
    return "LOOP_DEGRADED"


def _specialist_reports(*, investigation: dict, loop_verdict: str) -> list[dict]:
    reports: list[dict] = []
    for route in investigation.get("specialist_routes") or []:
        action = "ACT_SUGGEST" if loop_verdict == "DISPATCH_BLOCKED" and route.get(
            "id"
        ) == "freeze_block" else str(route.get("action") or "REPORT")
        reports.append(
            {
                "route_id": route.get("id"),
                "specialist": route.get("primary"),
                "specialist_label": route.get("primary_label"),
                "action": action,
                "counsel": "KEEP",
                "message": f"{loop_verdict}: {route.get('signal')}",
            }
        )
    if not reports and loop_verdict == "LOOP_HEALTHY":
        reports.append(
            {
                "route_id": "loop_ok",
                "specialist": "loop_specialist",
                "specialist_label": "Loop Specialist",
                "action": "INSIGHT",
                "counsel": "KEEP",
                "message": "Loop healthy — advisory ranks next prompts",
            }
        )
    return reports


def _judge_line(*, loop_verdict: str, investigation: dict, specialist: dict) -> str:
    inv = investigation.get("investigation_verdict") or "?"
    tick = specialist.get("tick_decision") or "?"
    routes = len(investigation.get("specialist_routes") or [])
    return f"judge-loop · {loop_verdict} · inv={inv} · tick={tick} · routes={routes}"


def run_judge_loop(*, write: bool = True) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    investigation = _read_json(INVESTIGATION)
    if not investigation or investigation.get("schema") != "loop-health-investigation-receipt-v1":
        try:
            from investigator_circle_run_v1 import run_investigation  # noqa: WPS433

            investigation = run_investigation(write=True)
        except Exception as exc:
            investigation = {"schema": "loop-health-investigation-receipt-v1", "error": str(exc)}

    specialist = _read_json(SINA / "loop-specialist-tick-receipt-v1.json")
    advisory = _read_json(SINA / "future-loop-prompt-advisory-v1.json")
    obs = _read_json(SINA / "loop-observatory-report-v1.json")
    chat_judge = _read_json(SINA / "judge-center" / "latest-resolution-v1.json")

    loop_verdict = _loop_verdict(investigation=investigation, specialist=specialist, obs=obs)
    reports = _specialist_reports(investigation=investigation, loop_verdict=loop_verdict)

    escalations: list[str] = []
    if loop_verdict == "DISPATCH_BLOCKED":
        escalations.append((obs.get("freeze") or {}).get("action") or "ASF: resume drain")
    if investigation.get("investigation_verdict") == "RED":
        escalations.append("Run hospital pipeline or find_critical_bugs owner")

    row = {
        "schema": "judge-loop-verdict-v1",
        "ok": loop_verdict in LOOP_VERDICTS,
        "at": _now(),
        "execution_authority": False,
        "loop_verdict": loop_verdict,
        "investigation_verdict": investigation.get("investigation_verdict"),
        "investigation_hash": investigation.get("deterministic_hash"),
        "advisory_hash": advisory.get("deterministic_hash"),
        "tick_decision": specialist.get("tick_decision"),
        "specialist_reports": reports,
        "escalations": escalations,
        "chat_judge_case_id": chat_judge.get("case_id"),
        "insights": investigation.get("insights") or [],
        "suggested_heals": investigation.get("suggested_heals") or [],
        "judge_loop_line": "",
        "command": "python3 scripts/judge_loop_room_v1.py --json",
        "hub_api": "POST /api/judge-loop/tick/v1",
    }
    row["judge_loop_line"] = _judge_line(
        loop_verdict=loop_verdict,
        investigation=investigation,
        specialist=specialist,
    )
    if write:
        JUDGE_LOOP_DIR.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def hub_slice() -> dict:
    row = _read_json(RECEIPT)
    if not row or row.get("schema") != "judge-loop-verdict-v1":
        row = run_judge_loop(write=True)
    return {
        "schema": "worker-hub-judge-room-v1",
        "ok": row.get("ok"),
        "at": row.get("at"),
        "loop_verdict": row.get("loop_verdict"),
        "judge_loop_line": row.get("judge_loop_line"),
        "specialist_reports": row.get("specialist_reports") or [],
        "escalations": row.get("escalations") or [],
        "hub_api": "POST /api/judge-loop/tick/v1",
    }


def handle_hub_post(body: dict | None = None) -> dict:
    return run_judge_loop(write=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Judge Loop Room verdict")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--hub-slice", action="store_true")
    args = ap.parse_args()
    if args.hub_slice:
        row = hub_slice()
    else:
        row = run_judge_loop(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("judge_loop_line") or row.get("loop_verdict"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
