# Sina poison tracking method — PT-METHOD (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14  
**Authority:** ASF order — reverse-engineered from INCIDENT-028 · 034 · conduct+poison audits · Brain/Gov/Commercial cross-chat synthesis  
**Parent:** `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md` §5 · `SOURCEA_INCIDENT_FIX_OWNERSHIP_GOVERNANCE_HARDENING_LOCKED_v1.md`  
**Companion:** `archive/attachments/2026-06-14/POISON_TRACK_RECEIPT_TEMPLATE_AND_TRACKER_SHEET_LOCKED_v1.md`  
**Case study (first full PT run):** `archive/attachments/2026-06-14/OLD_INJECT_HUNT_CHAT_TIMELINE_PIPELINE_MAP_LOCKED_v1.md`

---

## 1. One sentence

**Poison = a writer logged or in the hub that injects the wrong founder path into agent sessions — PT-METHOD finds the writer, fixes the wire, proves PASS on validators, and tracks until Governance + ASF close with streak proof.**

---

## 2. When to invoke (conflict-hard triggers)

Run **full PT-METHOD** (not chat debate) when **any** of:

| Trigger | Signal |
|---------|--------|
| **T1 Multi-chat conflict** | Brain · Worker · Gov · Commercial tell founder different daily paths |
| **T2 Validator flip** | R1–R3 PASS once then FAIL within same hub session / 12s window |
| **T3 Founder correction** | ASF says advice is stale / wrong / “you already fixed that” |
| **T4 Chat vs disk** | Agent close-line contradicts `*-live-context-v1.json` or truth bundle |
| **T5 Conduct + poison** | Agent disobeyed order **and** automation kept running wrong queue/drain |
| **T6 Propagation gap** | LOCKED law changed · broker/INBOX/hub/API still old (Gov specialist class) |
| **T7 Prohibition paradox** | New “never say X” law · agents say X more (INCIDENT-034) |

**Do not invoke for:** external critic paste alone · single typo · museum-only lag with execution green.

---

## 3. Poison taxonomy (P-CLASS — reverse-engineered)

| Class | Name | Writer examples | Consumer | First seen |
|-------|------|-----------------|----------|------------|
| **P1-INJECT** | Session inject | `.cursor/rules/*.mdc` · `agent-memory-mirror` inject · skills | Every Cursor session | INCIDENT-028 |
| **P2-CACHE** | Disk cache re-infection | `goal1-lane-broker` · `execution-lane` · `099-worker-inbox-active.mdc` | Worker INBOX · gate | INCIDENT-028 |
| **P3-API** | Hub route wrapper | POST `/api/prompt-direction` attaches full `command-data` in `data` | UI + agents using POST | INCIDENT-034 / AR-034-01 |
| **P4-RUNTIME** | Stale process | Old `dashboard_server` PID reverts JSON every ~5s | All disk validators | 2026-06-14 hunt |
| **P5-PROJECTION** | Hub projection lag | `command-data*.json` hero · `must_do_today` | Founder glance · set_context | INCIDENT-033 |
| **P6-PROHIBITION** | Forbid-by-naming | “Never say Prompt feed” tables in inject | Model repeats banned string | INCIDENT-034 |
| **P7-QUEUE** | Wrong queue head | `phase-s5-commercial-lanes` before WTM spine | Autodrain · broker pick | Conduct audit P05 |
| **P8-PROPAGATION** | Law not on all surfaces | LOCKED doc updated · stairlift/broker/INBOX not | All agents | Gov fix program 2026-06-13 |
| **P9-CHAT-ECHO** | Self-authored history | Agent repeated stale close-line in transcript | Same chat next turn | INCIDENT-013 |
| **P10-SPLIT-AUTHORITY** | Two SSOTs | Chat memory vs `~/.sina/` vs hub projection | Brain route errors | INCIDENT-033 |

**Rule:** Fix the **writer** (P1–P8). Never close on P9 alone without fixing upstream writer.

---

## 4. PT-METHOD — nine phases (machine + roles)

```
PT-0 CLASSIFY → PT-1 SNAPSHOT → PT-2 DRIFT LINE → PT-3 PIPELINE MAP
     → PT-4 OWN → PT-5 REMEDIATE → PT-6 HARDEN → PT-7 VERIFY → PT-8 TRACK → PT-9 CLOSE
```

Same spine as `detect → classify → remediate → harden → verify → record` — **poison-specific**.

### PT-0 — Classify (Brain + Governance)

| Output | Who |
|--------|-----|
| Line 1: `POISON TRACK: PT-METHOD_v1 · class P?_ · incident ___` | Whoever opened track |
| Tag: `POISON` \| `CONDUCT` \| `BOTH` \| `DRIFT` \| `PROPAGATION` | Brain routes; Gov records |

**Brain job:** Name class · hand Worker execute · **do not** implement sa · quote `brain-live-context-v1.json`.

**Commercial job:** Flag **P7-QUEUE** if sa-05xx / commercial phase in default achievable queue · confirm `execution_authority: false` — advise only.

---

### PT-1 — Snapshot (Executor — disk only)

Run **verbatim** (no chat memory):

```bash
cd ~/Desktop/SourceA
bash scripts/validate-brain-disk-no-prompt-feed-v1.sh
bash scripts/validate-worker-disk-no-prompt-feed-v1.sh
bash scripts/validate-disk-live-wire-v1.sh
python3 scripts/anti_staleness_auto_wire_v1.py --role brain --tier session --json
python3 scripts/agent_session_gate_run_v1.py --role brain --json
python3 scripts/agent_session_gate_run_v1.py --role worker --json
```

**Plus class-specific:**

| Class | Extra commands |
|-------|----------------|
| P3-API | GET vs POST same route · measure payload size · name poison key |
| P4-RUNTIME | 12s stability on suspect JSON · `pgrep -fl dashboard_server` |
| P7-QUEUE | `factory-now-v1.json` · `healthy-queue-30-active.json` head phase |
| P8-PROPAGATION | `founder_input_cascade` receipt · stairlift mtime |

**Receipt:** `~/.sina/poison-track-receipt-v1.json` (template in companion doc).

---

### PT-2 — Drift line (Governance + Executor)

| Step | Action |
|------|--------|
| Read transcripts | Brain · Worker · Gov · Commercial · executor arc |
| Find **first founder-facing** poison line | Not diagnosis text |
| Record | transcript id · line · date · exact string |
| Correlate | Which writer existed logged **at that time** |

**Forbidden:** “Fresh chat fixes it” · “Brain reads chat not disk” · blame consumer agent.

---

### PT-3 — Pipeline map (Executor)

Draw writer chain (companion template):

```text
WRITER → SURFACE FILE/API → SESSION CONSUMER → FOUNDER OUTPUT
```

**Rank writers** by re-infection power (example INCIDENT-034):

1. alwaysApply rules  
2. POST API wrappers  
3. INBOX / broker cache  
4. background sync PID  
5. static `~/.sina/brain/*.md`  
6. hub projection  

---

### PT-4 — Own (RACI — results policy)

| Role | Owns fix | Tracks | Approves close |
|------|----------|--------|----------------|
| **ASF** | Product truth | — | **Yes** |
| **Cursor executor (SourceA)** | P1 P2 P4 P6 P9 harden · disk scripts/rules | Self-verify | No |
| **Maintainer 2** | P3 P5 hub UI/API | Gov verifies | No |
| **Brain** | PT-0 classify · route · `mandatory_next` | No | No |
| **Governance Specialist** | PT-8 tracker · streak · meta-audit | **Primary** | Recommends |
| **Commercial Specialist** | P7 queue advise · PICK drafts | Gov | No |

**No handoff fiction:** Executor ships disk; Maintainer ships hub; Governance never claims fix without validator stdout.

---

### PT-5 — Remediate (minimal writer fix)

| Principle | Law |
|-----------|-----|
| **Positive wire > prohibition** | INCIDENT-034 — fix disk inject, not ban tables |
| **Fix writer not reader** | Scrub broker, not “train Brain” |
| **One writer per commit** | Identify root re-poisoner in PT-3 |
| **Subprocess sync** | When fighting stale hub PID — scrub after write |

**Ship map (by class):**

| Class | Typical fix |
|-------|-------------|
| P1-INJECT | Rule version bump · `alwaysApply: false` on legacy · live context JSON |
| P2-CACHE | Scrub scripts · broker snapshot without prompt body |
| P3-API | Stop attaching full hub payload on POST success |
| P4-RUNTIME | Kill stale PID · restart with fresh Python |
| P5-PROJECTION | Rebuild projection · museum-only labeling |
| P6-PROHIBITION | Supersede with `AGENT_DISK_LIVE_WIRE_FIRST` positive map |
| P7-QUEUE | `queue_ssot_unify` · phase order per `FOUNDER_BUSY_OPERATING_MODEL` |
| P8-PROPAGATION | `founder_input_cascade_v1.py` · stairlift · broker gate |

---

### PT-6 — Harden (fail-closed)

| Layer | Machine |
|-------|---------|
| Guard | `worker_steer_guard_v1.py` · `founder_close_line_gate_v1.py` · `cursor_entry_gate --scan-text` |
| Scrub | `brain_stale_prompt_scrub_v1.py` · `worker_stale_prompt_scrub_v1.py` |
| Validator | Class-specific + `validate-disk-live-wire-v1.sh` |
| Receipt | Append `~/.sina/agent-governance-events.jsonl` |

**Governance Specialist:** Add row to fix matrix if new class — `SOURCEA_INCIDENT_FIX_OWNERSHIP_*` format.

---

### PT-7 — Verify (results R-table)

Use **`STALE_ADVICE_RESULTS_POLICY_OWNERSHIP_TRACKING_LOCKED_v1.md`** R1–R10 as default poison track results.

**Minimum PASS to unblock founder:**

- R1 + R2 + R3 green  
- PT-3 root writer named and patched OR AR filed with owner  
- P4: 12s stability green  
- P3: GET clean **and** POST poison documented until Maintainer ships  

**Conduct add-on:** If `BOTH`, run conduct checklist from `SOURCEA_CONDUCT_AND_POISONED_LOOP_AUDIT_PROMPT_LOCKED_v2.md` C01–C15.

---

### PT-8 — Track (Governance Specialist)

| Cadence | Action |
|---------|--------|
| Every executor session touching poison | Copy tracker sheet · fill R1–R8 |
| After remediate | Log PT event jsonl |
| Weekly / incident | Meta-audit open ARs · streak count |
| Recurrence | Re-open PT · PT-3 must name **new** writer (C-16) |

**Tracker SSOT:** companion doc §2 sheet · policy doc §8.

---

### PT-9 — Close (ASF + Governance)

**Poison track closes when ALL:**

- [ ] PT-3 root writer fixed or Maintainer AR shipped with R10 PASS  
- [ ] R1–R3 green on **3 consecutive** Brain **and** Worker sessions (R9)  
- [ ] No new drift lines in founder-facing replies since fix  
- [ ] Governance tracker signed · jsonl event `POISON_TRACK_CLOSED`  
- [ ] ASF confirms live close-line once with disk proof  

**Forbidden close criteria:** fresh chat · “agents reminded” · prohibition-only · chat apology without disk.

---

## 5. Role playbooks (reverse-engineered)

### 5.1 Brain (L1 #1 — route, not execute)

```text
READ   ~/.sina/brain-live-context-v1.json first
CLASS  PT-0 · assign P-CLASS · mandatory_next → Worker RUN INBOX
MAP    Do not re-poison founder with Prompt feed / hub daily / AUTO-RUN
HANDOFF Worker executes PT-1/5/6 · Governance tracks PT-8
FORBID Implement sa · blame Worker for inject · fresh chat as fix
```

### 5.2 Cursor executor (SourceA — disk surgeon)

```text
RUN    PT-1 snapshot · PT-3 map · PT-5 remediate · PT-6 harden · PT-7 verify
USE    CART C-00–C-16 when class P1/P2/P4/P6
LOG    agent-governance-events.jsonl every material heal
NEVER  Hub panel edits · prohibition stacks · report-only close
```

### 5.3 Governance Specialist (L1 #2 — tracker)

```text
OWN    PT-8 · R9 streak · fix matrix · meta-audit
READ   STALE_ADVICE_RESULTS_POLICY · this doc · incident registry
PROVE  Validator stdout before “fixed” language
FORBID Fake green · partial blame close · critic-driven reorder
```

### 5.4 Commercial Specialist (L1 #3 — queue + picks)

```text
OWN    P7-QUEUE class · 9.07 A scope · open PICKs to Canvas
READ   live_founder_decision_form --json before hero claims
FLAG   sa-05xx in default queue · execution_authority false
FORBID GOV_UNIFY batch when 3.07 NO · factory drain hero · chat-substitute picks
```

### 5.5 Maintainer 2 (hub — P3/P5 only)

```text
OWN    API wrappers · H1 hero · command-data projection rebuild
FIX    POST routes that attach full payload · museum link INCIDENT-032
FORBID Disk script ownership · sa execution · “refresh fixes it” without rebuild proof
```

---

## 6. Integration map (do not duplicate)

| Existing machine | PT phase |
|------------------|----------|
| `anti_staleness_auto_wire_v1.py` | PT-1 · PT-5 |
| CART C-16 stale inject hunt | PT-3 · PT-5 |
| Conduct+Poison audit v2 | PT-0 BOTH · P7 |
| `governance_drift_engine.py` | PT-8 sensor (not poison-specific) |
| G7 self-heal daemon | PT-6 delegate (not replace PT) |
| `founder_input_cascade_v1.py` | P8-PROPAGATION |
| `STALE_ADVICE_RESULTS_POLICY_*` | PT-4 · PT-7 · PT-8 |
| S10 eternal audit | Weekly deep · not session poison |

---

## 7. First canonical case (INCIDENT-034 class — template)

| Phase | What we proved |
|-------|----------------|
| PT-0 | POISON + PROPAGATION · P1 P2 P3 P4 P6 |
| PT-2 | Brain L121 · Worker L908 · Gov L611 |
| PT-3 | prompt-queue.mdc → POST prompt-direction → broker → dashboard PID |
| PT-4 | Executor disk · Maintainer POST API · Gov tracks |
| PT-5 | Live wire · scrub · guards · prompt-queue v8 |
| PT-7 | R1–R8 PASS · R10 POST still FAIL |
| PT-9 | **OPEN** — R9 + AR-034-01 |

---

## 8. Quick invoke (founder one line)

> **“Run poison track PT-METHOD on [symptom].”**

Agent line 1 reply:

`POISON TRACK: PT-METHOD_v1 · [P-CLASS] · read disk first`

Then PT-1 snapshot before any advice.

---

**END PT-METHOD v1**
