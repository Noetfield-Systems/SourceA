# ENFORCEMENT-6MO — 30-day backlog (REGISTRY-ready slices)

**Law:** `brain-os/law/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md`  
**Track ID:** `DEMO-ENF-COPILOT-2026-06-11`  
**Note:** Slices use `DEMO-ENF-S*` IDs — separate from locked `sa-1000` pack slots. Brain may crosswalk to `sa-*` when assigning Worker turns.

---

## Win condition reminder

| ID | PASS by |
|----|---------|
| W1 | 5-min filmed demo — BLOCK / ALLOW / tamper FAIL |
| W2 | Demo writes only via commit path + validator |
| W3 | TF-001 or NF-001 deposit / LOI (CAD ≥2K) |

---

## Slice registry

| Slice ID | Title | Owner | Days | Status | Done when |
|----------|-------|-------|------|--------|-----------|
| **DEMO-ENF-S1** | Policy + intent fixtures (P-001) | Worker | 1–3 | **done** | `governance_demo_policy_v1.json` + intents logged |
| **DEMO-ENF-S2** | Demo gate + BLOCK path | Worker | 4–6 | **done** | `--case block` exits ≠ 0 |
| **DEMO-ENF-S3** | ALLOW + receipt + spine | Worker | 7–10 | **done** | `--case allow` + `spine_event_id` |
| **DEMO-ENF-S4** | Append-only receipt log | Worker | 11–13 | **done** | `receipt-log.jsonl` append-only |
| **DEMO-ENF-S5** | Tamper validator | Worker | 14–16 | **done** | `validate-demo-enforcement-v1.sh` PASS + tamper |
| **DEMO-ENF-S6** | Runbook + dry-run witness | Worker/Maintainer | 17–20 | **done** | `INVESTOR_DEMO_RUNBOOK_v1.md` + internal dry-run |
| **DEMO-ENF-S7** | Film W1 (2 takes max) | ASF + executor | 21–25 | **take1_witness** | Take 1 witness PASS · ASF screen file pending |
| **DEMO-ENF-S8** | Hub “Run governance demo” Action | Maintainer | 26–30 | open | One-tap `demo-enforcement-5min-v1.sh` |
| **DEMO-ENF-S9** | Bypass inventory validator | Worker | 21–30 | open | Scan spawn-without-gate → FAIL |
| **DEMO-ENF-W3** | TF/NF money conversation | ASF + Commercial | 1–30 | open | LOI / deposit / SOW |

**Maintainer parallel (non-blocking):** FR-003 → Phase 1.10 seal.

---

## Week-by-week

### Week 1 (Jun 11–17)

| Day | Engineering | Commercial (ASF) |
|-----|-------------|------------------|
| 1–2 | S1–S3 verify + closeout receipts | Pick wedge: NF Copilot vs TF RPAA |
| 3–5 | S5 tamper hardening if flaky | 3 discovery calls scheduled |
| 5 | Internal dry-run `demo-enforcement-5min-v1.sh` | Send 3-slide deck link |

### Week 2 (Jun 18–24)

| Day | Engineering | Commercial |
|-----|-------------|------------|
| 1–3 | S6 runbook polish | Outreach batch 1 (5 targets) |
| 4–5 | S7 film take 1 | Follow-up with demo link |
| 5 | `validate-demo-enforcement-v1.sh` in CI habit | Log pipeline in CRM |

### Week 3–4 (Jun 25 – Jul 8)

| Focus | Exit |
|-------|------|
| S8 Hub Action (Maintainer) | Founder one-tap demo |
| S9 bypass scan (Worker) | Honest bypass list updated |
| W3 | LOI draft or deposit path |

---

## Worker prompt stubs (paste to Brain)

### DEMO-ENF-S7 — Film W1

```
ENFORCEMENT-6MO — Record investor demo. Run demo-enforcement-5min-v1.sh twice; save logs to archive/attachments/YYYY-MM-DD/. Verify validate-demo-enforcement-v1.sh PASS before and after. No hub rewrite.
```

### DEMO-ENF-S8 — Hub Action (Maintainer)

```
Wire Hub Action "Run governance demo (5-min)" → bash scripts/demo-enforcement-5min-v1.sh. Founder one-tap only. Do not edit command-data hero copy in same slice unless FR-003 complete.
```

### DEMO-ENF-S9 — Bypass inventory

```
Add scripts/validate-demo-bypass-inventory-v1.sh — FAIL if known Worker spawn paths skip commit_intent_v1/gatekeeper. Document in DEMO_BYPASS_AUDIT_v1.md. Demo scope first.
```

---

## sa-* crosswalk (optional Brain assign)

| Slice | Suggested factory sa | Lane |
|-------|---------------------|------|
| S7 film | `sa-0802` (if free) or new VERIFY receipt | Worker |
| S8 Hub | Maintainer slice — not sa pack | Maintainer |
| S9 bypass | `sa-0803` | Worker |
| W3 | Commercial — no sa | ASF |

*Do not overwrite locked `sa-0800` titles in REGISTRY.json without Brain.*

---

## Acceptance (30-day)

| # | Check |
|---|-------|
| 1 | `bash scripts/validate-demo-enforcement-v1.sh` green |
| 2 | Recording exists OR live demo rehearsed 3× |
| 3 | ≥3 TF/NF conversations logged |
| 4 | 1 LOI draft or deposit invoice sent |
| 5 | Bypass audit doc updated |
