#!/usr/bin/env python3
"""Generate automation-converge-1000 LOCKED pack — Musk program Worker prompts (10×4×25)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "brain-os" / "plan-registry" / "automation-converge-1000"
PROMPTS = PACK / "prompts"
AGENT = "AGENT-AUTO-SOURCEA"
TAG = "AGENT-AUTO-SOURCEA"
PROGRAM = "brain-os/contract/AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md"

PHASES = [
    ("phase-ac1-loop-a-headless", "goal1_auto_loop, broker=yes, orchestrator, batch log, no manual paste"),
    ("phase-ac2-inject-activate", "inject→validate→activate→sync chain, worker_inject, lane broker"),
    ("phase-ac3-l2-dispatch", "dispatch_ready, eval_1b_gate_ok, dispatch-policy, founder gate honesty"),
    ("phase-ac4-s1-drain-fast", "phase-first pick 1, s1 eval-dispatch drain at max throughput"),
    ("phase-ac5-loop-b-promptos", "SinaPromptOS dispatch-day, auto_sync m5 verified-only, scheduler"),
    ("phase-ac6-loop-c-hub", "agent_loop, auto-paste unlock, Cursor SDK M8b, submit-round"),
    ("phase-ac7-spine-s4", "graph executor, event bus, execution memory — minimal wiring"),
    ("phase-ac8-ship-revenue", "FORGE Vercel ship, TrustField pilot LOI, founder Actions only"),
    ("phase-ac9-enforce-min", "validators + critical 0 only — no drift/MANIFEST scope creep"),
    ("phase-ac10-l3-exit", "L3 blocker clearance, zero-human gates, 10k ecosystem handoff"),
]

TIERS = [
    ("T0", "Critical — ship now, minimal diff, machine verify"),
    ("T1", "High — next autoloop sprint"),
    ("T2", "Medium — hardening without new architecture"),
    ("T3", "Low — research / doc / near-miss only"),
]

TIER_DEPTH = {
    "T0": "Do now. One file. Verify before closeout. No scope creep.",
    "T1": "Sprint task. Evidence row in SOURCEA-PRIORITY.md.",
    "T2": "Hardening only. No parallel rails.",
    "T3": "Document or spike. No hub rewrite unless verify fails.",
}

VERIFY = {
    "T0": "cd scripts && python3 brain_validate_goal1_v1.py --json && python3 find_critical_bugs.py",
    "T1": "cd scripts && bash validate-eval-packet-v1b-live.sh && bash validate-dispatch-policy-v1.sh && python3 find_critical_bugs.py",
    "T2": "cd scripts && bash validate-goal1-auto-loop-v1.sh && bash validate-goal1-loop-activation-chain-v1.sh",
    "T3": "cd scripts && python3 goal-progress-v1.py && python3 find_critical_bugs.py",
}

# 25 strong tasks per phase — Musk: remove human touchpoints
PHASE_TASKS: list[list[str]] = [
    [  # ac1 loop A headless
        "Run goal1_auto_loop_v1.py --prepare-only --turns 1 --json; report deliver ok",
        "Verify batch log last line broker=yes; fix sa_mismatch if broker=no",
        "Clear stale goal1-auto-loop-lock only when pid dead — never kill live loop",
        "Confirm healthy-drain-orchestrator deliver writes INBOX without Brain hijack",
        "Document headless path: Worker chat empty, agent -p -f executes turn",
        "Run validate-goal1-auto-loop-v1.sh — must PASS before scale to 50 turns",
        "Count broker=yes streak in goal1-worker-batch-latest.log — target 50",
        "Stop goal1 loop cleanly via stop_goal1_loop_v1.py when broker fails 3×",
        "Wire post-turn advance-healthy-queue-v1.py only after VERIFY STOP",
        "Reject manual paste when pending=true in worker_inject_lib --status",
        "Sync orchestrator poll_once after each headless turn",
        "Prove activate PASS holds across 10 consecutive autoloop turns",
        "Fix brain_lane_guard import shim if deliver --force fails",
        "Hub Action path only for founder — document no Terminal law",
        "Run goal1_auto_loop --turns 10 detached; log AGENT START/DONE",
        "Validate one_sa_per_turn_gate on WORKER_ROUND_REPORT yaml",
        "Ensure sa_focus in report matches INBOX meta sa_id exactly",
        "Clear worker_inject after worker-submit per MANDATORY_SOURCEA_WORKER",
        "Measure turns/hour from batch log timestamps",
        "Add SOURCEA-PRIORITY row: autoloop streak N broker=yes",
        "Forbidden: pick 30 unattended batch during Phase 1",
        "Forbidden: healthy pack parallel rail while autoloop Phase 1 active",
        "Compare inbox JSON vs queue state file — report drift only",
        "Run brain_validate after hygiene clear stale broker=no tail",
        "Closeout: Phase 1 autoloop readiness receipt",
    ],
    [  # ac2 inject activate
        "brain_validate_goal1_v1.py --json — all four chain steps PASS",
        "worker_inject_lib.py --status — pending true before turn execute",
        "goal1_lane_broker.py brain-poll + brain-ack cycle",
        "worker-submit stdin parses WORKER_ROUND_REPORT yaml",
        "INJECT step: disk prompt not chat memory",
        "VALIDATE step: validators per CHECK/ACT/VERIFY role",
        "ACTIVATE step: full turn in chat or headless agent output",
        "SYNC step: worker-submit + inject --clear",
        "validate-goal1-loop-activation-chain-v1.sh PASS",
        "Refuse narrate lock blocks goal1_auto_loop spawn",
        "Orchestrator status done vs awaiting_worker honest",
        "Batch log AGENT DONE includes broker=yes|no",
        "Fix expected_role lag in orchestrator snapshot only",
        "Document GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED steps 1-4",
        "Headless SYNC: broker parses agent -p -f output",
        "Reject INBOX delivery alone as loop complete",
        "Pickup path: goal1_lane_broker.py pickup returns disk prompt",
        "Session-start before first edit per Worker law",
        "Entry gate 000-entry-gate.mdc — report blockers only",
        "one_sa_per_turn mechanical gate PASS",
        "PRIORITY evidence row on every VERIFY closeout",
        "REGISTRY mark_done via closeout_sa_task.py only",
        "Turn lib worker_turn_lib open/close pairing",
        "Post-pack hygiene: activate PASS + broker=yes",
        "Activation chain receipt YAML for Brain handoff",
    ],
    [  # ac3 L2 dispatch
        "validate-dispatch-policy-v1.sh — eval_1b_gate_ok honest",
        "Hub /api/dispatch-policy-v1 matches policy_engine",
        "dispatch_ready=false until founder confirm — no code bypass",
        "Document founder Hub confirm path for dispatch_ready=true",
        "eval_1b_ci_mode_v1.json mode=live when credits ok",
        "validate-eval-packet-v1b-live.sh live pilots ≥80%",
        "graph_executor gate receipts eval_1b honest vs dispatch",
        "validate-graph-executor-gate-honesty-v1 CRITICAL",
        "dispatch_ready lock validator PASS",
        "No global dispatch_ready=true in scripts grep",
        "Phase 2b eligibility doc in dispatch policy payload",
        "SOURCEA-PRIORITY dispatch gate row fresh",
        "After founder confirm: re-run validate-dispatch-policy",
        "Spine bridge founder gate separate from dispatch",
        "model_dispatch gate_eligible enforce mode honest",
        "Council brief eval_1 vs eval_1b arms present",
        "eval_report_capture timestamps fresh",
        "OpenRouter 402 structural_only fallback honest",
        "L2 ceiling checklist in AUTOMATION_CONVERGE_PROGRAM",
        "Reject claiming L3 when dispatch_ready false",
        "Hub refresh shows live eval tier",
        "command-data dispatch_policy block sync",
        "validate-dispatch-ready-lock-v1.sh",
        "Dispatch tier behavioral_pass documented",
        "L2 unlock receipt after founder confirm",
    ],
    [  # ac4 s1 drain fast
        "plan-no-asf-run.sh pick 1 — trust output not chat",
        "goal-progress-v1.py LIVE_PICK matches pick script",
        "Drain sa-0131 band: eval live SINA_AUDIT_STRICT capture",
        "One sa per session — REGISTRY_DRAIN_RAIL",
        "Phase-first: no skip to s4 while s1 backlog >0",
        "sourcea_pick_lib phase order validator",
        "validate-sourcea-pick-order-v1.py PASS",
        "mark_done only on VERIFY machine PASS",
        "66 s1 tasks — track backlog delta per day",
        "Throughput: 10 turns/day minimum target",
        "No MANIFEST sa during s1 drain",
        "No path drift sa during s1 drain",
        "validate-eval-packet-v1b on VERIFY turns",
        "find_critical_bugs critical 0 at closeout",
        "audit_hub_source_alignment when hub task only",
        "Skip done sa replay — REGISTRY status done",
        "PRIORITY row every closeout",
        "REPO_EXECUTION_LOGS append on verify",
        "pick-sourcea-no-asf-plan.py alone is drift — use plan-no-asf-run.sh",
        "Brain handoff yaml goal_1_progress field",
        "Healthy queue paused during autoloop Phase 1",
        "sa-0130 done — do not replay",
        "sa-0129 done — do not replay",
        "s1 exit: backlog <40 gate",
        "s1 drain velocity receipt",
    ],
    [  # ac5 loop B promptos
        "Read SinaPromptOS config auto_sync_plan flag",
        "Flip auto_sync_plan only with m5 verified-only path",
        "m5_sync.py — mutate plan.json only when verify_passed",
        "dispatch-day.sh output to queue file not clipboard",
        "Document launchd/cron schedule for 08:00 dispatch",
        "Loop B semi-auto vs full-auto exit criteria",
        "ready_to_paste_*.txt ingest without founder paste",
        "DevBridge consumer hook for dispatch output",
        "Reject blind auto_sync without verify gate",
        "validate Prompt OS dispatch-day dry run",
        "TrustField/mono/virlux lanes parallel not north star",
        "PROGRAM_PROGRESS sync from Prompt OS outputs",
        "auto-sync-plan-verified.sh smoke",
        "Log 7-day Loop B unattended run",
        "SOURCEA-PRIORITY Loop B row",
        "Forbidden: daily founder paste when auto_sync true",
        "Morning factory architecture doc one page",
        "SINAAI_10X_AUTOMATION_ARCHITECTURE cross-ref",
        "n8n self-host trigger optional",
        "Event listener stub for dispatch complete",
        "Broker ingest Prompt OS output JSON",
        "Loop A green while Loop B runs",
        "Phase 2 exit: 7-day scheduled dispatch",
        "config/settings.json change receipt",
        "Loop B unlock receipt",
    ],
    [  # ac6 loop C hub cursor
        "agent_loop.py max 10 rounds documented",
        "POST /api/agent-loop submit-round path",
        "Auto-paste incident lock status honest",
        "founder/ASF_CURSOR_AND_M8.md unlock checklist",
        "Cursor SDK M8b integration spike doc",
        "Headless submit-round without clipboard",
        "Planner OpenRouter vault key probe",
        "Executor remains Cursor not planner",
        "INBOX + agent-loop coexistence",
        "Stop loop founder one tap",
        "Round report yaml shape locked",
        "validate agent-loop idle after R10",
        "Event: turn complete → next planner prompt",
        "Webhook or daemon design one page",
        "Queue stream vs static 10-batch",
        "Loop C depends on Loop A broker JSON",
        "Forbidden: re-enable auto-paste without checklist",
        "Privacy mode storage eligibility note",
        "Automations API prefill vs hub loop",
        "Phase 3 exit: R1→R10 without founder paste",
        "agent-loop response action schema",
        "Seeds set_seeds once per loop start",
        "Brain does not act as Advisor",
        "Loop C receipt in SOURCEA-PRIORITY",
        "Loop C unlock receipt",
    ],
    [  # ac7 spine s4
        "graph-executor gate honesty validator",
        "spine bridge founder event shipped structural",
        "validate-execution-spine-v1.sh PASS",
        "event bus scaffold locate scripts/runtime",
        "execution memory receipt path",
        "s4 phase-first after s1+s3 drain law",
        "sa-0401 band readiness check only",
        "No skip phase law — document only",
        "orchestrator shadow dry_run=true honest",
        "C1-C7 runtime dispatch_ready ceiling",
        "pre_llm tool_router local-first note",
        "prompt_router validate-prompt-router-v1",
        "Spine automation ≠ L3 claim",
        "Machine routes turns — design doc",
        "poll_once extend for event chain",
        "validate-spine-bridge-founder-v1.sh",
        "audit_backend_e2e spine section",
        "REGISTRY s4 backlog count from goal-progress",
        "Minimal diff spine wiring only",
        "Reject new architecture before s4 pick",
        "FORGE spine parity read-only probe",
        "RunReceipt parallel not spine SSOT",
        "STRATEGIC-SLICE north star unchanged",
        "s4 velocity metric",
        "Spine phase receipt",
    ],
    [  # ac8 ship revenue
        "FORGE LAUNCH_CHECKLIST all items checked",
        "Hub Actions MP-SHIP Vercel path",
        "forge/ validate-launch-checklist.mjs PASS",
        "FORGE live /health 200 public",
        "TrustField outreach 15 email template",
        "founder_live_sales_checklist.sh evidence",
        "Pilot LOI scoped conversation metric",
        "FORGE observability post-ship backlog only",
        "PROGRAM_PROGRESS FORGE signal",
        "MergePack parallel lane not north star",
        "Revenue ≠ automation factory conflation guard",
        "T2 FORGE vs T2b side SKUs law",
        "Hub products tab FORGE entry",
        "No Terminal founder ship steps",
        "Vercel deployment protection disable",
        "Supabase RLS stub validated",
        "Stripe webhook idempotent proof",
        "Beta cohort registry logged",
        "Commercial Brain parallel not blocking Loop A",
        "SOURCEA-PRIORITY FORGE ship row",
        "TrustField demo booked optional gate",
        "Wire G3 separate lane",
        "Evidence factory MergePack health",
        "Ship receipt yaml",
        "Revenue parallel receipt",
    ],
    [  # ac9 enforce min
        "find_critical_bugs.py critical 0 only metric",
        "Reject MANIFEST build during Phase 1",
        "Reject path drift hunt during Phase 1",
        "validate-sourcea-e2e-core-v1 not full noisy suite",
        "audit_backend_e2e PASS sufficient",
        "validate-governance-fleet-v1 nudges 0",
        "validate-governance-drift-v1 score 100",
        "No new validators without SSOT gap",
        "One sa fixes one verify FAIL",
        "Minimal diff law enforcement",
        "WORKER_ROUND_REPORT required shape",
        "Broker reject ONE_SA_BATCH_VIOLATION",
        "No hub panel rewrite from Worker",
        "SinaaiDataBase workspace for panel builds",
        "Post agent-review for hub bugs",
        "Near-miss log agent-governance-events.jsonl",
        "Self-heal detect classify remediate verify",
        "Smart judgment line test",
        "External critic compare only",
        "No reorder from GPT tables",
        "validate-no-asf-eval-authority-v1",
        "cursor_entry_gate Layer 3 when touching mdc",
        "Forbidden UNATTENDED BATCH",
        "Forbidden pick 30",
        "Enforcement min receipt",
    ],
    [  # ac10 L3 exit
        "List 7 L3 blockers from BRAIN_FULL_SYSTEM_MAP",
        "OpenRouter 402 blocker cleared receipt",
        "dispatch_ready true blocker cleared receipt",
        "Auto-paste incident unlock receipt",
        "Cursor SDK M8b wired receipt",
        "auto_sync_plan true verified receipt",
        "Hub sa-1000 queue tab receipt",
        "10k ecosystem pack handoff doc",
        "Goal 1 1000/1000 gate",
        "Goal 2 WTM pre-LLM overlap note",
        "L3 zero-human not claimed until all 7 clear",
        "Loop A+B+C fused definition test",
        "Event-driven orchestration design",
        "AI Dev Bridge router cheapest provider",
        "Pre-LLM D1-D16 _phase_d_complete audit",
        "dispatch Phase 3 when law allows",
        "REGISTRY 10k next tier hierarchy",
        "Automation level honest in hub",
        "Founder walk-away criteria doc",
        "No calendar date promises in law",
        "Throughput sustained 50/day proof",
        "broker=yes 100 streak proof",
        "activate PASS 7-day proof",
        "Full automation functional test plan",
        "L3 exit receipt — program complete",
    ],
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _md_body(
    ac_id: str,
    phase_key: str,
    phase_desc: str,
    tier: str,
    tier_label: str,
    slot: int,
    title: str,
    verify: str,
) -> str:
    agent_prompt = (
        f"PLAN WITH NO ASF — {ac_id}: {title} ({tier_label}). "
        f"Law: {PROGRAM}. Pre-flight: AUTOMATION_CONVERGE_PROGRAM + MANDATORY_SOURCEA_WORKER. "
        f"Founder: Hub Actions only — no Terminal. Headless default: goal1_auto_loop. "
        f"Post-flight: verify gate + PRIORITY row + WORKER_ROUND_REPORT → broker submit → STOP."
    )
    return f"""---
id: {ac_id}
phase: {phase_key}
tier: {tier}
priority: {"P0" if tier == "T0" else "P1" if tier == "T1" else "P2" if tier == "T2" else "P3"}
status: backlog
lane: sourcea
library: automation-converge-1000-locked
agent: {AGENT}
agent_tag: {TAG}
written_at: 2026-06-07
slot: {slot}
generator: scripts/generate-automation-converge-1000.py
locked: true
program: AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md
---

# [{TAG}@2026-06-07] {ac_id} — {title}

**Phase:** `{phase_key}` — {phase_desc}  
**Tier:** `{tier}` — {TIER_DEPTH[tier]}  
**Program:** `AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md`

## Agent prompt (copy to chat)

```
{agent_prompt}
```

## Task

{title}

## Musk rules (this pack)

- **Delete friction** — headless autoloop over manual paste
- **One rail** — pick 1 / ac-XXXX only; no parallel healthy pack during Phase 1
- **No over-engineering** — no MANIFEST, drift hunts, or hub rewrites unless verify fails
- **Founder** — Hub ▶ AUTO-RUN · Refresh · Actions only

## Sources

- `brain-os/contract/AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md`
- `brain-os/memory/BRAIN_FULL_SYSTEM_MAP_LOCKED_v1.md`
- `brain-os/law/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md`
- `brain-os/plan-registry/SOURCEA-PRIORITY.md`
- `scripts/goal1_auto_loop_v1.py` · `scripts/goal1_lane_broker.py`

## Verify

```bash
{verify}
```

## Closeout

REGISTRY `done` · SOURCEA-PRIORITY evidence row · `WORKER_ROUND_REPORT` · broker `worker-submit` · STOP.
"""


def main() -> int:
    PROMPTS.mkdir(parents=True, exist_ok=True)
    plans: list[dict] = []
    n = 0
    for pi, (phase_key, phase_desc) in enumerate(PHASES):
        tasks = PHASE_TASKS[pi]
        for ti, (tier, tier_label) in enumerate(TIERS):
            tier_dir = PROMPTS / phase_key / tier
            tier_dir.mkdir(parents=True, exist_ok=True)
            for slot in range(25):
                n += 1
                ac_id = f"ac-{n:04d}"
                title = tasks[slot]
                rel = f"prompts/{phase_key}/{tier}/{ac_id}.md"
                path = PROMPTS / phase_key / tier / f"{ac_id}.md"
                path.write_text(
                    _md_body(ac_id, phase_key, phase_desc, tier, tier_label, slot + 1, title, VERIFY[tier]),
                    encoding="utf-8",
                )
                plans.append(
                    {
                        "id": ac_id,
                        "phase": phase_key,
                        "tier": tier,
                        "priority": "P0" if tier == "T0" else "P1" if tier == "T1" else "P2" if tier == "T2" else "P3",
                        "lane": "sourcea",
                        "slot": slot + 1,
                        "title": title,
                        "path": rel,
                        "status": "backlog",
                        "verify": VERIFY[tier],
                        "agent_tag": TAG,
                        "agent_prompt": f"PLAN WITH NO ASF — {ac_id}: {title}",
                        "program": "AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md",
                    }
                )

    registry = {
        "schema_version": 1,
        "library": "automation-converge-1000-locked",
        "locked": True,
        "count": 1000,
        "generated_at": _now(),
        "agent": AGENT,
        "agent_tag": TAG,
        "repo": "SourceA",
        "grid": "10 phases × 4 tiers × 25 prompts = 1000",
        "trigger": "PLAN WITH NO ASF — AUTOMATION CONVERGE",
        "pick_script": "scripts/plan-automation-converge-run.sh",
        "program_doc": PROGRAM,
        "parent_pack": "sourcea-1000-locked",
        "law": "Phase 1: autoloop + ship FORGE + dispatch_ready — see program doc",
        "plans": plans,
    }
    PACK.mkdir(parents=True, exist_ok=True)
    reg_path = PACK / "REGISTRY.json"
    reg_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    lock_md = PACK.parent / "AUTOMATION-CONVERGE-1000-LOCK.md"
    lock_md.write_text(
        f"""# Automation Converge 1000 — LOCKED prompt pack

**Status:** LOCKED · **Count:** 1000 · **Date:** 2026-06-07  
**Program:** [`AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md`](../contract/AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md)

## Pick

```bash
bash scripts/plan-automation-converge-run.sh pick 1
```

## Regenerate

```bash
python3 scripts/generate-automation-converge-1000.py
```

## IDs

`ac-0001` … `ac-1000` in [`automation-converge-1000/REGISTRY.json`](automation-converge-1000/REGISTRY.json)

## Phases

| Phase | Focus |
|-------|--------|
| ac1 | Loop A headless autoloop |
| ac2 | inject→activate chain |
| ac3 | L2 dispatch gates |
| ac4 | s1 fast drain |
| ac5 | Loop B PromptOS |
| ac6 | Loop C hub↔Cursor |
| ac7 | Spine s4 minimal |
| ac8 | FORGE + TrustField ship |
| ac9 | Enforcement minimal |
| ac10 | L3 exit blockers |
""",
        encoding="utf-8",
    )
    print(f"OK: automation-converge-1000 · {n} prompts · {reg_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
