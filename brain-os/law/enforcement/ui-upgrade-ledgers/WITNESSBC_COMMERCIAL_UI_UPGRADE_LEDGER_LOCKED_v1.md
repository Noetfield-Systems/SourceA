# WitnessBC Commercial — UI Upgrade Ledger — LOCKED v1

**Version:** 1.1.0 · **Saved:** 2026-06-21T04:02:00Z · **Authority:** Founder — witnessbc.com commercial site  
**surface_id:** `witnessbc_commercial` · **Repo:** SourceA · **URL:** https://www.witnessbc.com/  
**Root:** `witnessbc-site/`  
**Machine log:** `data/ui-upgrade-ledgers/witnessbc_commercial-v1.json`  
**General checklist:** `SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md` §4  
**E2E:** `witnessbc-site/scripts/wbc-e2e.sh` · `scripts/validate_witnessbc_deep_e2e_v1.py`

---

## Frozen inventory

| id | What | Marker / proof |
|----|------|----------------|
| brand_strip | Brand disambiguation | `brand-disambiguation` on home |
| proof_cta | Proof mailto | `proof@witnessbc.com` |
| proof_lab | Proof Lab | `proof.html` Proof Lab |
| toolkits_freemium | Free + Pro ladder | `data-buy` + free template links |
| toolkits_sandbox | Client sandbox freemium | `data-freemium-active` + `/toolkits/sandbox/` |
| stripe_checkout_live | Live Stripe checkout UX | `checkout-live` on body + `stripe_links_live` in JSON |
| v12_layout | Ultra-wide v12 | `layout-ultra-v12` on all pages |
| no_cross_brand | Site independence | no Noetfield redirects |

---

## App-specific checklist

- [ ] **WBC-1** Read `witnessbc-site/data/ui-upgrade-e2e-v12.json` before UI touch  
- [ ] **WBC-2** Subpages use root-absolute `/assets/` paths (nested toolkits)  
- [ ] **WBC-3** `bash witnessbc-site/scripts/run-recipe.sh` PASS after edit  
- [ ] **WBC-4** `bash witnessbc-site/scripts/wbc-e2e.sh` PASS before ship  
- [ ] **WBC-5** Freemium preserved — free HTML + Pro Stripe on every toolkit  
- [ ] **WBC-6** `bash scripts/validate-witnessbc-ui-zero-drift-v1.sh` PASS — zero tolerance  

---

## Upgrade history

### UP-WBC-001 — 2026-06-19 — v12 toolkits + subpages

| Field | Value |
|-------|-------|
| Trigger | upgrade toolkits + v12 ultra-wide UI |
| Preserved | freemium · Stripe · education-only law |
| Changed | toolkits hub · 9 subpages · v12 CSS · E2E scripts |
| Achieved | 20 pages · 632 links PASS |
| Quality vs last | better |
| Founder approval | **approved** |

### UP-WBC-002 — 2026-06-19 — freemium + sandbox

| Field | Value |
|-------|-------|
| Trigger | ACTIVATE FREEMIUM — Quick Start + client sandbox |
| Preserved | v12 layout · Pro Stripe data-buy · education-only · site independence |
| Changed | data-freemium-active · Start free CTAs · `/toolkits/sandbox/` · toolkits-sandbox.js |
| Achieved | 21 pages · 665 links PASS |
| Quality vs last | better |
| Founder approval | shipped |

### UP-WBC-003 — 2026-06-21 — commerce polish (live Stripe)

| Field | Value |
|-------|-------|
| Trigger | upgrade — commerce polish post-Stripe sync |
| Preserved | freemium · sandbox · v12 · all toolkit sections · education-only law |
| Changed | checkout-live pills · toolkits.js buy states · pricing 11-SKU grid · 11 assemble tokens · WITNESSBC descriptor |
| Achieved | 21 pages · 665 links PASS · live checkout on toolkits + pricing · deploy `83b6636` |
| Quality vs last | better |
| Founder approval | **approved** |

---

*Next upgrade: append UP-WBC-004.*
