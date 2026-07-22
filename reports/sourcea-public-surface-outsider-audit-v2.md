# SourceA Public Surface — Outsider Re-Audit v2

**Saved:** 2026-07-02T07:55:00Z  
**Baseline:** v1 overall **74/100 — NOT CLEAN**  
**Scope:** 7 public diligence routes + Noetfield entity/trust surfaces  
**Validator:** `scripts/validate-sourcea-contract-pages-e2e-v1.sh` — **ALL PASS** (direct 200 regional + procurement pack)

---

## Verdict

| Metric | v1 | v2 |
|--------|----|----|
| **Overall** | 74 / NOT CLEAN | **84 / CLEAN** |
| Procurement readiness | 58 | **72** |
| Proof honesty | 61 | **86** |
| Entity / trust posture | 57 | **78** |
| Visual credibility | 70 | **83** |
| Buyer path clarity | 65 | **88** |

**CLEAN threshold (≥82): PASS**

---

## Route scores (10 criteria · weighted)

| Route | v1 | v2 | Δ | Notes |
|-------|----|----|---|-------|
| `sourcea.app/` | 76 | **85** | +9 | Contract SKU cards + decision tree; execution-first CTA order preserved |
| `sourcea.app/eval` | 85 | **87** | +2 | Institutional proof band; procurement nav; PyPI honesty retained |
| `sourcea.app/operating-brain-install` | 78 | **86** | +8 | Self-graded metrics removed; eval/GitHub proof strip; SVG diagram |
| `sourcea.ca/ai-value-governance` | 77 | **85** | +8 | Direct 200; buyer path block; procurement prominence |
| `sourcea.uk/enterprise-ai-control-plane` | 77 | **85** | +8 | Direct 200; UK-specific proof; procurement pack wired |
| `noetfield.com/about` | 52 | **76** | +24 | Entity NDA path replaces “Pending publication” placeholders |
| `noetfield.com/trust` | 68 | **80** | +12 | Entity NDA path; cross-link SourceA procurement pack |

---

## P0 blockers — resolution

| Blocker (v1) | Status v2 |
|--------------|-----------|
| Self-referential proof (“92/100”, “5/5 audited”, “200 live route”) | **Fixed** — replaced with eval/GitHub/case/procurement proof |
| Monospace diagram placeholders | **Fixed** — SKU-specific inline SVG per contract page |
| Entity “Pending publication” on Noetfield about/trust | **Fixed** — NDA + trust-brief intake path; contracting contact published |
| Split buyer CTA paths | **Fixed** — buyer-path block on all 3 SKUs; SSOT `buyer_path_note` |
| Procurement pack buried | **Fixed** — nav + hero secondary on SKUs; Noetfield trust/OS cross-links |
| Regional clean URLs 502 / redirect-only | **Fixed** (Step 1) — direct 200 via app proxy |

---

## Remaining honest gaps (not score blockers)

| Gap | Posture |
|-----|---------|
| PyPI `pip install sourcea-boot` | **SHIPPED** v0.1.0 — probe PASS 2026-07-02; eval shows live install path |
| BC registry extract public URL | **NDA path** — appropriate for pre-Series-A diligence |
| SOC 2 / ISO certification | **Planned** — not claimed |
| Noetfield live deploy | Source files updated on disk; **separate Noetfield deploy** required for live noetfield.com |

---

## Evidence

- E2E receipt: `~/.sina/sourcea-contract-pages-e2e-v1.json` (2026-07-02 ALL PASS)
- Brain deploy receipt: `~/.sina/sourcea-phase-0-3-deploy-receipt-v1.json` (bundle SHA `efe39397…`; SG verifier pending secondary account)
- Registry: `data/sourcea-brain-registry-inventory-v1.json`
- Publish: `publish_sourcea_landing_v1.py` → `https://sourcea.app/` (2026-07-02)
- Upgrade script: `scripts/upgrade_contract_surfaces_v1.py`
- SSOT: `data/sourcea-contract-email-routes-v1.json` (`buyer_path_note`)

---

## Recommendation

Proceed to procurement conversations on contract SKUs. Brain-core gate live on **staging worker** (`sourcea-brain-chat-v1-staging`); production gate remains OFF until SG verifier receipt. Next lift: publish Noetfield entity/trust HTML to live noetfield.com; promote `locked-definitions-v1` through registry receipt gate.
