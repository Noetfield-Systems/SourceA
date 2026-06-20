---
agent_tag: sourcea-executor
agent_display: "[EXECUTOR]"
authored_at: "2026-06-14"
doc_id: agent-law-wire-audit-report-2026-06-14
---

# Agent law-wire audit — full report (LOCKED v1)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Trigger:** ASF — “lock law but don’t wire everywhere”  
**Check cart (duty):** `~/.sina/agent-law-wire-checkcart-v1.json`  
**Law:** `SOURCEA_INCIDENT_FIX_OWNERSHIP_GOVERNANCE_HARDENING_LOCKED_v1.md` · `GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md`

---

## 1. Verdict (honest)

**You are correct.** Validators can PASS while agents stay confused because **locked law ≠ wired surfaces**. We repeatedly:

1. Lock or fix **one file** (Brain receipt, `.mdc` rule, new script)
2. Skip **SOURCEA-PRIORITY**, **ACTIVE_NOW**, **hub projection**, **queue cursor**, **INBOX meta**
3. Leave **FREEZE** copy on surfaces after ASF **cleared resume**

That is **executor/Maintainer wiring failure**, not Brain “being sick” alone.

---

## 2. Live surface divergence (snapshot 2026-06-14 ~12:45 UTC)

| Surface | factory_mode | queue | FREEZE signal | Match? |
|---------|--------------|-------|---------------|--------|
| `factory-now-v1.json` | SINGLE_SA | sa-0512 | kill=false | **SSOT** |
| `founder-resume-drain` | — | — | ACTIVE (cleared FREEZE) | **SSOT** |
| `run-inbox-disk-truth` | SINGLE_SA | sa-0512 verify | freeze=false | **role drift** (verify vs check) |
| `brain-goal1-validation` | — | sa-0512 check | INBOX pending | **partial** |
| `ACTIVE_NOW.md` | — | sa-0512 | “kill flag OFF” but sprint “Paused” | **stale tone** |
| `SOURCEA-PRIORITY.md` | **FREEZE** | **sa-0779** | yes | **FAIL — 241 sa behind** |
| Hub `command-data` | **FREEZE default** | stale pick | yes | **FAIL — Maintainer** |
| `SOURCEA-PRIORITY` honest_done | **597** | — | — | **FAIL — live 838** |

**Root cause class:** `WIRE_INCOMPLETE` — anti-staleness bundle does not yet gate SOURCEA-PRIORITY machine table or hub command-data freeze default.

---

## 3. Incidents (relevant)

| ID | Title | Wiring gap |
|----|-------|------------|
| **INCIDENT-015** | Agent ignored STOP · resumed drain | factory-now vs stop receipt not single writer |
| **INCIDENT-022** | Stale AUTO-RUN advice under FREEZE | Brain/hub not reading factory-now line |
| **INCIDENT-027** | Maintainer drain projection staleness | hub command-data ≠ disk |
| **INCIDENT-028** | Sina Command archived · chat still steers hub | partial `.mdc` wire · hub copy lag |
| **INCIDENT-030** (law) | Fake progress / ownership | stairlift exists · not run on every lock |

---

## 4. Near-misses (this session — not yet filed)

| # | What happened | Should have wired |
|---|---------------|-------------------|
| NM-1 | Hospital false-FAIL H7b | hospital receipt ≠ find_critical last-run |
| NM-2 | Queue jumped pos 1→30 via `worker_factory_heal` | phase_strict cursor SSOT (fixed today) |
| NM-3 | Brain said sa-0511 done while cursor sa-0502 | queue_ssot_unify (shipped today) |
| NM-4 | INBOX 7,400-char paste | slim prompt mode (shipped today) |
| NM-5 | Resume cleared FREEZE · SOURCEA-PRIORITY still FREEZE | priority sync (shipped today) |
| NM-6 | `run-inbox truth_match: false` | inbox meta heal on every unify |
| NM-7 | `auto-run-disabled-v1.flag` absent intermittently | factory gate + ACTIVE_NOW blocker |
| NM-8 | Brain `worker_report` stale sa-0511 | brain_validate drop stale report (shipped) |

---

## 5. Executor mistakes (this agent — do not repeat)

1. **Declared Brain “healthy”** while SOURCEA-PRIORITY still said FREEZE + sa-0779  
2. **Shipped law docs** (hub deactivate, stale sweep) without same-turn priority/hub/cascade wire  
3. **Ran heal scripts** that advanced queue without verifying phase_strict cursor  
4. **Gave one 4-upgrade Maintainer megaprompt** instead of stairlift checklist  
5. **Trusted validate-anti-staleness PASS** as “everything wired” — it does not scan SOURCEA-PRIORITY table or hub JSON freeze defaults  

---

## 6. What “wire everything” means (11-step check cart)

**Disk:** `~/.sina/agent-law-wire-checkcart-v1.json`

Every lock / ASF order / incident close → run **W1–W10** (W11 Maintainer hub):

| Step | Surface |
|------|---------|
| W1 | Authority index |
| W2 | Stairlift payload |
| W3 | Founder input cascade |
| W4 | factory-now |
| W5 | ACTIVE_NOW |
| W6 | SOURCEA-PRIORITY machine truth |
| W7 | queue_ssot_unify |
| W8 | brain-goal1-validation |
| W9 | session gate + mirror |
| W10 | anti-staleness bundle |
| W11 | hub command-data (Maintainer) |

**Forbidden closeout:** “Law locked” without W6 + W7 + W8 PASS on same disk snapshot.

---

## 7. Fixes shipped this turn

| Fix | Path |
|-----|------|
| Queue SSOT unifier | `scripts/queue_ssot_unify_v1.py` |
| Priority machine truth sync | `scripts/sync_sourcea_priority_machine_truth_v1.py` |
| Wired into factory rebuild | `scripts/factory_control_v1.py` |
| Phase-strict heal guard | `worker_factory_heal_v1.py` · `healthy_queue_ssot_lib.py` |
| Slim Worker INBOX | `healthy_prompt_turn_v1.py` |
| Brain concrete founder_line | `brain_validate_goal1_v1.py` |
| Check cart | `~/.sina/agent-law-wire-checkcart-v1.json` |

---

## 8. Still open (P0 wire backlog)

| # | Item | Owner |
|---|------|-------|
| P0-1 | Hub `command-data` FREEZE when factory SINGLE_SA + resume | **Maintainer** (SinaaiDataBase) |
| P0-2 | Validator: `validate-sourcea-priority-fresh-v1.sh` in anti-staleness bundle | Maintainer |
| P0-3 | `ACTIVE_NOW` founder_mode stuck `founder_absent` when ASF chatting | cascade / active_now_v1 |
| P0-4 | Prompt pack sa-* still say “hub Refresh” in pre-flight | registry prompt regen |
| P0-5 | `run-inbox` role verify vs queue check — deliver path | run_inbox ensure_inbox |

---

## 9. One-line truth for founder now

**Factory is NOT FREEZE logged** (SINGLE_SA · resume until ~13:15 UTC · sa-0512).  
**Brain/hub/PRIORITY were lying** because we did not wire the same snapshot everywhere.

**You:** Worker chat → **RUN INBOX** (one word).  
**Us:** Run check cart W1–W10 after every law change.

---

*End report · check cart is duty SSOT — never skip W6–W8*
