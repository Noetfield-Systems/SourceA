#!/usr/bin/env python3
"""Build founder daily prompt pack — v1 mined · v2 smart · v3 pro (all frozen on rebuild).

Output:
  ~/.sina/founder-prompt-pack-index.json
  ~/.sina/founder-prompt-pack-v1-mined.json
  ~/.sina/founder-prompt-pack-v2-smart.json
  ~/.sina/founder-prompt-pack-v3-pro.json
  ~/.sina/founder-prompt-pack-v1.json (alias → v3 active)
  archive/attachments/2026-06-14/FOUNDER_DAILY_PROMPT_PACK_v{1,2,3}_*.md
  FOUNDER_DAILY_PROMPT_PACK_LOCKED_v1.md (router index)
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from founder_prompt_pack_versions import V1_MINED, V2_SMART

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
ATTACH = ROOT / "archive/attachments/2026-06-14"
OUT_JSON_V3 = SINA / "founder-prompt-pack-v3-pro.json"
OUT_JSON_V2 = SINA / "founder-prompt-pack-v2-smart.json"
OUT_JSON_V1 = SINA / "founder-prompt-pack-v1-mined.json"
OUT_JSON_INDEX = SINA / "founder-prompt-pack-index.json"
OUT_JSON_ACTIVE = SINA / "founder-prompt-pack-v1.json"  # backward compat → v3 active
OUT_MD_V3 = ATTACH / "FOUNDER_DAILY_PROMPT_PACK_v3_PRO_LOCKED.md"
OUT_MD_V2 = ATTACH / "FOUNDER_DAILY_PROMPT_PACK_v2_SMART_LOCKED.md"
OUT_MD_V1 = ATTACH / "FOUNDER_DAILY_PROMPT_PACK_v1_MINED_LOCKED.md"
OUT_MD_LEGACY = ATTACH / "FOUNDER_DAILY_PROMPT_PACK_LOCKED_v1.md"  # alias → v3
ROUTER_MD = ROOT / "FOUNDER_DAILY_PROMPT_PACK_LOCKED_v1.md"
PACK_SIZE = 100

CURSOR = {
    "mode": "Agent",
    "rules": "Executor runs shell — founder never Terminal",
    "attach": "@LOCKED law or @scripts/ when scope is governance or machine",
    "proof": "Every reply ends with receipt path or PASS/FAIL — not vibes",
    "formula": "ACTION + SCOPE + CONSTRAINTS + DONE-WHEN",
}

# v3 pro long: full paste-ready orders for Cursor Agent mode
PRO: list[dict] = [
    # ── ONE-WORD ROUTERS (6) — trigger expands to full pipeline
    {
        "id": "001", "cat": "one_word", "len": 3,
        "text": (
            "orientation — Run scripts/agent_orientation_pipeline_v1.py for role worker. "
            "Load rules-in-charge, reading pack, and session truth from disk only; no code edits and no INBOX execution. "
            "Done when ~/.sina/agent-orientation-receipt-v1.json shows ok:true and you paste orientation summary plus one recommended next action."
        ),
    },
    {
        "id": "002", "cat": "one_word", "len": 3,
        "text": (
            "hospital — Run scripts/agent_hospital_pipeline_v1.py --role worker. "
            "Execute memory sync, session gate, dual heal, and honest registry checks in pipeline order; escalate to maze only if machine sets critical_count > 0. "
            "Done when ~/.sina/agent-hospital-receipt-v1.json is written with discharge note or explicit maze escalation path."
        ),
    },
    {
        "id": "003", "cat": "one_word", "len": 3,
        "text": (
            "maze — Run scripts/agent_maze_pipeline_v1.py --role worker only after hospital escalation or explicit quarantine flag. "
            "Complete gauntlet steps in order; do not skip passport or self-validate recursion. "
            "Done when maze passport receipt exists and ~/.sina/agent-maze-quarantine-v1.json status is cleared or documented BLOCKED with reason."
        ),
    },
    {
        "id": "004", "cat": "one_word", "len": 3,
        "text": (
            "calibrate — Run scripts/machine_calibrate_pipeline_v1.py. "
            "Map validators, upgrade board, and machine registry from disk; read-only except calibrate receipt writes. "
            "Done when ~/.sina/machine-calibrate-receipt-v1.json lists mapped validators and any gaps with file paths."
        ),
    },
    {
        "id": "005", "cat": "one_word", "len": 3,
        "text": (
            "tune — Run scripts/machine_tune_pipeline_v1.py --ladder-tier daily. "
            "Execute daily test ladder, refresh baseline, and sync H2 maintainer_ship if UP rows apply. "
            "Done when ~/.sina/machine-tune-receipt-v1.json and machine-test-ladder-receipt-v1.json both show steps_passed with escalate_forge false or explicit forge hold."
        ),
    },
    {
        "id": "006", "cat": "one_word", "len": 3,
        "text": (
            "forge — Run scripts/machine_forge_pipeline_v1.py (machine prove — NOT Forge product) --ladder-tier weekly (or monthly if flagged). "
            "Prove upgrade with before/after baseline and full ladder tier; block factory ship if critical_count > 0. "
            "Done when machine prove receipt ok:true and critical_count is 0 in ~/.sina/find-bugs/last-run.json."
        ),
    },
    # ── FACTORY (12)
    {
        "id": "007", "cat": "factory", "len": 4,
        "text": (
            "Execute one full Worker INBOX turn end-to-end. Read ~/.sina/worker-prompt-inbox-v1.json and the bound sa_id on disk; run the disk prompt exactly with no scope creep. "
            "Broker-submit when the turn completes and stop — do not batch a second sa. "
            "Done when WORKER_ROUND_REPORT YAML is written, orchestrator advanced, and you paste receipt path plus new queue head."
        ),
    },
    {
        "id": "008", "cat": "factory", "len": 4,
        "text": (
            "INBOX CHECK turn only for the currently bound sa. Read disk prompt and sa metadata; run read-only validators and gap analysis — zero file edits this turn. "
            "Produce a structured gap report: what is missing, what blocks ACT, and which validator would prove readiness. "
            "Done when gap report is pasted with PASS/FAIL per check and explicit GO/NO-GO for ACT."
        ),
    },
    {
        "id": "009", "cat": "factory", "len": 4,
        "text": (
            "INBOX ACT turn only: implement minimal diff strictly for the bound sa_id — match repo conventions, no drive-by refactors. "
            "Run only validators required to prove the act; do not write closeout or broker-submit yet. "
            "Done when diff is scoped, cited files changed, and validator output shows ACT checks green or BLOCKED with reason."
        ),
    },
    {
        "id": "010", "cat": "factory", "len": 4,
        "text": (
            "INBOX VERIFY turn only: re-run full validator set for bound sa, write honest closeout, and confirm critical_count is 0. "
            "Then broker-submit and confirm orchestrator idle or advanced correctly. "
            "Done when VERIFY receipt path pasted, critical_count 0, and WORKER_ROUND_REPORT last lines match expected sa/role."
        ),
    },
    {
        "id": "011", "cat": "factory", "len": 3,
        "text": (
            "Show factory-now snapshot from disk only — no hub HTML scrape. "
            "Report queue head sa_id, role, position, factory mode, turn open/closed, and inbox pending flag. "
            "Done when all fields cite JSON paths and mismatches vs last broker report are listed."
        ),
    },
    {
        "id": "012", "cat": "factory", "len": 4,
        "text": (
            "If orchestrator is idle and inbox has a pending prompt, run exactly one INBOX turn. "
            "If blocked by feasibility gate, kill_flag, or SINGLE_SA hold, print BLOCKED with disk reason — do not force through. "
            "Done when turn completed with broker advance OR explicit BLOCKED line with file path evidence."
        ),
    },
    {
        "id": "013", "cat": "factory", "len": 4,
        "text": (
            "Fix turn-bind drift: goal1-worker-turn-bind and headsup must match queue head sa on disk. "
            "Show before/after for every field that changed; minimal fix only — no unrelated edits. "
            "Done when bind JSON matches orchestrator expected sa and validate step for turn-bind passes."
        ),
    },
    {
        "id": "014", "cat": "factory", "len": 3,
        "text": (
            "Broker submit after this turn: ensure WORKER_ROUND_REPORT YAML footer is complete and orchestrator advances queue position. "
            "If submit fails, diagnose from disk logs — do not claim success from chat. "
            "Done when orchestrator state after submit is pasted with sa_id and role confirmed."
        ),
    },
    {
        "id": "015", "cat": "factory", "len": 3,
        "text": (
            "Drain exactly one sa from plan-no-asf-run.sh output — pick the first eligible row, execute fully, then stop. "
            "No batch drain, no parallel sa work. "
            "Done when that single sa shows completed status on disk and you paste which sa_id was drained."
        ),
    },
    {
        "id": "016", "cat": "factory", "len": 3,
        "text": (
            "If this chat round was tagged SINA_LOOP, POST agent-loop response via API with one-line summary plus full body. "
            "Founder does not run curl — you execute. "
            "Done when API returns ok and you paste round number advanced."
        ),
    },
    {
        "id": "017", "cat": "factory", "len": 4,
        "text": (
            "Run prompt_feasibility_gate for worker strict before any INBOX ACT. "
            "If STOP_INJECT or feasibility fail, report verdict and do not implement — add gap to Form or H2 deferred if needed. "
            "Done when gate JSON pasted with inject_allowed true/false and explicit next step."
        ),
    },
    {
        "id": "018", "cat": "factory", "len": 3,
        "text": (
            "Never claim this turn done without a disk receipt that moved state. "
            "Cite exact path, ok field, and timestamp from receipt JSON. "
            "Done when receipt path is in your last message or status is honestly BLOCKED with missing receipt reason."
        ),
    },
    # ── CHECK (20)
    {
        "id": "019", "cat": "check", "len": 4,
        "text": (
            "Daily health snapshot from disk JSON only — no hub color as truth. "
            "Report queue head sa_id, critical_count from find-bugs, form open_questions_count, and H1 worker-hub/v1 health fields. "
            "Done when all four metrics cite file paths and any STALE hub-vs-receipt mismatch is flagged."
        ),
    },
    {
        "id": "020", "cat": "check", "len": 3,
        "text": (
            "Run validate-super-fast-hub-v1.sh and validate-two-hub-v1.sh sequentially. "
            "Report PASS/FAIL only — if FAIL, paste first failing line and file, not a summary essay. "
            "Done when both scripts exit and verdict table is in your reply."
        ),
    },
    {
        "id": "021", "cat": "check", "len": 3,
        "text": (
            "Run find_critical_bugs.py and read ~/.sina/find-bugs/last-run.json. "
            "Report critical_count, verdict, and top issue titles if count > 0. "
            "Done when count is numeric and ship-talk is blocked if critical_count > 0."
        ),
    },
    {
        "id": "022", "cat": "check", "len": 3,
        "text": (
            "Run agentic_layer_pipeline_v2.py --tier fast --json. "
            "Report health.status, issue count, and first three issue ids if unhealthy. "
            "Done when JSON health block is pasted or PASS with zero issues stated."
        ),
    },
    {
        "id": "023", "cat": "check", "len": 4,
        "text": (
            "Blocker sweep: read architect_report.yaml and global_blockers from disk. "
            "List every open P0 with owner, age, and fix-or-escalate recommendation — one action per blocker. "
            "Done when P0 table is complete or explicit 'zero P0' with file mtime cited."
        ),
    },
    {
        "id": "024", "cat": "check", "len": 3,
        "text": (
            "Cross-chat drift audit: compare Worker, Brain, and Maintainer last claims to current disk receipts. "
            "List mismatches only — skip aligned rows. "
            "Done when drift list is empty or each mismatch has disk truth and suggested single fix."
        ),
    },
    {
        "id": "025", "cat": "check", "len": 4,
        "text": (
            "Ingest check: SinaPromptOS outputs/inbox/rejected/ must be empty. "
            "If any files exist, run repair_promptos_rejected_ingest and re-check until empty or BLOCKED. "
            "Done when rejected dir file count is 0 with ls evidence or repair receipt pasted."
        ),
    },
    {
        "id": "026", "cat": "check", "len": 3,
        "text": (
            "Broker check: last WORKER_ROUND_REPORT must match orchestrator expected sa_id and role. "
            "If mismatch, identify bind drift vs broker bug — do not guess. "
            "Done when match confirmed or mismatch table with both disk sources cited."
        ),
    },
    {
        "id": "027", "cat": "check", "len": 3,
        "text": (
            "Session gate: run agent_session_gate_run_v1.py --role worker --json. "
            "Paste gate_id, ok, and fail reason if any. "
            "Done when gate JSON is in reply — worker factory blocked if ok:false."
        ),
    },
    {
        "id": "028", "cat": "check", "len": 3,
        "text": (
            "Registry honesty: dry-run enforce_honest_registry and list unproven done rows only. "
            "Do not auto-fix — report ids that claim done without receipt proof. "
            "Done when unproven list is pasted or 'zero unproven' with dry-run output snippet."
        ),
    },
    {
        "id": "029", "cat": "check", "len": 3,
        "text": (
            "Anti-staleness spot check: run validate-hub-p0-no-autorun-v1.sh (INCIDENT-028 class). "
            "Report PASS/FAIL — staleness means hub green but disk stale. "
            "Done when script verdict pasted; if FAIL, name stale artifact path."
        ),
    },
    {
        "id": "030", "cat": "check", "len": 3,
        "text": (
            "Hub alignment: run audit_hub_source_alignment.py — compare WTM active steps vs hub surface fields. "
            "List gaps where hub shows step not in SSOT or SSOT step missing from hub. "
            "Done when gap count and top three ids are pasted."
        ),
    },
    {
        "id": "031", "cat": "check", "len": 4,
        "text": (
            "Read-only audit this scope — zero file edits. "
            "List gaps with exact file paths and one suggested next single action per gap. "
            "Done when audit table is complete and ends with recommended order 1-2-3 for founder clicks only."
        ),
    },
    {
        "id": "032", "cat": "check", "len": 3,
        "text": (
            "Two-hub sibling check: H1 worker-hub/v1 payload must stay small (<16KB); H2 machine-hub health must be fresh on disk. "
            "Confirm H2 is not nested inside H1 UI response. "
            "Done when sizes, mtimes, and sibling separation are cited."
        ),
    },
    {
        "id": "033", "cat": "check", "len": 3,
        "text": (
            "Agentic wire: run validate-agentic-layer-wire-v1.sh — Brain L1 L2 master must PASS. "
            "If FAIL, paste first broken wire and owning script. "
            "Done when PASS/FAIL verdict with script exit code."
        ),
    },
    {
        "id": "034", "cat": "check", "len": 3,
        "text": (
            "Governance fast: governance_center_run_v1.py --tier fast --json. "
            "Report any failing step id and law file pointer. "
            "Done when fast tier JSON shows all pass or named failures only."
        ),
    },
    {
        "id": "035", "cat": "check", "len": 3,
        "text": (
            "Quarantine flags: read agent-maze-quarantine-v1.json and machine-forge-quarantine on disk. "
            "Report active true/false for each and what pipeline is blocked. "
            "Done when both flags cited with timestamps."
        ),
    },
    {
        "id": "036", "cat": "check", "len": 4,
        "text": (
            "E2E factory loop proof: inbox pending → execute turn → broker advanced → orchestrator idle. "
            "Report each step with disk evidence — skip if already mid-turn. "
            "Done when four-step chain is PASS or first failing step named BLOCKED."
        ),
    },
    {
        "id": "037", "cat": "check", "len": 3,
        "text": (
            "Compare UI vs receipt: if hub shows green but receipt mtime is old, receipt wins — say STALE. "
            "Name the stale receipt path and recommended heal action. "
            "Done when truth source is declared and mismatch resolved or escalated."
        ),
    },
    {
        "id": "038", "cat": "check", "len": 4,
        "text": (
            "Give me a 5-line founder status report from disk: (1) top P0 task (2) queue head (3) open blockers count (4) critical_count (5) next one H1 click for me. "
            "No Terminal steps for founder. "
            "Done when exactly five numbered lines with JSON paths in parentheses."
        ),
    },
    # ── FIX / HEAL (14)
    {
        "id": "039", "cat": "fix", "len": 4,
        "text": (
            "Auto-heal routine: run hub_dual_heal_v1.py then machine_tune_pipeline_v1.py --ladder-tier daily. "
            "Paste both receipt ok lines; if either fails, stop and report — do not proceed to INBOX. "
            "Done when dual-heal and tune receipts both ok:true or BLOCKED with fix plan."
        ),
    },
    {
        "id": "040", "cat": "fix", "len": 4,
        "text": (
            "Fix the single highest P0 blocker only — minimal diff, one validator proof, then stop. "
            "Do not fix lower priority items in the same turn. "
            "Done when P0 id is closed on disk and validator PASS pasted."
        ),
    },
    {
        "id": "041", "cat": "fix", "len": 3,
        "text": (
            "Hospital this worker agent: run agent_hospital_pipeline_v1.py --role worker. "
            "Paste discharge note or maze escalation — do not skip memory sync. "
            "Done when agent-hospital-receipt-v1.json ok field pasted."
        ),
    },
    {
        "id": "042", "cat": "fix", "len": 3,
        "text": (
            "If critical_count > 0, do not ship feature work — run forge or fix root cause until critical_count is 0. "
            "Factory INBOX ACT is forbidden until bugs receipt clears. "
            "Done when find-bugs last-run shows critical_count 0 or explicit BLOCKED with bug ids."
        ),
    },
    {
        "id": "043", "cat": "fix", "len": 4,
        "text": (
            "Repair yesterday's session drift: re-read receipts from last session, fix orphan turn or stale bind. "
            "Show before/after for orchestrator and turn-bind JSON. "
            "Done when queue head matches bind and no orphan WORKER_ROUND_REPORT."
        ),
    },
    {
        "id": "044", "cat": "fix", "len": 4,
        "text": (
            "Debug with evidence: reproduce the failure, state root cause, apply minimal fix, re-run the failing validator. "
            "No speculative edits — hypothesis must match observed output. "
            "Done when validator that failed now PASS and cause is one sentence."
        ),
    },
    {
        "id": "045", "cat": "fix", "len": 3,
        "text": (
            "Write incident to brain-os/incidents/ with reason, fix applied, and validator proof path. "
            "Follow existing incident filename pattern. "
            "Done when incident file path pasted and linked to receipt."
        ),
    },
    {
        "id": "046", "cat": "fix", "len": 3,
        "text": (
            "Clear rejected PromptOS ingest: if any files in outputs/inbox/rejected/, run repair_promptos_rejected_ingest. "
            "Re-verify directory empty. "
            "Done when rejected count 0 or repair BLOCKED with file list."
        ),
    },
    {
        "id": "047", "cat": "fix", "len": 4,
        "text": (
            "Fix false green: hub says OK but receipt is stale — run light refresh, dual heal, re-validate super-fast hub. "
            "Receipt mtime must be fresher than hub claim. "
            "Done when validate-super-fast-hub PASS and receipt mtime cited."
        ),
    },
    {
        "id": "048", "cat": "fix", "len": 3,
        "text": (
            "Fix lane cross: Brain agent must not execute Worker INBOX turn — route to correct role workspace. "
            "Document which lane violated and corrective action. "
            "Done when role boundary restored and wrong execution undone if any."
        ),
    },
    {
        "id": "049", "cat": "fix", "len": 3,
        "text": (
            "Memory sync before next INBOX: agent_memory_mirror_v1.py --sync --validate --json. "
            "Fix mirror errors before factory work. "
            "Done when sync JSON ok:true pasted."
        ),
    },
    {
        "id": "050", "cat": "fix", "len": 4,
        "text": (
            "Self-heal loop: detect → classify → fix → harden validator → verify receipt — log near-miss to agent-governance-events.jsonl if material. "
            "One incident class per turn. "
            "Done when verify step PASS and log line or 'no material fix' stated."
        ),
    },
    {
        "id": "051", "cat": "fix", "len": 4,
        "text": (
            "Mistake audit this chat: list every error vs disk truth, unify into session attachment under archive/attachments/, correct SSOT if wrong claim was shipped. "
            "Do not hide mistakes. "
            "Done when attachment path and correction list pasted."
        ),
    },
    {
        "id": "052", "cat": "fix", "len": 3,
        "text": (
            "Both refine: refinement_unified_router_v1.py both hospital tune --role worker --json. "
            "Run agent hospital and machine tune in one coordinated pass. "
            "Done when unified router receipt shows both pipelines complete."
        ),
    },
    # ── HUB (10)
    {
        "id": "053", "cat": "hub", "len": 4,
        "text": (
            "H1 Super Fast only: fetch worker-hub/v1 JSON — report task, queue, form count, health fields. "
            "No legacy endpoints, no 9MB payloads, no full HTML hub scrape. "
            "Done when JSON snippet pasted with byte size under 16KB confirmed."
        ),
    },
    {
        "id": "054", "cat": "hub", "len": 3,
        "text": (
            "Light refresh hub (mode light) then confirm H1 health pill is fresh on disk. "
            "Never full rebuild on founder Refresh — cite SUPER_FAST_HUB law if tempted. "
            "Done when refresh receipt or health mtime proves update."
        ),
    },
    {
        "id": "055", "cat": "hub", "len": 3,
        "text": (
            "Safety check path: run anti-staleness fast subset relevant to founder daily — report only, no edits. "
            "Flag INCIDENT-028 class issues. "
            "Done when PASS/FAIL and first failure path if any."
        ),
    },
    {
        "id": "056", "cat": "hub", "len": 3,
        "text": (
            "H2 deep link only when needed: pending registry plus Judge alarm — do not embed machine UI on H1. "
            "Worker daily truth stays H1 + disk JSON. "
            "Done when link targets cited and H1 payload still small."
        ),
    },
    {
        "id": "057", "cat": "hub", "len": 3,
        "text": (
            "Never full hub rebuild on founder Refresh — if asked, implement light refresh path only and cite SUPER_FAST_HUB_LOCKED law. "
            "Founder clicks only. "
            "Done when lawful path named and heavy rebuild rejected with reason."
        ),
    },
    {
        "id": "058", "cat": "hub", "len": 3,
        "text": (
            "Dual hub heal plus h2_pending_registry sync — run hub_dual_heal_v1.py. "
            "Paste two-hub-heal receipt ok line. "
            "Done when receipt ok:true and pending registry mtime fresh."
        ),
    },
    {
        "id": "059", "cat": "hub", "len": 3,
        "text": (
            "Worker law reminder: daily operational truth is H1 worker-hub/v1 plus ~/.sina JSON — not routine /machines/ browsing. "
            "Apply this when scope is ambiguous. "
            "Done when you state which hub tier applies to this task."
        ),
    },
    {
        "id": "060", "cat": "hub", "len": 4,
        "text": (
            "Convert this founder request into H1 one-tap Action spec for Maintainer SHIP — founder clicks only, no Terminal. "
            "Include button label, API action id, and success receipt path. "
            "Done when Action spec is paste-ready for Maintainer workspace."
        ),
    },
    {
        "id": "061", "cat": "hub", "len": 3,
        "text": (
            "Form mirror: live_founder_decision_form_v1.py --json — report open_questions_count and top three question ids. "
            "Link each to M1 Canvas or receipt if answered. "
            "Done when JSON fields pasted with paths."
        ),
    },
    {
        "id": "062", "cat": "hub", "len": 3,
        "text": (
            "Which receipt moved in the last hour? List path, ok field, mtime — not hub color. "
            "Sort by mtime descending, top five only. "
            "Done when table of receipts with timestamps."
        ),
    },
    # ── SHIP (10)
    {
        "id": "063", "cat": "ship", "len": 4,
        "text": (
            "Implement only the scope I attached or stated — match repo conventions, minimal diff, no drive-by cleanup. "
            "Run validators before you say done; founder never runs Terminal. "
            "Done when changed files listed, validator PASS pasted, and receipt path if state moved."
        ),
    },
    {
        "id": "064", "cat": "ship", "len": 3,
        "text": (
            "Ship proof: run machine_test_ladder daily tier green and cite all receipt paths in closeout. "
            "No ship talk if ladder fails. "
            "Done when steps_passed equals total and paths in bullet list."
        ),
    },
    {
        "id": "065", "cat": "ship", "len": 4,
        "text": (
            "Lock this decision: one new LOCKED doc or one clause in existing LOCKED doc — no parallel duplicate rules or .mdc copies. "
            "Supersede old version to archive/superseded/ if bumping version. "
            "Done when LOCKED file path pasted and authority index updated if required."
        ),
    },
    {
        "id": "066", "cat": "ship", "len": 3,
        "text": (
            "Save attachment under archive/attachments/YYYY-MM-DD/ with traceable tag and role in filename. "
            "Content must be self-contained for a new chat. "
            "Done when full attachment path pasted."
        ),
    },
    {
        "id": "067", "cat": "ship", "len": 4,
        "text": (
            "Update roadmap/WTM only if convinced by disk evidence — attach proof, do not renumber phases from critic paste. "
            "ASF order or Form pick required for step order changes. "
            "Done when diff shows only convinced rows changed."
        ),
    },
    {
        "id": "068", "cat": "ship", "len": 3,
        "text": (
            "Implement the attached plan exactly — do not edit the plan file itself. "
            "Stop at plan boundaries; defer extras to H2 deferred bucket. "
            "Done when plan checklist items marked with validator proof each."
        ),
    },
    {
        "id": "069", "cat": "ship", "len": 4,
        "text": (
            "Before ship: machine_upgrade_baseline_v1.py --tag before, apply change, run forge or tune, baseline --tag after. "
            "Report critical_count delta. "
            "Done when before/after JSON paths and delta pasted."
        ),
    },
    {
        "id": "070", "cat": "ship", "len": 3,
        "text": (
            "Name W1/W2/W3 delta for this change — if none applies, defer row to H2 pending registry with reason. "
            "Do not invent upgrade ids. "
            "Done when tier label or defer receipt cited."
        ),
    },
    {
        "id": "071", "cat": "ship", "len": 3,
        "text": (
            "No fake progress: show validator stdout or receipt JSON — otherwise status must be BLOCKED. "
            "Vibes and 'should work' are forbidden. "
            "Done when proof artifact is in the message or BLOCKED is honest."
        ),
    },
    {
        "id": "072", "cat": "ship", "len": 4,
        "text": (
            "Upgrade fully in order: contract → validator → code → receipt → surface (H1 one-line OR H2 table, not both). "
            "Skip no step. "
            "Done when all five layers cited with paths."
        ),
    },
    # ── FORM / ASF (8)
    {
        "id": "073", "cat": "form", "len": 3,
        "text": (
            "Add this decision as open question on live founder Form — not a chat-only bullet list. "
            "Use live_founder_decision_form_v1.py append API or lawful disk write. "
            "Done when new question id pasted from Form JSON."
        ),
    },
    {
        "id": "074", "cat": "form", "len": 4,
        "text": (
            "Read my last Form answer as ASF order — execute exactly that pick, update SSOT, mark Form row answered from evidence. "
            "Do not reinterpret the pick wider than written. "
            "Done when Form row status answered and SSOT diff cited."
        ),
    },
    {
        "id": "075", "cat": "form", "len": 4,
        "text": (
            "Five-step SCAN→SAY→PICK→PROVE→SHIP: run SCAN on disk truth, SAY status in five lines, propose one PICK for Form, wait for founder — do not SHIP without PROVE. "
            "Founder clicks Form, not Terminal. "
            "Done when SCAN+SAY pasted and PICK row draft ready."
        ),
    },
    {
        "id": "076", "cat": "form", "len": 3,
        "text": (
            "List must-do-now items missing from Form and mandatory rule list — prioritize top five by P0 impact. "
            "Add gaps to Form as open questions. "
            "Done when top five table with add-to-Form ids."
        ),
    },
    {
        "id": "077", "cat": "form", "len": 3,
        "text": (
            "Multi-sentence founder fork goes to Form row plus H2 deferred bucket — never a long chat decision list. "
            "One row per fork option. "
            "Done when Form ids created and chat summary points to Form."
        ),
    },
    {
        "id": "078", "cat": "form", "len": 3,
        "text": (
            "What is open on Form right now? List each open question id with one-line summary and link to M1 Canvas or receipt if partial. "
            "Disk JSON only. "
            "Done when complete open list or explicit zero open."
        ),
    },
    {
        "id": "079", "cat": "form", "len": 4,
        "text": (
            "ASF approved this Form pick — execute exactly that row scope, then mark Form answered from validator or receipt evidence. "
            "No scope expansion. "
            "Done when pick id closed and proof path in answer field."
        ),
    },
    {
        "id": "080", "cat": "form", "len": 3,
        "text": (
            "Defer scope creep: if task is not on Form and not direct ASF order, add to H2 deferred bucket — do not implement. "
            "Tell founder which Form row to open. "
            "Done when defer receipt or new Form row id pasted."
        ),
    },
    # ── TEST / REFINE (8)
    {
        "id": "081", "cat": "test", "len": 3,
        "text": (
            "Run machine_test_ladder_run_v1.py --tier daily --json — paste steps_passed, steps_total, and first FAIL step if any. "
            "Daily tier is minimum bar for factory days. "
            "Done when ladder JSON block in reply."
        ),
    },
    {
        "id": "082", "cat": "test", "len": 4,
        "text": (
            "Run weekly ladder tier plus find_critical_bugs — ship talk blocked if critical_count > 0. "
            "Report both receipts. "
            "Done when weekly steps_passed and critical_count 0 or BLOCKED."
        ),
    },
    {
        "id": "083", "cat": "test", "len": 3,
        "text": (
            "Run validate-agent-three-pipelines-v1.sh and validate-machine-three-pipelines-v1.sh. "
            "Both must PASS for refinement routers to be trusted. "
            "Done when dual PASS/FAIL with first error line if fail."
        ),
    },
    {
        "id": "084", "cat": "test", "len": 3,
        "text": (
            "Run validate-anti-staleness-bundle-v1.sh — weekly gate, report first FAIL only. "
            "Do not dump full log. "
            "Done when PASS or single FAIL identifier."
        ),
    },
    {
        "id": "085", "cat": "test", "len": 3,
        "text": (
            "machine_upgrade_baseline_v1.py --tag before then after this session's change — show critical_count delta. "
            "Tags must be unique and dated. "
            "Done when both baseline paths and delta number."
        ),
    },
    {
        "id": "086", "cat": "test", "len": 4,
        "text": (
            "Test plus upgrade plan: read SOURCEA_MACHINE_TEST_AND_UPGRADE_LADDER_LOCKED_v1.md, name one W1/W2/W3 gap from disk, propose one UP-id for H2 registry. "
            "Planning only unless ASF says implement. "
            "Done when gap, tier, and UP-id row draft pasted."
        ),
    },
    {
        "id": "087", "cat": "test", "len": 3,
        "text": (
            "ecosystem_master_catalog_v1.py --json — use for planning and coverage maps only, not daily run-all. "
            "Summarize count by tier. "
            "Done when catalog stats pasted, no mass execution."
        ),
    },
    {
        "id": "088", "cat": "test", "len": 3,
        "text": (
            "Tune then report: if tune receipt shows escalate_forge true, stop factory work until forge passport complete. "
            "State hold reason from receipt JSON. "
            "Done when escalate flag cited and factory hold honored."
        ),
    },
    # ── RESEARCH / ADVISOR (6)
    {
        "id": "089", "cat": "research", "len": 4,
        "text": (
            "Deep search VC-grade on the topic I state — save report plus lessons under archive/attachments/ with date folder, wire WTM only if convinced. "
            "Follow sina-research-lessons skill flow. "
            "Done when report path and three golden insights pasted."
        ),
    },
    {
        "id": "090", "cat": "research", "len": 4,
        "text": (
            "Read pasted content — compare to latest LOCKED law, add insight table, rewrite as one canonical doc proposal (not duplicate rules). "
            "First line if critic paste: INPUT CLASS EXTERNAL_CRITIC. "
            "Done when accept/reject/duplicate verdict per item."
        ),
    },
    {
        "id": "091", "cat": "research", "len": 3,
        "text": (
            "Unify fragmented docs: one topic → one LOCKED file, move superseded to archive/superseded/, update authority index pointers only. "
            "No parallel read-first chains. "
            "Done when canonical path and archived paths listed."
        ),
    },
    {
        "id": "092", "cat": "research", "len": 3,
        "text": (
            "Session index: unify this chat arc into one router attachment — decisions, receipts, mistakes, next actions — nothing lost. "
            "Self-contained for cold start. "
            "Done when attachment path under archive/attachments/ pasted."
        ),
    },
    {
        "id": "093", "cat": "advisor", "len": 4,
        "text": (
            "What should I do now? Give three disk-backed options with tradeoffs, one recommended, zero Terminal steps for me — H1 clicks only. "
            "Cite receipt or Form id per option. "
            "Done when numbered 1-2-3 with recommendation bolded in prose."
        ),
    },
    {
        "id": "094", "cat": "advisor", "len": 4,
        "text": (
            "Explain like advisor: options, tradeoffs, cite LOCKED law paths — I decide on Form, you do not pick for me unless asked. "
            "No implementation this turn unless I pick. "
            "Done when advisor memo with law citations and Form row suggestion."
        ),
    },
    # ── CURSOR / SESSION / CRITIC (6)
    {
        "id": "095", "cat": "cursor", "len": 3,
        "text": (
            "@REFINEMENT_UNIFIED_AGENT_MACHINE_LOCKED_v1.md — execute one lawful refinement action with receipt proof. "
            "Agent mode, batch reads first. "
            "Done when unified router or pipeline receipt pasted."
        ),
    },
    {
        "id": "096", "cat": "cursor", "len": 3,
        "text": (
            "@FOUNDER_DAILY_PROMPT_PACK_LOCKED_v1.md — run prompt 081 exactly as written in Agent mode. "
            "Do not paraphrase the order. "
            "Done when prompt 081 DONE-WHEN criteria met."
        ),
    },
    {
        "id": "097", "cat": "cursor", "len": 4,
        "text": (
            "Batch parallel reads this turn — gather all context first, then one implement action. "
            "I do not run Terminal; you run every command. "
            "Done when read list cited and single action outcome with proof."
        ),
    },
    {
        "id": "098", "cat": "session", "len": 4,
        "text": (
            "Session start ritual: rules-in-charge API, truth bundle JSON, session gate for worker — paste ok lines only. "
            "Do not start factory until gate passes. "
            "Done when all three ok or first blocker named."
        ),
    },
    {
        "id": "099", "cat": "session", "len": 4,
        "text": (
            "Session closeout: one golden insight, founder next actions as H1 clicks only, all receipt paths cited, mistakes honest. "
            "Save closeout attachment if multi-file turn. "
            "Done when closeout block ready for Submit round paste."
        ),
    },
    {
        "id": "100", "cat": "critic", "len": 4,
        "text": (
            "First line must be: INPUT CLASS EXTERNAL_CRITIC. Compare pasted audit to latest LOCKED SSOT and hub alignment — verdict each item accept/reject/duplicate/already-in-SSOT. "
            "Never change build order or active step from critic alone. "
            "Done when §6 critic template complete in reply."
        ),
    },
]

ANALYSIS = {
    "v1_problems": [
        "Too vague alone (check, implement, yes) — agent guesses wrong scope",
        "Bullet fragments — notes not executable orders",
        "Duplicates — wasted slots",
        "No done-when proof — chat claims without receipts",
    ],
    "v2_formula": "ACTION + SCOPE + DONE-WHEN",
    "v3_formula": "ACTION + SCOPE + CONSTRAINTS + DONE-WHEN (pro long paste-ready)",
    "keep_one_words": "001-006 still start with orientation/hospital/maze/calibrate/tune/forge (forge=machine prove only) — full pipeline in same paste",
}

V1_CAT_TITLES = {
    "one_word": "One-word triggers (6)",
    "factory": "Factory · INBOX (12)",
    "check": "Check · audit (20)",
    "fix": "Fix · heal (14)",
    "hub": "Hub H1/H2 (10)",
    "ship": "Ship · lock · implement (10)",
    "form": "Form · ASF (8)",
    "test": "Test · tune ladder (8)",
    "research": "Research · unify · advisor (4)",
    "unify": "Research · unify · advisor (2)",
    "advisor": "Research · unify · advisor (2)",
    "cursor": "Cursor · session · critic (4)",
    "session": "Cursor · session · critic (1)",
    "critic": "Cursor · session · critic (1)",
}

V2_CAT_TITLES = {
    "one_word": "One-word routers (6)",
    "factory": "Factory · INBOX (12)",
    "check": "Smart checks (20)",
    "fix": "Fix · heal (14)",
    "hub": "Hub H1/H2 (10)",
    "ship": "Ship · lock (10)",
    "form": "Form · ASF (8)",
    "test": "Test · refine (8)",
    "research": "Research · advisor (6)",
    "cursor": "Cursor · session · critic (6)",
}

CAT_TITLES = {
    "one_word": "One-word routers — pro long (6)",
    "factory": "Factory · INBOX (12)",
    "check": "Smart checks (20)",
    "fix": "Fix · heal (14)",
    "hub": "Hub H1/H2 (10)",
    "ship": "Ship · lock (10)",
    "form": "Form · ASF (8)",
    "test": "Test · refine (8)",
    "research": "Research · advisor (6)",
    "cursor": "Cursor · session · critic (6)",
}


def _categories(prompts: list[dict], titles: dict[str, str]) -> dict:
    return {cid: {"title": title, "prompts": [p for p in prompts if p["cat"] == cid]} for cid, title in titles.items()}


def _by_len(prompts: list[dict]) -> dict[int, int]:
    out: dict[int, int] = {}
    for p in prompts:
        out[p["len"]] = out.get(p["len"], 0) + 1
    return out


def _pack_v1() -> dict:
    assert len(V1_MINED) == PACK_SIZE
    return {
        "schema": "founder-prompt-pack-v1-mined",
        "pack_size": PACK_SIZE,
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "upgrade": "v1 mined — raw founder voice from 104 transcripts (frozen reference)",
        "note": "Historical — use v3 for daily Cursor orders",
        "total_prompts": PACK_SIZE,
        "by_sentence_count": _by_len(V1_MINED),
        "cursor_defaults": {"mode": "Agent", "rules": "Executor runs shell — founder never Terminal"},
        "prompts": V1_MINED,
        "categories": _categories(V1_MINED, V1_CAT_TITLES),
    }


def _pack_v2() -> dict:
    assert len(V2_SMART) == PACK_SIZE
    return {
        "schema": "founder-prompt-pack-v2-smart",
        "pack_size": PACK_SIZE,
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "upgrade": "v2 smart — ACTION + SCOPE + DONE-WHEN (frozen reference)",
        "analysis": {"v2_formula": "ACTION + SCOPE + DONE-WHEN (disk receipt or PASS/FAIL)"},
        "total_prompts": PACK_SIZE,
        "by_sentence_count": _by_len(V2_SMART),
        "cursor_defaults": {
            "mode": "Agent",
            "rules": "Executor runs shell — founder never Terminal",
            "attach": "@LOCKED law or @scripts/ when scope is governance or machine",
            "proof": "Every reply ends with receipt path or PASS/FAIL — not vibes",
        },
        "prompts": V2_SMART,
        "categories": _categories(V2_SMART, V2_CAT_TITLES),
    }


def _pack_v3() -> dict:
    assert len(PRO) == PACK_SIZE
    return {
        "schema": "founder-prompt-pack-v3-pro",
        "pack_size": PACK_SIZE,
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "upgrade": "v3 pro long — ACTION + SCOPE + CONSTRAINTS + DONE-WHEN (active daily)",
        "analysis": ANALYSIS,
        "total_prompts": PACK_SIZE,
        "by_sentence_count": _by_len(PRO),
        "cursor_defaults": CURSOR,
        "prompts": PRO,
        "categories": _categories(PRO, CAT_TITLES),
    }


def _pack_index(v1: dict, v2: dict, v3: dict) -> dict:
    return {
        "schema": "founder-prompt-pack-index-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "active_version": "v3",
        "versions": {
            "v1": {
                "label": "mined",
                "formula": "raw founder voice · mined habits",
                "json": str(OUT_JSON_V1),
                "md": str(OUT_MD_V1.relative_to(ROOT)),
                "use_when": "Reference original habits · frequency study",
            },
            "v2": {
                "label": "smart",
                "formula": "ACTION + SCOPE + DONE-WHEN",
                "json": str(OUT_JSON_V2),
                "md": str(OUT_MD_V2.relative_to(ROOT)),
                "use_when": "Short smart orders · quick paste",
            },
            "v3": {
                "label": "pro",
                "formula": "ACTION + SCOPE + CONSTRAINTS + DONE-WHEN",
                "json": str(OUT_JSON_V3),
                "md": str(OUT_MD_V3.relative_to(ROOT)),
                "use_when": "Daily Cursor Agent orders (default)",
            },
        },
        "rebuild": "python3 scripts/founder_prompt_pack_build_v1.py",
        "counts": {"v1": v1["total_prompts"], "v2": v2["total_prompts"], "v3": v3["total_prompts"]},
    }


def write_md_v1(pack: dict) -> str:
    lines = [
        "# Founder daily prompt pack — v1 mined (100 frozen reference)",
        "",
        "**Source:** 104 agent transcripts · raw founder voice · ids 001–100",
        "**Status:** Frozen reference — prefer **v3 pro** for daily use",
        "",
        "**Formula:** none — authentic mined habits (includes duplicates and typos by design)",
        "",
    ]
    order = [
        ("one_word", "One-word triggers (6)"),
        ("factory", "Factory · INBOX (12)"),
        ("check", "Check · audit (20)"),
        ("fix", "Fix · heal (14)"),
        ("hub", "Hub H1/H2 (10)"),
        ("ship", "Ship · lock · implement (10)"),
        ("form", "Form · ASF (8)"),
        ("test", "Test · tune ladder (8)"),
        ("research", "Research · unify · advisor (6)"),
        ("cursor", "Cursor · session · critic (6)"),
    ]
    for cid, title in order:
        if cid == "research":
            prompts = [p for p in pack["prompts"] if p["cat"] in ("research", "unify", "advisor")]
        elif cid == "cursor":
            prompts = [p for p in pack["prompts"] if p["cat"] in ("cursor", "session", "critic")]
        else:
            prompts = [p for p in pack["prompts"] if p["cat"] == cid]
        if not prompts:
            continue
        lines.append(f"## {title}")
        lines.append("")
        for p in prompts:
            freq = f" _({p['freq']}× mined)_" if p.get("freq") else ""
            lines.append(f"**{p['id']}.** {p['text']}{freq}")
            lines.append("")
    lines.append("---")
    lines.append("*End — v1 mined reference · 100 prompts*")
    return "\n".join(lines)


def write_md_v2(pack: dict) -> str:
    a = pack.get("analysis", {})
    lines = [
        "# Founder daily prompt pack — v2 smart (100 frozen reference)",
        "",
        f"**Formula:** {a.get('v2_formula', 'ACTION + SCOPE + DONE-WHEN')}",
        "",
        "**Status:** Frozen reference — prefer **v3 pro** for daily use",
        "",
    ]
    for cid, cat in pack["categories"].items():
        if not cat["prompts"]:
            continue
        lines.append(f"## {cat['title']}")
        lines.append("")
        for p in cat["prompts"]:
            note = f" _({p['note']})_" if p.get("note") else ""
            lines.append(f"**{p['id']}.** {p['text']}{note}")
            lines.append("")
    lines.append("---")
    lines.append("*End — v2 smart reference · 100 prompts*")
    return "\n".join(lines)


def write_md_v3(pack: dict) -> str:
    lines = [
        "# Founder daily prompt pack — v3 pro long (100 active daily)",
        "",
        "**Formula:** ACTION + SCOPE + CONSTRAINTS + DONE-WHEN",
        "",
        "**Cursor:** Agent mode · executor runs shell · founder never Terminal · @ attach LOCKED laws when cited",
        "",
        "**JSON:** `~/.sina/founder-prompt-pack-v3-pro.json` · **Rebuild:** `python3 scripts/founder_prompt_pack_build_v1.py`",
        "",
        "**Also kept:** v1 mined + v2 smart — see `FOUNDER_DAILY_PROMPT_PACK_LOCKED_v1.md` router",
        "",
    ]
    for cid, cat in pack["categories"].items():
        if not cat["prompts"]:
            continue
        lines.append(f"## {cat['title']}")
        lines.append("")
        for p in cat["prompts"]:
            lines.append(f"### {p['id']}")
            lines.append("")
            lines.append(p["text"])
            lines.append("")
    lines.append("---")
    lines.append("*End — v3 pro long · 100 prompts*")
    return "\n".join(lines)


def write_router_md(v3: dict) -> str:
    lines = [
        "# Founder daily prompt pack (LOCKED — v1 · v2 · v3)",
        "",
        "**Active daily default:** v3 pro long · ids **001–100**",
        "**Rebuild all versions:** `python3 scripts/founder_prompt_pack_build_v1.py`",
        "",
        "## Version index",
        "",
        "| Version | File | Formula | When to use |",
        "|---------|------|---------|-------------|",
        "| **v1 mined** | `archive/attachments/2026-06-14/FOUNDER_DAILY_PROMPT_PACK_v1_MINED_LOCKED.md` | Raw founder voice | Reference · habit frequency · why v2/v3 exist |",
        "| **v2 smart** | `archive/attachments/2026-06-14/FOUNDER_DAILY_PROMPT_PACK_v2_SMART_LOCKED.md` | ACTION + SCOPE + DONE-WHEN | Short paste · quick orders |",
        "| **v3 pro** | `archive/attachments/2026-06-14/FOUNDER_DAILY_PROMPT_PACK_v3_PRO_LOCKED.md` | ACTION + SCOPE + CONSTRAINTS + DONE-WHEN | **Daily Cursor Agent (default)** |",
        "",
        "## JSON on disk",
        "",
        "| Version | Path |",
        "|---------|------|",
        "| Index | `~/.sina/founder-prompt-pack-index.json` |",
        "| v1 mined | `~/.sina/founder-prompt-pack-v1-mined.json` |",
        "| v2 smart | `~/.sina/founder-prompt-pack-v2-smart.json` |",
        "| v3 pro | `~/.sina/founder-prompt-pack-v3-pro.json` |",
        "| Active alias | `~/.sina/founder-prompt-pack-v1.json` → v3 |",
        "",
        "## Evolution (one line each)",
        "",
        "- **v1** — mined from 104 chats (`run inbox` 232×, `check` 662×) — kept with typos/duplicates",
        "- **v2** — deduped + smart formula — 1–2 sentence orders",
        "- **v3** — pro long — full paste-ready with constraints + done-when",
        "",
        "## v3 top 10 daily",
        "",
        "| ID | Order (abbrev) |",
        "|----|----------------|",
    ]
    top = ["007", "019", "039", "053", "063", "081", "093", "002", "071", "098"]
    for tid in top:
        p = next(x for x in v3["prompts"] if x["id"] == tid)
        short = p["text"][:72] + ("…" if len(p["text"]) > 72 else "")
        lines.append(f"| **{tid}** | {short} |")
    lines.extend([
        "",
        "---",
        "",
        "Open **v3 pro** attachment for full 100 orders · v1 and v2 frozen for reference only.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    v1 = _pack_v1()
    v2 = _pack_v2()
    v3 = _pack_v3()
    index = _pack_index(v1, v2, v3)

    SINA.mkdir(parents=True, exist_ok=True)
    ATTACH.mkdir(parents=True, exist_ok=True)

    OUT_JSON_V1.write_text(json.dumps(v1, indent=2) + "\n", encoding="utf-8")
    OUT_JSON_V2.write_text(json.dumps(v2, indent=2) + "\n", encoding="utf-8")
    OUT_JSON_V3.write_text(json.dumps(v3, indent=2) + "\n", encoding="utf-8")
    OUT_JSON_INDEX.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    OUT_JSON_ACTIVE.write_text(json.dumps(v3, indent=2) + "\n", encoding="utf-8")

    md_v1 = write_md_v1(v1)
    md_v2 = write_md_v2(v2)
    md_v3 = write_md_v3(v3)

    OUT_MD_V1.write_text(md_v1 + "\n", encoding="utf-8")
    OUT_MD_V2.write_text(md_v2 + "\n", encoding="utf-8")
    OUT_MD_V3.write_text(md_v3 + "\n", encoding="utf-8")
    OUT_MD_LEGACY.write_text(md_v3 + "\n", encoding="utf-8")

    ROUTER_MD.write_text(write_router_md(v3) + "\n", encoding="utf-8")

    print(f"OK: v1 mined + v2 smart + v3 pro · {PACK_SIZE} each · index + router synced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
