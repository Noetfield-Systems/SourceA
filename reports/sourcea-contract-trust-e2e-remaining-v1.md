# Contract & Trust E2E — Full Upgrade Check + Remaining

**Saved:** 2026-07-02T00:45:00Z  
**Validator:** `scripts/validate-sourcea-contract-pages-e2e-v1.sh` (v1.1.0 trust stack)  
**Receipt:** `~/.sina/sourcea-contract-pages-e2e-v1.json`  
**SSOT:** `data/sourcea-contract-email-routes-v1.json` → `trust_e2e_v1`

---

## E2E verdict

| Lane | Status | Checks |
|------|--------|--------|
| **SourceA (live)** | **ALL PASS** | 62 assertions |
| **Noetfield (live)** | **REMAINING** | 2 routes — disk fixed, not deployed |
| **PyPI Phase 0b** | **BLOCKED** | `sourcea-boot` not on PyPI |

**Command:** `bash scripts/validate-sourcea-contract-pages-e2e-v1.sh`  
**Result:** `ALL PASS (SourceA) · 2 remaining item(s)`

Strict Noetfield mode (fails on remaining): `SOURCEA_E2E_STRICT_NOETFIELD=1 bash scripts/validate-sourcea-contract-pages-e2e-v1.sh`

---

## What E2E now covers (new in v1.1)

### Contract SKUs (3 paths × sourcea.app + 2 regional mirrors)

- HTTP 200 + **direct 200** (no redirect chain)
- Title, CTA, domain-correct `contract@` mailto
- **Trust stack:** `proof-strip`, `buyer-path`, `diagram-svg`, procurement link, Noetfield trust-brief cross-link
- **Forbidden absent:** `92/100`, `5/5 audited`, `200 live route`, `Entity proof placeholder`
- Disk parity: CTA + public address on green-unified HTML

### Auxiliary SourceA surfaces

| Route | Checks |
|-------|--------|
| `/eval` | `eval-institutional-band`, procurement link, PyPI honesty, direct 200 |
| `/` | `#contract-skus`, decision tree, links to all 3 SKUs |
| `/attach/procurement-pack.html` | direct 200 on **sourcea.app**, **sourcea.ca**, **sourcea.uk** |

### Inbox / SSOT

- Google Workspace MX on sourcea.app + noetfield.com
- `buyer_path_note` present in SSOT
- All contract routes deliver to `operations@noetfield.com`
- No forbidden personal email leaks

### Noetfield (optional — reported as REMAINING, not FAIL)

| URL | Expected live | Current live |
|-----|---------------|--------------|
| `noetfield.com/about/` | NDA entity path | Still shows **Pending publication** + placeholder title |
| `noetfield.com/trust/` | NDA entity path | Still shows **Pending publication** |

**Disk fix ready:** `~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield/about/index.html` and `trust/index.html`

---

## Remaining work (ordered)

### P0 — Close Noetfield live gap

1. **Deploy Noetfield** entity/trust HTML from `Noetfield-All-Documents/` to live `www.noetfield.com`
2. Re-run E2E — expect 0 `REMAINING` lines
3. Optional: deploy `ai-value-governance-os/` procurement cross-links (SourceA pack button)

### P1 — PyPI Phase 0b

1. Wire PyPI trusted publishing OIDC (`.github/workflows/publish-pypi-v1.yml` on disk)
2. Publish `sourcea-boot` to PyPI
3. Verify `pip install sourcea-boot` resolves
4. **Only then** remove “PyPI Phase 0b — not on PyPI yet” from `/eval` and trust signals

### P2 — Strict CI gate (when Noetfield live)

- Add `SOURCEA_E2E_STRICT_NOETFIELD=1` to cloud CI ship window
- Chain remains: `validate-sourcea-brain-landing-e2e-v1.sh` → includes contract E2E

### P3 — Not in E2E scope (manual / separate)

| Item | Why not automated |
|------|-------------------|
| Outsider score re-run | Qualitative audit — see `reports/sourcea-public-surface-outsider-audit-v2.md` |
| Google Workspace alias proof | Admin console — E2E checks MX + SSOT only |
| BC registry extract public URL | NDA path by design until founder publishes |
| SOC 2 / ISO certification | Honest “Planned” — must not pass until real |

---

## Live spot-check summary (2026-07-02)

| Surface | Trust markers | Status |
|---------|---------------|--------|
| sourcea.app SKUs | proof-strip, SVG, buyer-path | ✅ Live |
| sourcea.ca / sourcea.uk | direct 200 + trust stack | ✅ Live |
| sourcea.app/eval | institutional band + PyPI honesty | ✅ Live |
| sourcea.app/ | contract SKU cards + decision tree | ✅ Live |
| Procurement pack (3 domains) | direct 200 | ✅ Live |
| noetfield.com/about + /trust | NDA entity proof | ❌ Deploy pending |
| PyPI `sourcea-boot` | pip resolves | ❌ BLOCKED |

---

## Next command

```bash
bash scripts/validate-sourcea-contract-pages-e2e-v1.sh
# After Noetfield deploy:
SOURCEA_E2E_STRICT_NOETFIELD=1 bash scripts/validate-sourcea-contract-pages-e2e-v1.sh
```
