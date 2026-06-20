# Founder daily prompt pack — v3 pro long (100 active daily)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Formula:** ACTION + SCOPE + CONSTRAINTS + DONE-WHEN

**Cursor:** Agent mode · executor runs shell · founder never Terminal · @ attach LOCKED laws when cited

**JSON:** `~/.sina/founder-prompt-pack-v3-pro.json` · **Rebuild:** `python3 scripts/founder_prompt_pack_build_v1.py`

**Also kept:** v1 mined + v2 smart — see `FOUNDER_DAILY_PROMPT_PACK_LOCKED_v1.md` router

## One-word routers — pro long (6)

### 001

orientation — Run scripts/agent_orientation_pipeline_v1.py for role worker. Load rules-in-charge, reading pack, and session truth from disk only; no code edits and no INBOX execution. Done when ~/.sina/agent-orientation-receipt-v1.json shows ok:true and you paste orientation summary plus one recommended next action.

### 002

hospital — Run scripts/agent_hospital_pipeline_v1.py --role worker. Execute memory sync, session gate, dual heal, and honest registry checks in pipeline order; escalate to maze only if machine sets critical_count > 0. Done when ~/.sina/agent-hospital-receipt-v1.json is written with discharge note or explicit maze escalation path.

### 003

maze — Run scripts/agent_maze_pipeline_v1.py --role worker only after hospital escalation or explicit quarantine flag. Complete gauntlet steps in order; do not skip passport or self-validate recursion. Done when maze passport receipt exists and ~/.sina/agent-maze-quarantine-v1.json status is cleared or documented BLOCKED with reason.

### 004

calibrate — Run scripts/machine_calibrate_pipeline_v1.py. Map validators, upgrade board, and machine registry from disk; read-only except calibrate receipt writes. Done when ~/.sina/machine-calibrate-receipt-v1.json lists mapped validators and any gaps with file paths.

### 005

tune — Run scripts/machine_tune_pipeline_v1.py --ladder-tier daily. Execute daily test ladder, refresh baseline, and sync H2 maintainer_ship if UP rows apply. Done when ~/.sina/machine-tune-receipt-v1.json and machine-test-ladder-receipt-v1.json both show steps_passed with escalate_forge false or explicit forge hold.

### 006

forge — Run scripts/machine_forge_pipeline_v1.py --ladder-tier weekly (or monthly if flagged). Prove upgrade with before/after baseline and full ladder tier; block factory ship if critical_count > 0. Done when forge receipt ok:true and critical_count is 0 in ~/.sina/find-bugs/last-run.json.

## Factory · INBOX (12)

### 007

Execute one full Worker INBOX turn end-to-end. Read ~/.sina/worker-prompt-inbox-v1.json and the bound sa_id logged; run the disk prompt exactly with no scope creep. Broker-submit when the turn completes and stop — do not batch a second sa. Done when WORKER_ROUND_REPORT YAML is written, orchestrator advanced, and you paste receipt path plus new queue head.

### 008

INBOX CHECK turn only for the currently bound sa. Read disk prompt and sa metadata; run read-only validators and gap analysis — zero file edits this turn. Produce a structured gap report: what is missing, what blocks ACT, and which validator would prove readiness. Done when gap report is pasted with PASS/FAIL per check and explicit GO/NO-GO for ACT.

### 009

INBOX ACT turn only: implement minimal diff strictly for the bound sa_id — match repo conventions, no drive-by refactors. Run only validators required to prove the act; do not write closeout or broker-submit yet. Done when diff is scoped, cited files changed, and validator output shows ACT checks green or BLOCKED with reason.

### 010

INBOX VERIFY turn only: re-run full validator set for bound sa, write honest closeout, and confirm critical_count is 0. Then broker-submit and confirm orchestrator idle or advanced correctly. Done when VERIFY receipt path pasted, critical_count 0, and WORKER_ROUND_REPORT last lines match expected sa/role.

### 011

Show factory-now snapshot from disk only — no hub HTML scrape. Report queue head sa_id, role, position, factory mode, turn open/closed, and inbox pending flag. Done when all fields cite JSON paths and mismatches vs last broker report are listed.

### 012

If orchestrator is idle and inbox has a pending prompt, run exactly one INBOX turn. If blocked by feasibility gate, kill_flag, or SINGLE_SA hold, print BLOCKED with disk reason — do not force through. Done when turn completed with broker advance OR explicit BLOCKED line with file path evidence.

### 013

Fix turn-bind drift: goal1-worker-turn-bind and headsup must match queue head sa logged. Show before/after for every field that changed; minimal fix only — no unrelated edits. Done when bind JSON matches orchestrator expected sa and validate step for turn-bind passes.

### 014

Broker submit after this turn: ensure WORKER_ROUND_REPORT YAML footer is complete and orchestrator advances queue position. If submit fails, diagnose from disk logs — do not claim success from chat. Done when orchestrator state after submit is pasted with sa_id and role confirmed.

### 015

Drain exactly one sa from plan-no-asf-run.sh output — pick the first eligible row, execute fully, then stop. No batch drain, no parallel sa work. Done when that single sa shows completed status logged and you paste which sa_id was drained.

### 016

If this chat round was tagged SINA_LOOP, POST agent-loop response via API with one-line summary plus full body. Founder does not run curl — you execute. Done when API returns ok and you paste round number advanced.

### 017

Run prompt_feasibility_gate for worker strict before any INBOX ACT. If STOP_INJECT or feasibility fail, report verdict and do not implement — add gap to Form or H2 deferred if needed. Done when gate JSON pasted with inject_allowed true/false and explicit next step.

### 018

Never claim this turn done without a disk receipt that moved state. Cite exact path, ok field, and timestamp from receipt JSON. Done when receipt path is in your last message or status is honestly BLOCKED with missing receipt reason.

## Smart checks (20)

### 019

Daily health snapshot from disk JSON only — no hub color as truth. Report queue head sa_id, critical_count from find-bugs, form open_questions_count, and H1 worker-hub/v1 health fields. Done when all four metrics cite file paths and any STALE hub-vs-receipt mismatch is flagged.

### 020

Run validate-super-fast-hub-v1.sh and validate-two-hub-v1.sh sequentially. Report PASS/FAIL only — if FAIL, paste first failing line and file, not a summary essay. Done when both scripts exit and verdict table is in your reply.

### 021

Run find_critical_bugs.py and read ~/.sina/find-bugs/last-run.json. Report critical_count, verdict, and top issue titles if count > 0. Done when count is numeric and ship-talk is blocked if critical_count > 0.

### 022

Run agentic_layer_pipeline_v2.py --tier fast --json. Report health.status, issue count, and first three issue ids if unhealthy. Done when JSON health block is pasted or PASS with zero issues stated.

### 023

Blocker sweep: read architect_report.yaml and global_blockers from disk. List every open P0 with owner, age, and fix-or-escalate recommendation — one action per blocker. Done when P0 table is complete or explicit 'zero P0' with file mtime cited.

### 024

Cross-chat drift audit: compare Worker, Brain, and Maintainer last claims to current disk receipts. List mismatches only — skip aligned rows. Done when drift list is empty or each mismatch has disk truth and suggested single fix.

### 025

Ingest check: SinaPromptOS outputs/inbox/rejected/ must be empty. If any files exist, run repair_promptos_rejected_ingest and re-check until empty or BLOCKED. Done when rejected dir file count is 0 with ls evidence or repair receipt pasted.

### 026

Broker check: last WORKER_ROUND_REPORT must match orchestrator expected sa_id and role. If mismatch, identify bind drift vs broker bug — do not guess. Done when match confirmed or mismatch table with both disk sources cited.

### 027

Session gate: run agent_session_gate_run_v1.py --role worker --json. Paste gate_id, ok, and fail reason if any. Done when gate JSON is in reply — worker factory blocked if ok:false.

### 028

Registry honesty: dry-run enforce_honest_registry and list unproven done rows only. Do not auto-fix — report ids that claim done without receipt proof. Done when unproven list is pasted or 'zero unproven' with dry-run output snippet.

### 029

Anti-staleness spot check: run validate-hub-p0-no-autorun-v1.sh (INCIDENT-028 class). Report PASS/FAIL — staleness means hub green but disk stale. Done when script verdict pasted; if FAIL, name stale artifact path.

### 030

Hub alignment: run audit_hub_source_alignment.py — compare WTM active steps vs hub surface fields. List gaps where hub shows step not in SSOT or SSOT step missing from hub. Done when gap count and top three ids are pasted.

### 031

Read-only audit this scope — zero file edits. List gaps with exact file paths and one suggested next single action per gap. Done when audit table is complete and ends with recommended order 1-2-3 for founder clicks only.

### 032

Two-hub sibling check: H1 worker-hub/v1 payload must stay small (<16KB); H2 machine-hub health must be fresh logged. Confirm H2 is not nested inside H1 UI response. Done when sizes, mtimes, and sibling separation are cited.

### 033

Agentic wire: run validate-agentic-layer-wire-v1.sh — Brain L1 L2 master must PASS. If FAIL, paste first broken wire and owning script. Done when PASS/FAIL verdict with script exit code.

### 034

Governance fast: governance_center_run_v1.py --tier fast --json. Report any failing step id and law file pointer. Done when fast tier JSON shows all pass or named failures only.

### 035

Quarantine flags: read agent-maze-quarantine-v1.json and machine-forge-quarantine logged. Report active true/false for each and what pipeline is blocked. Done when both flags cited with timestamps.

### 036

E2E factory loop proof: inbox pending → execute turn → broker advanced → orchestrator idle. Report each step with disk evidence — skip if already mid-turn. Done when four-step chain is PASS or first failing step named BLOCKED.

### 037

Compare UI vs receipt: if hub shows green but receipt mtime is old, receipt wins — say STALE. Name the stale receipt path and recommended heal action. Done when truth source is declared and mismatch resolved or escalated.

### 038

Give me a 5-line founder status report from disk: (1) top P0 task (2) queue head (3) open blockers count (4) critical_count (5) next one H1 click for me. No Terminal steps for founder. Done when exactly five numbered lines with JSON paths in parentheses.

## Fix · heal (14)

### 039

Auto-heal routine: run hub_dual_heal_v1.py then machine_tune_pipeline_v1.py --ladder-tier daily. Paste both receipt ok lines; if either fails, stop and report — do not proceed to INBOX. Done when dual-heal and tune receipts both ok:true or BLOCKED with fix plan.

### 040

Fix the single highest P0 blocker only — minimal diff, one validator proof, then stop. Do not fix lower priority items in the same turn. Done when P0 id is closed logged and validator PASS pasted.

### 041

Hospital this worker agent: run agent_hospital_pipeline_v1.py --role worker. Paste discharge note or maze escalation — do not skip memory sync. Done when agent-hospital-receipt-v1.json ok field pasted.

### 042

If critical_count > 0, do not ship feature work — run forge or fix root cause until critical_count is 0. Factory INBOX ACT is forbidden until bugs receipt clears. Done when find-bugs last-run shows critical_count 0 or explicit BLOCKED with bug ids.

### 043

Repair yesterday's session drift: re-read receipts from last session, fix orphan turn or stale bind. Show before/after for orchestrator and turn-bind JSON. Done when queue head matches bind and no orphan WORKER_ROUND_REPORT.

### 044

Debug with evidence: reproduce the failure, state root cause, apply minimal fix, re-run the failing validator. No speculative edits — hypothesis must match observed output. Done when validator that failed now PASS and cause is one sentence.

### 045

Write incident to brain-os/incidents/ with reason, fix applied, and validator proof path. Follow existing incident filename pattern. Done when incident file path pasted and linked to receipt.

### 046

Clear rejected PromptOS ingest: if any files in outputs/inbox/rejected/, run repair_promptos_rejected_ingest. Re-verify directory empty. Done when rejected count 0 or repair BLOCKED with file list.

### 047

Fix false green: hub says OK but receipt is stale — run light refresh, dual heal, re-validate super-fast hub. Receipt mtime must be fresher than hub claim. Done when validate-super-fast-hub PASS and receipt mtime cited.

### 048

Fix lane cross: Brain agent must not execute Worker INBOX turn — route to correct role workspace. Document which lane violated and corrective action. Done when role boundary restored and wrong execution undone if any.

### 049

Memory sync before next INBOX: agent_memory_mirror_v1.py --sync --validate --json. Fix mirror errors before factory work. Done when sync JSON ok:true pasted.

### 050

Self-heal loop: detect → classify → fix → harden validator → verify receipt — log near-miss to agent-governance-events.jsonl if material. One incident class per turn. Done when verify step PASS and log line or 'no material fix' stated.

### 051

Mistake audit this chat: list every error vs disk truth, unify into session attachment under archive/attachments/, correct SSOT if wrong claim was shipped. Do not hide mistakes. Done when attachment path and correction list pasted.

### 052

Both refine: refinement_unified_router_v1.py both hospital tune --role worker --json. Run agent hospital and machine tune in one coordinated pass. Done when unified router receipt shows both pipelines complete.

## Hub H1/H2 (10)

### 053

H1 Super Fast only: fetch worker-hub/v1 JSON — report task, queue, form count, health fields. No legacy endpoints, no 9MB payloads, no full HTML hub scrape. Done when JSON snippet pasted with byte size under 16KB confirmed.

### 054

Light refresh hub (mode light) then confirm H1 health pill is fresh logged. Never full rebuild on founder Refresh — cite SUPER_FAST_HUB law if tempted. Done when refresh receipt or health mtime proves update.

### 055

Safety check path: run anti-staleness fast subset relevant to founder daily — report only, no edits. Flag INCIDENT-028 class issues. Done when PASS/FAIL and first failure path if any.

### 056

H2 deep link only when needed: pending registry plus Judge alarm — do not embed machine UI on H1. Worker daily truth stays H1 + disk JSON. Done when link targets cited and H1 payload still small.

### 057

Never full hub rebuild on founder Refresh — if asked, implement light refresh path only and cite SUPER_FAST_HUB_LOCKED law. Founder clicks only. Done when lawful path named and heavy rebuild rejected with reason.

### 058

Dual hub heal plus h2_pending_registry sync — run hub_dual_heal_v1.py. Paste two-hub-heal receipt ok line. Done when receipt ok:true and pending registry mtime fresh.

### 059

Worker law reminder: daily operational truth is H1 worker-hub/v1 plus ~/.sina JSON — not routine /machines/ browsing. Apply this when scope is ambiguous. Done when you state which hub tier applies to this task.

### 060

Convert this founder request into H1 one-tap Action spec for Maintainer SHIP — founder clicks only, no Terminal. Include button label, API action id, and success receipt path. Done when Action spec is paste-ready for Maintainer workspace.

### 061

Form mirror: live_founder_decision_form_v1.py --json — report open_questions_count and top three question ids. Link each to M1 Canvas or receipt if answered. Done when JSON fields pasted with paths.

### 062

Which receipt moved in the last hour? List path, ok field, mtime — not hub color. Sort by mtime descending, top five only. Done when table of receipts with timestamps.

## Ship · lock (10)

### 063

Implement only the scope I attached or stated — match repo conventions, minimal diff, no drive-by cleanup. Run validators before you say done; founder never runs Terminal. Done when changed files listed, validator PASS pasted, and receipt path if state moved.

### 064

Ship proof: run machine_test_ladder daily tier green and cite all receipt paths in closeout. No ship talk if ladder fails. Done when steps_passed equals total and paths in bullet list.

### 065

Lock this decision: one new LOCKED doc or one clause in existing LOCKED doc — no parallel duplicate rules or .mdc copies. Supersede old version to archive/superseded/ if bumping version. Done when LOCKED file path pasted and authority index updated if required.

### 066

Save attachment under archive/attachments/YYYY-MM-DD/ with traceable tag and role in filename. Content must be self-contained for a new chat. Done when full attachment path pasted.

### 067

Update roadmap/WTM only if convinced by disk evidence — attach proof, do not renumber phases from critic paste. ASF order or Form pick required for step order changes. Done when diff shows only convinced rows changed.

### 068

Implement the attached plan exactly — do not edit the plan file itself. Stop at plan boundaries; defer extras to H2 deferred bucket. Done when plan checklist items marked with validator proof each.

### 069

Before ship: machine_upgrade_baseline_v1.py --tag before, apply change, run forge or tune, baseline --tag after. Report critical_count delta. Done when before/after JSON paths and delta pasted.

### 070

Name W1/W2/W3 delta for this change — if none applies, defer row to H2 pending registry with reason. Do not invent upgrade ids. Done when tier label or defer receipt cited.

### 071

No fake progress: show validator stdout or receipt JSON — otherwise status must be BLOCKED. Vibes and 'should work' are forbidden. Done when proof artifact is in the message or BLOCKED is honest.

### 072

Upgrade fully in order: contract → validator → code → receipt → surface (H1 one-line OR H2 table, not both). Skip no step. Done when all five layers cited with paths.

## Form · ASF (8)

### 073

Add this decision as open question on live founder Form — not a chat-only bullet list. Use live_founder_decision_form_v1.py append API or lawful disk write. Done when new question id pasted from Form JSON.

### 074

Read my last Form answer as ASF order — execute exactly that pick, update SSOT, mark Form row answered from evidence. Do not reinterpret the pick wider than written. Done when Form row status answered and SSOT diff cited.

### 075

Five-step SCAN→SAY→PICK→PROVE→SHIP: run SCAN logged truth, SAY status in five lines, propose one PICK for Form, wait for founder — do not SHIP without PROVE. Founder clicks Form, not Terminal. Done when SCAN+SAY pasted and PICK row draft ready.

### 076

List must-do-now items missing from Form and mandatory rule list — prioritize top five by P0 impact. Add gaps to Form as open questions. Done when top five table with add-to-Form ids.

### 077

Multi-sentence founder fork goes to Form row plus H2 deferred bucket — never a long chat decision list. One row per fork option. Done when Form ids created and chat summary points to Form.

### 078

What is open on Form right now? List each open question id with one-line summary and link to M1 Canvas or receipt if partial. Disk JSON only. Done when complete open list or explicit zero open.

### 079

ASF approved this Form pick — execute exactly that row scope, then mark Form answered from validator or receipt evidence. No scope expansion. Done when pick id closed and proof path in answer field.

### 080

Defer scope creep: if task is not on Form and not direct ASF order, add to H2 deferred bucket — do not implement. Tell founder which Form row to open. Done when defer receipt or new Form row id pasted.

## Test · refine (8)

### 081

Run machine_test_ladder_run_v1.py --tier daily --json — paste steps_passed, steps_total, and first FAIL step if any. Daily tier is minimum bar for factory days. Done when ladder JSON block in reply.

### 082

Run weekly ladder tier plus find_critical_bugs — ship talk blocked if critical_count > 0. Report both receipts. Done when weekly steps_passed and critical_count 0 or BLOCKED.

### 083

Run validate-agent-three-pipelines-v1.sh and validate-machine-three-pipelines-v1.sh. Both must PASS for refinement routers to be trusted. Done when dual PASS/FAIL with first error line if fail.

### 084

Run validate-anti-staleness-bundle-v1.sh — weekly gate, report first FAIL only. Do not dump full log. Done when PASS or single FAIL identifier.

### 085

machine_upgrade_baseline_v1.py --tag before then after this session's change — show critical_count delta. Tags must be unique and dated. Done when both baseline paths and delta number.

### 086

Test plus upgrade plan: read SOURCEA_MACHINE_TEST_AND_UPGRADE_LADDER_LOCKED_v1.md, name one W1/W2/W3 gap from disk, propose one UP-id for H2 registry. Planning only unless ASF says implement. Done when gap, tier, and UP-id row draft pasted.

### 087

ecosystem_master_catalog_v1.py --json — use for planning and coverage maps only, not daily run-all. Summarize count by tier. Done when catalog stats pasted, no mass execution.

### 088

Tune then report: if tune receipt shows escalate_forge true, stop factory work until forge passport complete. State hold reason from receipt JSON. Done when escalate flag cited and factory hold honored.

## Research · advisor (6)

### 089

Deep search VC-grade on the topic I state — save report plus lessons under archive/attachments/ with date folder, wire WTM only if convinced. Follow sina-research-lessons skill flow. Done when report path and three golden insights pasted.

### 090

Read pasted content — compare to latest LOCKED law, add insight table, rewrite as one canonical doc proposal (not duplicate rules). First line if critic paste: INPUT CLASS EXTERNAL_CRITIC. Done when accept/reject/duplicate verdict per item.

### 091

Unify fragmented docs: one topic → one LOCKED file, move superseded to archive/superseded/, update authority index pointers only. No parallel read-first chains. Done when canonical path and archived paths listed.

### 092

Session index: unify this chat arc into one router attachment — decisions, receipts, mistakes, next actions — nothing lost. Self-contained for cold start. Done when attachment path under archive/attachments/ pasted.

## Cursor · session · critic (6)

### 095

@REFINEMENT_UNIFIED_AGENT_MACHINE_LOCKED_v1.md — execute one lawful refinement action with receipt proof. Agent mode, batch reads first. Done when unified router or pipeline receipt pasted.

### 096

@FOUNDER_DAILY_PROMPT_PACK_LOCKED_v1.md — run prompt 081 exactly as written in Agent mode. Do not paraphrase the order. Done when prompt 081 DONE-WHEN criteria met.

### 097

Batch parallel reads this turn — gather all context first, then one implement action. I do not run Terminal; you run every command. Done when read list cited and single action outcome with proof.

---
*End — v3 pro long · 100 prompts*
