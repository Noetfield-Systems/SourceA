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

## Vercel dashboard — MUST match (404 fix)

### Project `source-a`

| Setting | Value |
|---------|--------|
| **Root Directory** | leave **empty** (repo root) **OR** `SourceA-landing/green-unified` |
| **Framework Preset** | **Other** (not Next.js) |
| **Build Command** | **empty** (override ON · clear field) |
| **Output Directory** | empty if root=repo · **`dist`** if root=green-unified |
| **Install Command** | empty |

After save → **Deployments → Redeploy** latest commit `e2279eb8` or newer.

Test: https://source-a.vercel.app/sourcea/

### Project `deploy-witnessbc-agents-governance`

| Setting | Value |
|---------|--------|
| **Root Directory** | **`witnessbc-site`** (required) |
| **Framework Preset** | **Other** |
| **Build / Install** | empty |

Test: https://deploy-witnessbc-agents-governance.vercel.app/

If still 404 → Deployment log likely shows wrong output path or failed build.

## Cloudflare (unchanged — separate logins)

- witnessbc.com → witness.bc@gmail.com → CNAME to Vercel when ready
- noetfield.com · trustfield.ca · sourcea.com → main lane CF
