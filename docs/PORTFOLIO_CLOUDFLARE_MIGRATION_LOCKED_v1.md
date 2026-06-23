# Portfolio Cloudflare migration — SourceA · TrustField · Noetfield

**Saved:** 2026-06-23T06:00:00Z · **Authority:** ASF  
**Machine SSOT:** `data/portfolio-cloudflare-migration-v1.json`  
**Account map:** `docs/PORTFOLIO_ACCOUNT_STRUCTURE_LOCKED_v1.md`

## One law

> **Official domains on main Cloudflare account (`sinakazemnezhad.ca@gmail.com`). Vercel = interim only until Pages green. WitnessBC = separate witness.bc lane.**

| Domain | Brand | CF account | Interim Vercel |
|--------|-------|------------|----------------|
| **sourcea.com** | SourceA | Main | source-a.vercel.app |
| **trustfield.ca** | TrustField | Main | trustfield-personal.vercel.app |
| **noetfield.com** | Noetfield | Main | noetfield-www-main.vercel.app |
| witnessbc.com | WitnessBC | witness.bc | witnessbc-governance-main |

**Main account ID:** `0d0b967b77e2e5535455d39ff3dae72c` — verify with `wrangler whoami` before every deploy.

---

## SourceA (sourcea.com) — first cutover

1. **Build** (monorepo root):

```bash
python3 scripts/build_sourcea_vercel_output_v1.py
```

Output: `SourceA-landing/green-unified/dist/`

2. **Pages deploy** (main CF account — not WitnessBC):

```bash
python3 scripts/publish_sourcea_landing_v1.py --target cloudflare
```

Token: `~/.sina/cf-pages-token-v1.json` (SourceA-only — law: `scripts/sourcea_cf_pages_token_v1.py`)

3. **DNS** (zone sourcea.com on main account):

| Type | Name | Target |
|------|------|--------|
| CNAME | www | `sourcea-com.pages.dev` |
| CNAME | @ | `sourcea-com.pages.dev` (or apex flatten per CF UI) |

4. **Smoke:** `curl -sI https://sourcea.com/sourcea/` → 200  
5. **Keep Vercel** 24h rollback window → then pause/delete trial `sourcea-landing` on noetfield-systems.

---

## TrustField + Noetfield (same main account batch)

- Import/build each product’s static or framework output to **separate Pages projects** (`trustfield-ca`, `noetfield-com`).
- DNS: same pattern — CNAME www → `*.pages.dev`.
- Email outbound unchanged: `hello@trustfield.ca` · `operation@noetfield.com` (Google Workspace — not CF email API for MSB wave).

---

## Workers / cron (already on main account)

Autonomous loop worker: `cloud/workers/cloud-drain-tick-v1/` — checklist `docs/checklists/cloudflare-railway-loop-setup.md`.

**Never:** deploy portfolio Workers while OAuth’d as `witness.bc@gmail.com`.

---

## After all three green

1. Delete noetfield-systems trial projects (`sourcea-landing`, `deploy`, `www`).
2. Update `data/vercel-portfolio-map-v1.json` status → `cloudflare_primary`.
3. Receipt: `~/.sina/portfolio-cloudflare-migration-v1.json`
