# MergePack — Post-moat strategy PATH A (LOCKED)

| | |
|--|--|
| **Version** | `MERGEPACK-PATH-A-1.0-LOCKED` |
| **Locked** | 2026-06-04 |
| **ASF choice** | Path **1** — cash extraction + light Organize Pro |
| **Parent** | `MERGEPACK_LOCKED_v1.md` · `MERGEPACK_SEO_10K_LOCKED_v1.md` |
| **Strategic truth** | **No product moat** — **distribution / intent window** only |

---

## Lock statement

MergePack is **not** positioned to defeat Claude/NotebookLM on capability. It is positioned to **capture merge-PDF search intent** and convert to **file + payment** before platform consolidation.

**Not in PATH A:** Document OS (Path C), early pivot to FormToPDF (Path B) unless **risk gates** fire below.

---

## What we say (copy)

| Say | Do not say |
|-----|------------|
| Combine PDFs in your order — one download | Smart merge / better than Claude |
| Fast, no install, clear limits | AI moat / we understand your docs |
| Organize Pro (when live): sort pack → merge | Replace NotebookLM |

---

## Execution stack (unchanged)

- **v1.1:** concat merge, 3/day IP, Railway API, Vercel UI, Stripe, 5 SEO pages (Days 4–7)
- **Vault:** `~/.sina/mergepack.env`
- **API live:** `https://mergepack-api-production.up.railway.app`

---

## PATH A — Sprint clock (do not confuse)

| Window | What it means |
|--------|----------------|
| **48h / 2 days** | **SHIP** — Vercel UI, Stripe, live merge, minimum SEO → **M1 + soft launch** |
| **Days 3–7** | BUILD_CHECKLIST finish (5 SEO pages, privacy, domain if ready) |
| **Days 8–42** | G2 SEO scale (background; not blocking launch) |
| **Day 30 gate** | 0 payments → fix checkout/trust (hours/days, not months) |
| **Day 7** | **M8 $10K MRR** or pivot B — see `MERGEPACK_10K_7DAY_LOCKED_v1.md` |

ASF intent: **$10K MRR in 7 days** — paid search + 30 SEO pages + Stripe, not organic-only ramp.

---

## PATH A — Phase 1 (first 48h): cash extraction LAUNCH

| Priority | Work |
|----------|------|
| P0 (today–tomorrow) | Day 3 UI test → Day 4 Vercel → Day 5 Stripe → **public URL merges + pays** |
| P0 (48h) | 1 landing + `/health` smoke — **M1 done** |
| P1 (by day 7 max) | 5 SEO pages + sitemap (G1) |
| P2 (week 2+) | More SEO pages per map — **after** live |

**Out of scope first 48h:** heavy AI, accounts, 50 pages, Organize AI.

---

## PATH A — Phase 2: light Organize Pro (upsell)

Ship **only after M1 + M2** (live URL + 1 payment).

| Tier | Features | Price band |
|------|----------|------------|
| **Free** | Upload-order concat, 3/day | $0 |
| **Plus** | Unlimited concat | $9–12/mo |
| **Organize Pro** | Drag reorder, presets (newest/alpha), page counts, optional cover page | +$10/mo or $19 standalone |
| **Organize AI (v2.1)** | Suggested order from filename + first-page snippet | Pro only; token caps |

**No** full-doc chat, **no** NotebookLM-style corpus. Last-mile: **order → merge → download**.

Requires version bump to document in `MERGEPACK-2.0` when build starts (not before M2).

---

## Risk gates (checkpoints — not build duration)

| When | Signal | Action |
|------|--------|--------|
| **Hour 48** | No public Vercel merge | **Stop** — finish Day 4–5 only |
| Day 7 | No Stripe test payment | Fix paywall before more SEO |
| Day 30 | 0 payments, &lt;300 impressions | Fix trust/UX/checkout — **no** new AI |
| **Day 7** | MRR &lt; $3K | **Pivot Path B** — no 30/90d extension |

---

## Moat language (internal)

| Term | Meaning |
|------|---------|
| Moat | **Do not claim** for MergePack v1 |
| Window | SEO intent + speed-to-file + timing vs AI platforms |
| Upsell | Organize Pro = workflow lock-in, not LLM superiority |

---

## References

- Build days: `~/Desktop/mergepack/BUILD_CHECKLIST.md`
- Incident / deploy: `~/Desktop/mergepack/docs/INCIDENT_2026-06-03_AGENT_PLACEHOLDER_DEPLOY.md`
- Defense (honest): `MERGEPACK_BUSINESS_DEFENSE_MEMO.md`

**LOCKED — Path A until ASF publishes PATH B or `MERGEPACK_CANCELLED`.**
