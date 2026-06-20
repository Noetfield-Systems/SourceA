# WitnessBC Commercial — UI Upgrade Ledger — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-19T18:00:00Z · **Authority:** Founder — witnessbc.com commercial site  
**surface_id:** `witnessbc_commercial` · **Repo:** SourceA · **URL:** https://witnessbc-commercial.pages.dev/  
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
| v12_layout | Ultra-wide v12 | `layout-ultra-v12` on all pages |
| no_cross_brand | Site independence | no Noetfield redirects |

---

## App-specific checklist

- [ ] **WBC-1** Read `witnessbc-site/data/ui-upgrade-e2e-v12.json` before UI touch  
- [ ] **WBC-2** Subpages use root-absolute `/assets/` paths (nested toolkits)  
- [ ] **WBC-3** `bash witnessbc-site/scripts/run-recipe.sh` PASS after edit  
- [ ] **WBC-4** `bash witnessbc-site/scripts/wbc-e2e.sh` PASS before ship  
- [ ] **WBC-5** Freemium preserved — free HTML + Pro Stripe on every toolkit  

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
| Founder approval | **pending** |

---

*Next upgrade: append UP-WBC-002.*
