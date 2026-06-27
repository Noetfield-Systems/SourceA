#!/usr/bin/env python3
"""Live founder decision form — machine mirror for pending/answered/open questions."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from governance_paths_v1 import FOUNDER_MESSAGE_NORM, LIVE_FOUNDER_FORM

FORM_MD = LIVE_FOUNDER_FORM
NORM_MD = FOUNDER_MESSAGE_NORM
FIRST_FORM_ARCHIVE = (
    ROOT / "archive/attachments/2026-06-11/SOURCEA_LIVE_FOUNDER_DECISION_FORM_FIRST_FORM_LOCKED_v1.md"
)
RECEIPT = Path.home() / ".sina" / "live-founder-decision-form-v1.json"
INTAKE_PATH = Path.home() / ".sina/live-founder-decision-form-intake-v1.json"
FIRST_FORM_JSON = Path.home() / ".sina" / "live-founder-decision-form-first-v1.json"
SECOND_FORM_ARCHIVE = (
    ROOT / "archive/attachments/2026-06-12/SOURCEA_LIVE_FOUNDER_DECISION_FORM_SECOND_FORM_LOCKED_v1.md"
)
SECOND_FORM_JSON = Path.home() / ".sina" / "live-founder-decision-form-second-v1.json"
ANSWERS_RECEIPT_JSON = Path.home() / ".sina" / "live-founder-decision-form-v2-answers.json"
ANSWERS_RECEIPT_MD = (
    ROOT
    / "archive/attachments/2026-06-11/SOURCEA_LIVE_FOUNDER_DECISION_FORM_V2_ANSWERS_RECEIPT_2026-06-11_LOCKED_v1.md"
)
FORM_EDITION = "v2"
THIRD_FORM_JSON = Path.home() / ".sina" / "live-founder-decision-form-third-v1.json"
GATHERING_PHASE_PATH = Path.home() / ".sina/form-official-gathering-phase-v1.json"
EXTRACTION_PATH = Path.home() / ".sina/live-founder-decision-form-extraction-v1.json"
FINAL_FIX_JSON = Path.home() / ".sina/live-founder-decision-form-final-fix-v1.json"
NERVE_MAP_JSON = ROOT / "data/form_official_nerve_map_v1.json"
ASF_FILLED_AT = "2026-06-11T21:15:00Z"
DRIFT_FLOOR = 90

SHIPPED_CANVAS = frozenset(
    {
        "1.02",
        "1.05",
        "1.08",
        "2.02",
        "2.03",
        "2.04",
        "2.05",
        "2.06",
        "2.07",
        "2.08",
        "2.09",
        "3.07",
        "4.08",
        "5.08",
        "6.07",
        "6.10",
        "7.05",
        "7.06",
        "7.07",
        "8.08",
        "8.09",
        "9.07",
        "9.08",
        "10.07",
        "10.09",
        "10.10",
        "11.01",
        "11.02",
        "11.03",
        "11.04",
        "11.05",
        "Q-PLAN-300",
    }
)

CANVAS_OPEN: frozenset[str] = frozenset()

CANVAS_SESSION_PICKS = [
    {
        "id": "3.07",
        "pick": "NO",
        "ruling": "No GOV_UNIFY batch · Phase 3 index-only · skip unification engine",
        "evidence": "ASF FIVE-STEP PICK batch 2026-06-12 · SOURCEA_INTEGRITY_PICK_BATCH_2026-06-12_LOCKED_v1.md",
    },
    {
        "id": "5.08",
        "pick": "APPROVE",
        "ruling": "sa-0798 check turn · factory background only",
        "evidence": "ASF FIVE-STEP PICK batch 2026-06-12",
    },
    {
        "id": "6.07",
        "pick": "B",
        "ruling": "Council stays Phase 1 until W3 signal",
        "evidence": "ASF FIVE-STEP PICK batch 2026-06-12",
    },
    {
        "id": "6.10",
        "pick": "NO",
        "ruling": "Roster trimmed to 7 agents — sinaai_maintainer removed (ASF 2026-06-15)",
        "evidence": "ASF FIVE-STEP PICK batch 2026-06-12",
    },
    {
        "id": "7.05",
        "pick": "DEFER",
        "ruling": "Conflict #1 logged · continue_work · ACE triage only",
        "evidence": "ASF FIVE-STEP PICK batch 2026-06-12",
    },
    {
        "id": "7.07",
        "pick": "NEVER",
        "ruling": "No paradox→policy LOCKED doc this sprint",
        "evidence": "ASF FIVE-STEP PICK batch 2026-06-12",
    },
    {
        "id": "8.08",
        "pick": "YES",
        "ruling": "Weekly incident certify on",
        "evidence": "ASF FIVE-STEP PICK batch 2026-06-12",
    },
    {
        "id": "8.09",
        "pick": "B",
        "ruling": "Keep existing incident severity rubric · registry as-is",
        "evidence": "ASF FIVE-STEP PICK batch 2026-06-12",
    },
    {
        "id": "9.07",
        "pick": "A",
        "ruling": "30-day ship order: ENFORCE W1 film + NOETFIELD-W3 batch 1 · FORGE/MergePack background",
        "evidence": "ASF FIVE-STEP PICK batch 2026-06-12 · SOURCEA_SHIP_ORDER_9_07_RECEIPT_2026-06-12_LOCKED_v1.md",
    },
    {
        "id": "9.08",
        "pick": "C",
        "ruling": "Defer Paid.ai billing pilot until post-W3",
        "evidence": "ASF FIVE-STEP PICK batch 2026-06-12",
    },
    {
        "id": "10.07",
        "pick": "B",
        "ruling": "Integrity playbook monthly SCAN cadence",
        "evidence": "ASF FIVE-STEP PICK batch 2026-06-12",
    },
    {
        "id": "Q-PLAN-300",
        "pick": "LOCKED",
        "ruling": "Tier-1 commercial P0 five-step block locked until ASF supersede",
        "evidence": "SOURCEA_COMMERCIAL_P0_FIVE_STEP_PICK_BATCH_2026-06-13_LOCKED_v1.md",
    },
    {
        "id": "11.01",
        "pick": "SHIP",
        "ruling": "W3 TF+NF outreach this week",
        "evidence": "PLAN-001,002,103,273 · PLAN-300 block",
    },
    {
        "id": "11.02",
        "pick": "SHIP",
        "ruling": "Film W1 ALLOW/TAMPER/BLOCK under 6 min",
        "evidence": "PLAN-041–044 · PLAN-300 block",
    },
    {
        "id": "11.03",
        "pick": "SHIP",
        "ruling": "K1 receipt on read + export + bypass=0",
        "evidence": "PLAN-026,038,141,145,157 · Maintainer 2",
    },
    {
        "id": "11.04",
        "pick": "SHIP",
        "ruling": "Procurement pack — SOW + SOC2 letter + security deck",
        "evidence": "PLAN-006,064,065,140,217",
    },
    {
        "id": "11.05",
        "pick": "SHIP",
        "ruling": "Instrument TF+NF workflows + 10-min scaffold",
        "evidence": "PLAN-076,077,201,217",
    },
]

HUB_REPAIR_POLICY = (
    "FORM v2 FILLED · RT LIVE PASS · Phase 3–10 resume · "
    "ENFORCE W1 + W3 parallel · FR-003 P0 · no Cursor AUTO-RUN"
)

# FIRST FORM (v1) — frozen 2026-06-11 — see FIRST_FORM_ARCHIVE
FIRST_FORM_QUESTIONS = [
    {"id": "Q-HUB-REPAIR", "question": "Confirm hub repair-only until RT wired — yes/no"},
    {"id": "Q-1.10", "question": "Seal Phase 1 now or defer until hub RT?"},
    {"id": "Q-7.06", "question": "GPT report-only (FR-003) — yes/no"},
    {"id": "Q-10.10", "question": "After repair: playbook 3–10 / WTM / Layer A / pause"},
    {"id": "Q-10.09", "question": "System grade A/B/C/D + why"},
    {"id": "Q-4.08", "question": "Min drift score 85/90/95/100"},
]

# v2 answers — ASF 2026-06-11 (receipt logged)
ANSWERED_V2 = [
    {
        "id": "Q-RT-LIVE",
        "pick": "YES",
        "ruling": "Hub repair-only until RT LIVE proven · no Cursor AUTO-RUN · no auto-prompt",
        "evidence": "ASF FIVE-STEP 2026-06-11 · SOURCEA_LIVE_FOUNDER_DECISION_FORM_V2_ANSWERS_RECEIPT_2026-06-11_LOCKED_v1.md",
    },
    {
        "id": "Q-1.10",
        "pick": "DEFER",
        "ruling": "Seal Phase 1 closeout after hub RT LIVE wired",
        "evidence": "ASF FIVE-STEP 2026-06-11 · SESSION_LOG 1.10 stays DEFERRED",
    },
    {
        "id": "Q-CRITIC",
        "pick": "YES",
        "ruling": "EXTERNAL_CRITIC report-only · never auto-apply build specs",
        "evidence": "ASF FIVE-STEP 2026-06-11 · FR-2026-06-05-003",
    },
    {
        "id": "Q-NEXT-WORK",
        "pick": "10.10 D",
        "ruling": "Pause Phases 3–10 until hub RT LIVE · then continue SYS-INTEGRITY playbook",
        "evidence": "ASF FIVE-STEP PICK 2026-06-11",
    },
    {
        "id": "Q-GRADE",
        "pick": "C",
        "ruling": "Spine green · hub not RT LIVE yet",
        "evidence": "ASF FIVE-STEP 2026-06-11 · SESSION_LOG",
    },
    {
        "id": "Q-DRIFT",
        "pick": "90",
        "ruling": "Minimum governance drift score 90",
        "evidence": "ASF FIVE-STEP 2026-06-11 · drift_floor=90",
    },
]

# Live v2 question templates (archived — all answered)
OPEN_QUESTIONS_TEMPLATE = [
    {
        "id": "Q-RT-LIVE",
        "title": "Hub repair until RT LIVE",
        "question": "Lock hub + auto-prompt OFF for Cursor agents until RT LIVE bar is proven (cascade + hub-sync seconds, not minutes)?",
        "blocks": "Hub activation · AUTO-RUN · agent autorun",
        "recommended": "YES",
        "options": [
            "YES — repair-only until RT LIVE (monitor/inbox RT today; hub full panel still LAG)",
            "NO — allow hub hero to drive agents before RT proof (not recommended)",
        ],
        "effect": "YES → FREEZE copy + form stays live · NO → Maintainer must cite ASF override receipt",
        "reply_template": (
            "ASF: FIVE-STEP — QUESTION on [Q-RT-LIVE]\n"
            "YES — hub repair-only until RT LIVE proven · no Cursor AUTO-RUN · no auto-prompt\n"
            "Effect: hub stays custodian/read-only for agents until Phase 4 RT gate PASS"
        ),
    },
    {
        "id": "Q-1.10",
        "title": "Phase 1 closeout seal",
        "question": "Phase 1 validators already PASS — seal closeout now or defer until hub RT LIVE?",
        "blocks": "Playbook Phase 2→3 gate · SESSION_LOG 1.10",
        "recommended": "DEFER",
        "options": [
            "DEFER — seal 1.10 after hub RT LIVE wired (recommended with repair mode)",
            "YES — seal Phase 1 closeout now (validators already PASS)",
        ],
        "effect": "DEFER → 1.10 stays deferred logged · YES → Maintainer marks 1.10 DONE + receipt",
        "reply_template": (
            "ASF: FIVE-STEP — QUESTION on [Q-1.10]\n"
            "DEFER — seal Phase 1 closeout after hub RT LIVE wired\n"
            "Effect: integrity Phase 3+ stays parked until hub RT + your Q-NEXT-WORK pick"
        ),
    },
    {
        "id": "Q-CRITIC",
        "title": "GPT / external critic default",
        "question": "Lock GPT and external paste to report-only (EXTERNAL_CRITIC) — never auto-apply build specs?",
        "blocks": "FR-2026-06-05-003 · CHATGPT_EXTERNAL_CRITIC law",
        "recommended": "YES",
        "options": [
            "YES — report-only default · compare to LOCKED · ASF adopt row required to ship",
            "NO — allow GPT paste to steer builds (violates CRITIC law)",
        ],
        "effect": "YES → close FR-003 on answer · Maintainer wires default class on paste paths",
        "reply_template": (
            "ASF: FIVE-STEP — QUESTION on [Q-CRITIC]\n"
            "YES — EXTERNAL_CRITIC report-only · never auto-apply build specs\n"
            "Effect: FR-003 shippable · Brain/Worker ignore GPT build orders without adopt row"
        ),
    },
    {
        "id": "Q-NEXT-WORK",
        "title": "After hub repair — what next",
        "question": "When hub RT LIVE is proven, what is the next integrity priority?",
        "blocks": "SYS-INTEGRITY-100 Phases 3–10 · WTM · Layer A",
        "recommended": "D",
        "options": [
            "A — Continue SYS-INTEGRITY playbook Phases 3–10 on Canvas",
            "B — Pivot to WTM ENFORCE gate + strategic slice only",
            "C — Personal DB Layer A promotion only",
            "D — Pause integrity phases until hub RT proven, then A (recommended now)",
        ],
        "effect": "Pick sets PROGRAM_PROGRESS founder_open and Maintainer phase order",
        "reply_template": (
            "ASF: FIVE-STEP — PICK: 10.10 D — pause Phases 3–10 until hub RT LIVE, then continue playbook\n"
            "Effect: Maintainer holds Phase 3 law batch until RT gate · factory Worker still one sa/turn"
        ),
    },
    {
        "id": "Q-GRADE",
        "title": "Honest system grade",
        "question": "Letter grade for the whole machine today (factory spine + hub + governance)?",
        "blocks": "SESSION_LOG · Track honesty",
        "recommended": "C",
        "options": [
            "A — RT LIVE end-to-end · hub instant · no LAG",
            "B — spine green · hub LAG under 60s on light path",
            "C — factory/monitor RT · hub repair · form live (typical today)",
            "D — critical bugs or dual_proof broken",
        ],
        "effect": "Logged to SESSION_LOG + Track — not cosmetic",
        "reply_template": (
            "ASF: FIVE-STEP — QUESTION on [Q-GRADE]\n"
            "C — factory spine and validators green · hub not RT LIVE yet · form v2 live\n"
            "Effect: honest grade locally for Phase 1.10 closeout table"
        ),
    },
    {
        "id": "Q-DRIFT",
        "title": "Governance drift floor",
        "question": "Minimum acceptable governance drift score before hub shows red / blocks ship?",
        "blocks": "Phase 4.08 · drift engine · hub tile",
        "recommended": "90",
        "options": ["85 — lenient", "90 — balanced (recommended)", "95 — strict", "100 — zero tolerance"],
        "effect": "Sets drift engine threshold config after pick",
        "reply_template": (
            "ASF: FIVE-STEP — QUESTION on [Q-DRIFT]\n"
            "90 — minimum governance drift score\n"
            "Effect: drift engine + hub red tile use 90 until superseded"
        ),
    },
]

OPEN_QUESTIONS_CORE: list[dict] = [
    {
        "id": "Q-1.10-SEAL",
        "number": 1,
        "title": "Phase 1.10 closeout seal",
        "question": "RT LIVE gate is PASS logged. Seal Phase 1 closeout now?",
        "blocks": "SESSION_LOG 1.10 · INTEGRITY playbook Phase 1",
        "recommended": "YES",
        "options": [
            "YES — seal 1.10 DONE · update SESSION_LOG",
            "DEFER — wait until cascade sustained 7 days",
            "NO — keep 1.10 open",
        ],
        "effect": "YES → Maintainer marks 1.10 DONE · Phase 3–10 resume unblocked",
        "asked_by": "Maintainer 2 · 2026-06-12",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-1.10-SEAL YES — seal Phase 1 closeout",
    },
    {
        "id": "Q-M2-029",
        "number": 2,
        "title": "INCIDENT-029 remediation SHIP",
        "question": "SHIP Canvas tick sync + hub must_do scrub + form §OPEN sync (029 class)?",
        "blocks": "INCIDENT-029 · M1 Canvas slot D",
        "recommended": "YES",
        "options": ["YES — Maintainer 2 SHIP all 029 remediation", "PARTIAL — hub only", "DEFER"],
        "effect": "YES → hub stops saying Open Canvas 7.05 · Canvas matches batch PICK",
        "asked_by": "Maintainer 2 · 2026-06-12",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-M2-029 YES",
    },
    {
        "id": "Q-M2-REG",
        "number": 3,
        "title": "Regulator hub Action",
        "question": "Add one-tap Sina Command Action: run governance_signal_regulator on paste?",
        "blocks": "Founder signal intake · zero governance latency",
        "recommended": "YES",
        "options": ["YES — ship hub Action", "DEFER — script only for now"],
        "effect": "YES → every founder message auto-scored 13 layers + P0–P7",
        "asked_by": "Maintainer 2 · 2026-06-12",
        "reply_template": "ASF: SHIP regulator hub Action",
    },
    {
        "id": "Q-INC-015",
        "number": 4,
        "title": "INCIDENT-015 conduct disposition",
        "question": "Pick disposition for INCIDENT-015 (015-CONDUCT vs 023 collision)?",
        "blocks": "Incident registry · cadence drill",
        "recommended": "B",
        "options": [
            "A — archive 015 draft only",
            "B — refile under 023 conduct (recommended)",
            "C — founder workshop",
            "D — defer",
        ],
        "effect": "Unlocks conduct cadence drill without ID collision",
        "asked_by": "Maintainer 2 transcript audit",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-INC-015 B",
    },
    {
        "id": "7.05",
        "number": 5,
        "title": "Who wins when agents push AUTO-RUN but you still have open form picks?",
        "question": "Conflict Case 1 — confirm DEFER (keep working; weekly ACE review) or pick another disposition?",
        "blocks": "Conflict room · form-first vs factory hero",
        "diskToday": "Case 1 logged · FR-003 + 9.07 A form-first · continue_work",
        "recommended": "DEFER",
        "options": [
            "DEFER — keep executing picks · weekly review (recommended)",
            "A — auto-resolve · form-first permanent in ACE",
            "B — escalate · founder call on Case 1",
            "C — stop related work until Case 1 closed",
        ],
        "effect": "DEFER → Case 1 logged · agents stay on film/W3 picks",
        "option_effects": {
            "DEFER": "Case 1 stays logged · agents keep film/W3 picks · weekly ACE review",
            "A": "ACE registry · form-first permanent · factory must refuse AUTO-RUN hero",
            "B": "Case 1 escalated · AECT schedules founder sync",
            "C": "Hard stop on Cloud Forge Run + Hub rebuild until Case 1 closed",
        },
        "asked_by": "Founder comment on Canvas · Maintainer 1 form",
        "reply_template": "ASF: FIVE-STEP — PICK: 7.05 DEFER",
    },
    {
        "id": "7.06",
        "number": 6,
        "title": "Advisor paste (ChatGPT audit) — report only, never reorder build",
        "question": "Case 2 — confirm YES: every advisor paste is report-only (matches FR-003 logged)?",
        "blocks": "Advisor paste law · FR-003",
        "diskToday": "FR-003 shipped · critic template in agent rules",
        "recommended": "YES",
        "options": [
            "YES — report-only locked (recommended)",
            "NO — revert FR-003",
            "EXPLAIN — need second example on card",
        ],
        "effect": "YES → FR-003 stays · no step changes from paste alone",
        "option_effects": {
            "YES": "FR-003 stays law · agents classify paste before acting",
            "NO": "FR-003 revert requested · Gov drafts rollback",
            "EXPLAIN": "Row stays open · Gov posts second example · no rule change yet",
        },
        "asked_by": "Founder comment · Canvas 7.06",
        "reply_template": "ASF: FIVE-STEP — PICK: 7.06 YES",
    },
    {
        "id": "7.07",
        "number": 7,
        "title": "Do not turn this sprint paradox into a new law file yet",
        "question": "Confirm NEVER — no new paradox LOCKED doc this sprint (W1 film + W3 priority)?",
        "blocks": "Integrity sprint scope · ACE paradox notes",
        "diskToday": "Paradox in ACE notes · no new paradox law file this week",
        "recommended": "NEVER",
        "options": [
            "NEVER — room notes only (recommended)",
            "YES — author LOCKED clarification now",
            "DEFER — revisit after W1 PASS",
        ],
        "effect": "NEVER → no new paradox law file · execute W1/W3 picks",
        "option_effects": {
            "NEVER": "No new paradox law file · agents stay on film/W3 spine",
            "YES": "Gov + AECT draft new LOCKED doc · sprint scope widens",
            "DEFER": "Paradox parked until W1 PASS receipt",
        },
        "asked_by": "Founder: EXPLAIN CLEARLY · Canvas 7.07",
        "reply_template": "ASF: FIVE-STEP — PICK: 7.07 NEVER",
    },
    {
        "id": "8.09",
        "number": 8,
        "title": "Incident severity rubric",
        "question": "Keep existing registry rubric (pick B) — confirm after explanation?",
        "blocks": "AGENT_INCIDENTS_REGISTRY",
        "recommended": "B",
        "options": ["B — keep rubric", "A — tighten", "C — loosen", "EXPLAIN more"],
        "effect": "B → no rubric rewrite this sprint",
        "asked_by": "Founder: EXPLAIN CLEARLY · Canvas 8.09",
        "reply_template": "ASF: FIVE-STEP — PICK: 8.09 B",
    },
    {
        "id": "2.02",
        "number": 9,
        "title": "SourceA public-site mirror — stay parallel-private?",
        "question": "Quarantine mirror (not TrustField / Noetfield) — pick C parallel-private, B hold, or A promote after gates?",
        "blocks": "Product surface · SourceA quarantine mirror",
        "diskToday": "Quarantine active · no public promote shipped",
        "recommended": "C",
        "options": [
            "C — parallel-private · no public promote (recommended)",
            "B — hold promote until after W1 filmed",
            "A — promote after Stripe + Gov sign-off",
        ],
        "effect": "C → quarantine stays · confidential research path",
        "option_effects": {
            "C": "Quarantine stays · no DNS/marketing promote",
            "B": "Promote decision parked until W1 PASS logged",
            "A": "M1 opens promote checklist · Stripe + Gov gate",
        },
        "asked_by": "Founder Canvas comment 2.02",
        "reply_template": "ASF: FIVE-STEP — PICK: 2.02 C",
    },
    {
        "id": "Q-M2-READ",
        "number": 10,
        "title": "Ack cross-chat synthesis read",
        "question": "Confirm Maintainer 2 read Gov + Commercial + INCIDENT 027/028/029 synthesis logged?",
        "blocks": "All chats · same mistake prevention",
        "recommended": "YES",
        "options": [
            "YES — law locked · M1 form discipline active",
            "NO — re-read synthesis doc first",
        ],
        "effect": "YES → agents use Canvas not chat polls · JSON before hub",
        "asked_by": "ASF order 2026-06-12",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-M2-READ YES",
    },
    {
        "id": "Q-M2-FORM-SYNC",
        "number": 11,
        "title": "FORM_OFFICIAL — sync everything to Canvas",
        "question": "Put ALL §OPEN_QUESTIONS + §PENDING_OUTSIDE_FORM rows on M1 Canvas UI now (ASF: everything on form)?",
        "blocks": "Q-FORM-OFFICIAL · INCIDENT-029 · PACK5 slot D",
        "recommended": "YES",
        "options": [
            "YES — Maintainer 2 SHIP full Canvas sync (recommended)",
            "PARTIAL — open forks only",
            "DEFER",
        ],
        "effect": "YES → every human–machine fork visible in sidebar Canvas · chat backup only",
        "asked_by": "ASF order 2026-06-12 FORM_OFFICIAL",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-M2-FORM-SYNC YES",
    },
    {
        "id": "Q-ENGINE-TEST-01",
        "number": 12,
        "title": "Week-1 24/7 test harness",
        "question": "Approve bounded 24/7 TEST mode: 5 n8n flows · health sweep 15m · no auto-send · aligns ENFORCEMENT W1?",
        "blocks": "SINA_24_7_PARALLEL_ENGINE_FULL_MODE_DESIGN_PLAN · CLOCK C",
        "recommended": "YES",
        "options": [
            "YES — Worker ships Phase 1 test harness (recommended)",
            "PARTIAL — health sweep only",
            "DEFER — design only",
        ],
        "effect": "YES → integration-fabric-registry + n8n wf-health + wf-form-cascade stub",
        "asked_by": "ASF automation engine ask 2026-06-12",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-ENGINE-TEST-01 YES",
    },
    {
        "id": "Q-ENGINE-TEST-02",
        "number": 13,
        "title": "Orchestrator stack",
        "question": "Lock orchestration: n8n primary · Make/Zapier adapters only · Railway/Vercel health lanes?",
        "blocks": "SINA_AUTOMATION_SPINE_AND_N8N · integration fabric",
        "recommended": "YES",
        "options": [
            "YES — n8n-first (recommended)",
            "NO — Zapier-first",
            "DEFER",
        ],
        "effect": "YES → no parallel orchestration SSOT · Raygun/Railway = observability/deploy not law",
        "asked_by": "ASF automation engine ask 2026-06-12",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-ENGINE-TEST-02 YES",
    },
    {
        "id": "Q-JUDGE-STACK-v1",
        "number": 14,
        "title": "Judge Stack — Human · Disk/Machine · AI Center",
        "question": "Approve nested Judge Stack: Human(Form PICK) > Disk+validators > AI Center (Audit→Lawyer→AI Judge→Form row only)?",
        "blocks": "FORM-OFFICE · cross-chat alarms · INCIDENT-029 · EXECUTION_AUTHORITY_MAP",
        "recommended": "A",
        "options": [
            "A — APPROVE — lock draft attachment · ship judge_center v1.0 scripts",
            "B — APPROVE design only — draft locked · scripts DEFER post-W1",
            "C — REVISE — amend draft before any ship",
            "D — REJECT — Form-only office · no Judge Center pipeline",
        ],
        "effect": "A → archive/attachments/2026-06-12/SINA_JUDGE_STACK_DRAFT_v1.md becomes active design · Maintainer ships audit/counsel/bench stubs",
        "asked_by": "ASF YES file 2026-06-12 · cursor-agent draft",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-JUDGE-STACK-v1 A",
        "attachment": "archive/attachments/2026-06-12/SINA_JUDGE_STACK_DRAFT_v1.md",
    },
    {
        "id": "Q-THREAD-ROOM-v1",
        "number": 15,
        "title": "Thread Room — Scout · Cartographer · Curator",
        "question": "Approve Thread Room (separate from Judge Center): map chats · T30 nothing lost · §THREAD rows — Scout→Cartographer→Curator?",
        "blocks": "THREAD-CHAT-CONSOLIDATION · THREAD_ACTIVATION · ROOMS blueprint · LOST_LINK",
        "recommended": "A",
        "options": [
            "A — APPROVE — lock Thread Room draft · ship thread_room v1.0 scripts",
            "B — APPROVE design only — draft locked · scripts DEFER post-W1",
            "C — MERGE with Judge Center — REJECT (keep separate rooms)",
            "D — REJECT — manual Brain thread map only",
        ],
        "effect": "A → SINA_THREAD_ROOM_DRAFT_v1.md active · feeds THREAD-CHAT-CONSOLIDATION · weekly scout workflow",
        "asked_by": "ASF YES file rooms blueprint 2026-06-12",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-THREAD-ROOM-v1 A",
        "attachment": "archive/attachments/2026-06-12/SINA_ROOMS_UNIFIED_BLUEPRINT_DRAFT_v1.md",
    },
    {
        "id": "Q-GOV-FAST-WIRE-v1",
        "number": 16,
        "title": "Fast governance wire — Judge + Thread n8n",
        "question": (
            "Ship the fast governance pack: run Judge + Thread on a schedule (not every worker turn), "
            "15-minute fast center, and n8n triggers — while Super Fast Hub stays light?"
        ),
        "blocks": "Super Fast Hub · integration-fabric v1.4 · Maintainer 2 SHIP · zero governance latency",
        "recommended": "A",
        "options": [
            "A — SHIP full pack — fast center daily · Judge+Thread n8n weekly · alarm strip only on hub (recommended)",
            "B — PARTIAL — Judge n8n batch only · Thread manual weekly",
            "C — DEFER — keep CLI scripts only · no n8n until ENGINE-TEST sustained",
            "D — REJECT — no scheduled room runs",
        ],
        "effect": (
            "A → wf-governance-fast-15m + wf-judge-audit-batch + wf-thread-scout-weekly SHIP · "
            "governance_center --tier fast SLA 15s · workers never run full judge every turn"
        ),
        "option_effects": {
            "A": "Maintainer 2 wires n8n + hub one-tap · integration-fabric GS-08 GS-09 live",
            "B": "Judge batch only · Thread stays manual CLI",
            "C": "Scripts only · n8n stubs stay planned",
            "D": "No automation · rooms manual only",
        },
        "asked_by": "Brain · ASF 2026-06-14 · integration-fabric-registry v1.4",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-GOV-FAST-WIRE-v1 A",
        "attachment": "~/.sina/integration-fabric-registry-v1.yaml",
        "machine_refs": [
            "governance_center_run_v1.py --tier fast",
            "wf-judge-audit-batch",
            "wf-thread-scout-weekly",
            "wf-governance-fast-15m",
        ],
    },
    {
        "id": "Q-CHANGE-QUORUM-v1",
        "number": 17,
        "title": "Change Quorum — who changed SSOT/policy",
        "question": (
            "Make Judge Center the weekly Change Quorum: machine fingerprints LOCKED docs and attachments, "
            "scans megachats, names the owner — you see one alarm line on Super Fast Hub (not full diffs)?"
        ),
        "blocks": "Judge L1 Audit --ssot-delta · Counsel owner class · Bench Form draft · anti manual diff",
        "recommended": "A",
        "options": [
            "A — SHIP Change Quorum weekly — fingerprint + owner + ≤20 delta rows (recommended)",
            "B — PARTIAL — fingerprint hot laws only · no counsel owner field yet",
            "C — DEFER — keep chat audit only · no SSOT fingerprint",
            "D — REJECT — manual change review",
        ],
        "effect": (
            "A → judge_center_audit_v1.py --ssot-delta · latest-change-quorum-v1.json · "
            "hub alarm change_quorum_summary one line · Maintainer 2 SHIP"
        ),
        "option_effects": {
            "A": "No human reads every DOCX/SSOT diff · Judge quorum assigns owner · Form row on BAD only",
            "B": "Stairlift fingerprint only · weekly full quorum deferred",
            "C": "Chat scan only · no file delta machine",
            "D": "Manual review burden returns",
        },
        "asked_by": "Brain · ASF 2026-06-14 · change_quorum integration-fabric v1.4",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-CHANGE-QUORUM-v1 A",
        "attachment": "GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md section 7.6",
        "machine_refs": [
            "judge_center_run_v1.py --ssot-delta",
            "governance_stairlift_sync_v1.py",
            "validate-change-quorum-v1.sh",
        ],
    },
]

ENF_FORKS_YAML = Path.home() / ".sina/forms/thread-enforcement-forks-v1.yaml"

# §PENDING_OUTSIDE_FORM + cross-anchor forks → §OPEN (FORM_OFFICIAL 2026-06-12)
PENDING_OUTSIDE_AS_OPEN: list[dict] = [
    {
        "id": "Q-SYS-INTEGRITY-RESUME",
        "title": "SYS-INTEGRITY Phases 3–10 resume",
        "question": "Resume 100-step playbook Phases 3–10 now (RT LIVE PASS + batch 2026-06-12)?",
        "blocks": "PROGRAM_PROGRESS SYS-INTEGRITY-100 · 10.10 D lifted",
        "recommended": "YES",
        "options": ["YES — resume monthly SCAN cadence", "DEFER — seal 1.10 first", "PAUSE"],
        "effect": "YES → Maintainer continues playbook from Phase 3 index",
        "asked_by": "PROGRAM_PROGRESS · M1/M2 anchors",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-SYS-INTEGRITY-RESUME YES",
        "source_chat": "a53f3fa1 · 74f5ccab",
    },
    {
        "id": "Q-WIRE-G3",
        "title": "Tailscale G3 wire — reconcile pass vs pending logged",
        "question": "Mono logged pass · SSOT files still pending — RECONCILE one receipt, PASS trust Mono, or PENDING re-run?",
        "blocks": "Wire lane · Tailscale G3 proof",
        "diskToday": (
            "g3_tailscale=pending on SSOT files · Mono reconcile receipt logged · "
            "validate-verify-wire PASS (general wire — not G3 row)"
        ),
        "recommended": "RECONCILE",
        "options": [
            "RECONCILE — one wire receipt everyone reads (recommended)",
            "PASS — accept Mono pass as law",
            "PENDING — re-run Hub wire Action",
        ],
        "effect": "RECONCILE → single g3_tailscale row in PROGRAM_PROGRESS",
        "option_effects": {
            "RECONCILE": "Mono publishes single g3_tailscale receipt · all SSOT files aligned",
            "PASS": "All SSOT files flip to pass per Mono anchor",
            "PENDING": "Status stays pending · Hub Action re-run required",
        },
        "asked_by": "M1 vs M2 wire audit",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-WIRE-G3 RECONCILE",
        "source_chat": "a53f3fa1 · 74f5ccab",
    },
    {
        "id": "Q-FR-002-WTM",
        "title": "FR-002 D2 Graph Fusion (WTM)",
        "question": "Start FR-002 strategic WTM build this sprint?",
        "blocks": "§PENDING_OUTSIDE_FORM high",
        "recommended": "DEFER",
        "options": ["DEFER — W1 film + W3 first (9.07 A)", "START — WTM now", "CANCEL"],
        "effect": "DEFER → no WTM sprint until ASF reorders",
        "asked_by": "§PENDING_OUTSIDE_FORM",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-FR-002-WTM DEFER",
        "source_chat": "74f5ccab",
    },
    {
        "id": "Q-FR-1013f0",
        "title": "When to close commercial track FR-1013f0",
        "question": "Close when Week-3 signal locally (deposit, LOI, honest attempt) — YES, DEFER batch, or CANCEL?",
        "blocks": "Commercial Track · Week-3 closure",
        "diskToday": "FR-1013f0 open · Week-3 honest $0 · outreach design logged",
        "recommended": "YES",
        "options": [
            "YES — close on W3 receipt only (recommended)",
            "DEFER — keep open until first outreach batch ships",
            "CANCEL — remove FR-1013f0 from active Track",
        ],
        "effect": "YES → Track closes only when W3 proof exists",
        "option_effects": {
            "YES": "Track closes on W3 receipt · no early checkbox",
            "DEFER": "Row stays open until batch 1 ships",
            "CANCEL": "FR-1013f0 archived · closure target dropped",
        },
        "asked_by": "Commercial · pending outside form",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-FR-1013f0 YES",
        "source_chat": "e54ddfa8 · 74f5ccab",
    },
    {
        "id": "Q-ACTIVE-NOW-SYNC",
        "title": "ACTIVE_NOW footer sync",
        "question": "Sync ACTIVE_NOW footer with factory-now (step 1.04)?",
        "blocks": "Anti-staleness AS-04",
        "recommended": "YES",
        "options": ["YES — Maintainer sync", "DEFER"],
        "effect": "YES → footer matches factory-now JSON",
        "asked_by": "§PENDING_OUTSIDE_FORM",
        "reply_template": "ASF: SHIP ACTIVE_NOW sync",
        "source_chat": "74f5ccab",
    },
    {
        "id": "Q-HUB-LAG",
        "title": "Hub rebuild LAG",
        "question": "Accept hub full-rebuild minutes LAG until true RT cascade?",
        "blocks": "HUB-LAG · projection law",
        "recommended": "YES",
        "options": ["YES — projection LAG documented", "NO — block until seconds"],
        "effect": "YES → hero reads form JSON first (027 law)",
        "asked_by": "§PENDING_OUTSIDE_FORM",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-HUB-LAG YES",
        "source_chat": "74f5ccab",
    },
    {
        "id": "Q-NF-SPEC-PROMOTE",
        "title": "Noetfield spec promote",
        "question": "Approve promote _organized/noetfield/spec → Noetfield/docs?",
        "blocks": "PROGRAM_PROGRESS T-IC-1 · SUPERBRAIN-P0",
        "recommended": "REVIEW",
        "options": ["APPROVE — promote", "HOLD — confidential", "DEFER"],
        "effect": "APPROVE → Noetfield docs update",
        "asked_by": "PROGRAM_PROGRESS · M1 arc",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-NF-SPEC-PROMOTE REVIEW",
        "source_chat": "a53f3fa1",
    },
    {
        "id": "Q-MONO-SSOT-LANE",
        "title": "MonoRepo vs SourceA apex",
        "question": "Confirm SourceA PACK5 form wins · MonoRepo = mx/runtime lane only?",
        "blocks": "3369d11c anchor · FORM_OFFICIAL",
        "recommended": "YES",
        "options": [
            "YES — SourceA form official · Mono runtime only",
            "NO — merge roots (not recommended)",
        ],
        "effect": "YES → Mono picks append to form with evidence only",
        "asked_by": "3369d11c Mono anchor audit",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-MONO-SSOT-LANE YES",
        "source_chat": "3369d11c",
    },
    {
        "id": "Q-PLAN-300",
        "title": "Lock Tier-1 commercial P0 block (300 plans)",
        "question": "Lock the top-5 P0 commercial block on the form until first deposit — outreach, film, kernel, procurement, TF/NF?",
        "blocks": "W1/W2/W3 · STRATEGIC-SLICE · INCIDENT-026 anti-validator",
        "recommended": "LOCKED",
        "options": [
            "LOCKED — 11.01–11.05 are law until ASF supersede (recommended)",
            "DEFER — keep advisory only",
            "CANCEL — drop PLAN-300 block",
        ],
        "effect": "LOCKED → Maintainer SHIPs K1 without validator spiral · deposits KPI only",
        "asked_by": "Commercial · blueprint market 300 plans 2026-06-13",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-PLAN-300 LOCKED",
        "source_chat": "74f5ccab",
        "attachment": "archive/attachments/commercial_goal_specialist/sina_os/SOURCEA_COMMERCIAL_P0_FIVE_STEP_PICK_BATCH_2026-06-13_LOCKED_v1.md",
    },
    {
        "id": "11.01",
        "title": "Step 1 — Send outreach (TrustField + Noetfield)",
        "question": "Ship W3 outreach this week — TF direct email + NF batch-1 (5 targets)?",
        "blocks": "W3 commercial · Week-4 deposit KPI",
        "recommended": "SHIP",
        "options": ["SHIP — send this week (recommended)", "DEFER — wait for W1 film", "CANCEL"],
        "effect": "SHIP → PLAN-001,002,103,273 · Track rows · no wait for demo perfection",
        "asked_by": "PLAN-300 block · SSOT v3.1 Part 10",
        "reply_template": "ASF: FIVE-STEP — PICK: 11.01 SHIP",
    },
    {
        "id": "11.02",
        "title": "Step 2 — Film W1 demo",
        "question": "Film enforcement demo on camera — ALLOW, TAMPER FAIL, BLOCK — terminal + receipt visible, under 6 minutes?",
        "blocks": "W1 · Geordie 10-min benchmark",
        "recommended": "SHIP",
        "options": ["SHIP — schedule 30 min film block (recommended)", "DEFER", "CANCEL"],
        "effect": "SHIP → PLAN-041–044 · unlisted video link for Buyer 1 eval",
        "asked_by": "PLAN-300 block · ENFORCEMENT W1",
        "reply_template": "ASF: FIVE-STEP — PICK: 11.02 SHIP",
    },
    {
        "id": "11.03",
        "title": "Step 3 — Ship receipt kernel (K1)",
        "question": "Ship receipt validator on read + forged-receipt CI fail + export bundle — Maintainer owns, no validator marathon?",
        "blocks": "W2 kernel · Art 12 PoC scenario",
        "recommended": "SHIP",
        "options": ["SHIP — K1 P0 this sprint (recommended)", "DEFER — after outreach only", "CANCEL"],
        "effect": "SHIP → PLAN-026,038,141,145,157 · bypass inventory must stay 0",
        "asked_by": "PLAN-300 block · Maintainer 2",
        "reply_template": "ASF: FIVE-STEP — PICK: 11.03 SHIP",
    },
    {
        "id": "11.04",
        "title": "Step 4 — Procurement pack",
        "question": "Ship pilot SOW (CAD $4K / $2K deposit / refund) + SOC2-in-progress letter + 2-page security deck + mutual pilot success doc?",
        "blocks": "Buyer 1 procurement · 30-day PoC norm",
        "recommended": "SHIP",
        "options": ["SHIP — pack ready for discovery calls (recommended)", "DEFER", "CANCEL"],
        "effect": "SHIP → PLAN-006,064,065,140,217 · attach to TF/NF outreach",
        "asked_by": "PLAN-300 block · commercial",
        "reply_template": "ASF: FIVE-STEP — PICK: 11.04 SHIP",
    },
    {
        "id": "11.05",
        "title": "Step 5 — Instrument TF + NF workflows",
        "question": "Instrument one TrustField MSB workflow + one Noetfield Copilot eval path + 10-minute scaffold for Buyer 1?",
        "blocks": "TF/NF vertical · identity separation law",
        "recommended": "SHIP",
        "options": ["SHIP — one workflow each for pilot (recommended)", "DEFER", "CANCEL"],
        "effect": "SHIP → PLAN-076,077,201,217 · separate vocabulary per SSOT §9",
        "asked_by": "PLAN-300 block · portfolio",
        "reply_template": "ASF: FIVE-STEP — PICK: 11.05 SHIP",
    },
]

_ENF_OPTION_DEFAULTS: dict[str, str] = {
    "A_film_week2": "A",
    "B_wait_hub": "B",
    "APPROVE": "APPROVE",
    "NO": "NO",
    "DEFER": "DEFER",
    "YES": "YES",
    "NO_TF_primary": "NO_TF_primary",
    "A_whole_repo_zero": "A",
    "B_demo_scope_only": "B",
    "C_defer": "C",
    "A_week4": "A",
    "B_after_film": "B",
    "LOI_only": "LOI_only",
    "YES_background": "YES_background",
    "NEVER": "NEVER",
    "narrative_only": "narrative_only",
    "A_5": "A",
    "B_10": "B",
    "C_3": "C",
    "YES_with_receipt": "YES_with_receipt",
    "NO_stub": "NO_stub",
    "AFTER_film": "AFTER_film",
    "strategy_only": "strategy_only",
    "A_AI_Trust_Brief": "A",
    "B_Copilot_Governance_Pilot": "B",
    "C_custom": "C",
    "NO_change": "NO_change",
}


def _load_enf_open_questions() -> list[dict]:
    """THREAD-ENFORCEMENT ENF-01..20 from ~/.sina/forms YAML → form rows."""
    if not ENF_FORKS_YAML.is_file():
        return []
    text = ENF_FORKS_YAML.read_text(encoding="utf-8", errors="replace")
    rows: list[dict] = []
    pat = re.compile(
        r'id:\s*(ENF-\d+).*?subject:\s*"([^"]*)".*?question:\s*"([^"]*)".*?'
        r'options:\s*\[([^\]]+)\].*?effect_hint:\s*"([^"]*)"',
        re.DOTALL,
    )
    for m in pat.finditer(text):
        eid, subject, question, opts_raw, effect = m.groups()
        opt_keys = [o.strip() for o in opts_raw.split(",")]
        options = [f"{_ENF_OPTION_DEFAULTS.get(k, k)} — {k.replace('_', ' ')}" for k in opt_keys]
        rec = _ENF_OPTION_DEFAULTS.get(opt_keys[0], opt_keys[0]) if opt_keys else "DEFER"
        rows.append(
            {
                "id": eid,
                "title": subject,
                "question": question,
                "blocks": f"THREAD-ENFORCEMENT · {ENF_FORKS_YAML.name}",
                "recommended": rec,
                "options": options,
                "effect": effect,
                "asked_by": "ENFORCEMENT-6MO · CANVAS_PER_CHAT_ROLLOUT W1",
                "reply_template": f"ASF: FIVE-STEP — PICK: {eid} {rec}",
                "source_chat": "74f5ccab · THREAD-ENFORCEMENT",
            }
        )
    return rows


def _canvas_applied_pick_ids() -> set[str]:
    path = Path.home() / ".sina/canvas-form-picks-applied-v1.json"
    if not path.is_file():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return set((data.get("picks") or {}).keys())
    except Exception:
        return set()


def _load_intake_questions() -> list[dict]:
    """New conflicts / founder-permission forks queued for §OPEN (FORM_OFFICIAL intake)."""
    if not INTAKE_PATH.is_file():
        return []
    try:
        data = json.loads(INTAKE_PATH.read_text(encoding="utf-8"))
        return list(data.get("rows") or [])
    except Exception:
        return []


def _gathering_phase_active() -> bool:
    if not GATHERING_PHASE_PATH.is_file():
        return False
    try:
        data = json.loads(GATHERING_PHASE_PATH.read_text(encoding="utf-8"))
        return bool(data.get("active"))
    except Exception:
        return False


def all_open_questions() -> list[dict]:
    if _gathering_phase_active():
        rows = _load_intake_questions()
        seen: set[str] = set()
        out: list[dict] = []
        for q in rows:
            qid = q.get("id")
            if not qid or qid in seen:
                continue
            seen.add(qid)
            out.append(q)
        return out
    applied = _canvas_applied_pick_ids()
    rows = (
        OPEN_QUESTIONS_CORE
        + PENDING_OUTSIDE_AS_OPEN
        + _load_enf_open_questions()
        + _load_intake_questions()
    )
    seen: set[str] = set()
    out: list[dict] = []
    for q in rows:
        qid = q.get("id")
        if not qid or qid in applied or qid in seen:
            continue
        seen.add(qid)
        out.append(q)
    return out


OPEN_QUESTIONS: list[dict] = all_open_questions()  # import snapshot only — use all_open_questions() in payload()


def normalize_founder_text(text: str) -> str:
    """CAPS = non-caps per FOUNDER_MSG_NORM."""
    t = (text or "").strip()
    t = re.sub(r"\s+", " ", t)
    return t.casefold()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_pick(text: str) -> dict | None:
    norm = normalize_founder_text(text)
    if "five-step" not in norm or "pick" not in norm:
        return None
    m = re.search(r"([\d]+\.[\d]+|q-[a-z0-9-]+|enf-\d+)\s+([a-d])\b", norm)
    if not m:
        return None
    return {"step": m.group(1).upper(), "key": m.group(2).upper()}


def _active_form_edition() -> str:
    if FINAL_FIX_JSON.is_file() and _gathering_phase_active():
        return "final_fix_gathering"
    if _gathering_phase_active():
        return "gathering_extraction"
    intake = _load_intake_questions()
    if intake and THIRD_FORM_JSON.is_file():
        return "third_form"
    if SECOND_FORM_JSON.is_file():
        return "v2"
    return FORM_EDITION


def founder_readable_card(q: dict) -> dict:
    """Hub / form page card — stable 5-slot schema (A–D + option 5 free-text)."""
    from form_official_option_schema_v1 import normalize_question_row  # noqa: WPS433

    return normalize_question_row(q)


def _load_option_schema() -> dict:
    from form_official_option_schema_v1 import load_schema  # noqa: WPS433

    return load_schema()


def founder_readable_cards(*, limit: int | None = None) -> list[dict]:
    rows = all_open_questions()
    numbered = [
        {**q, "number": i, "search_key": f"Q{i} {q.get('id', '')}"}
        for i, q in enumerate(rows, start=1)
    ]
    cards = [founder_readable_card(q) for q in numbered]
    if limit is not None and limit > 0:
        return cards[:limit]
    return cards


def form_official_line(*, open_count: int | None = None) -> str:
    oq = open_count if open_count is not None else len(all_open_questions())
    edition = _active_form_edition()
    if oq > 0:
        return (
            f"FORM_OFFICIAL · {edition} · {oq} open PICKs logged · "
            "INCIDENT-037 block ON · agent-submit forbidden"
        )
    return f"FORM_OFFICIAL · {edition} · filled · official form"


def _form_headline(open_count: int) -> str:
    edition = _active_form_edition()
    if open_count > 0:
        return (
            f"{open_count} OPEN PICKs · FORM {edition.upper()} logged · "
            "M1 Canvas · INCIDENT-037 block ON · agent-submit forbidden"
        )
    try:
        from rt_live_gate_v1 import receipt_pass  # noqa: WPS433

        if receipt_pass():
            return f"FORM {edition.upper()} FILLED — RT LIVE PASS — Phase 3 resume"
    except Exception:
        pass
    return f"FORM {edition.upper()} FILLED — RT LIVE gate next"


def save_answers_receipt() -> dict:
    row = {
        "schema": "live-founder-decision-form-v2-answers",
        "filled_at": ASF_FILLED_AT,
        "form_edition": FORM_EDITION,
        "drift_floor": DRIFT_FLOOR,
        "answers": ANSWERED_V2,
        "receipt_md": str(ANSWERS_RECEIPT_MD),
        "asf_verbatim": (
            "ASF: FIVE-STEP — QUESTION on [Q-RT-LIVE]\n"
            "YES — hub repair-only until RT LIVE proven\n"
            "ASF: FIVE-STEP — QUESTION on [Q-1.10]\n"
            "DEFER — seal Phase 1 after hub RT LIVE\n"
            "ASF: FIVE-STEP — QUESTION on [Q-CRITIC]\n"
            "YES — EXTERNAL_CRITIC report-only\n"
            "ASF: FIVE-STEP — PICK: 10.10 D — pause until RT LIVE then playbook\n"
            "ASF: FIVE-STEP — QUESTION on [Q-GRADE]\n"
            "C — spine green · hub not RT yet\n"
            "ASF: FIVE-STEP — QUESTION on [Q-DRIFT]\n"
            "90"
        ),
    }
    ANSWERS_RECEIPT_JSON.parent.mkdir(parents=True, exist_ok=True)
    ANSWERS_RECEIPT_JSON.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    sina_home = Path.home() / ".sina"
    sina_home.mkdir(parents=True, exist_ok=True)
    (sina_home / "governance-drift-floor-v1.json").write_text(
        json.dumps({"floor": DRIFT_FLOOR, "set_at": ASF_FILLED_AT, "source": "Q-DRIFT"}, indent=2) + "\n",
        encoding="utf-8",
    )
    return row


def save_first_form_archive() -> dict:
    """Persist FIRST FORM snapshot (v1 questions) — idempotent."""
    row = {
        "schema": "live-founder-decision-form-first-v1",
        "saved_at": _now(),
        "edition": "first_form",
        "superseded_by": FORM_EDITION,
        "archive_path": str(FIRST_FORM_ARCHIVE),
        "question_count": len(FIRST_FORM_QUESTIONS),
        "questions": FIRST_FORM_QUESTIONS,
        "law": "ASF SAVE FIRST FORM 2026-06-11",
    }
    FIRST_FORM_JSON.parent.mkdir(parents=True, exist_ok=True)
    FIRST_FORM_JSON.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def save_second_form_archive() -> dict:
    """Persist SECOND FORM snapshot — PACK5 + Gov + v2 fills (idempotent read from disk)."""
    applied: dict[str, str] = {}
    applied_path = Path.home() / ".sina/canvas-form-picks-applied-v1.json"
    if applied_path.is_file():
        try:
            applied = dict((json.loads(applied_path.read_text(encoding="utf-8")).get("picks") or {}))
        except Exception:
            applied = {}
    row = {
        "schema": "live-founder-decision-form-second-v1",
        "saved_at": _now(),
        "edition": "second_form",
        "supersedes": "first_form",
        "live_form_edition": FORM_EDITION,
        "archive_path": str(SECOND_FORM_ARCHIVE),
        "law": "ASF lock second filled form 2026-06-12",
        "fill_1_v2_answers": [{"id": r["id"], "pick": r["pick"]} for r in ANSWERED_V2],
        "fill_2_pack5_gov_applied": applied,
        "fill_2_integrity_canvas_batch": [
            {"id": p["id"], "pick": p["pick"]} for p in CANVAS_SESSION_PICKS
        ],
        "canvas_shipped": sorted(SHIPPED_CANVAS),
        "open_remaining_count": len(all_open_questions()),
        "open_remaining_ids": [q["id"] for q in all_open_questions()],
    }
    if SECOND_FORM_JSON.is_file():
        row["prior_snapshot_at"] = json.loads(
            SECOND_FORM_JSON.read_text(encoding="utf-8")
        ).get("saved_at")
    SECOND_FORM_JSON.parent.mkdir(parents=True, exist_ok=True)
    SECOND_FORM_JSON.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def _founder_voice_sources() -> dict:
    try:
        from founder_voice_sources_v1 import payload as voice_payload  # noqa: WPS433

        return voice_payload()
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def payload() -> dict:
    form_ok = FORM_MD.is_file()
    norm_ok = NORM_MD.is_file()
    first_ok = FIRST_FORM_ARCHIVE.is_file()
    pending_high = 0
    if form_ok:
        body = FORM_MD.read_text(encoding="utf-8", errors="replace")
        pending_high += body.count("| **high** |")
    open_rows = all_open_questions()
    oq_count = len(open_rows)
    numbered_questions = [
        {**q, "number": i, "search_key": f"Q{i} {q.get('id', '')}"}
        for i, q in enumerate(open_rows, start=1)
    ]
    answers_ok = ANSWERS_RECEIPT_MD.is_file() and ANSWERS_RECEIPT_JSON.is_file()
    awaiting_picks = oq_count > 0
    active_edition = _active_form_edition()
    third_meta: dict = {}
    if THIRD_FORM_JSON.is_file():
        try:
            third_meta = json.loads(THIRD_FORM_JSON.read_text(encoding="utf-8"))
        except Exception:
            third_meta = {}
    return {
        "ok": form_ok and norm_ok and first_ok and answers_ok,
        "schema": "live-founder-decision-form-v2",
        "form_edition": FORM_EDITION,
        "active_form_edition": active_edition,
        "form_official_line": form_official_line(open_count=oq_count),
        "nerve_map_path": str(NERVE_MAP_JSON),
        "asf_filled_at": ASF_FILLED_AT,
        "drift_floor": DRIFT_FLOOR,
        "first_form": {
            "saved": first_ok,
            "archive_path": str(FIRST_FORM_ARCHIVE),
            "snapshot_path": str(FIRST_FORM_JSON),
            "question_count": len(FIRST_FORM_QUESTIONS),
        },
        "second_form": {
            "saved": SECOND_FORM_ARCHIVE.is_file() and SECOND_FORM_JSON.is_file(),
            "archive_path": str(SECOND_FORM_ARCHIVE),
            "snapshot_path": str(SECOND_FORM_JSON),
            "applied_pick_count": len(_canvas_applied_pick_ids()),
            "open_remaining_count": oq_count,
        },
        "third_form": {
            "saved": THIRD_FORM_JSON.is_file(),
            "snapshot_path": str(THIRD_FORM_JSON),
            "pack": third_meta.get("pack") or "",
            "question_ids": third_meta.get("question_ids") or [],
            "intake_path": str(INTAKE_PATH),
            "intake_open_count": len(_load_intake_questions()),
            "canvas": third_meta.get("canvas") or "sourcea-system-integrity-100.canvas.tsx",
        },
        "v2_answers": {
            "filled": True,
            "count": len(ANSWERED_V2),
            "receipt_md": str(ANSWERS_RECEIPT_MD),
            "receipt_json": str(ANSWERS_RECEIPT_JSON),
            "rows": ANSWERED_V2,
        },
        "updated_at": _now(),
        "form_path": str(FORM_MD),
        "norm_path": str(NORM_MD),
        "hub_repair_policy": HUB_REPAIR_POLICY,
        "needs_asf_fill": not answers_ok,
        "awaiting_founder_picks": awaiting_picks,
        "hub_tab": "track",
        "doc_pick": "SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md",
        "answers_doc_pick": str(ANSWERS_RECEIPT_MD.relative_to(ROOT)),
        "first_form_doc_pick": str(FIRST_FORM_ARCHIVE.relative_to(ROOT)),
        "second_form_doc_pick": str(SECOND_FORM_ARCHIVE.relative_to(ROOT)),
        "answered_count": len(SHIPPED_CANVAS) + len(CANVAS_SESSION_PICKS) + len(ANSWERED_V2),
        "canvas_session_picks": CANVAS_SESSION_PICKS,
        "canvas_shipped": sorted(SHIPPED_CANVAS),
        "canvas_open": sorted(q["id"] for q in open_rows),
        "canvas_open_count": oq_count,
        "form_intake": {
            "path": str(INTAKE_PATH),
            "pending_count": len(_load_intake_questions()),
            "policy": "Agents append forks via form_conflict_intake_v1.py — regen Canvas only (INCIDENT-037 block ON)",
            "gathering_phase": _gathering_phase_active(),
            "extraction_path": str(EXTRACTION_PATH),
        },
        "gathering": {
            "active": _gathering_phase_active(),
            "flag_path": str(GATHERING_PHASE_PATH),
            "extraction_path": str(EXTRACTION_PATH),
            "final_fix_path": str(FINAL_FIX_JSON),
            "law": "extraction → gather → unify → prioritize",
        },
        "final_fix": {
            "saved": FINAL_FIX_JSON.is_file(),
            "snapshot_path": str(FINAL_FIX_JSON),
            "synthesis_script": "scripts/form_official_chat_synthesis_v1.py",
        },
        "founder_voice_sources": _founder_voice_sources(),
        "open_questions": founder_readable_cards(),
        "open_questions_count": oq_count,
        "founder_readable_cards": founder_readable_cards(),
        "founder_head_card": founder_readable_cards(limit=1)[0] if oq_count else None,
        "form_page_url": "http://127.0.0.1:13023/form/",
        "form_headline": _form_headline(oq_count),
        "option_schema": _load_option_schema(),
        "pending_outside_count": pending_high,
        "norm_caps_locked": norm_ok and "100% equivalent" in NORM_MD.read_text(encoding="utf-8", errors="replace"),
        "live_policy": "form v2 filled · hub repair until RT LIVE gate PASS · read receipt on SCAN",
        "founder_reply_law": "SOURCEA_LIVE_FOUNDER_DECISION_FORM_V2_ANSWERS_RECEIPT_2026-06-11_LOCKED_v1.md",
        "parse_pick_demo": _parse_pick("ASF: FIVE-STEP — PICK: Q-BC-01 C"),
        "parse_pick_demo_legacy": _parse_pick("ASF: FIVE-STEP — PICK: 10.10 D — pause"),
    }


def write_receipt() -> dict:
    save_first_form_archive()
    save_answers_receipt()
    data = payload()
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    data["receipt_path"] = str(RECEIPT)
    try:
        from rt_live_gate_v1 import sync_gate_state  # noqa: WPS433

        data["rt_live_gate"] = sync_gate_state()
    except Exception:
        pass
    return data


def _form_dbg(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    # #region agent log
    debug_log = Path("/Users/sinakazemnezhad/Desktop/SourceA/.cursor/debug-e54ddf.log")
    payload = {
        "sessionId": "e54ddf",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
    }
    try:
        debug_log.parent.mkdir(parents=True, exist_ok=True)
        with debug_log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except OSError:
        pass
    # #endregion


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--save-first", action="store_true", help="Write FIRST FORM JSON snapshot")
    ap.add_argument("--save-second", action="store_true", help="Write SECOND FORM JSON snapshot")
    ap.add_argument("--normalize", metavar="TEXT")
    args = ap.parse_args()
    if args.normalize is not None:
        print(normalize_founder_text(args.normalize))
        return 0
    if args.save_first:
        print(json.dumps(save_first_form_archive(), indent=2))
        return 0
    if args.save_second:
        print(json.dumps(save_second_form_archive(), indent=2))
        return 0
    data = write_receipt() if args.write_receipt else payload()
    if args.json:
        # #region agent log
        open_ids = [q.get("id") for q in (data.get("open_questions") or []) if isinstance(q, dict)]
        _form_dbg(
            "H1",
            "live_founder_decision_form_v1.py:main",
            "form_scan",
            {
                "open_count": data.get("open_questions_count"),
                "open_ids": open_ids,
                "awaiting_founder_picks": data.get("awaiting_founder_picks"),
            },
        )
        # #endregion
    print(json.dumps(data, indent=2))
    return 0 if data.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
