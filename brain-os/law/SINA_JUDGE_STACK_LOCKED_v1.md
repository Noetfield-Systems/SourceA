# Sina Judge Stack — LOCKED v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**trace_id:** `JUDGE-STACK-LOCKED-2026-06-12`  
**sequence_id:** SA-2026-06-12-JUDGE-STACK-LOCKED  
**Status:** **LOCKED** — `Q-JUDGE-STACK-v1` PICK **A** 2026-06-12  
**Form fork:** `Q-JUDGE-STACK-v1` · receipt `SOURCEA_PACK5_ROOMS_PICK_BATCH_2026-06-12_LOCKED_v1.md`  
**Supersedes:** `SINA_JUDGE_STACK_DRAFT_v1.md` (draft retained in archive)  
**Archive mirror:** `archive/attachments/2026-06-12/SINA_JUDGE_STACK_LOCKED_v1.md` (non-canonical copy)  
**Machine:** `scripts/judge_center_*.py` · `~/.sina/judge-center/`  
**Parents:** PACK 5 · `SOURCEA_LIVE_FOUNDER_DECISION_FORM` · INCIDENT-029

---

## 0. One sentence

> **Sina PICK on Form wins all · Disk+validators prove truth · Judge Center (Audit→Lawyer→AI Judge) drafts alarms and remediation onto the Form — chat never wins alone.**

---

## 1. Outer stack (authority — constitution)

| Tier | Judge | Role | 24/7? | Creative? |
|------|-------|------|-------|-----------|
| **1** | **Human (Sina)** | Final PICK · Effect · Confirm on M1 Canvas | No (by design) | Intent |
| **2** | **Disk + Machine** | §ANSWERED · receipts · validator PASS/FAIL · alarm RIGHT/STALE/BAD | Yes | No (enforce only) |
| **3** | **AI Judge Center** | Reason · counsel · remediation prompts → **Form rows only** | Yes (batch) | Yes (bounded) |

**Precedence:** Tier 1 > Tier 2 > Tier 3. Inner AI layers **never** beat disk proof or Form PICK.

---

## 2. Inner stack (SHIPPED v1)

| Layer | Script | Output |
|-------|--------|--------|
| L1 Audit | `judge_center_audit_v1.py` | temporal alarms |
| L2 Counsel | `judge_center_counsel_v1.py` | settlements · KEEP/IGNORE |
| L3 Bench | `judge_center_bench_v1.py` | resolution · form drafts |
| Orchestrator | `judge_center_run_v1.py` | one command |
| Temporal | `judge_center_temporal_v1.py` | PAST vs ACTIVE STALE |

**Spine:** `~/.sina/judge-center/latest-resolution-v1.json`

---

## 3. Alarm tags

| Tag | Meaning |
|-----|---------|
| **TRUSTED / RIGHT** | Matches form §ANSWERED + receipt |
| **PAST_STALE_ONLY** | Archaeology bad · recent window clean |
| **ACTIVE_STALE** | Still wrong today — do not trust |
| **BAD** | INCIDENT class conduct |

---

**END LOCKED** — active law · authority index `JUDGE_CENTER`
