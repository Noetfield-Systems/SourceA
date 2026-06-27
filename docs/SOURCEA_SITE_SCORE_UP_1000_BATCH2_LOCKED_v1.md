# SourceA site score-up — batch 2 · 1000 plans (LOCKED v1)

**Saved at:** 2026-06-25T10:00:00Z  
**Machine:** `scripts/generate_sourcea_site_score_up_1000_plans_batch2_v1.py`  
**Master:** `brain-os/plan-registry/SOURCEA_SITE_SCORE_UP_1000_BATCH2_MASTER_v1.json`  
**Pack:** `brain-os/plan-registry/sourcea-site-score-up-1000-batch2/REGISTRY.json`  
**Analysis:** `docs/SOURCEA_SITE_SCORE_ANALYSIS_v2_LOCKED_v1.md`  
**Batch-1 (no dupes):** `docs/SOURCEA_SITE_SCORE_UP_1000_PLANS_LOCKED_v1.md`

---

## One law

> **Batch-2 = 1000 grade-A+ plans · 78→93+ · zero title overlap with `sa-score-*` batch-1.**

---

## How batch-2 differs from batch-1

| | Batch-1 | Batch-2 |
|---|---------|---------|
| Prefix | `sa-score-` | `sa-score2-` |
| Baseline | 76 | **78** (re-measured) |
| Target | 95 (moonshot) | **93** (credible market tier) |
| Grade | Ship / wire / prove | **Architect / harden / measure** |
| Themes | t01–t10 foundations | **t11–t20 advanced** |
| Focus | Get it working | **Enterprise · crypto · conversion · moat** |

---

## Advanced dimensions (batch-2 only)

| # | Theme | Now→Target | Market analog |
|---|-------|------------|---------------|
| 1 | Proof integrity & cryptography | 58→96 | Sigstore |
| 2 | Conversion funnel science | 62→94 | Amplitude |
| 3 | Enterprise buyer readiness | 48→93 | Vanta / SafeBase |
| 4 | Instant first-win onboarding | 55→94 | Replit Agent |
| 5 | Distribution & SEO | 50→92 | programmatic SEO |
| 6 | Social proof & trust signals | 52→93 | G2 |
| 7 | Product-led growth loops | 45→91 | referral PLG |
| 8 | Developer & partner API | 40→90 | Stripe API |
| 9 | Reliability & public SLA | 60→95 | statuspage.io |
| 10 | Competitive differentiation | 55→94 | category design |

---

## Workstreams (batch-2 only)

Architect · Harden · Measure · Automate · Integrate · Optimize · Comply · Scale · Monetize · Defend moat

---

## Phase law

| Phase | Ranks | Focus |
|-------|-------|-------|
| **NOW** | 1–60 | Signed receipts · funnel · enterprise CTAs · first-win |
| **NEXT** | 61–220 | SEO · PLG · API · SLA |
| **LATER** | 221–550 | Scale · comply · monetize depth |
| **MOONSHOT** | 551–1000 | Moat · research · defer |

---

## Top 12 NOW (batch-2)

| ID | Plan |
|----|------|
| sa-score2-0001 | Architect Ed25519-signed proof receipt + public verify API |
| sa-score2-0002 | Harden SHA-256 manifest for proof pack ZIP |
| sa-score2-0011 | Measure segment→proof→intake funnel in pulse-founder |
| sa-score2-0021 | Architect security.html CTA → proof live not mailto |
| sa-score2-0031 | Architect 60-second stranger path land→segment→receipt |
| sa-score2-0041 | Architect unique OG image per segment door |
| sa-score2-0051 | Architect live pageview counter on public status |
| sa-score2-0061 | Automate share proof URL with UTM ref=stranger |
| sa-score2-0071 | Integrate public Pulse API doc page |
| sa-score2-0081 | Harden worker health + KV latency probe |
| sa-score2-0091 | Defend comparison SourceA vs Cal-first agency |
| sa-score2-0100 | Defend category lock: Proof-native agentic execution |

---

## Commands

```bash
python3 scripts/generate_sourcea_site_score_up_1000_plans_batch2_v1.py
bash scripts/validate-sourcea-site-score-up-1000-batch2-v1.sh
python3 scripts/pick_sourcea_site_score_plan_v1.py --batch 2 --phase NOW --json
```

---

## Dedup guarantee

Generator aborts if any batch-2 title matches batch-1 `REGISTRY.json` title (case-insensitive). Validated on every generate.
