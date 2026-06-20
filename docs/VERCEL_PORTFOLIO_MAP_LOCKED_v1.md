# Vercel portfolio map — LOCKED v1

**Version:** 1.2.0 · **Saved:** 2026-06-21T01:00:00Z · **Authority:** ASF  
**Machine SSOT:** `data/vercel-portfolio-map-v1.json`

---

## One law (founder locked 2026-06-20)

> **SourceA + WitnessBC commercial** → same GitHub monorepo → **separate Vercel projects** on main team.  
> **Cloudflare** = DNS only (different login per zone) — not the deploy SSOT.

---

## Deploy stack

```
kazemnezhadsina144-dot/SourceA  (GitHub · private)
├── SourceA-landing/green-unified  →  Vercel project source-a
└── witnessbc-site/                →  Vercel deploy-witnessbc-agents-governance (create next)

Cloudflare (separate)
├── witnessbc.com zone  →  witness.bc@gmail.com  →  CNAME www → Vercel when ready
├── noetfield.com       →  main lane CF
└── trustfield.ca       →  main lane CF
```

---

## Main Vercel (the-777-foundation) — status

| Project | Repo path | Status |
|---------|-----------|--------|
| **source-a** | `SourceA-landing/green-unified` | **Live** · Git linked |
| **deploy-witnessbc-agents-governance** | `witnessbc-site` | **Create next** — URL `deploy-witnessbc-agents-governance.vercel.app` |
| noetfield | separate repo | Live |
| trustfield-personal | separate repo | Live |

### Add WitnessBC on Vercel (main Chrome)

1. https://vercel.com/the-777-foundation → **Add New → Project**
2. Import **SourceA** (already connected from source-a)
3. **Root Directory:** `witnessbc-site`
4. Name: **deploy-witnessbc-agents-governance** → Deploy  
   URL: `https://deploy-witnessbc-agents-governance.vercel.app`
5. Verify: page title **Witness AI** (commercial, not journalism)
6. Cloudflare: point `www.witnessbc.com` → new Vercel URL (or keep pages.dev during cutover)

---

## Trial team (noetfield-systems) — delete after main green

| Orphan | Superseded by |
|--------|----------------|
| sourcea-landing | **source-a** on main |
| deploy (sooty-seven) | **deploy-witnessbc-agents-governance** on main |
| www | main **noetfield** project |

---

## What is NOT changing

- **Stripe** stays on noetfield@gmail.com (Noetfield Systems)
- **Cloudflare DNS** stays on separate accounts per zone
- **No cross-Gmail Vercel transfer** — delete orphans, don't transfer

---

## Push latest to GitHub before Vercel redeploy

Local may have uncommitted FORGE FACTORY / vercel-map updates. Say **push SourceA to GitHub** to sync main branch, then redeploy both Vercel projects.
