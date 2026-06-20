# Product factory — re-score (no ads / low SEO) — LOCKED

| | |
|--|--|
| **Version** | `PRODUCT-FACTORY-RESCORE-1.0-LOCKED` |
| **Locked** | 2026-06-04 |
| **Supersedes** | MergePack as **factory P0 winner** only — **does not** ban MergePack SEO, paid search, or 7-day $10K blitz |
| **Weights** | Distribution w/o ads·SEO **40%** · Rivalry **30%** · MVP stack fit **20%** · Revenue **10%** |

**Rivalry scale:** 10 = few weak rivals · 1 = SEO/ad war (MergePack).

---

## Top 15 (weighted score)

| Rank | # | Idea | Dist | Riv | MVP | Rev | **Wtd** |
|------|---|------|------|-----|-----|-----|---------|
| 1 | 1 | **RunReceipt** | 9 | 7 | 10 | 6 | **8.3** |
| 2 | 29 | **TranscriptYAML** | 8 | 8 | 10 | 5 | **8.0** |
| 3 | 30 | **SmokeRemote** | 8 | 8 | 9 | 5 | **7.9** |
| 4 | 8 | **FormToPDF** | 8 | 6 | 8 | 9 | **7.7** |
| 5 | 2 | ApproveSend | 7 | 6 | 7 | 8 | **7.0** |
| 6 | 3 | TaskProof | 7 | 7 | 8 | 6 | **7.1** |
| 7 | 19 | SiteClose | 7 | 6 | 7 | 7 | **6.9** |
| 8 | 11 | VendorOnboard | 7 | 6 | 7 | 7 | **6.9** |
| 9 | 12 | ChaseInvoice | 6 | 5 | 7 | 8 | **6.4** |
| 10 | 10 | WeekOps | 6 | 6 | 8 | 6 | **6.4** |
| 11 | 7 | RedactLite | 5 | 6 | 6 | 7 | **6.0** |
| 12 | 14 | HandoffNote | 5 | 4 | 8 | 5 | **5.7** |
| 13 | 9 | SignPrep | 5 | 5 | 7 | 6 | **5.8** |
| 14 | 26 | CSVDoctor | 4 | 2 | 9 | 6 | **5.0** |
| 15 | 6 | **MergePack** | 3 | 1 | 10 | 9 | **5.2** |

*Ideas 13–28 not in top 15 mostly score ≤6.0 (ClipMap, RepurposeQ, RFP skim, ClauseDiff, IntakeSum, etc.) — distribution or rivalry or HIPAA drag.*

---

## Primary build (LOCKED recommendation)

| Role | SKU | Why |
|------|-----|-----|
| **P0 PRIMARY** | **RunReceipt** (#1) | Dogfoods your **M8 / wire / PASS-FAIL** story; sells to same buyers; community distribution (Cursor, GitHub, agencies) |
| **P0 feature fold-in** | TranscriptYAML (#29) | v1 = export tab on RunReceipt, not separate brand |
| **P0 feature fold-in** | SmokeRemote (#30) | v1.1 = optional “trigger smoke” action; reuses DevBridge phone lane |
| **P1 parallel cash** | **FormToPDF** (#8) | Only non-dev top pick; **one vertical** (e.g. cleaning/landscape quote PDF), not national SEO |
| **Lower rank for factory P0** | MergePack (#6) | Lost **factory P0** on no-ads *scoring* only — **SEO/paid/10K plans remain valid** for MergePack when ASF runs them |

---

## RunReceipt — 7-day MVP (no ads)

| Day | Deliverable |
|-----|-------------|
| 1 | Schema: `run.jsonl` + `summary.json` + PASS/FAIL from existing wire scripts |
| 2 | CLI: `run-receipt pack ./artifacts` → zip + HTML report |
| 3 | Landing: one page, 3 screenshots, pricing |
| 4 | Stripe $19/mo team · $5/run pack |
| 5 | Post: r/cursor, Indie Hackers, “CI receipt for agent runs” |
| 6 | GitHub Action example (read-only artifact upload) |
| 7 | 3 design-partner calls from DMs |

**Not in v1:** LLM judge, multi-cloud, enterprise SSO.

---

## FormToPDF — if you need non-dev revenue in parallel

- **One vertical landing** + Facebook group outreach only  
- **No** “invoice generator” head term SEO  
- 7-day plan unchanged from `PHASE2_3_EVALUATION_AND_WINNER.md` § Winner 2  

---

## Session line for agents

`Active thread: THREAD-FACTORY P0 RunReceipt. No MergePack SEO. Read PRODUCT_FACTORY_RESCORE_NO_ADS_LOCKED_v1.md`

---

**LOCKED.** Change P0 SKU → `PRODUCT-FACTORY-RESCORE-2.0` + ASF.
