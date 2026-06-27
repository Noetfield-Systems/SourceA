# SourceA site — score analysis v2 (LOCKED)

**Saved at:** 2026-06-25T10:00:00Z  
**Batch-1 pack:** `docs/SOURCEA_SITE_SCORE_UP_1000_PLANS_LOCKED_v1.md` (76→95)  
**Batch-2 pack:** `docs/SOURCEA_SITE_SCORE_UP_1000_BATCH2_LOCKED_v1.md` (78→93)  
**Live check:** 2026-06-25 — pulse dashboard OK · RESEND set · key pages 200

---

## Executive summary

| Metric | Batch-1 baseline | **Current (v2)** | After batch-1 NOW | After batch-2 NOW |
|--------|------------------|------------------|-------------------|-------------------|
| **Overall** | 76 | **78** | ~85 | **~93** |
| vs Cal-first agency | 85 | **86** | 90 | 94 |
| vs Trigger.dev (runs) | 45 | **46** | 65 | 78 |
| vs Vercel (polish) | 50 | **52** | 68 | 82 |
| vs Vanta (trust) | 65 | **66** | 72 | 88 |

**Verdict:** Wiring and vocabulary are **ahead of typical AI agencies**. Self-serve proof execution, enterprise procurement surfaces, and market polish still **trail** top SaaS. Batch-2 closes the **93+** gap with grade-A+ plans that do **not** duplicate batch-1.

---

## Dimension scorecard (v2 · re-measured)

| # | Dimension | v1 | **v2 now** | Gap to 93 | Batch-1 owns | Batch-2 owns |
|---|-----------|-----|------------|-----------|--------------|--------------|
| 1 | Live wiring | 88 | **90** | +3 | routes · workers · CORS | health · SLA · degrade |
| 2 | Client UI | 72 | **73** | +20 | hero CTA · FAB · segments | first-win · skeleton · mobile |
| 3 | Vocabulary SSOT | 85 | **86** | +7 | CTA JSON · ban book demo | category moat · comparisons |
| 4 | Deterministic routing | 80 | **81** | +12 | segment tracks · guided | cohort · funnel science |
| 5 | Self-serve proof | 65 | **65** | +28 | proof run API · status page | crypto verify · gallery |
| 6 | Intake → ops | 70 | **72** | +21 | sandbox worker · inbox | enterprise intake · webhooks |
| 7 | Analytics | 82 | **84** | +9 | rollup · export | funnel · A/B · alerts |
| 8 | Market polish | 55 | **56** | +37 | typography · lighthouse | OG · SEO · social trust |
| 9 | Commercial close | 60 | **60** | +33 | Stripe · pricing CTA | procurement · MSA · monetize |
| 10 | E2E quality | 88 | **89** | +4 | modern-stack E2E | batch-2 validate · CI smoke |

**Weighted overall v2: 78/100** (+2 since pulse auth + RESEND fixed)

---

## What improved since batch-1 score

- `FOUNDER_PULSE_KEY` correct on worker → dashboard API **200**
- `RESEND_API_KEY` on worker → email path ready
- Public stats + pulse-founder + segment router **live**
- E2E modern-stack **PASS** on sourcea.app

---

## What still blocks 93+

| Blocker | Severity | Batch |
|---------|----------|-------|
| No stranger-triggered proof run | P0 | 1 + 2 crypto |
| mailto on security · team · pricing · trust | P0 | 1 + 2 enterprise |
| Hero primary CTA = Forge not proof | P1 | 1 |
| sandbox → mailto not worker | P0 | 1 |
| No conversion funnel in founder UI | P1 | 2 |
| No signed / verifiable receipts | P1 | 2 |
| No enterprise security PDF / DPA | P1 | 2 |
| SEO / OG per segment missing | P2 | 2 |

---

## Market position (plain)

**You beat:** Cal-first AI agencies, generic “book a demo” dev shops, sites with no analytics loop.

**You tie:** Early-stage B2B with a status page and honest beta portal.

**They beat you:** Trigger.dev (run UX), Vercel (visual polish), Vanta (enterprise trust pack), Stripe (self-serve pay).

**Moat if you execute both batches:** *Proof-native agentic execution* — stranger picks lane → sees or runs proof → receipt they can verify → optional human. Almost nobody ships that end-to-end.

---

## Score path

```
Today 78 ──batch-1 NOW (50)──► ~85 ──batch-2 NOW (60)──► ~93 ──both LATER──► 95+
```

---

## Execute order (combined)

1. **sa-score-0001** (batch-1) — proof run API  
2. **sa-score2-0001** (batch-2) — Ed25519 signed receipts  
3. **sa-score-0041** — sandbox worker  
4. **sa-score2-0031** — security.html → proof not mailto  
5. **sa-score2-0002** — funnel chart in founder dashboard  
