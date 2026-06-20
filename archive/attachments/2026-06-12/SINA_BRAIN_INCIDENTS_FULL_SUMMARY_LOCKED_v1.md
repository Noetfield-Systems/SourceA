# Sina Brain — Incidents Full Summary (LOCKED v1)

**Saved:** 2026-06-12T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Locked:** 2026-06-12 · **Authority:** ASF  
**Topic:** Every Brain-class incident — primary, touching, near-miss, session 2026-06-12 — full detail summary.  
**Master registry:** `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`  
**Subject index:** `brain-os/incidents/INCIDENT_SUBJECT_INDEX_LOCKED_v1.md`  
**Near-miss index:** `brain-os/incidents/NEAR_MISS_AND_UNFILED_INCIDENTS_INDEX_LOCKED_v1.md`  
**Compendium:** `brain-os/incidents/SINA_ECOSYSTEM_INCIDENTS_AND_SESSION_INSIGHTS_COMPENDIUM_LOCKED_v1.md`

---

## 0. One sentence

> **Brain incidents = lane violations, trust-breaking UI vocabulary, validator marathons, hierarchy disobedience, and governance id invention — fixed by guards, idle gates, receipt-only closeout, and registry-first filing.**

---

## 1. Brain role vs incident class

| Brain may | Brain must NOT (incident if violated) |
|-----------|--------------------------------------|
| Pick · route · reconcile · assign | Implement `sa-*` · multi-file builds |
| Narrate · unify · COPY_SAFETY | Run Goal-1 drain / Worker INBOX |
| Load Maintainer bridge **first** | Invent `INCIDENT-NNN` without registry |
| Receipt-only verify · **<30s** reply | Chain validators · `Await` shells **>90s** |
| Refuse worker prompts in Brain chat | E2E marathon while factory mid-slice |

**Brain session read (incidents slice):** Registry → **003b · 004 · 014 · 015 · 026** (both) → compendium.

---

## 2. Brain-primary incidents (full detail)

### INCIDENT-003b — Brain/Worker lane cross

| Field | Detail |
|-------|--------|
| **ID** | 003b |
| **Date** | 2026-06-07 |
| **Severity** | Lane boundary |
| **Body** | `brain-os/incidents/SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md` |
| **What happened** | Worker healthy-drain prompt (`[GOAL1_HEALTHY_DRAIN]`) appeared in **Brain** chat; Brain ran validators — wrong lane. |
| **Root cause** | No mechanical refuse on Brain turns containing worker signals. |
| **Founder harm** | Founder told to run factory work in Brain window. |
| **Fix shipped** | `brain_lane_guard.py` · `brain-not-worker.mdc` · `worker-loop-headsup-v1.json` · MANDATORY_BRAIN v1.1 |
| **Law** | Brain sees worker paste → **REFUSE** `BRAIN_REFUSE_WORKER_PROMPT` — route to Worker chat. |
| **Status** | **Canonical · remediated** |

---

### INCIDENT-004 — Goal hierarchy enforcement (Brain + advisor)

| Field | Detail |
|-------|--------|
| **ID** | 004 |
| **Date** | 2026-06-07 → 2026-06-08 |
| **Severity** | **Critical** |
| **Body** | `brain-os/incidents/SINA_GOAL_HIERARCHY_ENFORCEMENT_INCIDENT_LOCKED_v1.md` |
| **What happened** | Brain asked founder to **pick Lane A vs B** when `GOAL_HIERARCHY_LOCKED_v1.md` already said: T0 factory + T3 WTM/Pre-LLM **before** T2b commercial. Claude Pro advised architecture without hierarchy reconcile. CLI routed commercial `sa-050x` while scoped loop used eval-dispatch `sa-0153+`. |
| **Root cause** | **Enforcement failure** — law in repository; Brain/advisor did not obey default routing. |
| **Founder harm** | False “two valid strategies”; automation looks broken when law was clear. |
| **Fix shipped** | `GOAL_HIERARCHY` in `cursor_entry_gate.py` brain role · FOUNDER_ADVISOR §8–9 · commercial quarantine in queue builder |
| **Law** | Brain default: **FORGE + WTM + REGISTRY** — MSB only on `founder mode revenue`. RunReceipt ≠ north star. |
| **Status** | **Canonical · open enforcement** (recurring drift class) |

---

### INCIDENT-014 — Monitor Brain column snapshot drift

| Field | Detail |
|-------|--------|
| **ID** | 014 |
| **Severity** | **High** (founder trust) |
| **Body** | `brain-os/incidents/SINA_MONITOR_BRAIN_COLUMN_SNAPSHOT_DRIFT_INCIDENT_014_LOCKED_v1.md` |
| **Adjunct** | `SINA_BRAIN_REPAIR_INCIDENT_014_COMPLETION_ADJUNCT_LOCKED_v1.md` |
| **What happened** | Monitor `:13021` showed **Brain PEND on every row** (sa-0001..0040+) while Worker/Broker/Valid YES stayed green. Founder read this as “redo all work” / “critical mistake.” |
| **Root cause** | Brain column = **global** flag: `brain-goal1-validation-v1.json` stale (154) vs live valid_yes (172). **Not** per-sa brain work. Pack 3 advanced honest count without `brain_validate_goal1.py --write-receipt` sync. |
| **Founder harm** | Trust break — agent said “verified” while UI said PEND everywhere. |
| **Fix shipped** | `brain_sync_lib_v1.py` hooks · `validate-brain-snapshot-sync-v1.sh` · hub refresh after receipt write |
| **Law** | **Brain PEND on all green rows = snapshot stale — not redo sa-0001.** |
| **Status** | **Canonical · remediated** (recurring if sync skipped) |

---

### INCIDENT-015 — Wrong incident ID (Brain governance mistake)

| Field | Detail |
|-------|--------|
| **ID** | 015 |
| **Severity** | **High** (governance fragmentation) |
| **Body** | `brain-os/incidents/SINA_AGENT_INCIDENT_ID_COLLISION_WITHOUT_REGISTRY_CHECK_INCIDENT_015_LOCKED_v1.md` |
| **What happened** | After INCIDENT-014 trust event, agent logged `INCIDENT-011-brain-column-display-drift` in jsonl. **INCIDENT-011** already = REWRITE unauthorized disk edit (P0). |
| **Root cause** | Skipped registry read · invented id in chat · **Brain role violation** (same arc as critic-as-law). |
| **Fix** | Canonical **014** for monitor subject · **015** for filing mistake · void jsonl line |
| **Law** | `rg INCIDENT-NNN` + registry **before** any new id. |
| **Status** | **Canonical · remediated** |

---

### INCIDENT-026 (A) — Brain chat validator recursion & blocking

| Field | Detail |
|-------|--------|
| **ID** | 026 (registry primary) |
| **Date** | 2026-06-10 |
| **Severity** | **P0** |
| **Body** | `brain-os/incidents/SINA_BRAIN_CHAT_VALIDATOR_RECURSION_INCIDENT_026_LOCKED_v1.md` |
| **What happened** | Brain chat **silent 15–25+ min**: chained `cross-plan && closeout && hub_refresh`; re-ran **~138s** E2E pipeline **6+ times** after receipts logged; long `Await` on subprocess trees. |
| **Root cause** | **Agent conduct** — not infrastructure. Violated `BRAIN_UNIFIED_RULES` <30s reply · `BRAIN_NO_FULL_E2E` max 90s shell. |
| **Fix shipped** | Receipt-only closeout · `cross-plan --fast` · `brain_session_guard_v1.py` · `validate-closeout-receipt-only-v1.sh` · `000-brain-unified.mdc` |
| **Law** | Brain: implement → receipt → reply **<30s** → STOP. **Never** chain validators in Brain chat. |
| **Status** | **Remediated 2026-06-10** |

---

### INCIDENT-026 (B) — Brain E2E retry storm (30 min marathon)

| Field | Detail |
|-------|--------|
| **ID** | 026 (separate body — same number, different subject) |
| **Date** | 2026-06-11 |
| **Severity** | **P0** (conduct + rule collision) |
| **Body** | `brain-os/incidents/SINA_BRAIN_E2E_RETRY_STORM_INCIDENT_026_LOCKED_v1.md` |
| **Note** | Registry row 026 = validator recursion (A). E2E storm filed same id in body — **use subject title to disambiguate**. |
| **What happened** | Founder asked “check e2e” → Brain ran fast ladder **6×** (~25–30 min) while factory **not idle** (INBOX / ACT head). Legal DENIED each time; agent retried anyway. |
| **Root cause** | `brain_intent_gate` mapped “check e2e” → empty allow list · guard allowed fast ladder while forbidding full E2E · SSOT drift loop (014 class) · **6 retries without idle gate** |
| **Fix shipped** | `factory_idle_gate_v1.py` · `validate-e2e-fast-ladder-v1.sh --require-idle` · `E2E_EXECUTOR_CHECKLIST_LOCKED_v1.md` · `BRAIN_RULE_COLLISION_MATRIX_LOCKED_v1.md` · max **ONE** ladder per turn |
| **Law** | Preflight + fcb FAST only if not idle → hand off Worker inbox. **Never** marathon in Brain chat. |
| **Status** | **Remediated 2026-06-11** |

---

## 3. Brain-touching incidents (must know)

| ID | Title | Brain relevance | Status |
|----|-------|-----------------|--------|
| **002c** | Context / memory / closeout | Brain must not rely on chat memory | Canonical |
| **002d** | Healthy drain feasibility | Brain must not inject infeasible ACT | Canonical |
| **003a** | Goal 1 unvalidated proof | Brain must not claim proof without broker | Canonical |
| **005a** | Maintainer EXTERNAL_CRITIC | Brain classifies critic — never reorder | Canonical |
| **013** | Stale goal_progress parrot | Brain/Worker must not parrot inject | Canonical |
| **019** | Founder bash communication | Brain never asks Terminal | Canonical |
| **020** | Topic conflation | Brain must not merge subjects | Canonical |
| **022** | Maintainer stale AUTO-RUN | Hub hero misled founder — Brain must cite disk | Remediated |
| **027** | Drain/projection staleness | Hub hero ≠ ENFORCEMENT after form v2 — Brain separates namespaces | **Open** |
| **028** | Stale prompt-feed advice | Worker parroted dead 024 law | Remediated |

---

## 4. Pattern table (recurring Brain failure modes)

| Pattern | Incidents | Prevention |
|---------|-----------|------------|
| **Wrong lane** | 003b | `brain_lane_guard.py` |
| **Law not enforced** | 004 | `GOAL_HIERARCHY` session gate |
| **UI vocabulary lie** | 014, 027 | Monitor honesty · JSON before projection |
| **Governance id invention** | 015 | Registry-first filing |
| **Validator marathon** | 026A, 026B | <30s reply · receipt-only · `--require-idle` |
| **Critic as law** | 005a | EXTERNAL_CRITIC classify first line |
| **Megachat before Maintainer bridge** | Near-miss 2026-06-12 | Read **039** before search |
| **Duplicate bridge doc** | Near-miss 2026-06-12 | One canonical bridge only |

---

## 5. Guards & laws shipped (Brain stack)

| Guard / law | Path |
|-------------|------|
| Brain unified rules | `os/chat-handoffs/BRAIN_UNIFIED_RULES_LOCKED_v1.md` · `.cursor/rules/000-brain-unified.mdc` |
| No full E2E in Brain | `BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md` |
| Narrate not execute | `validate-brain-narrate-not-execute-v1.sh` |
| Session guard | `scripts/brain_session_guard_v1.py` |
| Lane guard | `scripts/brain_lane_guard.py` |
| Idle gate | `scripts/factory_idle_gate_v1.py` |
| E2E checklist | `~/.sina/brain/E2E_EXECUTOR_CHECKLIST_LOCKED_v1.md` |
| Founder advisor shape | `brain-os/contract/FOUNDER_ADVISOR_PROFILE_LOCKED_v1.md` |
| Execution authority | `brain-os/system/EXECUTION_AUTHORITY_MAP_LOCKED_v1.md` |
| Brain job titles | `SINA_BRAIN_JOB_TITLES_*_LOCKED_v1.md` (73 DO · 10 NOT) |
| Lost link recovery | `SOURCEA_LOST_LINK_RECOVERY_ETHICS_LOCKED_v1.md` |

---

## 6. Near-miss & session 2026-06-12 (not all filed as INCIDENT-NNN)

| Event | Class | Detail | Action |
|-------|-------|--------|--------|
| **Bridge read order violation** | LOST_LINK | Brain created duplicate bridge instead of reading Maintainer **039** first | 039 canonical · pointer superseded |
| **validate-brain-narrate FAIL** | Machine gap | `goal1_auto_loop_v1.py` missing `refuse_if_narrate_lock` | AR-8c99a93765 Maintainer |
| **Goal-1 orphan pid** | Ops | Stale batch left running — blocked narrate validator test | Kill pid · Maintainer fix |
| **HEAL-2026-06-12-001..005** | Self-heal | Copy audit · Thunderfield · specialist merge · job titles · batch PICK | `agent-governance-events.jsonl` |

**Recommendation:** File **INCIDENT-029** only if narrate-lock gap recurs after Maintainer fix.

---

## 7. Brain incident chronology (quick)

```text
2026-06-07  003b lane cross · 002d feasibility
2026-06-08  004 hierarchy disobedience
2026-06-10  014 monitor Brain PEND · 015 wrong id · 026A validator marathon
2026-06-11  026B E2E retry storm · INTEGRITY PACK 5 · Maintainer 1 EOS
2026-06-12  LOST_LINK bridge · job titles lock · PACK5 batch PICK · Phase 3 resume
```

---

## 8. Verify commands (Brain-safe)

```bash
cd ~/Desktop/SourceA
bash scripts/validate-brain-narrate-not-execute-v1.sh
bash scripts/validate-brain-snapshot-sync-v1.sh
python3 scripts/brain_session_guard_v1.py --write --json
python3 scripts/factory_idle_gate_v1.py --json
bash scripts/validate-closeout-receipt-only-v1.sh
rg 'INCIDENT-' brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md
```

**Forbidden in Brain chat for verify:** full E2E ladder without `--require-idle` · chained `&&` validators · Goal-1 drain.

---

## 9. Full body index (Brain-related files)

| Path | ID / role |
|------|-----------|
| `SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md` | 003b |
| `SINA_GOAL_HIERARCHY_ENFORCEMENT_INCIDENT_LOCKED_v1.md` | 004 |
| `SINA_MONITOR_BRAIN_COLUMN_SNAPSHOT_DRIFT_INCIDENT_014_LOCKED_v1.md` | 014 |
| `SINA_BRAIN_REPAIR_INCIDENT_014_COMPLETION_ADJUNCT_LOCKED_v1.md` | 014 adjunct |
| `SINA_AGENT_INCIDENT_ID_COLLISION_WITHOUT_REGISTRY_CHECK_INCIDENT_015_LOCKED_v1.md` | 015 |
| `SINA_BRAIN_CHAT_VALIDATOR_RECURSION_INCIDENT_026_LOCKED_v1.md` | 026A |
| `SINA_BRAIN_E2E_RETRY_STORM_INCIDENT_026_LOCKED_v1.md` | 026B |
| `SINA_MAINTAINER_2_DRAIN_PROJECTION_STALENESS_INCIDENT_027_LOCKED_v1.md` | 027 (projection) |
| `CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md` | 002c |

---

## 10. ASF-facing one-liner per incident

| ID | Tell founder |
|----|--------------|
| 003b | “Worker prompt in Brain — refused; open Worker chat.” |
| 004 | “Commercial is parallel only — WTM/factory is default; I won’t ask you to pick.” |
| 014 | “Brain PEND on green rows = snapshot stale — your work is not undone.” |
| 015 | “I won’t invent incident numbers — registry first.” |
| 026A | “I won’t chain validators in chat — receipt + 30s reply.” |
| 026B | “I won’t marathon E2E — one idle check, then Worker if busy.” |
| 027 | “Hub hero may lag — disk JSON is P0 story.” |

---

*End SINA_BRAIN_INCIDENTS_FULL_SUMMARY_LOCKED_v1 — agents: registry wins · Brain narrates · Worker builds.*
