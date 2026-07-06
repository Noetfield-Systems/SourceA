# SourceA site score-up — 1000 plans (LOCKED v1)

**Saved at:** 2026-06-25T09:30:00Z  
**Machine:** `scripts/generate_sourcea_site_score_up_1000_plans_v1.py`  
**Master:** `brain-os/plan-registry/SOURCEA_SITE_SCORE_UP_1000_MASTER_v1.json`  
**Pack:** `brain-os/plan-registry/sourcea-site-score-up-1000/REGISTRY.json`

---

## One law

> **1000 plans = 10 score dimensions × 10 workstreams × 10 slices. Self-serve proof and commercial close NOW rows beat moonshot polish.**

**Baseline (2026-06-25):** ~76/100 · **Target:** 95+

---

## Grid

| Dimension | Count |
|-----------|-------|
| Score themes | 10 |
| Workstreams | 10 |
| Slices per cell | 10 |
| **Total plans** | **1000** |
| Prefix | `sa-score-` |

---

## Score dimensions (theme order = priority)

| # | Theme | Baseline | Target | Market analog |
|---|-------|----------|--------|---------------|
| 1 | Self-serve proof | 65 | 95 | Trigger.dev |
| 2 | Market polish | 55 | 90 | Linear |
| 3 | Commercial close | 60 | 92 | Stripe Atlas |
| 4 | Intake → ops loop | 70 | 95 | Typeform + Zapier |
| 5 | Client-facing UI | 72 | 93 | Vercel |
| 6 | Deterministic routing | 80 | 97 | Intercom Fin |
| 7 | Live wiring | 88 | 100 | Cloudflare Workers |
| 8 | Analytics & feedback | 82 | 98 | PostHog |
| 9 | Vocabulary SSOT | 85 | 99 | Notion GTM |
| 10 | E2E & quality gates | 88 | 100 | Playwright |

---

## Workstreams

Ship · Prove · Wire · UI · Copy · Worker · Deploy · E2E · Market bench · Receipt

---

## Phase law (ranks 1–1000)

| Phase | Ranks | Focus |
|-------|-------|-------|
| **NOW** | 1–50 | Stranger proof run · sandbox worker · hero CTA SSOT · polish P0 |
| **NEXT** | 51–200 | Commercial Stripe · inbox unification · routing hardening |
| **LATER** | 201–500 | Analytics funnel · vocabulary CI · trust polish |
| **MOONSHOT** | 501–1000 | Bench-only · scale · enterprise |

---

## Top 10 NOW plans (execute first)

| ID | Title |
|----|-------|
| sa-score-0001 | Ship stranger POST /api/proof/run/v1 → cloud job → public receipt URL |
| sa-score-0002 | Prove live proof run progress bar on /sourcea/proof/live |
| sa-score-0003 | Wire email receipt link after async proof completes |
| sa-score-0004 | Polish UI for proof run status page /sourcea/proof/run/:id |
| sa-score-0005 | Rewrite copy for Forge Terminal handoff after proof quiz pass |
| sa-score-0011 | Ship hero typography pass — match Linear/Vercel rhythm |
| sa-score-0031 | Ship pricing CTA → /start not mailto |
| sa-score-0041 | Ship sandbox-intake.js → sourcea-mvp-intake-v1 worker |
| sa-score-0051 | Ship founder-home hero primary = See live receipt per CTA SSOT |
| sa-score-0101 | Ship validate-sourcea-modern-stack-e2e-v1 weekly cron |

---

## W2 execution (10 upgrade plans × 10 steps)

**Wave:** W2 · **Gate:** `UP-SA-W2-10` · **Pulse:** `python3 scripts/sourcea_site_score_w2_pulse_v1.py --json`

| Plan | Theme | Step IDs (w01→w10 slice-01) |
|------|-------|------------------------------|
| UP-SA-W2-01 | Self-serve proof | 0001, 0011, …, 0091 |
| UP-SA-W2-02 | Market polish | 0101, …, 0191 |
| UP-SA-W2-03 | Commercial close | 0201, …, 0291 |
| UP-SA-W2-04 | Intake → ops | 0301, …, 0391 |
| UP-SA-W2-05 | Client-facing UI | 0401, …, 0491 |
| UP-SA-W2-06 | Deterministic routing | 0501, …, 0591 |
| UP-SA-W2-07 | Live wiring | 0601, …, 0691 |
| UP-SA-W2-08 | Analytics & feedback | 0701, …, 0791 |
| UP-SA-W2-09 | Vocabulary SSOT | 0801, …, 0891 |
| UP-SA-W2-10 | E2E & quality gates | 0901, …, 0991 |

**Critical path:** UP-SA-W2-07 → UP-SA-W2-01 → UP-SA-W2-02 + UP-SA-W2-09 → UP-SA-W2-10

**Merge W2 only (no full regen):**

```bash
python3 scripts/generate_sourcea_site_score_up_1000_plans_v1.py --write-w2
python3 scripts/sourcea_site_score_w2_pulse_v1.py --json
```

---

## Generate & validate

```bash
cd ~/Desktop/SourceA
python3 scripts/generate_sourcea_site_score_up_1000_plans_v1.py
bash scripts/validate-sourcea-site-score-up-1000-v1.sh
```

---

## Pick next plan

```bash
python3 scripts/pick_sourcea_site_score_plan_v1.py --phase NOW --json
```

---

## Closeout

Mark `status: done` + `score_delta` in REGISTRY.json · redeploy sourcea.app · E2E PASS receipt.
