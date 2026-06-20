#!/usr/bin/env python3
"""Generate broker-pack-1000 — 1000 unique Goal1 lane-broker Worker prompts.

Scope: goal1_lane_broker · worker-submit · brain-poll/ack · orchestrator sync only.
NOT: sourcea-1000 drain · automation-fast-track · retired automation-converge-1000.
Law: no tier mirrors · no duplicate titles · one br-id per unique task.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "brain-os" / "plan-registry" / "broker-pack-1000"
PROMPTS = PACK / "prompts"
AGENT = "AGENT-AUTO-SOURCEA"
TAG = "AGENT-AUTO-SOURCEA"
PROGRAM = "brain-os/plan-registry/BROKER-PACK-1000-LOCK.md"

VERIFY = (
    "cd scripts && bash validate-goal1-lane-broker-v1.sh && "
    "python3 goal1_lane_broker.py brain-poll --json && "
    "python3 brain_validate_goal1_v1.py --json"
)

# 10 broker phases × 10 areas × 10 probes = 100 unique tasks per phase
PHASE_SPEC: list[tuple[str, str, list[tuple[str, list[str]]]]] = [
    (
        "phase-br1-worker-submit",
        "Worker YAML → goal1_lane_broker worker-submit → orchestrator poll_once",
        [
            (
                "submit-parse",
                [
                    "Parse WORKER_ROUND_REPORT status key flat not nested",
                    "Reject submit missing status WORKER_ROUND_REPORT",
                    "Map round_type check to audit in broker normalize",
                    "Map round_type act to implement in broker normalize",
                    "Map round_type verify to fix in broker normalize",
                    "Extract sa_focus from YAML when sa alias present",
                    "Parse validate.spine nested dict in loose YAML",
                    "Parse validate.critical_bugs integer in loose YAML",
                    "Reject sa-TEST and sa-*-TEST in worker_submit",
                    "Append WORKER_SUBMIT event to goal1-lane-broker-events.jsonl",
                ],
            ),
            (
                "submit-inbox",
                [
                    "Compare INBOX meta sa_id before worker_submit",
                    "Return sa_mismatch when sa_focus differs from INBOX",
                    "clear_inbox after successful broker worker_submit",
                    "write_round_report before orchestrator poll_once",
                    "close_turn via worker_turn_lib on submit path",
                    "Document inbox_after field in broker state JSON",
                    "worker_submit source worker_chat vs headless agent",
                    "Broker stores last_worker_report snapshot honest",
                    "Forbidden submit without prior INBOX pending true",
                    "Receipt: submit ok false includes hint string",
                ],
            ),
            (
                "submit-auto",
                [
                    "auto_advance true triggers _auto_deliver_next",
                    "batch_running status when auto_advance enabled",
                    "checkpoint flag blocks auto deliver on submit",
                    "recent_turns ring buffer capped at 10 rows",
                    "turns_in_batch increments on each submit",
                    "WORKER_SUBMIT_AUTO event when auto_advance",
                    "Deliver next INBOX after VERIFY closeout only",
                    "Stop auto_advance when feasibility STOP_INJECT",
                    "Headless path: agent stdout ends with YAML block",
                    "Visible path: worker-submit --stdin from composer",
                ],
            ),
            (
                "submit-gate",
                [
                    "one_sa_per_turn_gate_v1 runs before orchestrator",
                    "guard_broker_submit rejects duplicate reports",
                    "Registry updated list empty on CHECK turns",
                    "turn_closed true required before next inject",
                    "Broker returns one_sa_gate block on failure",
                    "Single WORKER_ROUND_REPORT per turn law",
                    "Forbidden second submit same sa same turn",
                    "Open turn blocks submit until close_turn",
                    "validate-worker-one-sa-turn-v1.sh smoke",
                    "Receipt: violations array empty on PASS",
                ],
            ),
            (
                "submit-orch",
                [
                    "poll_once called immediately after successful submit",
                    "orchestrator_result stored in broker state",
                    "orchestrator_snapshot JSON after poll_once",
                    "completed true when role matches queue_role",
                    "skip_act_verify honored on orchestrator path",
                    "advanced block written to healthy-queue-state",
                    "done_all_30 when queue exhausted",
                    "stop_reason queue_exhausted honest in snapshot",
                    "turns_completed increments on completed turn",
                    "last_completed_sa matches submitted sa_focus",
                ],
            ),
            (
                "submit-errors",
                [
                    "Document error missing WORKER_ROUND_REPORT",
                    "Document error sa_focus required sa-XXXX",
                    "Document error sa_mismatch expected got",
                    "Document error sa-TEST rejected stale inject",
                    "Hint points to INBOX meta sa_id on mismatch",
                    "Broker ok false does not clear inbox",
                    "Broker ok false does not advance queue",
                    "Log fail_reason in goal1_run_loop turn JSON",
                    "batch log AGENT DONE broker=no on submit fail",
                    "Stop loop after 3 broker=no consecutive",
                ],
            ),
            (
                "submit-reports",
                [
                    "critical_bugs from validate dict precedence",
                    "critical_bugs top-level YAML fallback",
                    "round_type defaults check when absent",
                    "phase field audit act verify in report",
                    "summary string optional in WORKER_ROUND_REPORT",
                    "at timestamp ISO in report optional",
                    "turn_closed boolean in report shape",
                    "status must be first key recommendation",
                    "YAML fenced block extraction from markdown",
                    "Multiple YAML blocks: use last WORKER_ROUND_REPORT",
                ],
            ),
            (
                "submit-cli",
                [
                    "goal1_lane_broker.py worker-submit --stdin reads stdin",
                    "worker-submit accepts piped composer output",
                    "pickup subcommand returns inbox prompt preview",
                    "watch subcommand polls broker idle awaiting",
                    "brain-poll JSON for Brain handoff only",
                    "brain-ack clears checkpoint_pending status",
                    "brain-checkpoint-ack after batch gate",
                    "start-batch records batch_size default 5",
                    "CLI help documents broker state path",
                    "Exit code 1 on broker ok false",
                ],
            ),
            (
                "submit-validate",
                [
                    "validate-goal1-lane-broker-v1.sh PASS required",
                    "brain_validate broker_status field after submit",
                    "find_critical_bugs 0 at broker VERIFY closeout",
                    "validate-goal1-brain-validation-v1 brain-poll shape",
                    "E2E validate-goal1-e2e-v1 broker section",
                    "SOURCEA-PRIORITY row on broker VERIFY only",
                    "closeout_sa_task only when machine verify PASS",
                    "Forbidden REGISTRY mark_done on broker=no",
                    "WORKER_ROUND_REPORT then STOP one turn",
                    "Receipt br submit chain PASS",
                ],
            ),
            (
                "submit-law",
                [
                    "GOAL1_LOOP_ACTIVATION_CHAIN SYNC step proof",
                    "SINA_GOAL1_OPERATING_MODEL broker law cite",
                    "MANDATORY_SOURCEA_WORKER_CHAT broker submit order",
                    "Founder never runs worker-submit — Worker only",
                    "Brain polls brain-poll does not worker-submit",
                    "PEV Executor submits Verifier validators",
                    "No clipboard paste into Brain for broker",
                    "INBOX pickup not chat memory for sa_id",
                    "Default runtime Hub AUTO-RUN not manual submit",
                    "Pack br curriculum when autoloop breaks only",
                ],
            ),
        ],
    ),
    (
        "phase-br2-brain-poll",
        "Brain poll · ack · checkpoint · brain-broker-inbox",
        [
            (
                "poll-core",
                [
                    "brain_poll returns BRAIN_BROKER_POLL status",
                    "brain_poll action field for Brain routing",
                    "brain_poll includes inbox pending snapshot",
                    "brain_poll includes orchestrator phase idle",
                    "brain_poll last_worker_report when present",
                    "brain_poll YAML output when --yaml flag",
                    "brain_poll JSON default for machine",
                    "brain_poll broker_status idle awaiting_worker",
                    "brain_poll checkpoint_pending when batch done",
                    "brain_poll updated_at ISO timestamp",
                ],
            ),
            (
                "poll-action",
                [
                    "action run_goal1_auto_loop when inject ready",
                    "action broker_poll_worker_submit when checkpoint",
                    "action deliver_healthy_drain when inbox empty",
                    "action stop_inject when feasibility blocks",
                    "Brain narrate only never worker-submit",
                    "brain_action in brain_validate_goal1_v1",
                    "mandatory_next goal1_auto_loop when activate FAIL",
                    "founder_surface batch log not Worker chat",
                    "brain_watch_loop polls brain-poll on interval",
                    "Receipt: Brain handoff uses poll not invent",
                ],
            ),
            (
                "ack-core",
                [
                    "brain_ack clears checkpoint_pending to idle",
                    "brain_ack writes note optional string",
                    "brain_ack updates broker updated_at",
                    "brain_ack appends BRAIN_ACK event jsonl",
                    "brain_ack does not advance queue alone",
                    "brain_ack after founder reviews checkpoint",
                    "brain-checkpoint-ack requires machine pass",
                    "force flag on checkpoint ack documented",
                    "checkpoint path goal1-batch-checkpoint-v1.json",
                    "load_checkpoint returns schema honest",
                ],
            ),
            (
                "ack-batch",
                [
                    "start_batch sets batch_size parameter",
                    "batch turns_in_batch reset on start_batch",
                    "batch recent_turns empty on new batch",
                    "checkpoint_machine_pass all gates PASS",
                    "checkpoint fails if any turn gate FAIL",
                    "checkpoint gate field per turn summary",
                    "batch checkpoint after N turns default 5",
                    "Brain ack unblocks next AUTO-RUN",
                    "checkpoint_pending until brain_ack",
                    "Receipt batch checkpoint cycle",
                ],
            ),
            (
                "inbox-brain",
                [
                    "brain-broker-inbox-v1.json delivery target",
                    "Brain inbox separate worker-prompt-inbox",
                    "brain_poll reads broker not Worker chat",
                    "ignore_if_brain on worker inbox pickup",
                    "Brain does not open INBOX editor as start",
                    "brain_validate inject PASS when pending",
                    "brain_validate sync PASS after ack",
                    "feasibility PROCEED vs STOP_INJECT",
                    "prompt_feasibility_gate before inject",
                    "Receipt brain inbox path SSOT",
                ],
            ),
            (
                "poll-orch",
                [
                    "poll includes orchestrator expected_sa",
                    "poll includes orchestrator expected_role",
                    "poll includes queue_pos and queue_total",
                    "poll brief string for Hub display",
                    "orchestrator done status when exhausted",
                    "orchestrator awaiting_worker when inbox pending",
                    "turns_completed vs max_turns in poll",
                    "last_completed_role act verify check",
                    "commercial_blocker null when clear",
                    "poll does not fake RUNNING without broker=yes",
                ],
            ),
            (
                "poll-validate",
                [
                    "validate-brain-narrate-not-execute-v1",
                    "Brain forbidden goal1_auto_loop in narrate",
                    "000-brain-unified narrate not execute",
                    "brain_run_loop spawn detached only",
                    "brain_session_start NEXT_PICK mechanical",
                    "compare external receipt only Brain",
                    "brain_gather healthy before handoff",
                    "BRAIN_VALIDATION_REPORT shape PASS",
                    "chain inject validate activate sync",
                    "Receipt brain poll validate PASS",
                ],
            ),
            (
                "poll-errors",
                [
                    "checkpoint_pending blocks premature inject",
                    "awaiting_brain_ack status documented",
                    "broker idle vs batch_running vs stopped",
                    "stale last_worker_report hygiene note",
                    "poll when orchestrator lag expected_role",
                    "harmless lag act vs verify inbox doc",
                    "do not brain_ack without reading checkpoint",
                    "do not skip checkpoint on broker=no streak",
                    "report blocker after 3 broker=no",
                    "stop_goal1_loop clears stale executor",
                ],
            ),
            (
                "poll-events",
                [
                    "goal1-lane-broker-events.jsonl append only",
                    "WORKER_SUBMIT kind in events log",
                    "BRAIN_ACK kind in events log",
                    "WORKER_SUBMIT_AUTO kind when advance",
                    "events at ISO timestamp per row",
                    "events do not contain prompt bodies",
                    "events sa field per turn",
                    "events orch_ok boolean",
                    "tail events for debug not SSOT",
                    "Receipt events log rotation policy note",
                ],
            ),
            (
                "poll-law",
                [
                    "REGISTRY_DRAIN_RAIL Brain routes not executes",
                    "WORKER_ASSIGNMENT one SourceA Worker",
                    "Brain compare only external advisors",
                    "disk receipts arbitrate brain disagreement",
                    "Hub only founder control surface",
                    "no Terminal instructions to founder",
                    "TODAY_AUTORUN_50 plan Brain monitors",
                    "fast-track ft pack not broker poll topic",
                    "sourcea-1000 sa drain parallel not substitute",
                    "broker pack br for broker breaks only",
                ],
            ),
        ],
    ),
    (
        "phase-br3-sa-alignment",
        "sa_focus · sa_mismatch · INBOX meta · one_sa gate",
        [
            (
                "mismatch",
                [
                    "sa_mismatch when VERIFY report wrong sa",
                    "sa_mismatch when ACT report stale sa",
                    "sa_mismatch expected from INBOX meta only",
                    "fix sa_focus not queue advance manually",
                    "batch log fail_reason sa_mismatch string",
                    "one_sa_gate PASS still broker can fail",
                    "orchestrator expected_sa vs inbox sa_id",
                    "healthy-queue item sa_id alignment",
                    "REGISTRY pick 1 separate from inbox sa",
                    "WARN_PICK_MISMATCH not sa_mismatch",
                ],
            ),
            (
                "focus",
                [
                    "sa_focus single id per WORKER_ROUND_REPORT",
                    "sa_focus must start with sa- prefix",
                    "sa_focus matches queue_role turn law",
                    "sa_focus on CHECK audit round only",
                    "sa_focus on ACT implement no closeout",
                    "sa_focus on VERIFY fix with closeout",
                    "dual sa_focus_ids rejected by gate",
                    "report_count 1 per turn",
                    "open_sa matches inbox when turn_open",
                    "blocked true when turn_open verify due",
                ],
            ),
            (
                "inbox-meta",
                [
                    "worker-prompt-inbox-v1.json meta queue_pos",
                    "meta queue_total 30 healthy pack",
                    "meta queue_role check act verify",
                    "meta sa_id authoritative for broker",
                    "pending true required before ACTIVATE",
                    "delivered_at ISO on inject",
                    "source healthy-drain-orchestrator",
                    "chars count on prompt length",
                    "pickup ignore_if_brain true",
                    "inbox_md path sina-loop INBOX.md",
                ],
            ),
            (
                "queue-align",
                [
                    "healthy-queue-state next_pos after advance",
                    "last_completed_pos sync with orchestrator",
                    "queue_exhausted flag when 30 done",
                    "synced_from prompts path when replay",
                    "skip_sa_slice flag honest",
                    "advanced block in orchestrator JSON",
                    "next_pos 31 when pack complete",
                    "replay pack note in queue state",
                    "pos before pos after in run_loop",
                    "queue_not_advanced stop reason",
                ],
            ),
            (
                "gate-one-sa",
                [
                    "one_sa_per_turn_gate_v1.py guard_broker_submit",
                    "ONE_SA_GATE_PASS status string",
                    "violations list empty on pass",
                    "registry_updated on VERIFY only",
                    "expected_sa from inbox meta",
                    "turn_open false after closeout",
                    "inbox_sa matches open_sa",
                    "one_sa ok false blocks activate",
                    "validate-worker-one-sa-turn-v1",
                    "Receipt one sa gate broker path",
                ],
            ),
            (
                "round-map",
                [
                    "queue_role check maps round_type audit",
                    "queue_role act maps round_type implement",
                    "queue_role verify maps round_type fix",
                    "phase check act verify in YAML",
                    "round_type wrong causes broker hint",
                    "agent wrapper maps role to round_type",
                    "start_goal1_worker_turn passes role",
                    "batch log queue_role in JSON row",
                    "orchestrator last_completed_role",
                    "Receipt round_type mapping chain",
                ],
            ),
            (
                "drift",
                [
                    "orchestrator expected_role lag harmless",
                    "inbox verify orchestrator act metadata",
                    "stale worker_check inbox clear inject",
                    "worker_inject_lib --clear before reconcile",
                    "healthy-drain-orchestrator reset manual",
                    "advance-healthy-queue one step law",
                    "distributed desync incident pattern doc",
                    "reconcile inject clear reset advance",
                    "brain_validate feasibility action",
                    "Receipt alignment after desync",
                ],
            ),
            (
                "pick-vs-inbox",
                [
                    "plan-no-asf-run pick 1 phase drain head",
                    "healthy pack inbox separate rail",
                    "Phase 1 one rail autoloop primary",
                    "br pack when broker breaks not daily",
                    "sa-0131 live pick vs br-0001 curriculum",
                    "ft pack retired ac pack dead",
                    "no pick 30 unattended",
                    "phase-first pick order law",
                    "pick script not chat memory",
                    "Receipt two rails documented",
                ],
            ),
            (
                "validate-align",
                [
                    "validate-registry-drain-rail sa_id found",
                    "brain-os plan-registry path for REGISTRY",
                    "closeout_sa_task --id matches sa_focus",
                    "prompt front matter status done",
                    "execution log YAML on closeout",
                    "PRIORITY evidence row sa_id match",
                    "forbidden closeout on ACT turn",
                    "forbidden implement on CHECK turn",
                    "machine verify before mark_done",
                    "Receipt sa alignment VERIFY",
                ],
            ),
            (
                "align-law",
                [
                    "GOAL1 activation chain INBOX match law",
                    "INCIDENT sa_mismatch broker no advance",
                    "founder does not tap Advance autoloop",
                    "executor auto advance after STOP",
                    "WORKER_ROUND_REPORT then STOP",
                    "CHECK NO implement NO closeout",
                    "ACT minimal diff NO closeout",
                    "VERIFY validators then closeout",
                    "one sa per turn MANDATORY",
                    "Receipt sa alignment law",
                ],
            ),
        ],
    ),
    (
        "phase-br4-orchestrator",
        "healthy-drain-orchestrator poll_once · deliver · advance",
        [
            (
                "poll-once",
                [
                    "poll_once after worker submit only",
                    "poll_once reads last_worker_report baseline",
                    "poll_once completed when validators pass",
                    "poll_once skip when orchestrator stopped",
                    "poll_once idempotent on duplicate submit",
                    "status idle after completed turn",
                    "status awaiting_worker after deliver",
                    "status done when queue_exhausted",
                    "updated_at on orchestrator state",
                    "reset_at manual reset_reason",
                ],
            ),
            (
                "deliver",
                [
                    "deliver_current when inbox empty",
                    "deliver returns inbox_json path",
                    "deliver reason worker_inbox_delivery",
                    "clipboard_paste false default",
                    "editor_open skipped no_editor_hijack",
                    "active_rule 099-worker-inbox-active",
                    "focus_steal false on deliver",
                    "next_deliver after completed turn",
                    "deliver_failed when queue exhausted",
                    "inbox_already_pending skip redeliver",
                ],
            ),
            (
                "advance",
                [
                    "advance-healthy-queue-v1 completed_pos",
                    "next_pos increment one per VERIFY",
                    "last_advanced_at ISO timestamp",
                    "last_completed_pos sync",
                    "skip_sa_slice false default",
                    "skipped_positions counter",
                    "advance only after broker ok true",
                    "no advance on broker no",
                    "manual advance forbidden founder",
                    "Receipt advance chain",
                ],
            ),
            (
                "roles",
                [
                    "CHECK turn step_type check",
                    "ACT turn step_type act",
                    "VERIFY turn step_type verify_backend",
                    "closeout true only VERIFY items",
                    "live_eval_required false healthy pack",
                    "forbidden OpenRouter in healthy pack",
                    "forbidden eval_1b_gate_ok true in pack",
                    "one_sa_per_turn true in queue item",
                    "mandatory_reads list in item",
                    "instruction string per queue item",
                ],
            ),
            (
                "state",
                [
                    "schema healthy-drain-orchestrator-v1",
                    "turns_completed counter",
                    "max_turns 30 default",
                    "expected_pos expected_sa expected_role",
                    "report_baseline_at for broker",
                    "delivery inbox default",
                    "await_timeout_sec 3600",
                    "last_completed_at ISO",
                    "last_report_at from worker report",
                    "stop_reason null when running",
                ],
            ),
            (
                "reset",
                [
                    "healthy-drain-orchestrator-v1.py reset",
                    "reset_reason manual documented",
                    "reset clears stale expected fields",
                    "reset after reconcile playbook",
                    "worker_inject_lib clear with reset",
                    "do not reset mid broker=yes streak",
                    "reset turns_completed policy",
                    "reset deliver after queue replay",
                    "note field in queue state",
                    "Receipt reset hygiene",
                ],
            ),
            (
                "exhaust",
                [
                    "done_all_30 true at pos 30 verify",
                    "queue_exhausted in healthy-queue-state",
                    "next_pos 31 when complete",
                    "orchestrator deliver_failed when queue exhausted",
                    "new pack replay sa-0351 slice",
                    "orchestrator stop_reason queue_exhausted",
                    "autoloop stopped queue_not_advanced",
                    "start new pack without manual paste",
                    "brain_validate queue_pos null when done",
                    "Receipt pack exhaust",
                ],
            ),
            (
                "orch-validate",
                [
                    "validate-healthy-prompt-pack-v1",
                    "healthy-queue-30-active.json schema",
                    "generate-healthy-drain-paste.sh",
                    "healthy_queue_blocker_lib feasibility",
                    "worker_drain_lib queue item load",
                    "validate-agent-loop-gate-receipt",
                    "orchestrator deliver in e2e chain",
                    "find_critical_bugs orchestrator section",
                    "Hub goal1-loop-status API",
                    "Receipt orchestrator validate",
                ],
            ),
            (
                "orch-errors",
                [
                    "poll_once when no pending report",
                    "deliver when feasibility STOP",
                    "commercial_blocker surfaces honest",
                    "timeout awaiting_worker policy",
                    "orchestrator lag metadata only",
                    "do not double deliver same pos",
                    "expected_pos behind inbox verify",
                    "reconcile before blame orchestrator",
                    "log orch_result ok false",
                    "Receipt orch error handling",
                ],
            ),
            (
                "orch-law",
                [
                    "HEALTHY_PROMPT_SEQUENCE law",
                    "REGISTRY_DRAIN_RAIL healthy pack",
                    "GOAL_EXECUTION_ACTIVE deliver action",
                    "Hub Deliver healthy drain one tap",
                    "Advance healthy queue after STOP",
                    "founder no Terminal orchestrator",
                    "PEV planner queue executor worker",
                    "verifier machine validators only",
                    "AUTO-RUN replaces manual deliver",
                    "Receipt orchestrator law",
                ],
            ),
        ],
    ),
    (
        "phase-br5-batch-log",
        "goal1-worker-batch-latest.log · AGENT START/DONE · broker=yes",
        [
            (
                "log-format",
                [
                    "AGENT START sa role timestamp Z",
                    "AGENT DONE exit broker advance report",
                    "broker=yes required for RUNNING law",
                    "broker=no stops autoloop streak",
                    "exit=0 necessary not sufficient",
                    "advance=yes when queue moved",
                    "report=yes when YAML present",
                    "chars count in DONE line",
                    "loop_turn N in JSON row",
                    "method cursor_agent_cli headless",
                ],
            ),
            (
                "log-proof",
                [
                    "INCIDENT unvalidated proof batch log",
                    "never cite PID alone as RUNNING",
                    "never cite Worker chat silence",
                    "pgrep goal1_run_loop as secondary",
                    "tail log for founder surface",
                    "hub_self_refresh before loop status",
                    "batch log SSOT over orchestrator UI",
                    "stale tail broker=no hygiene",
                    "grep count broker=yes target 50",
                    "TODAY_AUTORUN_50 morning proof",
                ],
            ),
            (
                "log-json",
                [
                    "loop_turn ok started sa_id in JSON",
                    "broker object ok error hint",
                    "orchestrator completed in JSON",
                    "advanced block in broker JSON",
                    "deliver skipped inbox_already_pending",
                    "one_sa_gate in turn JSON",
                    "fail_reason sa_mismatch in JSON",
                    "output_preview truncated in JSON",
                    "stopped true error in JSON",
                    "pos_before pos_after in stop",
                ],
            ),
            (
                "log-streak",
                [
                    "broker=yes streak 50 Phase 1 exit",
                    "3 broker=no stop_goal1_loop",
                    "prepare-only does not append DONE",
                    "deliver alone does not append DONE",
                    "ACTIVATE requires AGENT DONE line",
                    "brain_validate progress_status",
                    "progress_sa from last DONE",
                    "executor_busy from pgrep",
                    "loop progress FAILED on broker no",
                    "Receipt streak metrics",
                ],
            ),
            (
                "log-run",
                [
                    "goal1_run_loop_v1 turns parameter",
                    "start_goal1_worker_turn one turn",
                    "goal1_worker_batch_loop batch path",
                    "goal1_auto_loop prepare spawn detach",
                    "stop_goal1_loop stale clear",
                    "block_until agent done timeout",
                    "await_timeout_sec 3600 default",
                    "turn ok false stops batch",
                    "queue pos_before pos_after log",
                    "Receipt run loop log",
                ],
            ),
            (
                "log-headless",
                [
                    "agent -p -f executes inbox wrapper",
                    "Worker chat empty on headless path",
                    "visibility headless_agent_cli message",
                    "founder_surface batch log path",
                    "no_editor_hijack on loop start",
                    "Brain chat not executor on headless",
                    "cursor agent CLI expect 2-5 min",
                    "AUTO LOOP START line in log",
                    "turn M/N queue=X/30 starting",
                    "Receipt headless log law",
                ],
            ),
            (
                "log-validate",
                [
                    "validate-goal1-worker-batch-v1.sh",
                    "auto_advance in goal1_lane_broker",
                    "brain-checkpoint-ack in broker",
                    "validate-goal1-loop-activation-chain",
                    "validate-brain-run-loop-v1",
                    "goal1_auto_loop --proof flag",
                    "brain_validate loop section",
                    "find_critical_bugs batch section",
                    "E2E goal1 section broker log",
                    "Receipt log validate PASS",
                ],
            ),
            (
                "log-errors",
                [
                    "queue_not_advanced stop error",
                    "sa_mismatch fail_reason log",
                    "broker error hint in JSON",
                    "exit non-zero AGENT DONE",
                    "started true ok false turn",
                    "batch log deliver_failed after pack exhaust",
                    "stopped turn error object",
                    "BRAIN_VALIDATION activate FAIL",
                    "historical stale tail note",
                    "Receipt log error taxonomy",
                ],
            ),
            (
                "log-hub",
                [
                    "POST api run-goal1-auto-loop",
                    "founder-auto-run-healthy-10 action",
                    "api goal1-loop-status health",
                    "Hub Goal 1 loop panel",
                    "command-data goal1 block",
                    "refresh_log fleet scan ok",
                    "no Terminal founder auto run",
                    "Hub Refresh before AUTO-RUN",
                    "batch log path in Hub docs",
                    "Receipt Hub log integration",
                ],
            ),
            (
                "log-law",
                [
                    "GOAL1_EXECUTION_SOLUTION acceptance",
                    "prepare not activate law",
                    "SINA_GOAL1_LOOP_UNVALIDATED incident",
                    "RUNNING only broker=yes law",
                    "external advisor not batch truth",
                    "disk log over chat claims",
                    "morning grep broker yes count",
                    "goal-progress done delta",
                    "activate PASS morning check",
                    "Receipt batch log law",
                ],
            ),
        ],
    ),
    (
        "phase-br6-activation",
        "inject → validate → activate → sync activation chain",
        [
            (
                "inject",
                [
                    "prompt_feasibility_gate STOP_INJECT",
                    "worker_inject_lib status pending",
                    "deliver ok true required",
                    "INBOX sa_id matches orchestrator",
                    "forbidden clipboard into Brain",
                    "forbidden INBOX editor as loop start",
                    "healthy-drain-autoloop inject only no agent",
                    "brain_validate inject PASS FAIL",
                    "feasibility WARN_PICK_MISMATCH ok",
                    "Receipt inject gate",
                ],
            ),
            (
                "validate-step",
                [
                    "machine validators per CHECK ACT VERIFY",
                    "WORKER_ROUND_REPORT ends validate step",
                    "validate spine in report optional",
                    "critical_bugs in report required VERIFY",
                    "brain_validate validate PASS",
                    "find_critical_bugs at verify",
                    "validate-execution-spine-v1.sh",
                    "validate-dispatch-policy-v1.sh",
                    "validate-governance-fleet-v1.sh",
                    "Receipt validate step",
                ],
            ),
            (
                "activate-step",
                [
                    "goal1_auto_loop activates loop",
                    "start_goal1_worker_turn activates",
                    "brain_execute_turn debug activate",
                    "Worker run inbox activates visible",
                    "deliver does NOT activate",
                    "Hub lock busy does NOT activate",
                    "autoloop watch inject does NOT activate",
                    "brain_validate activate PASS FAIL",
                    "pgrep or AGENT DONE activate proof",
                    "Receipt activate step",
                ],
            ),
            (
                "sync-step",
                [
                    "broker worker-submit is SYNC",
                    "orchestrator poll_once is SYNC",
                    "queue advance is SYNC proof",
                    "brain_ack after checkpoint SYNC",
                    "brain_validate sync PASS",
                    "no advance without report SYNC law",
                    "lane broker brain-poll post SYNC",
                    "inbox clear after submit SYNC",
                    "healthy-queue-state update SYNC",
                    "Receipt sync chain",
                ],
            ),
            (
                "chain-doc",
                [
                    "GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED",
                    "four gates mandatory no skip",
                    "chain inject validate activate sync",
                    "MANDATORY_BRAIN_CHAT chain cite",
                    "MANDATORY_WORKER_CHAT chain cite",
                    "validate-goal1-loop-activation-chain",
                    "prepare-only chain inject only",
                    "full loop all four PASS",
                    "activate FAIL stale log note",
                    "Receipt activation chain doc",
                ],
            ),
            (
                "chain-fail",
                [
                    "inject FAIL feasibility STOP",
                    "validate FAIL missing YAML",
                    "activate FAIL broker no",
                    "sync FAIL queue not advanced",
                    "chain ok false brain_validate",
                    "mandatory_next when activate FAIL",
                    "run_goal1_auto_loop_activate action",
                    "awaiting_worker broker status",
                    "awaiting_brain_ack status",
                    "Receipt chain failure modes",
                ],
            ),
            (
                "chain-hub",
                [
                    "Hub AUTO-RUN runs full chain",
                    "founder one tap activation",
                    "no Worker paste when chain green",
                    "TODAY_AUTORUN_50 chain target",
                    "L2 headless when chain stable",
                    "L1 semi-auto when manual paste",
                    "chain PASS not equal L3",
                    "dispatch_ready separate gate",
                    "eval_1b separate from activate",
                    "Receipt chain vs L2",
                ],
            ),
            (
                "chain-validate",
                [
                    "validate-goal1-brain-validation-v1",
                    "validate-brain-run-loop-v1",
                    "validate-agent-loop-gate-receipt",
                    "brain_validate_goal1_v1 shim",
                    "brain-os scripts brain_validate",
                    "chain JSON in batch log",
                    "BRAIN_VALIDATION inject validate lines",
                    "goal1_auto_loop prepare chain check",
                    "E2E chain section",
                    "Receipt chain validators",
                ],
            ),
            (
                "chain-pev",
                [
                    "Planner queue item header",
                    "Executor Worker or agent CLI",
                    "Verifier machine validators",
                    "Brain routes does not execute",
                    "REGISTRY bind on VERIFY turns",
                    "closeout REGISTRY PRIORITY logs",
                    "STOP one turn executor law",
                    "founder does not verify progress",
                    "auto_pass not ASF authority",
                    "Receipt PEV chain",
                ],
            ),
            (
                "chain-law",
                [
                    "GOAL_EXECUTION_ACTIVE daily loop",
                    "FOUNDER_DAILY no Terminal",
                    "GOAL_HIERARCHY T0 factory",
                    "honest gates dispatch_ready false",
                    "Level 1 semi-auto NOW",
                    "Level 3 not claimed",
                    "Loop A default not Loop C",
                    "fast-track not activation chain",
                    "broker pack supports chain debug",
                    "Receipt activation law",
                ],
            ),
        ],
    ),
    (
        "phase-br7-checkpoint",
        "batch checkpoint · brain-checkpoint-ack · batch_running",
        [
            (
                "checkpoint-start",
                [
                    "start_batch batch_size 5 default",
                    "batch turns_in_batch zero start",
                    "batch recent_turns empty start",
                    "checkpoint after N submits",
                    "checkpoint_machine_pass logic",
                    "gate PASS required per turn",
                    "gate FAIL blocks checkpoint",
                    "turn summary gate field",
                    "critical in turn summary",
                    "Receipt checkpoint start",
                ],
            ),
            (
                "checkpoint-pending",
                [
                    "status checkpoint_pending broker",
                    "brain must ack before next batch",
                    "checkpoint blocks auto_deliver",
                    "founder reviews Hub checkpoint UI",
                    "brain_poll action checkpoint",
                    "do not inject during pending",
                    "auto_advance false when checkpoint",
                    "checkpoint path JSON SSOT",
                    "load_checkpoint on broker start",
                    "Receipt checkpoint pending",
                ],
            ),
            (
                "checkpoint-ack",
                [
                    "brain-checkpoint-ack command",
                    "brain_ack clears pending idle",
                    "note optional on ack",
                    "force ack documented danger",
                    "ack appends event jsonl",
                    "ack does not skip validators",
                    "ack after machine pass only",
                    "GOAL1_BATCH_CHECKPOINT law",
                    "batch gate receipt shape",
                    "Receipt checkpoint ack",
                ],
            ),
            (
                "batch-running",
                [
                    "status batch_running during auto",
                    "auto_advance true in submit",
                    "last_auto_deliver in state",
                    "batch_running vs idle vs stopped",
                    "batch turns_in_batch increment",
                    "recent_turns ring buffer",
                    "batch reset on start_batch",
                    "batch vs loop_turn distinction",
                    "broker_status batch_running string",
                    "Receipt batch_running",
                ],
            ),
            (
                "batch-gate",
                [
                    "GOAL1_BATCH_CHECKPOINT_LOCKED",
                    "machine pass all turns",
                    "any FAIL blocks ack",
                    "spine gate in turn summary",
                    "critical zero gate",
                    "validate dict in summary",
                    "turn_closed in summary",
                    "sa in turn summary",
                    "round_type in summary",
                    "Receipt batch gate",
                ],
            ),
            (
                "batch-hub",
                [
                    "Hub checkpoint display",
                    "founder ack one tap",
                    "no Terminal checkpoint",
                    "api broker checkpoint if exists",
                    "command-data checkpoint block",
                    "Refresh after ack",
                    "checkpoint not REGISTRY drain",
                    "parallel AUTO-RUN checkpoint",
                    "brain_watch checkpoint poll",
                    "Receipt Hub checkpoint",
                ],
            ),
            (
                "batch-errors",
                [
                    "ack without pass rejected",
                    "checkpoint stale hygiene",
                    "pending forever debug",
                    "force ack incident only",
                    "batch interrupted stop loop",
                    "broker reset checkpoint",
                    "duplicate ack idempotent",
                    "missing checkpoint file default",
                    "corrupt checkpoint recover",
                    "Receipt checkpoint errors",
                ],
            ),
            (
                "batch-validate",
                [
                    "validate-goal1-worker-batch-v1",
                    "brain-checkpoint-ack in script grep",
                    "auto_advance in broker grep",
                    "checkpoint in goal1_lane_broker",
                    "E2E checkpoint section",
                    "brain_validate checkpoint_pending",
                    "find_critical_bugs checkpoint",
                    "test start_batch smoke",
                    "test brain_ack smoke",
                    "Receipt checkpoint validate",
                ],
            ),
            (
                "batch-law",
                [
                    "batch size 5 default not 50",
                    "50 turns may include checkpoints",
                    "checkpoint not every turn",
                    "founder ack between batches",
                    "Brain not Worker ack",
                    "auto_run may hit checkpoint",
                    "resume after ack AUTO-RUN",
                    "no skip checkpoint on broker no",
                    "honest pending status",
                    "Receipt checkpoint law",
                ],
            ),
            (
                "batch-receipt",
                [
                    "SOURCEA-PRIORITY checkpoint row",
                    "WORKER_ROUND_REPORT checkpoint note",
                    "execution log checkpoint YAML",
                    "batch complete receipt",
                    "turns summarized in ack",
                    "broker events checkpoint kinds",
                    "Hub evidence screenshot path",
                    "no architecture change checkpoint",
                    "minimal diff checkpoint fixes",
                    "STOP after checkpoint turn",
                ],
            ),
        ],
    ),
    (
        "phase-br8-inbox",
        "worker_inject_lib · INBOX delivery · feasibility gate",
        [
            (
                "inject-lib",
                [
                    "worker_inject_lib deliver function",
                    "worker_inject_lib clear reason",
                    "worker_inject_lib status JSON",
                    "pending true false honest",
                    "schema worker-prompt-inbox-v1",
                    "delivered_at ISO field",
                    "lane sourcea_worker",
                    "workspace SourceA root path",
                    "chars prompt length",
                    "pickup worker_chat instruction",
                ],
            ),
            (
                "inject-deliver",
                [
                    "healthy-drain-orchestrator deliver",
                    "Hub Deliver healthy drain action",
                    "generate-healthy-drain-paste.sh",
                    "worker_check source inbox",
                    "orchestrator source inbox",
                    "deliver ok false error",
                    "delivered inbox string",
                    "injected false headless",
                    "clipboard_paste false default",
                    "Receipt deliver path",
                ],
            ),
            (
                "inject-feasibility",
                [
                    "prompt_feasibility_gate worker role",
                    "prompt_feasibility_gate brain role",
                    "STOP_INJECT action",
                    "PROCEED action ok true",
                    "WARN_PICK_MISMATCH action",
                    "blocked_count in feasibility",
                    "feasible true false",
                    "strict mode feasibility",
                    "no inject impossible ACT",
                    "Receipt feasibility",
                ],
            ),
            (
                "inject-clear",
                [
                    "clear after broker submit",
                    "clear reason broker_worker_submit",
                    "clear before reconcile",
                    "worker_inject_lib --clear CLI",
                    "pending false after clear",
                    "do not clear before submit",
                    "stale pending blocks inject",
                    "clear vs deliver order",
                    "inject FAIL pending false",
                    "Receipt inject clear",
                ],
            ),
            (
                "inject-meta",
                [
                    "meta queue_pos total role sa_id",
                    "prompt header GOAL1_HEALTHY_DRAIN",
                    "role verify in header",
                    "queue N/30 in header",
                    "REGISTRY bind line in prompt",
                    "FORBIDDEN block in prompt",
                    "mandatory_reads in prompt body",
                    "THIS TURN section CHECK ACT VERIFY",
                    "path prompts phase sa md",
                    "Receipt inject meta",
                ],
            ),
            (
                "inject-rules",
                [
                    "099-worker-inbox-active mdc rule",
                    "ignore_if_brain on pickup",
                    "Brain must not execute inbox",
                    "Worker opens say run inbox",
                    "inbox_md sina-loop path",
                    "no paste into Brain chat",
                    "founder does not copy inbox",
                    "Hub deliver not clipboard",
                    "editor tab optional not start",
                    "Receipt inject rules",
                ],
            ),
            (
                "inject-errors",
                [
                    "deliver when queue exhausted",
                    "deliver when STOP_INJECT",
                    "stale sa-0142 inbox hygiene",
                    "meta mismatch orchestrator brief",
                    "pending true blocks redeliver",
                    "chars zero invalid",
                    "missing meta sa_id",
                    "wrong workspace path",
                    "inject without orchestrator",
                    "Receipt inject errors",
                ],
            ),
            (
                "inject-validate",
                [
                    "validate-agent-loop-gate-receipt",
                    "worker inject in activation chain",
                    "brain_validate inbox section",
                    "goal1_auto_loop deliver step",
                    "prepare-only inbox pending check",
                    "validate-worker-inbox if exists",
                    "find_critical_bugs inject section",
                    "E2E inject gate",
                    "feasibility in entry gate",
                    "Receipt inject validate",
                ],
            ),
            (
                "inject-autoloop",
                [
                    "goal1_auto_loop deliver if empty",
                    "prepare-only skips spawn",
                    "spawn detached goal1_run_loop",
                    "stop before new autoloop",
                    "inbox_pending in prepare JSON",
                    "deliver null when pending",
                    "orchestrator_brief in prepare",
                    "visibility headless message",
                    "AUTO-RUN uses same deliver",
                    "Receipt autoloop inject",
                ],
            ),
            (
                "inject-law",
                [
                    "INJECT gate activation chain",
                    "deliver not activate",
                    "Hub one tap deliver",
                    "founder no Terminal inject",
                    "Worker pickup disk not memory",
                    "br pack not replace autoloop",
                    "manual paste when autoloop breaks",
                    "TODAY plan AUTO-RUN primary",
                    "inject supports broker chain",
                    "Receipt inject law",
                ],
            ),
        ],
    ),
    (
        "phase-br9-run-loop",
        "goal1_run_loop · goal1_auto_loop · stop_goal1_loop integration",
        [
            (
                "auto-loop",
                [
                    "goal1_auto_loop_v1.py entry",
                    "prepare-only turns json",
                    "spawn_detached run loop",
                    "stop_goal1_loop before start",
                    "feasibility gate first step",
                    "deliver if inbox empty",
                    "turns parameter 10 50",
                    "proof flag batch log check",
                    "json output machine",
                    "Receipt auto loop",
                ],
            ),
            (
                "run-loop",
                [
                    "goal1_run_loop_v1.py child",
                    "start_goal1_worker_turn per turn",
                    "pos_before pos_after tracking",
                    "broker_ok in turn row",
                    "stopped on turn fail",
                    "queue_not_advanced stop",
                    "turn ok false break",
                    "loop_turn increment",
                    "message turn complete",
                    "Receipt run loop",
                ],
            ),
            (
                "worker-turn",
                [
                    "start_goal1_worker_turn_v1.py",
                    "agent -p -f invocation",
                    "inbox wrapper prompt path",
                    "exit_code in result",
                    "broker dict in result",
                    "one_sa_gate in result",
                    "output_preview truncate",
                    "method cursor_agent_cli",
                    "started true false",
                    "Receipt worker turn",
                ],
            ),
            (
                "stop-loop",
                [
                    "stop_goal1_loop_v1.py clear stale",
                    "stop pids goal1_run_loop",
                    "stop agent -p -f children",
                    "broker state reset partial",
                    "stop after 3 broker no",
                    "founder Hub stop if offered",
                    "stop before reconcile",
                    "stop reason in log",
                    "executor_busy false after stop",
                    "Receipt stop loop",
                ],
            ),
            (
                "watch-loop",
                [
                    "brain_watch_loop_v1.py poll",
                    "healthy-drain-autoloop inject only",
                    "autoloop does not call agent",
                    "watch not substitute AUTO-RUN",
                    "brain_run_loop spawn only",
                    "narrate loop no spawn",
                    "validate-brain-narrate-not-execute",
                    "watch interval config",
                    "ACTIVATE step in watch budget",
                    "Receipt watch vs run",
                ],
            ),
            (
                "hub-loop",
                [
                    "POST api run-goal1-auto-loop",
                    "founder-auto-run-healthy-10",
                    "serve-sina-command hub up",
                    "api goal1-loop-status",
                    "Hub Refresh before run",
                    "no Terminal AUTO-RUN",
                    "command-data loop block",
                    "Goal 1 loop panel UI",
                    "AUTO-RUN 50 tonight plan",
                    "Receipt Hub loop",
                ],
            ),
            (
                "loop-errors",
                [
                    "fragile shell 30s incident",
                    "detached start_new_session fix",
                    "exit 143 stop mid turn",
                    "broker no break streak",
                    "sa_mismatch break streak",
                    "queue_not_advanced end",
                    "prepare ok false no spawn",
                    "feasibility STOP no spawn",
                    "hub down no AUTO-RUN",
                    "Receipt loop errors",
                ],
            ),
            (
                "loop-validate",
                [
                    "validate-goal1-auto-loop-v1.sh",
                    "validate-goal1-loop-activation-chain",
                    "validate-brain-run-loop-v1",
                    "goal1_auto_loop in enforcement",
                    "E2E loop section",
                    "brain_validate loop section",
                    "find_critical_bugs loop",
                    "proof flag incident check",
                    "prepare inject PASS",
                    "Receipt loop validate",
                ],
            ),
            (
                "loop-law",
                [
                    "two products do not merge",
                    "goal1_auto_loop not agent_loop",
                    "10loop keyword separate",
                    "bridge only if healthy_queue_status",
                    "headless default lane",
                    "Worker visible optional",
                    "founder watches batch log",
                    "L2 when AUTO-RUN stable",
                    "br pack when loop breaks",
                    "Receipt run loop law",
                ],
            ),
            (
                "loop-receipt",
                [
                    "SOURCEA-PRIORITY autoloop row",
                    "WORKER_ROUND_REPORT when visible",
                    "headless YAML in agent stdout",
                    "broker submit after headless",
                    "50 broker yes streak",
                    "goal-progress delta",
                    "activate PASS morning",
                    "s1 backlog shrinking",
                    "no new daemon file",
                    "Receipt loop complete",
                ],
            ),
        ],
    ),
    (
        "phase-br10-broker-e2e",
        "Broker E2E · governance receipts · pack hygiene",
        [
            (
                "e2e-broker",
                [
                    "validate-goal1-lane-broker-v1.sh end",
                    "validate-goal1-e2e-v1 broker section",
                    "brain-poll smoke in e2e",
                    "worker-submit shape in e2e",
                    "orchestrator poll in e2e",
                    "one_sa gate in e2e",
                    "batch log in e2e optional",
                    "find_critical_bugs broker path",
                    "audit_backend_e2e sufficient",
                    "Receipt broker e2e",
                ],
            ),
            (
                "e2e-validate",
                [
                    "brain_validate full chain",
                    "validate-goal1-brain-validation",
                    "validate-brain-run-loop",
                    "validate-agent-loop-gate-receipt",
                    "validate-worker-one-sa-turn",
                    "validate-execution-spine-v1",
                    "validate-governance-fleet-v1",
                    "skip validate-sourcea-e2e-full noise",
                    "critical 0 at VERIFY",
                    "Receipt e2e validate",
                ],
            ),
            (
                "e2e-state",
                [
                    "goal1-lane-broker-v1.json schema",
                    "goal1-lane-broker-events.jsonl",
                    "brain-broker-inbox-v1.json",
                    "worker-prompt-inbox-v1.json",
                    "healthy-drain-orchestrator-v1.json",
                    "healthy-queue-state-v1.json",
                    "goal1-batch-checkpoint-v1.json",
                    "goal1-worker-batch-latest.log",
                    "today-plan-active-v1.json",
                    "Receipt e2e state paths",
                ],
            ),
            (
                "pack-hygiene",
                [
                    "broker-pack-1000 unique titles",
                    "no tier mirrors br pack",
                    "distinct from ft- fast track",
                    "distinct from sa- sourcea drain",
                    "distinct from ac- retired pack",
                    "br-0001 br-1000 ids",
                    "regenerate generate-broker-pack-1000",
                    "pick plan-broker-pack-run.sh",
                    "curriculum when broker breaks",
                    "Receipt pack hygiene",
                ],
            ),
            (
                "pack-pick",
                [
                    "plan-broker-pack-run.sh pick 1",
                    "pick-broker-pack-plan.py backlog",
                    "first pick br-0001 prepare only",
                    "status backlog done in REGISTRY",
                    "closeout mark_done br VERIFY",
                    "PRIORITY row br id",
                    "not daily pick if AUTO-RUN green",
                    "parallel sourcea pick 1 drain",
                    "phase-first sa drain primary",
                    "Receipt pack pick law",
                ],
            ),
            (
                "governance",
                [
                    "WORKER_ROUND_REPORT required",
                    "external receipt compare only",
                    "no reorder REGISTRY from chat",
                    "no invent sa or br ids",
                    "disk validators truth",
                    "Hub only founder",
                    "Level 3 not claimed",
                    "dispatch_ready founder gate",
                    "eval_1b honest gate",
                    "Receipt governance",
                ],
            ),
            (
                "cross-pack",
                [
                    "AUTOMATION_CONVERGE program parent",
                    "TODAY_AUTORUN_50 active today",
                    "fast-track-100 debug curriculum",
                    "sourcea-1000 factory drain",
                    "broker-pack broker spine only",
                    "no duplicate ft titles",
                    "no duplicate sa titles",
                    "RETIRED ac-1000 marker",
                    "INDEX broker pack entry",
                    "Receipt cross-pack",
                ],
            ),
            (
                "receipt-close",
                [
                    "closeout_sa_task br VERIFY only",
                    "REGISTRY br status done",
                    "SOURCEA-PRIORITY evidence",
                    "REPO_EXECUTION_LOGS yaml",
                    "execution log schema",
                    "turn closed worker_turn_lib",
                    "broker ok true at closeout",
                    "find_critical_bugs 0",
                    "WORKER_ROUND_REPORT STOP",
                    "Receipt closeout",
                ],
            ),
            (
                "morning-proof",
                [
                    "grep broker yes count 50",
                    "brain_validate activate PASS",
                    "goal-progress done moved",
                    "dispatch_ready if confirmed",
                    "eval_1b still true",
                    "inbox pending honest",
                    "orchestrator phase honest",
                    "no stale broker no tail",
                    "Hub Refresh sync PRIORITY",
                    "Receipt morning proof",
                ],
            ),
            (
                "pack-complete",
                [
                    "br-1000 last id broker e2e",
                    "pack count 1000 locked true",
                    "library broker-pack-1000-locked",
                    "agent AGENT-AUTO-SOURCEA",
                    "trigger PLAN WITH NO ASF BROKER",
                    "10 phases 100 each grid",
                    "program BROKER-PACK-1000-LOCK",
                    "runtime mirror sina REGISTRY",
                    "forbidden 1000 manual pastes",
                    "Receipt pack complete br-1000",
                ],
            ),
        ],
    ),
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _collect_tasks() -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    for phase_key, phase_desc, groups in PHASE_SPEC:
        assert len(groups) == 10, phase_key
        for area, probes in groups:
            assert len(probes) == 10, phase_key
            for probe in probes:
                # Area prefix guarantees global title uniqueness across phases
                out.append((phase_key, phase_desc, f"{area}: {probe}"))
        assert len([t for t in out if t[0] == phase_key]) == 100, phase_key
    assert len(out) == 1000
    return out


def _md(br_id: str, phase_key: str, phase_desc: str, slot: int, title: str) -> str:
    ap = (
        f"PLAN WITH NO ASF — BROKER — {br_id}: {title}. "
        f"Pack: broker-pack-1000 · Worker broker chain only. "
        f"End: WORKER_ROUND_REPORT → goal1_lane_broker worker-submit → STOP. "
        f"Default runtime: Hub AUTO-RUN headless — use this prompt only when broker breaks."
    )
    return f"""---
id: {br_id}
phase: {phase_key}
tier: T0
priority: P0
status: backlog
lane: sourcea_worker
library: broker-pack-1000-locked
agent: {AGENT}
agent_tag: {TAG}
written_at: 2026-06-07
slot: {slot}
generator: scripts/generate-broker-pack-1000.py
locked: true
pack_role: broker_curriculum
---

# [{TAG}] {br_id} — {title}

**Phase:** `{phase_key}` — {phase_desc}

## Broker law

- One turn · one sa or br closeout · YAML → broker submit · no architecture redesign
- Not a substitute for Hub ▶ AUTO-RUN 50 or `plan-no-asf-run.sh pick 1` factory drain
- Distinct from `ft-*` fast-track and `sa-*` sourcea-1000 (no shared titles)

## Agent prompt

```
{ap}
```

## Task

{title}

## Verify

```bash
{VERIFY}
```
"""


def _load_foreign_titles() -> set[str]:
    foreign: set[str] = set()
    for rel in (
        "brain-os/plan-registry/automation-fast-track-100/REGISTRY.json",
        "brain-os/plan-registry/sourcea-1000/REGISTRY.json",
    ):
        path = ROOT / rel
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            for pl in data.get("plans") or []:
                foreign.add((pl.get("title") or "").strip().lower())
    ac = ROOT / "brain-os/plan-registry/automation-converge-1000/REGISTRY.json"
    if ac.is_file():
        data = json.loads(ac.read_text(encoding="utf-8"))
        for pl in data.get("plans") or []:
            foreign.add((pl.get("title") or "").strip().lower())
    return foreign


def main() -> int:
    tasks = _collect_tasks()
    foreign = _load_foreign_titles()

    if PROMPTS.exists():
        shutil.rmtree(PROMPTS)
    PROMPTS.mkdir(parents=True, exist_ok=True)

    plans: list[dict] = []
    titles: set[str] = set()
    collisions: list[str] = []

    for n, (phase_key, _phase_desc, title) in enumerate(tasks, start=1):
        br_id = f"br-{n:04d}"
        key = title.strip().lower()
        if key in titles:
            raise SystemExit(f"FAIL: duplicate title in broker pack: {title}")
        if key in foreign:
            collisions.append(title)
        titles.add(key)

        phase_dir = PROMPTS / phase_key
        phase_dir.mkdir(parents=True, exist_ok=True)
        slot = ((n - 1) % 100) + 1
        phase_desc = next(d for k, d, _ in PHASE_SPEC if k == phase_key)
        rel = f"prompts/{phase_key}/{br_id}.md"
        (phase_dir / f"{br_id}.md").write_text(
            _md(br_id, phase_key, phase_desc, slot, title), encoding="utf-8"
        )
        plans.append(
            {
                "id": br_id,
                "phase": phase_key,
                "tier": "T0",
                "priority": "P0",
                "lane": "sourcea_worker",
                "slot": slot,
                "title": title,
                "path": rel,
                "status": "backlog",
                "verify": VERIFY,
                "agent_tag": TAG,
                "agent_prompt": f"PLAN WITH NO ASF — BROKER — {br_id}: {title}",
            }
        )

    if collisions:
        print(f"WARN: {len(collisions)} titles overlap foreign packs (substring) — review")
        for c in collisions[:5]:
            print(f"  - {c[:70]}")

    registry = {
        "schema_version": 1,
        "library": "broker-pack-1000-locked",
        "locked": True,
        "count": 1000,
        "unique": True,
        "no_tier_duplication": True,
        "broker_scope": True,
        "generated_at": _now(),
        "agent": AGENT,
        "grid": "10 broker phases × 100 unique probes = 1000",
        "trigger": "PLAN WITH NO ASF — BROKER",
        "pick_script": "scripts/plan-broker-pack-run.sh",
        "program_doc": PROGRAM,
        "distinct_from": [
            "sourcea-1000 (sa-* factory drain)",
            "automation-fast-track-100 (ft-* Musk curriculum)",
            "automation-converge-1000 (retired ac-* tier mirrors)",
        ],
        "runtime_default": "Hub AUTO-RUN 50 + goal1_run_loop_v1.py — not 1000 manual pastes",
        "plans": plans,
    }
    PACK.mkdir(parents=True, exist_ok=True)
    (PACK / "REGISTRY.json").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    lock = ROOT / "brain-os/plan-registry/BROKER-PACK-1000-LOCK.md"
    lock.write_text(
        f"""# Broker Pack 1000 — LOCKED (Goal1 lane broker)

**Count:** 1000 unique prompts · **IDs:** `br-0001` … `br-1000`  
**Scope:** `goal1_lane_broker` · worker-submit · brain-poll/ack · orchestrator · batch log  
**NOT:** sourcea-1000 drain · ft-* fast-track · retired ac-* pack

## Pick (curriculum — when broker breaks)

```bash
bash scripts/plan-broker-pack-run.sh pick 1
```

## Regenerate

```bash
python3 scripts/generate-broker-pack-1000.py
```

## Runtime default

**Hub ▶ AUTO-RUN 50** + `goal1_run_loop_v1.py` — parallel **factory drain:** `plan-no-asf-run.sh pick 1`

## Grid

10 phases × 100 unique broker probes — zero tier mirrors.
""",
        encoding="utf-8",
    )

    mirror = Path.home() / ".sina" / "broker-pack-1000-REGISTRY.json"
    mirror.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    print(f"OK: broker-pack-1000 · {len(plans)} unique prompts · mirror {mirror}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
