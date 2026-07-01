# SR&ED Hypothesis Register — 2026

**Plan:** 555-02 · **Saved:** 2026-07-01T10:33:29Z  
**Parent:** `docs/IRAP_TECHNICAL_NARRATIVE_ENFORCEMENT_KERNEL_UNCERTAINTY_DRAFT_LOCKED_v1.md` §3  
**Experiment log:** `EXPERIMENT_LOG.md`

---

## Technological uncertainty (T661 spine)

> It is not known whether a single deterministic commit gate can enforce heterogeneous organizational policies across multi-agent workflows in real time, while producing tamper-evident receipts suitable for regulatory examination, at latency acceptable for interactive developer agent sessions (<500ms gate overhead target).

---

## Project ↔ hypothesis map

| Project ID | Project name | Entity | Linked hypotheses | Log entries |
|------------|--------------|--------|-----------------|-------------|
| R&D-01 | Runtime agent enforcement kernel | SourceA | H1, H2 | EXP-001, EXP-003 |
| R&D-02 | Receipt integrity + tamper detection | SourceA | H3 | EXP-002, EXP-003 |
| R&D-03 | Pre-run dispatch gate (eval-1b) | SourceA | H4 | — (open) |
| R&D-04 | Regulated evidence export (Trust Brief) | TrustField | H5 | — (open) |
| R&D-05 | Govern-before-execution (Copilot) | Noetfield | H1 (shared primitive) | — (open) |

---

## Hypothesis status

| ID | Hypothesis | Test method | Criterion | Status | Last run |
|----|------------|-------------|-----------|--------|----------|
| H1 | Single write entrypoint enforces demo-scope commits | `validate-demo-write-path-v1.sh` | Zero bypass in demo scope | **Partial PASS** | 2026-07-01 |
| H2 | Policy eval p95 < 500ms | Latency benchmark | p95 under load | **Open** | — |
| H3 | Checksum detects tampering | `--tamper-test` | HARD FAIL on edit | **PASS** | 2026-07-01 |
| H4 | Eval gate blocks dispatch when eval fails | eval-1b + dispatch | honest false | **Open** | — |
| H5 | External reviewer reproduces from JSON | Blind review | No founder call | **Open** | — |

---

## R&D allocation note (for timesheets — SRED-08)

| Project | Estimated % effort (founder fill) | Evidence logged |
|---------|-----------------------------------|------------------|
| R&D-01 | ___% | commit_intent_v1.py · validators |
| R&D-02 | ___% | tamper suite · receipt schema |
| R&D-03 | ___% | eval gate (pending) |
| R&D-04 | ___% | TrustField commercial (pending) |
| R&D-05 | ___% | Noetfield Copilot (pending) |

---

*Update status column after each experiment run. Link to EXPERIMENT_LOG entry by ID.*
