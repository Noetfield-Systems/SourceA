#!/usr/bin/env python3
"""Generate automation-fast-track-100 — unique Musk prompts, zero duplication."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "brain-os" / "plan-registry" / "automation-fast-track-100"
PROMPTS = PACK / "prompts"
AGENT = "AGENT-AUTO-SOURCEA"
TAG = "AGENT-AUTO-SOURCEA"
PROGRAM = "brain-os/contract/AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md"

VERIFY = "cd scripts && python3 brain_validate_goal1_v1.py --json && python3 find_critical_bugs.py"

# 10 phases × 10 UNIQUE tasks — no tier mirrors, no variants
PHASES: list[tuple[str, str, list[str]]] = [
    (
        "phase-ft1-loop-a",
        "Headless Loop A — use existing daemon, no new files",
        [
            "Run goal1_auto_loop_v1.py --prepare-only --turns 1 --json; confirm deliver ok",
            "Hub path only: founder never runs Terminal — document in receipt",
            "Run validate-goal1-auto-loop-v1.sh — must PASS before AUTO-RUN 50",
            "Spawn goal1_auto_loop --turns 50 detached; Worker chat stays empty",
            "Fix broker=no: sa_focus in YAML must match INBOX meta sa_id",
            "Stop loop after 3 consecutive broker=no via stop_goal1_loop_v1.py",
            "Count broker=yes in goal1-worker-batch-latest.log — target 50 streak",
            "brain_validate inject/validate/activate/sync all PASS after batch",
            "worker_inject_lib --clear after worker-submit; no manual paste when pending",
            "Report inbox JSON vs healthy-queue-state drift only — no implement",
        ],
    ),
    (
        "phase-ft2-activate-chain",
        "inject → validate → activate → sync — mechanical only",
        [
            "validate-goal1-loop-activation-chain-v1.sh PASS end-to-end",
            "WORKER_ROUND_REPORT yaml parsed by goal1_lane_broker worker-submit",
            "one_sa_per_turn_gate_v1 PASS on last round report",
            "Headless turn: agent -p -f output brokered without composer paste",
            "Reject: INBOX delivered but activate step skipped",
            "Orchestrator poll_once after turn — status honest in receipt",
            "Clear stale goal1-worker-batch broker=no tail (hygiene only)",
            "closeout_sa_task.py mark_done only on VERIFY machine PASS",
            "advance-healthy-queue-v1.py only after Worker STOP",
            "Activation chain receipt — no new architecture",
        ],
    ),
    (
        "phase-ft3-dispatch-l2",
        "eval green + dispatch_ready founder unlock",
        [
            "validate-dispatch-policy-v1.sh — eval_1b_gate_ok honest true",
            "validate-eval-packet-v1b-live.sh — live pilots ≥80%",
            "Confirm dispatch_ready=false in code — no bypass until founder confirm",
            "Document founder Hub one-tap for dispatch_ready=true",
            "After founder confirm: re-run validate-dispatch-policy until PASS",
            "graph_executor gate receipts match dispatch_policy eval bit",
            "validate-dispatch-ready-lock-v1.sh PASS",
            "Hub /api/dispatch-policy-v1 matches policy_engine payload",
            "SOURCEA-PRIORITY one row: L2 dispatch unlock",
            "L2 ceiling receipt — forbidden L3 claim while dispatch_ready false",
        ],
    ),
    (
        "phase-ft4-s1-drain",
        "phase-first pick 1 — max throughput, one rail",
        [
            "plan-no-asf-run.sh pick 1 — trust script not chat memory",
            "Drain current LIVE_PICK sa end-to-end CHECK/ACT/VERIFY",
            "goal-progress s1 backlog delta — report only",
            "Forbidden: healthy pack parallel rail during Phase 1",
            "Forbidden: pick 30 or unattended batch",
            "find_critical_bugs critical 0 at VERIFY closeout",
            "Skip REGISTRY done sa — no replay",
            "validate-sourcea-pick-order-v1.py PASS",
            "One PRIORITY evidence row on VERIFY only",
            "s1 backlog < 40 gate check from goal-progress-v1.py",
        ],
    ),
    (
        "phase-ft5-loop-b",
        "SinaPromptOS — m5 verified sync only",
        [
            "Read SinaPromptOS config — auto_sync_plan current value",
            "Enable auto_sync_plan ONLY via m5_sync verified-only path",
            "Prove plan.json not mutated without verify_passed",
            "dispatch-day.sh writes queue file — no clipboard paste",
            "Document single daily scheduler trigger (launchd or cron)",
            "7-day log: dispatch ran without founder trigger",
            "Loop A stays green while Loop B test runs",
            "SOURCEA-PRIORITY one row: Loop B unlock",
            "Forbidden: blind auto_sync without m5 gate",
            "Loop B Phase 2 exit receipt",
        ],
    ),
    (
        "phase-ft6-loop-c",
        "Hub agent_loop — auto submit after incident unlock",
        [
            "Read auto-paste incident lock status — honest in receipt",
            "founder/ASF_CURSOR_AND_M8.md unlock checklist — checklist only",
            "agent_loop.py idle after round 10 — smoke",
            "POST /api/agent-loop submit-round path documented",
            "Forbidden: re-enable auto-paste without checklist",
            "Cursor SDK M8b spike doc one page — no hub rewrite",
            "Loop C depends on Loop A broker JSON — note only",
            "Planner stays OpenRouter; executor stays Cursor",
            "SOURCEA-PRIORITY one row: Loop C prep",
            "Loop C Phase 3 exit criteria doc",
        ],
    ),
    (
        "phase-ft7-spine-min",
        "s4 spine — minimal wiring after s1 drain",
        [
            "validate-execution-spine-v1.sh PASS",
            "validate-graph-executor-gate-honesty-v1 PASS",
            "orchestrator shadow dry_run=true honest in status",
            "Read scripts/runtime orchestrator — event hook points only",
            "No skip-phase law doc — phase-first reminder",
            "s4 backlog count from goal-progress-v1.py",
            "FORGE spine read-only parity note — no FORGE edits",
            "RunReceipt parallel — not spine SSOT reminder",
            "One minimal spine fix if VERIFY failed — else STOP",
            "Spine phase velocity receipt",
        ],
    ),
    (
        "phase-ft8-ship",
        "FORGE Vercel + TrustField parallel revenue",
        [
            "forge/docs/LAUNCH_CHECKLIST.md all [x] confirmed",
            "Hub Actions FORGE/MP-SHIP path — founder doc only",
            "FORGE /health 200 after ship — evidence path",
            "TrustField outreach template ready — commercial parallel",
            "Forbidden: FORGE hub observability before ship",
            "T2 FORGE vs T2b side SKUs — no north star swap",
            "PROGRAM_PROGRESS FORGE signal after ship",
            "No Terminal founder steps in ship runbook",
            "SOURCEA-PRIORITY ship row",
            "Revenue parallel receipt — Loop A still primary",
        ],
    ),
    (
        "phase-ft9-enforce",
        "validators only — no drift/MANIFEST hunts",
        [
            "find_critical_bugs.py critical 0",
            "audit_backend_e2e.py PASS — sufficient for Phase 1",
            "Forbidden: MANIFEST.yaml build this phase",
            "Forbidden: os/plan-library path drift sweep",
            "Forbidden: validate-sourcea-e2e-full noisy suite unless ASF asks",
            "One sa fixes one verify FAIL — minimal diff",
            "No hub panel edits from this Worker workspace",
            "WORKER_ROUND_REPORT required shape only",
            "External critic compare only — no reorder",
            "Enforcement min receipt",
        ],
    ),
    (
        "phase-ft10-l3-exit",
        "L3 blockers — honest checklist only",
        [
            "List 7 L3 blockers from BRAIN_FULL_SYSTEM_MAP — status each",
            "OpenRouter 402 cleared — receipt",
            "dispatch_ready true cleared — receipt",
            "auto_sync_plan verified cleared — receipt",
            "Auto-paste incident unlock cleared — receipt",
            "Cursor SDK M8b cleared — receipt",
            "Hub sa-1000 tab cleared — receipt",
            "Loop A+B+C fused smoke test plan one page",
            "Forbidden: claim zero-human until all 7 clear",
            "Fast track program complete receipt",
        ],
    ),
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _md(ac_id: str, phase_key: str, phase_desc: str, slot: int, title: str) -> str:
    ap = (
        f"PLAN WITH NO ASF — {ac_id}: {title}. "
        f"Law: {PROGRAM}. Fast track — one sa, minimal diff, STOP. "
        f"Founder: Hub only. Default execution: goal1_auto_loop headless — not manual paste. "
        f"WORKER_ROUND_REPORT → broker submit → STOP."
    )
    return f"""---
id: {ac_id}
phase: {phase_key}
tier: T0
priority: P0
status: backlog
lane: sourcea
library: automation-fast-track-100-locked
agent: {AGENT}
agent_tag: {TAG}
written_at: 2026-06-07
slot: {slot}
generator: scripts/generate-automation-fast-track-100.py
locked: true
program: AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md
---

# [{TAG}] {ac_id} — {title}

**Phase:** `{phase_key}` — {phase_desc}

## Agent prompt

```
{ap}
```

## Task

{title}

## Fast track law

- No duplication · no MANIFEST · no drift hunts · no new daemon (use goal1_auto_loop)
- One rail: headless autoloop OR pick 1 sa drain — not both manual

## Verify

```bash
{VERIFY}
```
"""


def main() -> int:
    old_1000 = ROOT / "brain-os/plan-registry/automation-converge-1000"
    if PROMPTS.exists():
        shutil.rmtree(PROMPTS)
    PROMPTS.mkdir(parents=True, exist_ok=True)

    plans: list[dict] = []
    n = 0
    for phase_key, phase_desc, tasks in PHASES:
        phase_dir = PROMPTS / phase_key
        phase_dir.mkdir(parents=True, exist_ok=True)
        for slot, title in enumerate(tasks, start=1):
            n += 1
            ac_id = f"ft-{n:04d}"
            rel = f"prompts/{phase_key}/{ac_id}.md"
            (phase_dir / f"{ac_id}.md").write_text(
                _md(ac_id, phase_key, phase_desc, slot, title), encoding="utf-8"
            )
            plans.append(
                {
                    "id": ac_id,
                    "phase": phase_key,
                    "tier": "T0",
                    "priority": "P0",
                    "lane": "sourcea",
                    "slot": slot,
                    "title": title,
                    "path": rel,
                    "status": "backlog",
                    "verify": VERIFY,
                    "agent_tag": TAG,
                    "agent_prompt": f"PLAN WITH NO ASF — {ac_id}: {title}",
                }
            )

    registry = {
        "schema_version": 1,
        "library": "automation-fast-track-100-locked",
        "locked": True,
        "count": 100,
        "unique": True,
        "no_tier_duplication": True,
        "generated_at": _now(),
        "agent": AGENT,
        "grid": "10 phases × 10 unique prompts = 100",
        "trigger": "PLAN WITH NO ASF — FAST TRACK",
        "pick_script": "scripts/plan-automation-fast-track-run.sh",
        "program_doc": PROGRAM,
        "supersedes": "automation-converge-1000-locked (duplication retired)",
        "plans": plans,
    }
    PACK.mkdir(parents=True, exist_ok=True)
    (PACK / "REGISTRY.json").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    lock = ROOT / "brain-os/plan-registry/AUTOMATION-FAST-TRACK-100-LOCK.md"
    lock.write_text(
        f"""# Automation Fast Track 100 — LOCKED (Elon style)

**Count:** 100 unique prompts · **Zero duplication** · **Date:** 2026-06-07  
**Supersedes:** `automation-converge-1000` (tier mirrors retired)  
**Program:** `brain-os/contract/AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md`

## Pick

```bash
bash scripts/plan-automation-fast-track-run.sh pick 1
```

## Regenerate

```bash
python3 scripts/generate-automation-fast-track-100.py
```

## IDs

`ft-0001` … `ft-0100` — one task each, no T0/T1 mirrors.

## Execution default

**Hub ▶ AUTO-RUN 50** — not 100 manual pastes. Pack is debug/phase-gate curriculum only.
""",
        encoding="utf-8",
    )

    # Retire old 1000 pack marker
    retire = old_1000 / "RETIRED_DUPLICATION.md"
    if old_1000.is_dir():
        retire.write_text(
            "RETIRED 2026-06-07 — superseded by automation-fast-track-100 (no duplication).\n",
            encoding="utf-8",
        )

    print(f"OK: automation-fast-track-100 · {n} unique prompts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
