#!/usr/bin/env python3
"""Generate 1000 ENFORCEMENT-6MO pivot prompts (10 phases × 4 tiers × 25). LOCKED pack v2."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "brain-os" / "plan-registry" / "enforcement-1000"
PROMPTS = PACK / "prompts"
AGENT = "AGENT-AUTO-ENFORCEMENT"
TAG = "AGENT-AUTO-ENFORCEMENT"
GENERATOR_VERSION = "v2-tier-expanded"

PHASES = [
    ("phase-e0-commit-gate", "Single commit entry · bypass inventory · demo write path only"),
    ("phase-e1-receipt-integrity", "Receipt per action · spine bind · append-only · checksum"),
    ("phase-e2-validator-tamper", "HARD FAIL on mismatch · tamper detect · universe invariants"),
    ("phase-e3-demo-live", "BLOCK/ALLOW/TAMPER · 5-min script · film · founder one-tap"),
    ("phase-e4-commercial-w3", "TF/NF pilot · LOI · deposit · design partner signal"),
    ("phase-e5-bypass-chaos", "Kill/replay · failure injection · demo-scope bypass closure"),
    ("phase-e6-investor-pipeline", "Seed narrative · deck · meetings · pipeline heat"),
    ("phase-e7-regulated-wedge", "Copilot · healthcare · procurement · RPAA buyer language"),
    ("phase-e8-kernel-harden", "commit() v1 demo scope · no full-repo OS expansion"),
    ("phase-e9-dec-closeout", "Dec freeze · W1+W2+W3 proof · honest miss criteria"),
]

PHASE_META = {
    "phase-e0-commit-gate": {"category": "W2_KERNEL", "owner": "worker", "month": "2026-06", "win": "W2"},
    "phase-e1-receipt-integrity": {"category": "W2_KERNEL", "owner": "worker", "month": "2026-06", "win": "W2"},
    "phase-e2-validator-tamper": {"category": "W2_KERNEL", "owner": "worker", "month": "2026-07", "win": "W2"},
    "phase-e3-demo-live": {"category": "W1_DEMO", "owner": "worker", "month": "2026-07", "win": "W1"},
    "phase-e4-commercial-w3": {"category": "W3_MONEY", "owner": "commercial", "month": "2026-06", "win": "W3"},
    "phase-e5-bypass-chaos": {"category": "CHAOS_HARDEN", "owner": "worker", "month": "2026-08", "win": "W2"},
    "phase-e6-investor-pipeline": {"category": "NARRATIVE", "owner": "commercial", "month": "2026-09", "win": "NARRATIVE"},
    "phase-e7-regulated-wedge": {"category": "W3_MONEY", "owner": "commercial", "month": "2026-08", "win": "W3"},
    "phase-e8-kernel-harden": {"category": "W2_KERNEL", "owner": "worker", "month": "2026-10", "win": "W2"},
    "phase-e9-dec-closeout": {"category": "CLOSEOUT", "owner": "brain", "month": "2026-12", "win": "CLOSEOUT"},
}

SLICE_BY_SLOT: dict[str, dict[int, str]] = {
    "phase-e0-commit-gate": {0: "DEMO-ENF-S9", 2: "DEMO-ENF-S2", 3: "DEMO-ENF-S2", 4: "DEMO-ENF-S2", 5: "DEMO-ENF-S3"},
    "phase-e1-receipt-integrity": {0: "DEMO-ENF-S3", 2: "DEMO-ENF-S4", 5: "DEMO-ENF-S4"},
    "phase-e2-validator-tamper": {0: "DEMO-ENF-S5", 1: "DEMO-ENF-S5", 2: "DEMO-ENF-S5"},
    "phase-e3-demo-live": {0: "DEMO-ENF-S7", 2: "DEMO-ENF-S7", 5: "DEMO-ENF-S8", 6: "DEMO-ENF-S8"},
    "phase-e4-commercial-w3": {9: "DEMO-ENF-W3", 17: "DEMO-ENF-W3"},
}

TIERS = [
    ("T0", "Critical — ship now · demo blocker"),
    ("T1", "High — next enforcement sprint"),
    ("T2", "Medium — hardening after W1 filmed"),
    ("T3", "Low — polish · only if W1+W2 green"),
]

TIER_DEPTH = {
    "T0": "Ship now. Minimal diff. Demo must not lie.",
    "T1": "Next sprint. Evidence in REPO_EXECUTION_LOGS or demo archive.",
    "T2": "Post-W1 hardening. No platform scope creep.",
    "T3": "Polish only. Delete if not (a) enforcement (b) demo (c) pay.",
}

VERIFY = {
    "T0": "cd ~/Desktop/SourceA && bash scripts/validate-demo-enforcement-v1.sh && bash scripts/validate-universe-invariants-v1.sh",
    "T1": "cd ~/Desktop/SourceA && bash scripts/validate-demo-enforcement-v1.sh && SINA_FCB_FAST=1 python3 scripts/find_critical_bugs.py",
    "T2": "cd ~/Desktop/SourceA && bash scripts/demo-enforcement-5min-v1.sh --dry-run",
    "T3": "cd ~/Desktop/SourceA && bash scripts/validate-enforcement-demo-v1.sh 2>/dev/null || bash scripts/validate-demo-enforcement-v1.sh",
}

# Done status set by scripts/audit-enforcement-1000-v1.py from disk — not blanket mark
DONE_IDS: set[str] = set()


def expand_task(base: str, tier: str, win: str) -> str:
    """Tier-specific task text — 1000 unique titles from 250 bases."""
    if tier == "T0":
        return base
    if tier == "T1":
        return f"[CI] Wire regression + REPO_EXECUTION_LOGS evidence for: {base}"
    if tier == "T2":
        return f"[CHAOS] Kill/replay stress — prove still holds: {base}"
    return f"[POLISH] Document or DELETE if no {win} impact: {base}"

PINNED_DONE = [
    "pinned-enf-6mo-win-locked",
    "pinned-enf-demo-policy",
    "pinned-enf-commit-gate",
    "pinned-enf-tamper-validator",
    "pinned-enf-5min-script",
]

PINNED_PARALLEL = [
    ("pinned-enf-fr-003-parallel", "Maintainer parallel: FR-003 EXTERNAL_CRITIC wiring"),
    ("pinned-enf-1-10-seal", "Maintainer parallel: Phase 1.10 seal after RT LIVE PASS"),
    ("pinned-enf-w3-tf-nf", "ASF parallel: TF-001 or NF-001 deposit/LOI (W3)"),
]

# 25 tasks per phase — each must pass gate: enforcement | demo | pay
PHASE_TASKS: list[list[str]] = [
    [  # e0 commit gate
        "Maintain bypass inventory in brain-os/demo/DEMO_BYPASS_AUDIT_v1.md — demo-scoped vs full-repo paths",
        "Add validate-demo-write-path-v1.sh: FAIL if demo receipt written outside commit_intent_v1.py",
        "Wire scripts/commit_intent_v1.py --demo-enforcement as sole demo write entry",
        "Extend sourcea_execute_v1.py --demo-enforcement to delegate commit_intent only",
        "BLOCK case: apply_copilot_policy_change high-risk missing approval_ref → gatekeeper DENY",
        "ALLOW case: same intent with approval_ref TLE-2026-001 → stub execute + receipt",
        "Reject direct write to rt-live-gate-receipt-v1.json from non-prove() callers in demo scope",
        "Document commit gate law in brain-os/law/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md §6",
        "CI grep: FAIL if new scripts use open(...,'w') on ~/.sina/receipts/enforcement/ without commit_intent",
        "Add --json output to commit_intent_v1.py for investor terminal demo",
        "Map governance_demo_gate_v1.py rule P-001 to gatekeeper_v1.py shared check",
        "Ensure BLOCK path appends spine AUTHORITY_REJECT without status DONE receipt",
        "Add demo scope env ENFORCEMENT_DEMO=1 guard on commit_intent entry",
        "Cross-check gatekeeper caller=commit_intent always for demo lane",
        "Validate factory lane still uses sourcea_execute without --demo-enforcement",
        "Add unit smoke: commit_intent --case block exits non-zero in <2s",
        "Add unit smoke: commit_intent --case allow exits zero + receipt path printed",
        "Freeze demo intent schema governance_demo_intents_v1.json — version bump only with ASF",
        "Reject hub rebuild as demo write path — projection read-only in demo",
        "Log commit_intent attempts to ~/.sina/receipts/enforcement/commit-audit-v1.jsonl",
        "Add validate-commit-gate-demo-v1.sh to enforcement CI bundle",
        "Compare bypass inventory count week-over-week; target monotonic decrease",
        "Wire demo-enforcement-5min-v1.sh step 1 to commit_intent --case block only",
        "Document 'one write path' in investor/ENFORCEMENT_OUTREACH_v1.md one bullet",
        "Append REPO_EXECUTION_LOGS row: commit gate demo scope PASS",
    ],
    [  # e1 receipt integrity
        "Ensure ALLOW receipt includes schema enforcement-receipt-v1 rule_id spine_event_id",
        "Bind receipt spine_event_id via governance_event_spine_v1.find_by_event_id on read",
        "Add receipt_checksum + spine_checksum fields; validate on sync_gate_state",
        "Append-only ~/.sina/receipts/enforcement/receipt-log-v1.jsonl — no truncate",
        "FAIL validate if receipt-log rewind or duplicate seq without spine row",
        "Mirror RT LIVE receipt bind pattern for demo enforcement receipts",
        "Add receipt.proved_at UTC ISO on every ALLOW",
        "Store rule_id P-001 on receipt evidence field for investor Q&A",
        "Reject receipt status DONE when gatekeeper returned safe_to_execute false",
        "Add --verify-receipt PATH to commit_intent_v1.py standalone check",
        "Cross-link receipt to governance_demo_policy_v1.json rule version",
        "Validate generation_id in hub_sync_detail when receipt includes hub probe",
        "Document receipt schema in brain-os/demo/ENFORCEMENT_ARTIFACTS_INDEX_v1.md",
        "Add validate-receipt-spine-bind-v1.sh for demo receipts only",
        "Ensure tamper of receipt_checksum triggers validator FAIL before spine check",
        "Export last 5 receipts as investor evidence pack under archive/attachments/",
        "Add receipt.incident field MAINT-REF-ENFORCEMENT-6MO when applicable",
        "Compare receipt count to spine AUTHORITY_ACCEPT rows — must match in demo scope",
        "Reject empty evidence field on ALLOW receipts",
        "Add redacted receipt sample for outreach (no secrets) in investor/",
        "Validate receipt JSON schema with jsonschema or manual required keys check",
        "Wire receipt write only after stub execute stdout EXECUTE_STUB logged",
        "Add receipt.rollback_pointer null on success path",
        "Freeze receipt path ~/.sina/receipts/enforcement/ — document in LOCKED law",
        "Append SOURCEA-PRIORITY row: demo receipt integrity PASS",
    ],
    [  # e2 validator tamper
        "Ship validate-demo-enforcement-v1.sh: PASS clean · FAIL on hand-edited receipt",
        "Extend validate-universe-invariants-v1.sh: gate PASS implies spine row exists",
        "Add tamper test case to demo-enforcement-5min-v1.sh step 3 automatic",
        "FAIL if gate status pass but receipt gate field not PASS",
        "FAIL if must_do_today cites drain when rt-live-gate status pass (INCIDENT-027 guard)",
        "Add validate-enforcement-demo-v1.sh alias wrapper for CI discoverability",
        "Document tamper steps in docs/ENFORCEMENT-6MO-DEMO-SCRIPT_v1.md",
        "CI: run tamper FAIL must exit 1 — grep exit code in runbook",
        "Add validator for forged spine_event_id not in governance-event-spine-v1.jsonl",
        "FAIL if receipt spine_checksum mismatch vs spine row hash",
        "Add --tamper-test flag to validate-demo-enforcement-v1.sh for CI",
        "Validate BLOCK case left no DONE receipt via glob scan",
        "Add universe rule: projection hero RT LIVE when receipt PASS",
        "Wire find_critical_bugs fast check for missing demo validator script",
        "Add validate-maintainer-scan-p0-v1.sh to demo preflight bundle",
        "Reject validator skip via SINA_SKIP_DEMO_VALIDATE env in CI",
        "Log validator PASS/FAIL to ~/.sina/receipts/enforcement/validator-audit-v1.jsonl",
        "Add investor-facing one-liner: tamper → FAIL on screen within 30s",
        "Cross-check validate-demo-enforcement against governance_demo_intents_v1.json cases",
        "Add weekly validator drift job: same tamper must still FAIL",
        "Document HARD FAIL philosophy in ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md §3",
        "FAIL if two receipts same event_id different checksum",
        "Add validate-receipt-ledger-generation-v1.sh stub for generation_id bind",
        "Ensure validator output human-readable for demo room terminal",
        "Append REPO_EXECUTION_LOGS: validator tamper FAIL proven",
    ],
    [  # e3 demo live
        "Finalize investor/ENFORCEMENT_DEMO_5MIN.md speaker notes BLOCK→ALLOW→TAMPER",
        "Run demo-enforcement-5min-v1.sh internal dry-run; fix flaky steps",
        "Film W1 take 1 — save recording to archive/attachments/YYYY-MM-DD/",
        "Film W1 take 2 backup — pick sharper audio",
        "Add demo-enforcement-5min-v1.sh --dry-run for pre-meeting check",
        "Hub Action one-tap Run governance demo (Maintainer) → demo script",
        "Reject portfolio DEMO_SCRIPT.md for governance investor meetings — pointer only",
        "Add 60s kill/replay segment optional after tamper FAIL",
        "Prepare offline backup: recorded video if live terminal fails",
        "Script opening line: We make AI execution impossible to bypass governance",
        "Script close: TF/NF pilot path — ask for design partner meeting",
        "Time each beat — total ≤5:00 on rehearsal",
        "Add demo checklist card for ASF pre-meeting (hub Refresh + terminal font size)",
        "Validate demo works with FREEZE ON — governance does not need Cloud Forge Run",
        "Add demo witness log signer field proved_by maintainer|worker",
        "Cross-check demo does not expose ~/.sina secrets in terminal",
        "Add ENFORCEMENT_DEMO_RUNBOOK_v1.md troubleshooting table",
        "Run demo on clean terminal profile — no confusing cwd",
        "Add post-demo FAQ: stub vs real M365 integration honest answer",
        "Capture screenshot tamper FAIL for deck slide 2",
        "Add demo success metric W1-DEMO binary to PROGRAM_PROGRESS parallel row",
        "Reject fake BLOCK — must show real gatekeeper DENY output",
        "Add investor room font: minimum 18pt terminal for recording",
        "Schedule first external demo dry-run with friendly advisor",
        "Append REPO_EXECUTION_LOGS: W1 demo filmed PASS",
    ],
    [  # e4 commercial w3
        "Draft NF-001 Copilot governance wedge one-pager for buyer",
        "Draft TF-001 RPAA / trust pilot scope doc",
        "Send 5 design-partner emails week 1 — log in CRM",
        "Target LOI template CAD 2K+ minimum design partner deposit",
        "Book 3 discovery calls — Copilot policy governance angle",
        "Prepare 3-slide deck: problem · proof · wedge (no Trust OS naming)",
        "Add investor/ENFORCEMENT_OUTREACH_v1.md email snippets",
        "Log pipeline stages: contacted · meeting · LOI · deposit",
        "Identify 10 regulated accounts: bank health energy defense procurement",
        "Pair demo link with tamper FAIL clip in outreach",
        "Honest factory metric slide: 616 receipts 0 unproven",
        "Reject $100M close language in external emails — seed narrative only",
        "Add pricing hypothesis design partner 2K–10K CAD pilot",
        "Follow up non-responders day 7 — one bump only",
        "Prepare SOW skeleton: governance demo → 30-day pilot",
        "Add reference architecture PDF ≤4 pages — enforcement only",
        "Track W3 binary: deposit OR LOI signed by Dec 31",
        "Commercial parallel — do not block Worker demo slices",
        "Add NF buyer language apply_copilot_policy_change to outreach",
        "TrustField portfolio cross-intro if NF stall",
        "Log objection matrix: budget · security review · build vs buy",
        "Prepare data room folder: demo video · validator logs · receipt sample",
        "Add calendar hold investor seed conversations Oct–Nov",
        "Reject whitepaper-first outreach — demo link primary CTA",
        "Append commercial goal receipt: W3 signal attempted",
    ],
    [  # e5 bypass chaos
        "Run kill worker mid-commit test — system recovers via replay",
        "Delete command-data.json — materialize — same canonical enforcement view",
        "Hand-edit receipt — validator FAIL — document in chaos log",
        "Simulate stale projection headline — scan validator catches drain",
        "Add chaos runbook brain-os/demo/CHAOS_ENFORCEMENT_v1.md",
        "Run governance_replay_worker_v1.py after simulated crash",
        "Validate disposable projection test for hub enforcement cards",
        "FAIL inject: queue pos as Maintainer P0 when gate pass",
        "Add --chaos tamper to monthly drill script",
        "Document recovery time target <60s for demo scope",
        "Kill hub process mid-cascade — prove receipt still valid",
        "Add bypass grep CI for subprocess spawn without commit_intent",
        "Simulate missing spine row — universe validator FAIL",
        "Run factory FREEZE ON during chaos — demo still PASS",
        "Add chaos evidence rows to archive/attachments/",
        "Compare INCIDENT-027 recurrence test monthly",
        "Validate no AUTO-RUN during chaos drill",
        "Add founder Safety tap simulation in chaos doc only",
        "Stress commit_intent 10 parallel — single-writer lock holds",
        "Document chaos PASS criteria: self-heal without human",
        "Add validate-chaos-enforcement-v1.sh thin wrapper",
        "Reject chaos tests that mutate production spine outside demo",
        "Log chaos drills to governance-event-spine-v1.jsonl reason chaos_drill",
        "Film 60s kill/replay clip for investor deck optional",
        "Append REPO_EXECUTION_LOGS: chaos drill PASS",
    ],
    [  # e6 investor pipeline
        "Build target list 25 seed funds AI governance enterprise",
        "Draft 10-line email: impossible to bypass governance hook",
        "Schedule 5 intro meetings Nov–Dec",
        "Prepare FAQ: how differs from OpenAI agent frameworks",
        "Add honest tier table A–B plan C upside D lottery to deck appendix",
        "Track meetings: intro · partner · term sheet",
        "Prepare 2-minute demo clip for email embed",
        "Add founder bio slide — execution control not research",
        "Log each meeting outcome within 24h",
        "Prepare objection handler: you are early but proof is real",
        "Add comparable wedge: Stripe payments → governance execution layer",
        "Reject platform OS claims in investor deck",
        "Add pipeline heat metric: 10+ meetings by Nov 30",
        "Prepare data room index ENFORCEMENT only",
        "Add referral ask to friendly advisors post-demo",
        "Track seed band target 3–10M at 15–40M pre",
        "Add monthly investor update template one page",
        "Prepare second meeting materials: technical DD pack",
        "Log pass reasons — refine narrative",
        "Add demo reproducibility statement for DD",
        "Prepare cap table snapshot for serious conversations",
        "Add team slide: founder + agent fleet honest framing",
        "Reject centaur valuation budget in 6-month plan",
        "Add Nov Dec investor conference target list",
        "Append pipeline receipt JSON ~/.sina/investor-pipeline-v1.json",
    ],
    [  # e7 regulated wedge
        "Map P-001 rule to Microsoft Copilot external share policy language",
        "Draft healthcare AI execution block scenario variant",
        "Draft procurement CanadaBuys governance hook one paragraph",
        "Add defense export-control placeholder rule P-002 deny",
        "Document RPAA alignment bullets for TF outreach",
        "Add energy SCADA placeholder — demo only disclaimer",
        "Map approval_ref pattern to enterprise change ticket ID",
        "Add bank SOC2 auditor question prep sheet",
        "Draft LOI clause: governance proof required before agent deploy",
        "Add regulated vertical FAQ in outreach kit",
        "Reject claiming compliance certification — proof not cert",
        "Add copilot policy_change intent variants for 3 verticals",
        "Document stub execute honest boundary in buyer calls",
        "Add privacy: no customer data in demo receipts",
        "Prepare NF pilot SOW section: BLOCK ALLOW tamper acceptance tests",
        "Add TF pilot success criteria: validator PASS weekly",
        "Map wedge to PacifiCan BDC LIFT language if relevant",
        "Add procurement officer persona script 2 min",
        "Document integration roadmap: stub → API phase 2 post-seed",
        "Add legal review checklist for LOI deposit terms",
        "Reject multi-vertical expansion before one wedge wins",
        "Add case study template post-pilot",
        "Prepare reference call script for design partner",
        "Add vertical-specific policy JSON samples under brain-os/demo/verticals/",
        "Append wedge receipt: primary vertical picked NF or TF",
    ],
    [  # e8 kernel harden
        "Close top 5 bypass paths from BYPASS_INVENTORY — one per week",
        "Add commit_intent wrapper for rt_live_gate prove() optional unify",
        "Validate all demo writes in single audit log",
        "Extend validate-universe-invariants for demo receipt ledger",
        "Add spine_event_id required on all new enforcement receipts",
        "Reject second write path to governance-event-spine from demo tools",
        "Add validate-single-commit-path-v1.sh demo scope only",
        "Document non-goals: full repo commit gate deferred post-seed",
        "Add gate test script: feature increases enforcement or DELETE",
        "Harden receipt_checksum algorithm document",
        "Add validate no hand-edit rt-live-gate-v1.json without prove",
        "Sync founder_p0 when enforcement demo filmed — parallel only",
        "Add CI habit: demo validator on every Worker closeout",
        "Reduce bypass inventory to zero in demo scope",
        "Add commit_intent rate limit 10/min demo safety",
        "Validate align_command_data_ui gate-aware when enforcement active",
        "Add enforcement lane row PROGRAM_PROGRESS parallel track",
        "Reject WTM Phase expansion during e8",
        "Add hash chain stub on receipt-log-v1.jsonl optional",
        "Document kernel % complete metric honest 40→70 target",
        "Add validate-governance-event-spine in demo preflight",
        "Freeze new scripts law: must call commit_intent or gatekeeper",
        "Add code review grep bypass patterns in PR habit",
        "Validate sourcea_execute factory path unchanged by e8 work",
        "Append kernel harden milestone receipt",
    ],
    [  # e9 dec closeout
        "Binary check W1: filmed demo exists in the repository",
        "Binary check W2: validate-demo-enforcement-v1.sh PASS + tamper FAIL proven",
        "Binary check W3: LOI deposit or SOW signed",
        "Freeze enforcement scope Dec 1 — no new features",
        "Write honest miss report if W3 absent",
        "Update ENFORCEMENT_6MO tracker all slices status",
        "Archive demo artifacts index complete",
        "Run final chaos drill before Dec freeze",
        "Update grade C→B if 1.10 sealed + W1+W2",
        "Prepare seed data room zip",
        "Log 6-month tier achieved A B C or D honest",
        "Document lessons INCIDENT-027 for investor DD",
        "Retire stale GPT paradigm docs to pointer only",
        "Set ENFORCEMENT-6MO status done or extended in PROGRAM_PROGRESS",
        "Validate factory unproven still 0 at closeout",
        "Export metrics: meetings LOIs deposits validators PASS count",
        "Prepare Jan roadmap only after Dec win/miss declared",
        "Add founder retrospective 1 page",
        "Reject starting enforcement-2000 before W1+W2",
        "Cross-check no Trust OS rename shipped",
        "Validate parallel FR-003 1.10 status documented",
        "Archive all demo recordings catalog",
        "Set 2027 north star only after seed path clear",
        "Thank design partners in writing",
        "Final receipt: ENFORCEMENT-6MO closeout PASS or honest FAIL",
    ],
]


def prompt_body(
    pid: str,
    phase: str,
    phase_desc: str,
    tier: str,
    task: str,
    slot: int,
    today: str,
    meta: dict,
    slice_ref: str,
) -> str:
    priority = {"T0": "P0", "T1": "P1", "T2": "P2", "T3": "P3"}[tier]
    slice_line = f"slice_ref: {slice_ref}\n" if slice_ref else ""
    return f"""---
id: {pid}
phase: {phase}
tier: {tier}
priority: {priority}
category: {meta['category']}
owner: {meta['owner']}
month: {meta['month']}
win: {meta['win']}
{slice_line}status: backlog
lane: enforcement-6mo
library: enforcement-1000-locked
agent: {AGENT}
agent_tag: {TAG}
written_at: {today}
slot: {slot}
generator: scripts/generate-enforcement-1000-prompts.py
generator_version: {GENERATOR_VERSION}
locked: true
pivot: ENFORCEMENT-6MO
---

# [{TAG}@{today}] {pid} — {task[:100]}

**Category:** `{meta['category']}` · **Win:** `{meta['win']}` · **Owner:** `{meta['owner']}` · **Month:** `{meta['month']}`  
**Phase:** `{phase}` — {phase_desc}  
**Tier:** `{tier}` — {TIER_DEPTH[tier]}

## Agent prompt (copy to chat)

```
PLAN WITH NO ASF — ENFORCEMENT-6MO {pid}: {task} ({TIER_DEPTH[tier]}) Gate test: increases (a) enforcement strength (b) demo credibility (c) willingness to pay — else DELETE. Read brain-os/law/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md + prompts/ENFORCEMENT_6MO_MASTER_CONTROL_PROMPT_v1.md first. FORBIDDEN: Trust OS rename · REGISTRY drain hero · hub rewrite · whitepaper-first. Verify + receipt + mark done.
```

## Task

{task}

## Sources (read first)

- `brain-os/law/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md`
- `prompts/ENFORCEMENT_6MO_MASTER_CONTROL_PROMPT_v1.md`
- `brain-os/demo/ENFORCEMENT_ARTIFACTS_INDEX_v1.md`
- `scripts/commit_intent_v1.py` · `scripts/demo-enforcement-5min-v1.sh`
- `scripts/validate-demo-enforcement-v1.sh` · `scripts/validate-universe-invariants-v1.sh`
- `investor/ENFORCEMENT_OUTREACH_v1.md` · `docs/ENFORCEMENT-6MO-DEMO-SCRIPT_v1.md`

## Verify

```bash
{VERIFY[tier]}
```

## Closeout

1. Set `status: done` in front matter when complete
2. Append `REPO_EXECUTION_LOGS/sourcea/` YAML with `enforcement_6mo: true`
3. Update `brain-os/demo/ENFORCEMENT_30DAY_BACKLOG_v1.md` if slice maps
4. Re-run `bash scripts/validate-enforcement-1000-pack.sh`
"""


def main() -> None:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entries: list[dict] = []
    seq = 0

    for p_idx, (phase, phase_desc) in enumerate(PHASES):
        tasks = PHASE_TASKS[p_idx]
        meta = PHASE_META[phase]
        for tier, _tier_desc in TIERS:
            tier_dir = PROMPTS / phase / tier
            tier_dir.mkdir(parents=True, exist_ok=True)
            for slot in range(25):
                seq += 1
                pid = f"enf-{seq:04d}"
                base = tasks[slot]
                task = expand_task(base, tier, meta["win"])
                slice_ref = SLICE_BY_SLOT.get(phase, {}).get(slot, "")
                rel = f"prompts/{phase}/{tier}/{pid}.md"
                path = PACK / rel
                status = "done" if pid in DONE_IDS else "backlog"
                body = prompt_body(
                    pid, phase, phase_desc, tier, task, slot, today, meta, slice_ref
                )
                if status == "done":
                    body = body.replace("status: backlog", "status: done", 1)
                path.write_text(body, encoding="utf-8")
                entries.append(
                    {
                        "id": pid,
                        "phase": phase,
                        "tier": tier,
                        "priority": {"T0": "P0", "T1": "P1", "T2": "P2", "T3": "P3"}[tier],
                        "category": meta["category"],
                        "owner": meta["owner"],
                        "month": meta["month"],
                        "win": meta["win"],
                        "slice_ref": slice_ref,
                        "lane": "enforcement-6mo",
                        "slot": slot,
                        "title": task[:120],
                        "path": rel,
                        "status": status,
                        "verify": VERIFY[tier],
                        "agent_tag": TAG,
                        "agent_prompt": f"PLAN WITH NO ASF — ENFORCEMENT-6MO {pid}: {task}",
                    }
                )

    pinned = [{"id": pin, "lane": "enforcement-6mo", "tier": "T0", "status": "done"} for pin in PINNED_DONE]
    for pin, title in PINNED_PARALLEL:
        pinned.append(
            {
                "id": pin,
                "lane": "enforcement-6mo",
                "tier": "T0",
                "status": "backlog",
                "title": title,
                "founder_only": pin.startswith("pinned-enf-w3"),
            }
        )

    from collections import Counter

    by_cat = Counter(e["category"] for e in entries)
    registry = {
        "schema_version": 2,
        "library": "enforcement-1000-locked",
        "locked": True,
        "count": len(entries),
        "generated_at": now,
        "generator_version": GENERATOR_VERSION,
        "agent": AGENT,
        "agent_tag": TAG,
        "repo": "SourceA",
        "pivot": "ENFORCEMENT-6MO",
        "grid": "10 phases × 4 tiers × 25 prompts = 1000 (tier-expanded titles)",
        "trigger": "PLAN WITH NO ASF ENFORCEMENT",
        "pick_script": "scripts/pick-enforcement-no-asf-plan.py",
        "run_script": "scripts/plan-enforcement-no-asf-run.sh",
        "validate_script": "scripts/validate-enforcement-1000-pack.sh",
        "audit_script": "scripts/audit-enforcement-1000-v1.py",
        "category_index": "brain-os/plan-registry/ENFORCEMENT-1000-CATEGORY-INDEX.md",
        "parent_law": "brain-os/law/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md",
        "supersedes_for_lane": "enforcement-6mo only — does not replace sourcea-1000 factory pack",
        "sources": [
            "brain-os/law/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md",
            "prompts/ENFORCEMENT_6MO_MASTER_CONTROL_PROMPT_v1.md",
            "brain-os/demo/ENFORCEMENT_30DAY_BACKLOG_v1.md",
            "brain-os/demo/ENFORCEMENT_ARTIFACTS_INDEX_v1.md",
            "os/plan-library/ENFORCEMENT-6MO-MASTER-PROMPT_LOCKED_v1.md",
        ],
        "phases": [
            {"id": p, "description": d, **PHASE_META[p]} for p, d in PHASES
        ],
        "tiers": [{"id": t, "description": d} for t, d in TIERS],
        "categories": {
            cat: {
                "count": by_cat[cat],
                "win": PHASE_META[next(ph for ph, m in PHASE_META.items() if m["category"] == cat)]["win"],
            }
            for cat in sorted(by_cat)
        },
        "pinned": pinned,
        "plans": entries,
        "success_criteria": {
            "W1": "5-min demo BLOCK ALLOW tamper FAIL filmed",
            "W2": "commit_intent + receipt + validate-demo-enforcement PASS",
            "W3": "TF-001 or NF-001 deposit LOI or SOW",
            "gate_test": "enforcement | demo | pay else DELETE",
        },
    }

    PACK.mkdir(parents=True, exist_ok=True)
    (PACK / "REGISTRY.json").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    assert len(entries) == 1000, f"expected 1000 got {len(entries)}"
    print(f"LOCKED {len(entries)} ENFORCEMENT-6MO prompts → {PACK / 'REGISTRY.json'}")


if __name__ == "__main__":
    main()
