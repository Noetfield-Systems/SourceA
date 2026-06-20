# Founder daily prompt pack — v2 smart (100 frozen reference)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Formula:** ACTION + SCOPE + DONE-WHEN (disk receipt or PASS/FAIL)

**Status:** Frozen reference — prefer **v3 pro** for daily use

## One-word routers (6)

**001.** orientation _(Runs agent orientation pipeline · reading pack · no execution)_

**002.** hospital _(Agent hospital · memory · gate · heal · discharge receipt)_

**003.** maze _(Agent maze gauntlet · passport required)_

**004.** calibrate _(Machine map · validators · upgrade board)_

**005.** tune _(Machine daily test ladder + baseline)_

**006.** forge _(Machine upgrade proof · weekly/monthly ladder)_

## Factory · INBOX (12)

**007.** Run Worker INBOX now: read ~/.sina/worker-prompt-inbox-v1.json, execute disk prompt, broker-submit, stop.

**008.** INBOX CHECK turn only: read bound sa, run read-only validators, gap report — no code changes.

**009.** INBOX ACT turn only: minimal diff for bound sa_id only, then stop — no closeout.

**010.** INBOX VERIFY turn only: validators + honest closeout + critical 0, then broker-submit.

**011.** Show factory-now from disk: queue head sa_id, role, position, factory mode, turn open/closed.

**012.** If orchestrator idle and inbox pending: run one INBOX turn; if blocked print BLOCKED + disk reason.

**013.** Fix turn-bind drift: goal1-worker-turn-bind and headsup must match queue head sa — show before/after.

**014.** Broker submit after this turn: WORKER_ROUND_REPORT YAML last lines, orchestrator must advance.

**015.** Drain one sa only — pick 1 from plan-no-asf-run.sh, execute, stop. No batch.

**016.** Run agent-loop response POST if this was a SINA_LOOP round — summary + full body.

**017.** Feasibility gate first: prompt_feasibility_gate worker strict. If STOP_INJECT, report and do not implement.

**018.** Never claim done without receipt: show path to receipt JSON that moved this turn.

## Smart checks (20)

**019.** Daily health snapshot: queue head, critical_count, form open count, H1 health — all from disk JSON.

**020.** Run validate-super-fast-hub-v1.sh and validate-two-hub-v1.sh — report PASS/FAIL only.

**021.** Run find_critical_bugs.py — report critical_count and verdict from last-run.json.

**022.** Run agentic_layer_pipeline_v2.py --tier fast --json — report health.status and issues.

**023.** Blocker sweep: architect_report.yaml + global_blockers — list open P0, owner, fix or escalate.

**024.** Cross-chat drift: compare Worker/Brain/Maintainer last claims to disk — list mismatches only.

**025.** Ingest check: SinaPromptOS outputs/inbox/rejected/ must be empty — if not, repair and re-ingest.

**026.** Broker check: last WORKER_ROUND_REPORT matches orchestrator expected sa and role.

**027.** Session gate: agent_session_gate_run_v1.py --role worker --json — paste gate_id and ok.

**028.** Registry honest: dry-run enforce_honest_registry — unproven done rows only.

**029.** Anti-staleness spot: run validate-hub-p0-no-autorun-v1.sh — INCIDENT-028 class.

**030.** Hub alignment: audit_hub_source_alignment.py — WTM steps vs hub surface.

**031.** Read-only audit: no file edits — list gaps with file paths and suggested next single action.

**032.** Two-hub sibling check: H1 worker-hub/v1 size <16KB, H2 machine-hub health fresh — not nested UI.

**033.** Agentic wire: validate-agentic-layer-wire-v1.sh — Brain L1 L2 master PASS/FAIL.

**034.** Governance fast: governance_center_run_v1.py --tier fast --json — any step fail?

**035.** Quarantine flags: agent-maze-quarantine and machine-forge-quarantine — active true/false.

**036.** E2E factory loop: inbox pending → execute → broker advanced → orchestrator idle. Report each step.

**037.** Compare UI vs receipt: if hub green but receipt stale, receipt wins — say STALE.

**038.** Give me a 5-line status report: P0 task, queue, blockers, critical_count, next one tap for me.

## Fix · heal (14)

**039.** Auto-heal routine: hub_dual_heal_v1.py then machine_tune --ladder-tier daily — paste both receipts.

**040.** Fix highest P0 blocker only — minimal diff, one validator proof, stop.

**041.** Hospital this agent (--role worker): run pipeline, paste discharge note or maze escalation.

**042.** If critical_count > 0: do not ship — run forge or fix root cause until critical 0.

**043.** Repair yesterday's drift: re-read receipts from last session, fix orphan turn or stale bind.

**044.** Debug with evidence: reproduce, root cause, minimal fix, re-run failing validator.

**045.** Incident write-up: save to brain-os/incidents/ with reason, fix, validator proof.

**046.** Clear rejected ingest: repair_promptos_rejected_ingest if any files in rejected inbox.

**047.** Fix false green: hub says OK but receipt old — light refresh + dual heal + re-validate.

**048.** Fix lane cross: Brain must not execute Worker turn — route to correct agent.

**049.** Memory sync: agent_memory_mirror_v1.py --sync --validate --json before next INBOX.

**050.** Self-heal loop: detect → classify → fix → harden validator → verify receipt — log near-miss.

**051.** Mistake audit this chat: list errors vs disk, unify into session attachment, correct SSOT.

**052.** Both refine: refinement_unified_router_v1.py both hospital tune --role worker --json.

## Hub H1/H2 (10)

**053.** H1 Super Fast only: curl worker-hub/v1 — task, queue, form count, health. No legacy, no 9MB.

**054.** Light refresh hub (mode light) — then confirm H1 health pill fresh logged.

**055.** Safety check path: run anti-staleness fast subset relevant to founder daily — report only.

**056.** H2 deep link only when needed: pending registry + Judge alarm — do not embed on H1.

**057.** Never full hub rebuild on founder Refresh — cite SUPER_FAST_HUB law if tempted.

**058.** Dual hub heal + h2_pending_registry sync — paste two-hub-heal receipt ok line.

**059.** Worker law reminder: daily truth = H1 + disk JSON — not routine /machines/ browsing.

**060.** Convert this request into H1 one-tap Action spec (Maintainer SHIP) — I click only.

**061.** Form mirror: live_founder_decision_form_v1.py --json — open_questions_count and top ids.

**062.** Which receipt moved last hour? List path + ok field — not hub color.

## Ship · lock (10)

**063.** Implement this scope only — match repo conventions, minimal diff, validators before you say done.

**064.** Ship proof: run tier daily ladder green + cite receipt paths in closeout.

**065.** Lock this decision: one new LOCKED doc or clause — no parallel duplicate rules.

**066.** Save attachment under archive/attachments/YYYY-MM-DD/ with traceable tag and role in filename.

**067.** Update roadmap/WTM only if convinced — attach evidence, do not renumber from critic paste.

**068.** Implement the attached plan — do not edit the plan file itself.

**069.** Before ship: baseline --tag before, change, forge or tune, baseline --tag after.

**070.** Name W1/W2/W3 delta for this change — if none, defer to H2 pending registry.

**071.** No fake progress: show validator output or receipt JSON — otherwise status BLOCKED.

**072.** Upgrade fully: contract → validator → code → receipt → H1 one-line OR H2 table, not both.

## Form · ASF (8)

**073.** Add this decision to live founder Form as open question — not chat-only list.

**074.** Read my last Form answer as ASF order — update SSOT and Form answered row.

**075.** Five-step SCAN→SAY→PICK→PROVE→SHIP: run SCAN logged, propose one PICK for Form.

**076.** List must-do-now items missing from Form and mandatory rule list — prioritize top 5.

**077.** Multi-sentence founder fork → Form row + H2 bucket — never long chat decision list.

**078.** What is open on Form right now? Link each id to M1 Canvas or receipt.

**079.** ASF approved this pick — execute exactly that row, then mark Form answered from evidence.

**080.** Defer scope creep: if not on Form and not ASF direct order, add to H2 deferred bucket.

## Test · refine (8)

**081.** Run machine_test_ladder_run_v1.py --tier daily --json — paste steps_passed/total.

**082.** Run weekly ladder + find_critical_bugs — ship talk blocked if critical_count > 0.

**083.** Run validate-agent-three-pipelines-v1.sh and validate-machine-three-pipelines-v1.sh.

**084.** Run validate-anti-staleness-bundle-v1.sh — weekly gate, report first FAIL only.

**085.** machine_upgrade_baseline_v1.py --tag before then after — show critical_count delta.

**086.** Test + upgrade plan: read SOURCEA_MACHINE_TEST ladder law, name W1/W2/W3 gap, propose one UP-id.

**087.** ecosystem_master_catalog_v1.py --json — use for planning only, not daily run-all.

**088.** Tune then report: if escalate_forge true, stop factory work until forge passport.

## Research · advisor (6)

**089.** Deep search VC-grade — save report + lessons under archive/attachments, wire WTM if convinced.

**090.** Read pasted content — add insight vs LOCKED law, rewrite as one canonical doc proposal.

**091.** Unify fragmented docs: one topic → one LOCKED file, archive superseded paths.

**092.** Session index: unify this chat arc into one router attachment — nothing lost.

## Cursor · session · critic (6)

**095.** @REFINEMENT_UNIFIED_AGENT_MACHINE_LOCKED_v1.md — execute one lawful action with receipt proof.

**096.** @FOUNDER_DAILY_PROMPT_PACK_LOCKED_v1.md prompt 081 — run it exactly, Agent mode.

**097.** Batch parallel reads this turn — then one implement action. I do not run Terminal.

---
*End — v2 smart reference · 100 prompts*
