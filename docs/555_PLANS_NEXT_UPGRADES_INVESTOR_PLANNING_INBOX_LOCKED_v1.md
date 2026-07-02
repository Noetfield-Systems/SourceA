# 555 Plans — Immediate Next Upgrades (Investor Planning Inbox)

**Saved:** 2026-07-01T10:33:29Z  
**Version:** 1.2 — LOCKED  
**route_id:** `locked_product_spec_doc`  
**sequence_id:** SA-2026-07-01-555-PLANS-INVESTOR-INBOX  
**Parent database:** `docs/CANADA_ICP_GRANT_VC_EVIDENCE_Q3_2026_INVESTOR_PLANNING_DATABASE_LOCKED_v1.md` (v1.1)  
**Machine inbox:** `data/investor-planning-555-inbox-v1.json`  
**555 immediate queue:** `docs/555_PLANS_NEXT_UPGRADES_INVESTOR_PLANNING_INBOX_LOCKED_v1.md`  
**Law:** One plan per turn · verification built in · bump matrix after each DONE

---

## Inbox law

| Rule | Detail |
|------|--------|
| Queue | 555-01 → 555-05 sequential — no skip |
| Execute | Worker/cloud runs ACT on head only |
| Done | Receipt path + matrix row update + inbox `status: done` |
| Forbidden | Batch all five · fake green without logs |

---

## Queue (5 immediate plans)

| ID | Title | Unblocks | Owner | Status |
|----|-------|----------|-------|--------|
| **555-01** | IRAP/SR&ED investor proof bundle logged | ANG-07 · SRED-04/05 · IRAP §15 | Worker | **DONE** — see receipt |
| **555-02** | SR&ED experiment log + hypothesis register (dated) | SRED-04 · SRED-05 · grant narrative | Worker | **DONE** — see receipt |
| **555-03** | Redacted receipt JSON + data-room `02 Technical/` folder | ANG-09 · angel DD | Worker | **queue head** |
| **555-04** | W1 demo transcript + filmed-run checklist | ANG-05 · ANG-10 · W1 | Founder+Worker | pending |
| **555-05** | Ocree send pack — champion fields + locked email attach list | ANG-18 · W3 · TRD-03 | Commercial | pending |

---

## 555-01 — IRAP/SR&ED investor proof bundle (EXECUTED)

**Intent:** Capture reproducible validator PASS logs + manifest for grant/IRAP/angel evidence — no founder narration required.

**Actions:**
1. Run four enforcement validators → tee logs
2. Copy latest demo receipt (redacted fields)
3. Write `MANIFEST.json` + `README.md` in bundle dir
4. Mark inbox head done

**Proof path:** `receipts/investor-planning-proof-bundle-2026-07-01/`

**Matrix updates:** ANG-07 → `[x]` · SRED-04 scaffold → `[~]`

**Verify:**
```bash
test -f receipts/investor-planning-proof-bundle-2026-07-01/MANIFEST.json
grep -q '"ok": true' receipts/investor-planning-proof-bundle-2026-07-01/MANIFEST.json
```

---

## 555-02 — SR&ED experiment log + hypothesis register

**Intent:** Contemporaneous grant records — CRA/IRAP audit spine.

**Actions:**
1. Create `receipts/sred-experiment-log-2026/` with `MANIFEST.json`
2. Append dated entries for H1 (partial PASS) and H3 (PASS) from IRAP doc
3. Link R&D-01..05 project IDs in `HYPOTHESIS_REGISTER.md`
4. Update matrix SRED-04, SRED-05 → `[x]` or `[~]`

**Acceptance:** ≥2 dated experiment entries with command + stdout hash reference.

**Scope:** docs + receipts only — no new product code.

---

## 555-02 — SR&ED experiment log (EXECUTED)

**Proof path:** `receipts/sred-experiment-log-2026/`

| Artifact | Purpose |
|----------|---------|
| `MANIFEST.json` | Machine index |
| `EXPERIMENT_LOG.md` | EXP-001..003 dated entries (H1 partial, H3 PASS) |
| `HYPOTHESIS_REGISTER.md` | R&D-01..05 ↔ H1..H5 map |

**Matrix updates:** SRED-04 → `[x]` · SRED-05 → `[x]` · R&D-01/02 → `[~]`

**Verify:**
```bash
test -f receipts/sred-experiment-log-2026/MANIFEST.json
grep -q 'EXP-003' receipts/sred-experiment-log-2026/EXPERIMENT_LOG.md
```

---

## 555-03 — Redacted receipt JSON + data-room technical folder

**Intent:** Angel associate opens one folder without calling founder.

**Actions:**
1. Create `investor/data-room-v1/02-Technical/` scaffold
2. Redact PII from `latest-demo-receipt.json` → `receipt-sample-redacted-v1.json`
3. Add `PROOF_COMMANDS.md` (copy from 555-01 bundle)
4. Update matrix ANG-09 packaging → `[x]`

**Acceptance:** Folder contains redacted JSON + validator log copies + one-line honest counter.

---

## 555-04 — W1 demo transcript + film checklist

**Intent:** Pre-film package so recording is one take — not discovery on camera.

**Actions:**
1. Run `bash scripts/demo-enforcement-5min-v1.sh` → capture stdout transcript
2. Write `investor/W1_FILM_CHECKLIST_LOCKED_v1.md` (beats: BLOCK · ALLOW · tamper · receipt)
3. List equipment/framing — 90s cut markers for ANG-10
4. Matrix ANG-05 → `[~]` until video file exists

**Acceptance:** Transcript logged + checklist locked — video optional same turn.

---

## 555-05 — Ocree send pack (W3 champion prep)

**Intent:** Close gap between APPROVED and sent — TrustField Priority A.

**Actions:**
1. Extract Ocree block from `os/commercial/CANADA_PRIORITY_A_SEND_READY_EMAILS_LOCKED_v1.md`
2. Create `os/commercial/send-packs/OCREE_TF001_SEND_PACK_v1.md` with champion fill-ins
3. Attach list: TF-P1-DP one-pager path · demo link placeholder · CASL footer
4. Log CRM row template in pack — matrix ANG-18 → `[~]`

**Acceptance:** Send pack ready — founder fills champion name + relationship basis only.

**Forbidden:** Send without champion · claim MSB license · mix Noetfield brand.

---

## Cross-reference index

| Doc | Path |
|-----|------|
| Investor planning database | `docs/CANADA_ICP_GRANT_VC_EVIDENCE_Q3_2026_INVESTOR_PLANNING_DATABASE_LOCKED_v1.md` |
| Entity matrix | `docs/ENTITY_EVIDENCE_MATRIX_SOURCEA_TRUSTFIELD_NOETFIELD_CANADA_GRANT_ANGEL_V_LOCKED_v1.md` |
| IRAP narrative | `docs/IRAP_TECHNICAL_NARRATIVE_ENFORCEMENT_KERNEL_UNCERTAINTY_DRAFT_LOCKED_v1.md` |
| Inbox machine | `data/investor-planning-555-inbox-v1.json` |

---

*Locked 555 queue. Bump `Saved:` UTC when queue changes.*
