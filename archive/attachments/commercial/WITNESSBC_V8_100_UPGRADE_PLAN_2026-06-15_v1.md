# WitnessBC Site v8 — 100-Grade Upgrade Plan

**Saved:** 2026-06-15T21:32:29Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15  
**Lane:** Commercial · witnessbc.com platform site (`witnessbc-site/`)  
**Authority:** `WITNESSBC_UI_UPGRADE_30_PLAN_2026-06-15_v1.md` · v7 high-grade ship · UPGR-201–210 trust items  
**Target:** v8 **100-grade** local PASS → live deploy → Trust 8→10

---

## Executive summary

v7 shipped a **9-page high-grade** Witness AI commercial site locally (`:8090`) but **witnessbc.com still shows legacy civic journalism**. v8 moves the **platform site to next grade**: live trust injection, deploy path with journalism coexistence, W1 film bridge, and validate v8 gate — then **wrangler deploy** as founder one-tap.

---

## Score baseline → v8 target

| Dimension | v7 baseline | v8.0 ship-local | v8.1 deploy-live | v8.2 trust 10 |
|-----------|-------------|-----------------|------------------|---------------|
| **Overall** | ~92 A | 94 A | 96 A+ | **100 A+** |
| Hero | 9 | 9 | 9 | 9 |
| Visual | 9 | 9 | 9 | 10 |
| **Trust** | 6–7 | **8** | **8** | **10** |
| CTA | 9 | 9 | 9 | 9 |
| Pricing UX | 9 | 9 | 9 | 9 |
| IA | 9 | **10** | 10 | 10 |
| Proof | 9 | **10** | 10 | 10 |
| Deploy readiness | 5 | **9** | **10** | 10 |

**Scoring:** Same 8-dimension rubric as UI 30-plan · overall = average × 10.

---

## 30-point UI plan — audit (v7 → v8)

| # | Item | v7 | v8 |
|---|------|----|-----|
| 1 | Category headline | DONE | — |
| 2 | Dual CTA row | DONE | — |
| 3 | Stat strip + cites | DONE | — |
| 4 | Buyer chips | DONE | — |
| 5 | Mobile hero stack | DONE | — |
| 6 | Framework trust strip | DONE | — |
| 7 | Analyst citation card | DONE | — |
| 8 | Trust pills | DONE | — |
| 9 | Cohort / logo strip | DONE | v8.2 customer logos when approved |
| 10 | Crosswalk print UX | DONE | — |
| 11 | Typography scale | DONE | — |
| 12 | Motion budget | DONE | — |
| 13 | SVG icon completion | PARTIAL | P2 menu ☰ → sprite |
| 14 | Dark contrast pass | DONE | — |
| 15 | OG card refresh | PARTIAL | P2 |
| 16 | Multi-page assemble | DONE | — |
| 17 | Home ≤10 sections | DONE | — |
| 18 | Explore hub | DONE | — |
| 19 | Breadcrumbs + page-hero | PARTIAL | **DONE v8** breadcrumbs |
| 20 | Footer IA | DONE | — |
| 21 | Proof film strip | DONE | — |
| 22 | Scenario pills | DONE | — |
| 23 | Control-plane toggle | GAP | **DONE v8** compact/detailed |
| 24 | Lifecycle scroll-snap | DONE | — |
| 25 | Compare responsive | DONE | — |
| 26 | Pricing Flow badge | DONE | — |
| 27 | Mobile CTA bar | DONE | — |
| 28 | FAQ accordion | DONE | — |
| 29 | Send bundles | DONE | — |
| 30 | Validate gate | v7 | **DONE v8** extended |

---

## NEW v8 items (beyond 30-plan)

| ID | Item | v8.0 | v8.1 | v8.2 |
|----|------|------|------|------|
| V8-01 | Live trust signals JSON + inject | DONE | live refresh on deploy | + customer proof numbers |
| V8-02 | `trust-signals.js` buyer bar on home | DONE | — | analyst badge row |
| V8-03 | W1 film `w1-demo.mp4` + commercial short bridge | iframe fallback | drop mp4 when filmed | 90s commercial short logged |
| V8-04 | `_redirects` clean URLs | DONE | verify live | — |
| V8-05 | `_routes.json` coexistence `/toolkits` journalism | DONE | DNS + Pages project | — |
| V8-06 | Wrangler deploy receipt v8 | script ready | **founder run --wrangler** | post-verify curl |
| V8-07 | Lighthouse gate (perf+a11y ≥90) | optional script | CI on deploy | hard gate |
| V8-08 | Validate.sh v8 PASS string | DONE | — | — |

---

## Phased rollout

### v8.0 — ship-local (this session)

- `bash witnessbc-site/scripts/run-recipe.sh --json` → PASS  
- Local preview: `http://127.0.0.1:8090/` (`run-recipe.sh --serve`)  
- Artifact: `witnessbc-site/dist/deploy/` + receipt `~/.sina/witnessbc-site-run-receipt-v1.json`

### v8.1 — deploy witnessbc.com

```bash
bash ~/Desktop/SourceA/witnessbc-site/scripts/deploy_witnessbc_v1.sh --wrangler
bash ~/Desktop/SourceA/witnessbc-site/scripts/deploy_witnessbc_v1.sh --verify https://witnessbc.com
```

- Point Cloudflare Pages project `witnessbc` to `dist/deploy/`  
- `_routes.json` keeps journalism at `/toolkits` + `/principles` on existing origin  
- Platform routes: `/platform` `/proof` `/pricing` etc. (clean URLs via `_redirects`)

### v8.2 — trust 8→10

- Approved customer logos in cohort strip (no fake Fortune row)  
- W1 film mp4 on proof (replace iframe fallback)  
- Lighthouse hard gate in run-recipe when `LIGHTHOUSE_MIN=90`  
- Optional status page link for live factory signals

---

## Commands

```bash
bash ~/Desktop/SourceA/witnessbc-site/scripts/run-recipe.sh --serve
python3 witnessbc-site/scripts/inject_trust_signals_v1.py --json
bash witnessbc-site/scripts/lighthouse_witnessbc_v1.sh http://127.0.0.1:8090/
bash witnessbc-site/scripts/deploy_witnessbc_v1.sh --wrangler
```

---

## Void list

- Do not overwrite journalism `/toolkits` in deploy without `_routes.json` exclude  
- No fake customer logos until written approval  
- No certification badges  
- witnessbc.com platform ≠ SourceA landing (separate lanes)

---

*Witness AI · witnessbc.com · v8 100-grade plan · educational framework mapping only.*
