# Permanent Architect Agent — LOCKED

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-02-020  
**Classification:** INTERNAL ONLY  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/SourceA/SINAAI_PERMANENT_ARCHITECT_AGENT_LOCKED_v1.md`  
**Implementation:** `~/Desktop/SinaPromptOS/core/architect/` · `scripts/run-architect.sh`  
**Output:** `~/Desktop/SourceA/ARCHITECT_REPORT.yaml`  
**Locked:** 2026-06-02  
**Maintainer:** ASF

---

## 1. Role (non-negotiable)

| Does | Does not |
|------|----------|
| Read Source A, Prompt OS, truth, plans | Write `plan.json` |
| Compare law vs disk vs runtime | Dispatch Cursor prompts |
| Emit `ARCHITECT_REPORT.yaml` | Ingest logs or publish ecosystem |
| Recommend ASF decisions | Re-rank priority or auto-fix |

**Operating law:** EXEC_PHASE_1 + SA-019. EXEC_PHASE_2 = BUILT_NOT_OPERATIONAL (observe only).

**Phase vocabulary:** GOV_PHASE_* and EXEC_PHASE_* only — never bare "Phase N" in new docs.

---

## 2. Three-layer model

```text
Architect  →  ARCHITECT_REPORT.yaml   (think)
Prompt OS  →  publish, dispatch, ingest (execute)
ASF        →  sign-offs, Sunday plan (decide)
```

---

## 3. Daily schedule (endorsed)

| Order | Command |
|-------|---------|
| 1 (optional 07:00) | `./scripts/run-architect.sh` |
| 2 | ASF reads `ARCHITECT_REPORT.yaml` (high/critical only) |
| 3 | `./scripts/run-full-day.sh` |
| 4 | 5× Cursor + ingest |

Alternative: run architect **after** `run-full-cycle.sh`, **before** Cursor pastes.

---

## 4. Outputs

| File | Writer |
|------|--------|
| `ARCHITECT_REPORT.yaml` | Architect only (overwrite each run) |
| `runtime/architect_reports/YYYY-MM-DD.yaml` | Optional history append |

---

## 5. MVP scope — v0.2 industrial (SA-026)

- **Not** contradiction hunting / registry police
- Output: max **5 system_blockers** + **consolidation_actions** + **execution_route**
- Policy: `SINAAI_ARCHITECT_V2_INDUSTRIAL_POLICY_LOCKED_v1.md`
- Config: `SinaPromptOS/config/architect_rules.yaml`

---

## 6. Lane 0 rule

Before repo work: read `ARCHITECT_REPORT.yaml` — surface **high/critical** findings to ASF only. Do not auto-remediate.

---

## Document control

| Version | seq_id |
|---------|--------|
| 1.0 | SA-2026-06-02-020 |

**ASF sign-off:** __________
