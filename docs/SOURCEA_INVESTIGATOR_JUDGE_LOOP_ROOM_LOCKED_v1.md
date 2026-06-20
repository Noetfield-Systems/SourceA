# SourceA Investigator Room · Judge Room · Loop Health — LOCKED v1

**Version:** 1.1.0 · **Saved:** 2026-06-18T22:52:00Z · **Authority:** ASF SAVE  
**Path:** `docs/SOURCEA_INVESTIGATOR_JUDGE_LOOP_ROOM_LOCKED_v1.md`  
**Plan id:** **IJ10** — Investigator + Judge loop upgrade (Mac-first · cloud-ready)  
**Supersedes:** chat-only “investigator” essays · scattered room prose without machine chain  

**Parents (pointer-only — do not duplicate law):**
- `SOURCEA_GOVERNANCE_CENTER_SELF_GOVERN_LOCKED_v1.md` — Judge · Lawyer · Planner
- `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md` — self-healing loop §5
- `docs/SOURCEA_STACK_MAP_AND_BETTER_LOOP_LOCKED_v1.md` — Better Loop · Critic · Nerve
- `docs/SOURCEA_TIER_PRIORITY_COST_INTELLIGENCE_POLICY_LOCKED_v1.md` — free tier first · ROI pick
- CL10: `loop_specialist_tick_v1.py` · `future_loop_prompt_advisory_circle_v1.py`
- OL10: `loop_observatory_report_v1.py`

---

## 0. One sentence (law)

> **Investigator Circle always tracks loop health on disk; Judge Room verdicts conflicts; Advisory Circle ranks next prompts; Loop Specialist composes and dispatches — Brain alone holds execution authority; rooms REPORT or bounded ACT, never a second Brain.**

---

## 1. What exists today (proof — Jun 2026)

| Surface | Job | Machine | Receipt |
|---------|-----|---------|---------|
| **Judge Center L3** | RIGHT / STALE / BAD on chat vs RECENT | `judge_center_bench_v1.py` | `~/.sina/judge-center/latest-resolution-v1.json` |
| **Judge Counsel L2** | KEEP / IGNORE / ESCALATE | `judge_center_counsel_v1.py` | `~/.sina/judge-center/latest-counsel-v1.json` |
| **Governance Center** | Planner + Judge + Lawyer + Thread cadence | `governance_center_run_v1.py` | `~/.sina/governance-center-receipt-v1.json` |
| **Loop Observatory** | Unified observe/check | `loop_observatory_report_v1.py` | `~/.sina/loop-observatory-report-v1.json` |
| **Future Prompt Advisory** | Deterministic ranked prompts · **no execution** | `future_loop_prompt_advisory_circle_v1.py` | `~/.sina/future-loop-prompt-advisory-v1.json` |
| **Loop Specialist** | Observe → compose → dispatch | `loop_specialist_tick_v1.py` | `~/.sina/loop-specialist-tick-receipt-v1.json` |
| **Better Loop** | BL1–BL11 health cart | `better_loop_pulse_v1.py` | `~/.sina/better-loop-pulse-receipt-v1.json` |
| **Critical bugs** | Machine investigator for FAIL rollup | `find_critical_bugs.py` | `~/.sina/find-bugs/last-run.json` |
| **Conflict Room** | ACE when laws disagree | `agent_conflict_room.py` | `~/.sina/conflict-room/cases.jsonl` |
| **Incident Room** | Weekly safety share | hub API | per `ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md` |
| **Council Room** | Mind share · paradox (Phase 1) | `agent_council_room.py` | `AGENT_COUNCIL_ROOM_LOCKED_v1.md` |
| **Hospital** | H0–H8 heal (founder word **hospital** only) | `agent_hospital_pipeline_v1.py` | `~/.sina/agent-hospital-receipt-v1.json` |

**Gap this law closes:** Judge today resolves **chat archaeology**; Investigator signals are split across observatory · pulse · FCB · drift · nerve — **no unified investigation receipt** routing to specialists before loop dispatch.

---

## 2. Three circles + one router (architecture)

```text
Brain (sole execution_authority)
  │
  ├── Investigator Circle (L0.5 · always track)
  │     loop observatory + better pulse + find_critical_bugs + drift + nerve
  │     → investigation_verdict: GREEN | YELLOW | RED
  │     → report to Judge + mapped specialist
  │
  ├── Future Prompt Advisory Circle (L0.5 · reasoning only)
  │     ranked_prompts + deterministic_hash · execution_authority: false
  │
  ├── Judge Room (L2 counsel · L3 bench)
  │     LOOP_HEALTHY | LOOP_DEGRADED | PROMPT_STALE | DISPATCH_BLOCKED
  │     → INSIGHT | REPORT | bounded ACT catalog | form row drafts
  │
  └── Loop Specialist (L0.5 · compose + policy-gated dispatch)
        → outbound assign / orchestrator · Worker INBOX executor (one sa/turn)
```

**Human rooms (parallel — not daily loop driver):** Council · Conflict · Incident — fleet discourse and ACE; agents **continue work**, never freeze project (`SINA_AGENT_CONFLICT_ROOM_LOCKED_v1.md`).

**Forbidden:** Museum / command-data audit as investigator SSOT (`SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md`) · second Brain chat · AUTO-RUN without ASF resume · Judge chat as authority (`SOURCEA_GOVERNANCE_CENTER_SELF_GOVERN_LOCKED_v1.md` §5).

---

## 3. Role matrix

| Room / Circle | Track | Check | Insight | ACT | REPORT |
|---------------|-------|-------|---------|-----|--------|
| **Investigator Circle** | ✓ | ✓ | root-cause hints | heal catalog only | ✓ always |
| **Advisory Circle** | — | ROI rank | next prompts | ✗ | to Specialist composer |
| **Judge Room** | — | verdict | KEEP/IGNORE | form drafts · remediate prompts | ✓ route table |
| **Loop Specialist** | via observatory | policy | compose line | dispatch when allowed | hub line |
| **Council / Conflict / Incident** | human | ACE | discourse | ✗ | peers + ASF queue |

---

## 4. Specialist routing (deterministic)

| Signal | Primary specialist | Secondary | Room if law clash |
|--------|-------------------|-----------|-------------------|
| `commercial_red_count` > 0 | Commercial / W3 lane | Loop Specialist compose | — |
| `w3_sina_read` FAIL | Founder Sina read path | ICP compiler | — |
| `system_red_count` > 0 | Governance specialist | G7 self-heal | Incident if material |
| `dual_pick` FAIL | SourceA Worker + ACTIVE_NOW sync | Brain route | Conflict if two SSOTs |
| `critical_count` > 0 | Investigator → hospital suggest | find_critical_bugs owner | Incident |
| `drift_score` < 85 | Governance Center full tier | anti-staleness | Conflict |
| `prompt_blocked_by_freeze` | ASF resume gate | — | — |
| ACE class C boundary | — | — | Conflict Room |

**Commercial compile order (unchanged):** SourceA Sina read → Noetfield compile → TrustField send.

---

## 5. Self-healing loop (machine)

From `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md` §5 — bound to Investigator + Judge:

```text
detect → classify → remediate → harden → verify → record
```

| Phase | Investigator source | Judge verdict | Allowed ACT (bounded) |
|-------|---------------------|---------------|------------------------|
| **Detect** | observatory reds · pulse FAIL · FCB critical | LOOP_DEGRADED / RED | — |
| **Classify** | tier + ROI policy | route specialist | — |
| **Remediate** | one next action from observatory `founder_action` | DISPATCH_BLOCKED if freeze | mirror sync · dual heal · active_now sync |
| **Harden** | validator FAIL class | ESCALATE INCIDENT-* | add checkcart row (GOV_UNIFY) |
| **Verify** | session gate · validate-* | LOOP_HEALTHY | — |
| **Record** | investigation receipt | resolution receipt | `agent-governance-events.jsonl` |

**Near-miss:** log + harden even if founder did not file incident.

---

## 6. IJ10 — ten implementation steps (Mac-first)

| Step | Deliverable | Status |
|------|-------------|--------|
| **IJ1** | Schema `loop-health-investigation-receipt-v1.json` | **shipped** · `~/.sina/loop-health-investigation-receipt-v1.json` |
| **IJ2** | `investigator_circle_run_v1.py` · verdict GREEN/YELLOW/RED | **shipped** |
| **IJ3** | `data/investigator-specialist-routing-v1.json` | **shipped** |
| **IJ4** | `judge_loop_room_v1.py` — loop receipt verdicts | **shipped** |
| **IJ5** | Specialist KEEP/REPORT/ACT_SUGGEST in judge receipt | **shipped** |
| **IJ6** | Wired in `disk_live_wire_sync_v1.py` + session gate | **shipped** |
| **IJ7** | Hub slices `investigator_room` · `judge_room` + POST APIs | **shipped** |
| **IJ8** | `data/investigator-self-heal-catalog-v1.json` | **shipped** |
| **IJ9** | Pipeline nodes `N_investigator_circle` · `N_judge_loop` | **shipped** |
| **IJ10** | `validate-investigator-judge-loop-v1.sh` | **shipped PASS** |

**Rollout order (tier policy):** free Mac tick + hub API → n8n cron glue → Cloudflare Worker observe-only (Phase 2b) → paid cloud only after ROI + ASF gate (`docs/SOURCEA_TIER_PRIORITY_COST_INTELLIGENCE_POLICY_LOCKED_v1.md`).

---

## 7. Cloud contract (Phase 2b prep)

Mirror `data/investigator-judge-cloud-contract-v1.json` pattern:

- **POST** `/api/investigator-circle/tick/v1` — observe only  
- **POST** `/api/judge-loop/tick/v1` — verdict + route; no dispatch  
- Dispatch remains **Loop Specialist** + Brain resume under freeze  

Mac SSOT until federated mirror ships.

---

## 8. Machine proof (wired)

```bash
python3 scripts/investigator_circle_run_v1.py --json
python3 scripts/judge_loop_room_v1.py --json
python3 scripts/loop_observatory_report_v1.py --json
python3 scripts/future_loop_prompt_advisory_circle_v1.py --json
python3 scripts/loop_specialist_tick_v1.py --json
bash scripts/validate-investigator-judge-loop-v1.sh
bash scripts/validate-loop-specialist-v1.sh
bash scripts/validate-better-loop-v1.sh
bash scripts/n8n_investigator_judge_tick_hook_v1.sh --local
```

---

## 9. Authority index

**Row id (next GOV_UNIFY):** `INVESTIGATOR_JUDGE_LOOP` → this path.

---

## 10. Founder one-liner

**Investigator watches · Judge verdicts · Advisory ranks · Specialist dispatches · Worker executes one turn — receipts prove health, not chat.**
