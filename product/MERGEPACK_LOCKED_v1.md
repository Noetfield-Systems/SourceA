# MergePack — LOCKED build plan v1

| | |
|--|--|
| **Version** | `MERGEPACK-1.1-LOCKED` |
| **Locked** | 2026-06-04 (SEO funnel upgraded same day) |
| **SEO plan** | `MERGEPACK_SEO_10K_LOCKED_v1.md` |
| **North-star MRR** | **$10,000 by Day 7** (`MERGEPACK_10K_7DAY_LOCKED_v1.md`) |
| **Status** | **ACTIVE — build authorized** |
| **Owner** | ASF |
| **Repo** | `~/Desktop/mergepack/` |
| **Defense** | `MERGEPACK_BUSINESS_DEFENSE_MEMO.md` |
| **Post-moat (PATH A)** | `MERGEPACK_POST_MOAT_PATH_A_LOCKED_v1.md` — cash extraction + light Organize Pro |
| **Evaluation** | `PHASE2_3_EVALUATION_AND_WINNER.md` |

---

## Lock statement

MergePack is the **primary utility SKU** from the 30-idea factory. It is **locked** for execution until ASF publishes `MERGEPACK-2.0` or **`MERGEPACK_CANCELLED`**.

**Not in scope for this lock:** Sina Hub, investor portfolio wire, Cursor OS Pro App Store lane, TrustField/Noetfield core platforms.

**Parallel OK:** TrustField/VIRLUX/777 delivery per force majeure — MergePack does not block other repos.

---

## Product (frozen v1)

| Field | Value |
|-------|--------|
| Name | **MergePack** |
| Job | Merge 2–30 PDFs + **FormToPDF** (quote/invoice) — see `MERGEPACK_SUITE_LOCKED_v1.md` |
| User | Admin, freelancer, realtor, ops — deadline-driven |
| Monetization | 3 free merges/day/IP · **$9–12/mo** unlimited · **$2** day pass |
| Distribution | **SEO = product** — see `MERGEPACK_SEO_10K_LOCKED_v1.md` |
| Domain (target) | **mergepdf.app** (or ASF pick) |

---

## Success criteria (measurable)

| Milestone | Done when |
|-----------|-----------|
| **M1 Ship** | Production URL merges 2 PDFs <15s p95 |
| **M2 Pay** | Stripe live — 1 real payment |
| **M3 SEO** | 20 indexed pages, 500 organic impressions/mo |
| **M4** | **$90 MRR** or 10 paying customers (proof of pay) |
| **M6** | **$1,000 MRR** |
| **M7** | **$3,000 MRR** |
| **M8** | **$10,000 MRR** — **Day 7** (blitz) |
| **M5 Decision** | **Day 7 fail** (&lt;$3K MRR) → pivot FormToPDF — **not** Day 90 |

Content map (50 URLs): `~/Desktop/mergepack/SEO_CONTENT_MAP_50.md`

---

## Build phases

### Phase A — MVP (Days 1–7) — LOCKED scope

| Day | Deliverable | Verify |
|-----|-------------|--------|
| 1 | FastAPI `/v1/merge`, pypdf, limits, tests green | `pytest` + manual 5-file merge |
| 2 | Deploy API Railway, `/health`, env limits | curl health |
| 3 | Next.js UI dropzone + download | phone + desktop test |
| 4 | Deploy UI Vercel, custom domain | end-to-end merge |
| 5 | Stripe Checkout day pass + sub | test card payment |
| 6 | Privacy page, max size messaging, error copy | encrypted PDF test |
| 7 | **30 SEO pages** + sitemap + paid search max + **M8 $10K MRR** | G3 hit or pivot |

**In scope:** file-order = upload order, 25MB/file, 30 files max.  
**Out of scope v1:** accounts, per-page reorder, OCR, API, teams.

### Phase B — **Only if M8 hit Day 7** (Days 8+)

- Pages #31–50 · PDF footer · 1h purge · Organize Pro

### ~~Phase C 90-day~~ **CANCELLED** — replaced by `MERGEPACK_10K_7DAY_LOCKED_v1.md`

---

## Stack (locked)

| Layer | Choice |
|-------|--------|
| API | Python 3.12, FastAPI, pypdf, uvicorn |
| Web | Next.js on Vercel |
| Pay | Stripe Checkout + webhook |
| Host API | Railway |
| DB v1 | **None** (IP daily limits in memory) |
| DB v2 | SQLite if multi-device limits needed |

---

## Commands (daily)

```bash
# Dev
cd ~/Desktop/mergepack/backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8090

cd ~/Desktop/mergepack/frontend && npm install && npm run dev
# NEXT_PUBLIC_API_URL=http://127.0.0.1:8090
```

---

## Risk gates (stop / pivot)

| Signal | Action |
|--------|--------|
| **Day 7 MRR &lt; $3K** | Pivot FormToPDF (Path B) |
| Day 5, 0 payments | Fix Stripe/trust before more SEO |
| Day 6, MRR &lt; $500 | Increase paid search + cap CTA |
| Cap-hit &gt;5% but checkout &lt;1% | Pricing/trust copy experiment |

---

## References

- Skeleton: `~/Desktop/mergepack/`
- Defense: `MERGEPACK_BUSINESS_DEFENSE_MEMO.md`
- SEO $10K: `MERGEPACK_SEO_10K_LOCKED_v1.md`
- Alternates (not now): FormToPDF, CSVDoctor — `PHASE2_3_EVALUATION_AND_WINNER.md`

---

**LOCKED — do not expand scope without ASF + version bump.**
