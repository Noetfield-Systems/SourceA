#!/usr/bin/env python3
"""Worker 1 unified pack — 40 prompts (20 sa + 20 autoloop).

Law: brain-os/contract/WORKER_PROMPT_PACK_FORMAT_LOCKED_v1.md (v1.1)
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "brain-os/plan-registry/worker-dual-40"
LAW = "brain-os/contract/WORKER_PROMPT_PACK_FORMAT_LOCKED_v1.md"
LOCK = "brain-os/plan-registry/WORKER-DUAL-40-LOCK.md"
TAG_LAW = "brain-os/contract/DOC_TRACE_TAG_FORMAT_LOCKED_v1.md"
AGENT = "Auto"
TRACE_REGISTRY = "AUTO-TRACE-WORKER-W1-REGISTRY-v1.3"
TRACE_QUEUE = "AUTO-TRACE-WORKER-W1-QUEUE-v1.3"
PROMPT_ROOT = ROOT / "brain-os/plan-registry/sourcea-1000/prompts/phase-s1-eval-dispatch/T1"
WORKER1_QUEUE = ROOT / ".sina-loop/WORKER-1-PASTE-QUEUE.md"

SA_BAND = [f"sa-{i:04d}" for i in range(131, 151)]

AUTOLOOP_TASKS = [
    "prepare-only goal1_auto_loop_v1.py --turns 1 --json; validate-goal1-auto-loop-v1.sh + activation-chain PASS",
    "Hub AUTO-RUN 10; Worker composer empty; verify last 10 AGENT DONE exit=0 broker=yes (10/10 gate)",
    "Fix broker=no sa_mismatch: sa_focus = INBOX meta sa_id; goal1_lane_broker stdin parse check",
    "stop_goal1_loop_v1.py after 3× broker=no; clear stale batch tail hygiene",
    "brain_validate_goal1_v1.py --json chain PASS; worker_inject_lib --clear after worker-submit",
    "Compare worker-prompt-inbox-v1.json vs healthy-queue-state — drift report only",
    "Orchestrator deliver_current when not awaiting_worker; advance-healthy-queue only after VERIFY",
    "Count broker=yes baseline+delta; one_sa_per_turn_gate on last WORKER_ROUND_REPORT",
    "AUTO-RUN 10 batch #2 after 10/10 (scale toward 50 cumulative); no manual paste during lock",
    "Autoloop receipt: 10/10 broker=yes or one-line blocker",
    "validate-goal1-loop-activation-chain-v1.sh PASS end-to-end",
    "WORKER_ROUND_REPORT yaml parsed by goal1_lane_broker worker-submit",
    "one_sa_per_turn_gate_v1 PASS on last round report; close stale worker_turn_state if blocked",
    "Headless turn: agent -p -f output brokered without composer paste",
    "Reject activate skip: INBOX delivered must chain to broker=yes or honest blocker",
    "Orchestrator poll_once after turn — status honest in receipt",
    "Clear stale goal1-worker-batch broker=no tail (hygiene only)",
    "closeout_sa_task.py mark_done only on VERIFY machine PASS",
    "advance-healthy-queue-v1.py only after Worker round report closed",
    "Activation chain receipt — inject/validate/activate/sync all PASS; scale AUTO-RUN toward 50",
]

E2E_3 = (
    "PLUS E2E-3 GATE: full E2E on last 3 turns — validate-execution-spine-v1.sh PASS, "
    "implement+verify+fix any gap, search missing wiring/docs/receipts, find_critical_bugs critical 0 before closeout."
)

DEBUG_5_SA = (
    "PLUS DEBUG-5 GATE: full debug sweep — brain_validate_goal1_v1.py --json, "
    "validate-goal1-loop-activation-chain-v1.sh, validate-eval-packet-v1b-live.sh, "
    "hub Refresh/sync state (13020), worker-prompt-inbox vs healthy-queue drift fix, "
    "orchestrator deliver + runtime hygiene; fix all before closeout."
)

DEBUG_5_LOOP = (
    "PLUS DEBUG-5 GATE: full autoloop debug — validate-goal1-auto-loop-v1.sh, "
    "validate-goal1-loop-activation-chain-v1.sh, brain_validate_goal1_v1.py --json, "
    "hub health 13020 + batch log tail, inbox/queue drift fix, stop/restart hygiene if broker=no streak; fix all before closeout."
)

FORBIDDEN_PASTE_MARKERS = (
    "CHECK ONLY",
    "ACT ONLY",
    "VERIFY+closeout",
    "wait STOP before next",
    "NEW WORKER",
    "OLD WORKER",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _gate_labels(pos: int) -> list[str]:
    gates: list[str] = []
    if pos % 3 == 0:
        gates.append("E2E-3")
    if pos % 5 == 0:
        gates.append("DEBUG-5")
    return gates


def _gate_clauses(pos: int, *, loop: bool) -> str:
    parts: list[str] = []
    if pos % 3 == 0:
        parts.append(E2E_3)
    if pos % 5 == 0:
        parts.append(DEBUG_5_LOOP if loop else DEBUG_5_SA)
    return " ".join(parts)


def _sa_title(sa: str) -> str:
    path = PROMPT_ROOT / f"{sa}.md"
    if not path.exists():
        return sa
    m = re.search(r"— (.+)$", path.read_text(encoding="utf-8").split("\n", 25)[16])
    return m.group(1).strip() if m else sa


def _sa_prompt(sa: str, title: str, pos: int, wid: str) -> str:
    rel = f"brain-os/plan-registry/sourcea-1000/prompts/phase-s1-eval-dispatch/T1/{sa}.md"
    suffix = f" {_gate_clauses(pos, loop=False)}" if _gate_clauses(pos, loop=False) else ""
    return (
        f"PLAN WITH NO ASF — WORKER 1 {sa} ONE TURN ({wid}). Task: {title}. "
        f"Read {rel} + session-start + spine + find_critical_bugs. "
        f"Implement gaps minimal diff. Verify inside same turn: validate-eval-packet-v1b-live.sh + "
        f"find_critical_bugs critical 0 + mark_done + PRIORITY row.{suffix} "
        f"WORKER_ROUND_REPORT → broker submit. One sa end-to-end — no separate CHECK/ACT/VERIFY pastes."
    )


def _loop_prompt(task: str, pos: int, wid: str) -> str:
    suffix = f" {_gate_clauses(pos, loop=True)}" if _gate_clauses(pos, loop=True) else ""
    return (
        f"PLAN WITH NO ASF — WORKER 1 autoloop ONE TURN ({wid}): {task}.{suffix} "
        f"Loop A only — fix broker/autoloop; REGISTRY implement only if broker fix requires. "
        f"WORKER_ROUND_REPORT → broker submit."
    )


def _validate_plans(plans: list[dict]) -> None:
    for plan in plans:
        pos = plan["position"]
        if plan.get("gates") != _gate_labels(pos):
            raise ValueError(f"{plan['id']}: gate mismatch")
        if any(m in plan["prompt"] for m in FORBIDDEN_PASTE_MARKERS):
            raise ValueError(f"{plan['id']}: forbidden marker")
        for gate in plan.get("gates", []):
            if gate == "E2E-3" and "PLUS E2E-3 GATE" not in plan["prompt"]:
                raise ValueError(f"{plan['id']}: missing E2E-3")
            if gate == "DEBUG-5" and "PLUS DEBUG-5 GATE" not in plan["prompt"]:
                raise ValueError(f"{plan['id']}: missing DEBUG-5")
        if plan.get("kind") == "sa":
            if "Verify inside same turn" not in plan["prompt"]:
                raise ValueError(f"{plan['id']}: sa must verify inside turn")


def _gate_suffix(gates: list[str]) -> str:
    return "task only" if not gates else " + ".join(gates)


def _write_worker1_queue(plans: list[dict]) -> None:
    lines = [
        "# Worker 1 — unified paste queue (w1-01 → w1-40)",
        "",
        f"**trace_tag:** `{TRACE_QUEUE}`",
        f"**agent:** `{AGENT}`",
        "",
        "**Worker 1 unified.** One Cursor window · one paste = one full turn · Rail A AUTO-RUN default.",
        "",
        f"**Law:** `{LAW}` · `{LOCK}`",
        "",
        "## Block A — REGISTRY sa (w1-01 → w1-20)",
        "",
        "| ID | Gate | sa |",
        "|----|------|-----|",
    ]
    for p in plans[:20]:
        lines.append(f"| {p['id']} | {_gate_suffix(p.get('gates', []))} | {p.get('sa_id', '')} |")
    lines.extend(
        [
            "",
            "## Block B — Loop A autoloop (w1-21 → w1-40)",
            "",
            "| ID | Gate |",
            "|----|------|",
        ]
    )
    for p in plans[20:]:
        lines.append(f"| {p['id']} | {_gate_suffix(p.get('gates', []))} |")
    lines.extend(["", "---", ""])

    for p in plans:
        gate = f" · {_gate_suffix(p.get('gates', []))}" if p.get("gates") else ""
        if p.get("kind") == "sa":
            h = f"## {p['id']} — {p['sa_id']}{gate}"
        else:
            h = f"## {p['id']}{gate} · {p['title'][:70]}"
        lines.extend([h, "", "```", p["prompt"], "```", "", "---", ""])

    WORKER1_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    WORKER1_QUEUE.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    PACK.mkdir(parents=True, exist_ok=True)
    plans: list[dict] = []

    for i, sa in enumerate(SA_BAND, start=1):
        wid = f"w1-{i:02d}"
        plans.append(
            {
                "id": wid,
                "worker": 1,
                "kind": "sa",
                "sa_id": sa,
                "position": i,
                "gates": _gate_labels(i),
                "title": _sa_title(sa)[:100],
                "prompt": _sa_prompt(sa, _sa_title(sa), i, wid),
                "status": existing.get(wid, "backlog"),
            }
        )

    for j, task in enumerate(AUTOLOOP_TASKS, start=1):
        pos = 20 + j
        wid = f"w1-{pos:02d}"
        plans.append(
            {
                "id": wid,
                "worker": 1,
                "kind": "autoloop",
                "position": pos,
                "gates": _gate_labels(pos),
                "title": task[:100],
                "prompt": _loop_prompt(task, pos, wid),
                "status": existing.get(wid, "backlog"),
            }
        )

    _validate_plans(plans)

    existing: dict[str, str] = {}
    reg_path = PACK / "REGISTRY.json"
    if reg_path.is_file():
        for row in json.loads(reg_path.read_text(encoding="utf-8")).get("plans") or []:
            if row.get("id") and row.get("status"):
                existing[row["id"]] = row["status"]

    reg = {
        "trace_tag": TRACE_REGISTRY,
        "agent": AGENT,
        "tag_law": TAG_LAW,
        "schema": "worker-1-unified.v1.3",
        "locked": True,
        "worker_1_only": True,
        "count": 40,
        "sa_block": "w1-01..w1-20",
        "autoloop_block": "w1-21..w1-40",
        "gate_law": {"every_3": "E2E-3", "every_5": "DEBUG-5"},
        "generated_at": _now(),
        "law": LAW,
        "paste_queue": ".sina-loop/WORKER-1-PASTE-QUEUE.md",
        "usage": "Worker 1 only. Rail A: Hub AUTO-RUN. Manual fallback: paste w1-* in order.",
        "plans": plans,
    }
    (PACK / "REGISTRY.json").write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
    _write_worker1_queue(plans)

    print(f"OK: Worker 1 unified · 40 prompts · w1-01..w1-40")
    print(f"    {WORKER1_QUEUE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
