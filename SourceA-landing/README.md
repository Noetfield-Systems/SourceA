# SourceA commercial landing (adapted layouts)

**NOT Noetfield** — Buyer 1 · platform eng · Asset B DFY  
**Law:** `SOURCEA_ASSET_B_GOVERNED_AGENTIC_AUTOMATION_LOCKED_v1.md` · `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md`

## Canonical site (green-unified — 12 pages)

**Run recipe** — sync · deploy · validate · receipt:

```bash
bash SourceA-landing/green-unified/scripts/run-recipe.sh
bash SourceA-landing/green-unified/scripts/run-recipe.sh --open --e2e   # + browser + Playwright
bash SourceA-landing/green-unified/open.sh
```

Live: **http://127.0.0.1:5180/sourcea/** · Receipt: `~/.sina/sourcea-landing-run-receipt-v1.json`  
Detail: `SourceA-landing/green-unified/README.md`

| Layout | File | Clone source |
|--------|------|--------------|
| **Canonical (Agent Run)** | `green-unified/` |  polish · 12 pages |
| design-benchmark (light) | `.html` | `C12/` |
| -style (dark) | `.html` | `C13/` · SourceA Asset B |

## Open (legacy layouts)

```bash
bash SourceA-landing/open.sh          #  +  static HTML
open SourceA-landing/.html
open SourceA-landing/.html
```

Witness BC (separate brand): `bash witnessbc-site/scripts/run-recipe.sh`

## Copy

- **From:** hello@sourcea.com  
- **Site:** https://sourcea.com  
- **Category:** Execution Proof Infrastructure — policy at dispatch · ledger + replay  
- **SKUs:** $750 audit · $3–10K DFY · $2–5K/mo retainer  

## Also on disk

`~/.sina/sourcea-commercial--layout-v1.html` · `~/.sina/sourcea-commercial--layout-v1.html`  
**Desktop:** bootstrap once if paths missing, then `cd ~/Desktop/agentrun-app && ./serve.sh` → Agent Run :5180/sourcea/
