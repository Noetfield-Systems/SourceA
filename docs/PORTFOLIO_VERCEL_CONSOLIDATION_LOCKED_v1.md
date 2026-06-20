# Portfolio consolidation — trial Vercel → main GitHub + main Vercel

**Saved:** 2026-06-21T01:35:00Z · **Authority:** ASF

## One law

All latest commercial code lives in **`kazemnezhadsina144-dot/SourceA`** monorepo → deployed on **`the-777-foundation`**. Cloudflare = DNS only.

## Main Vercel projects (the-777-foundation)

| Product | Vercel project | GitHub | Root directory | URL |
|---------|----------------|--------|----------------|-----|
| **SourceA** | `source-a` | SourceA | `SourceA-landing/green-unified` | https://source-a.vercel.app/sourcea/ |
| **WitnessBC** | `deploy-witnessbc-agents-governance` | SourceA | `witnessbc-site` | https://deploy-witnessbc-agents-governance.vercel.app |
| Noetfield | `noetfield` | kazemnezhadsina144-dot/noetfield | (repo root) | www.noetfield.com |
| TrustField | `trustfield-personal` | kazemnezhadsina144-dot/trustfield-personal | (repo root) | trustfield-personal.vercel.app |

## Delete on noetfield-systems trial (after main green)

- `sourcea-landing` → replaced by **source-a**
- `deploy` (sooty) → replaced by **deploy-witnessbc-agents-governance**
- `www` (gc7lm) → merge into **noetfield** or delete

## SourceA 404 fix (2026-06-21)

Trial deploy had `/sourcea/` + `/assets/` layout. Git deploy needed build:

```bash
python3 scripts/build_sourcea_vercel_output_v1.py
```

`SourceA-landing/green-unified/vercel.json` runs this on Vercel → output `dist/`.

**Vercel settings for source-a:** Root Directory = `SourceA-landing/green-unified` · Framework = **Other** · Build Command = **empty** · Output = **`dist`** (committed to Git — no Python build on cloud)

**Vercel settings for deploy-witnessbc-agents-governance:** Root Directory = `witnessbc-site` · Framework = **Other** · Build Command = **empty**

## Cloudflare (unchanged — separate logins)

- witnessbc.com → witness.bc@gmail.com → CNAME to Vercel when ready
- noetfield.com · trustfield.ca · sourcea.com → main lane CF
