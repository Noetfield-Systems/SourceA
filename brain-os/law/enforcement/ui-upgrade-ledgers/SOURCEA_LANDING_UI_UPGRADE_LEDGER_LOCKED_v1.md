# SourceA Landing — UI Upgrade Ledger — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-19T16:54:05Z · **Authority:** Founder — per-app UI upgrade tracking  
**surface_id:** `sourcea_landing` · **Repo:** SourceA · **URL:** http://127.0.0.1:5180/sourcea/  
**Root:** `SourceA-landing/green-unified`  
**Machine log:** `data/ui-upgrade-ledgers/sourcea_landing-v1.json`  
**General checklist:** `SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md` §4 (UP-0..UP-7)

---

## Frozen inventory (never drop without `UI BASELINE BUMP`)

| id | What | Marker / proof |
|----|------|----------------|
| buyer_toggle | Buyer toggle | `sa-buyer-toggle` |
| chain_beats | Chain beats (≥6) | `sa-chain-beats` · min 6 on home/proof |
| mock_panel | Mock panel | `sa-mock-panel` |
| trust_strip | Live trust strip | `data-trust-valid-yes` on all 5 pages |
| trust_receipts | Receipts lifetime | `data-trust-receipts-lifetime` |
| agent_pill | Agent pill text | `id="sa-agent-pill-text"` |
| factory_pass_chip | Factory pass chip | `sa-factory-pass-chip` |
| hero_cta | Hero CTA copy | "Close clients with live proof" |
| live_proof_link | Live proof nav | `/sourcea/proof/live.html` |
| trust_bar_js | Trust bar script | `sourcea-trust-bar.js` · `paintFactoryChip` |
| live_console_js | Live console | `sourcea-live-console.js` |
| sa_live_dataset | Live dataset wiring | `dataset.saLive` |

**Machine baseline:** `SourceA-landing/green-unified/data/ui-upgrade-baseline-v1.json` v1.0.0

---

## App-specific checklist (beyond general UP)

- [ ] **LAND-1** Baseline `check` each controlled file before edit  
- [ ] **LAND-2** Never use `reference/` or `Downloads/*.html` as canonical  
- [ ] **LAND-3** `run-recipe.sh --e2e` PASS before baseline bump  
- [ ] **LAND-4** All 5 HTML + CSS + 3 JS inventoried  

---

## Upgrade history

### UP-LANDING-000 — 2026-06-18 — baseline lock

| Field | Value |
|-------|-------|
| Trigger | baseline lock — no downgrade law |
| General | UP-0..UP-7 |
| App | LAND-1..LAND-4 |
| Preserved | All frozen inventory → baseline JSON |
| Changed | Initial machine baseline v1.0.0 from E2E pass |
| Achieved | Machine-enforceable no-downgrade guard |
| Quality vs last | baseline |
| Founder approval | **approved** |
| Proof | `validate-ui-upgrade-no-downgrade-v1.sh` PASS · `run-recipe --e2e` PASS |

---

*Next upgrade: append UP-LANDING-001 to JSON + this section.*
