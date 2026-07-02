# Contract & Trust E2E — Full Upgrade Check + Remaining

**Saved:** 2026-07-02T03:42:00Z  
**Validator:** `scripts/validate-sourcea-contract-pages-e2e-v1.sh` (v1.2.0 trust stack)  
**Receipt:** `~/.sina/sourcea-contract-pages-e2e-v1.json`  
**SSOT:** `data/sourcea-contract-email-routes-v1.json` → `trust_e2e_v1`

---

## E2E verdict

| Lane | Status | Checks |
|------|--------|--------|
| **SourceA (live)** | **ALL PASS** | contract + eval + home + procurement |
| **Noetfield (live)** | **PASS** (optional mode) | about + trust live |
| **PyPI Phase 0b** | **LIVE** | `sourcea-boot` v0.1.0 · `pip install` resolves |

**Command:** `bash scripts/validate-sourcea-contract-pages-e2e-v1.sh`  
**Result:** `ALL PASS`

---

## What E2E covers (v1.2)

### Contract SKUs (3 paths × sourcea.app + 2 regional mirrors)

- HTTP 200 + **direct 200**
- Title, CTA, domain-correct `contract@` mailto
- **Trust stack:** `proof-strip`, `buyer-path`, `diagram-svg`, procurement, Noetfield trust-brief, `hreflang`, demo tag
- **Forbidden absent:** fake scores, `not on PyPI yet`
- **Canonical/hreflang** disk assertions per `canonical_e2e_v1`

### Auxiliary SourceA surfaces

| Route | Checks |
|-------|--------|
| `/eval` | `eval-institutional-band`, procurement link, **`pip install sourcea-boot`**, direct 200 |
| `/` | `#contract-skus`, decision tree, all 3 SKU links |
| Procurement pack | 200 on `.app` / `.ca` / `.uk` |

---

## Remaining (not E2E blockers)

| Item | Owner | Notes |
|------|-------|-------|
| Merge sandbox → main | Founder | `166b1441a` + acquisition execution on branch |
| Outsider re-audit v2 | Worker | Target ≥82 CLEAN after soak |
| Noetfield PyPI org transfer | Founder | Optional when org approved |
| Customer reference blocks | Founder | Never fake — add only when verified |
| Pricing bands on contract pages | Founder | SSOT: never lead with price |

---

**End v1.2**
