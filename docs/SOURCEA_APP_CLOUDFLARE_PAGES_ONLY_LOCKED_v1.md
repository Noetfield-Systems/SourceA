# sourcea.app — Cloudflare Pages only (no Vercel)

**Saved:** 2026-06-23T07:48:00Z

## Two products, one domain

| URL | Product | Buyer |
|-----|---------|-------|
| **sourcea.app/** | MVP Builder — *48 hours* | Non-technical founders |
| **sourcea.app/kernel/** | Source-A kernel — governance infra | Technical / partners |

Vercel is **not required**. Grey-cloud DNS was only for Vercel’s IP (`76.76.21.21`).

## DNS (Cloudflare → Pages)

**Replace** A records to `76.76.21.21` with:

| Type | Name | Target | Proxy |
|------|------|--------|-------|
| **CNAME** | `@` | `sourcea-com.pages.dev` | Proxied OK |
| **CNAME** | `www` | `sourcea-com.pages.dev` | Proxied OK |

Pages project: **sourcea-com** · add custom domains `sourcea.app` + `www.sourcea.app` in dashboard.

## Publish (Mac)

```bash
python3 scripts/publish_sourcea_landing_v1.py --backend cloudflare --project sourcea-com --custom-domain --skip-recipe
cd cloud/workers/sourcea-app-proxy-v1 && wrangler deploy
python3 scripts/sourcea_pages_activate_domains_v1.py --json
```

**Live path today:** zone Worker `sourcea-app-proxy-v1` routes `sourcea.app/*` → `sourcea-com.pages.dev` (TLS on zone). Pages custom-domain rows may stay `pending` until apex/www CNAME → `sourcea-com.pages.dev` (needs API token with Zone DNS Edit, or dashboard confirm).

## Routing (in repo — not dashboard-only)

| Path | File | Notes |
|------|------|-------|
| `/` | `start.html` copied to `dist/index.html` | 48h MVP homepage (200, no redirect) |
| `/sourcea/start.html` | `start.html` | Same MVP subpage |
| `/kernel/` | `index.html` | Governance kernel |
| `_redirects` | staging root | Short paths only (`/start`, `/kernel`, …) |

## Later (optional)

`forge.sourcea.app` → same MVP form if you want a separate commercial subdomain before `forgefactory.com`.
