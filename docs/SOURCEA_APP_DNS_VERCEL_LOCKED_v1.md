# sourcea.app — go live on Vercel (source-a)

**Saved:** 2026-06-23T07:30:00Z  
**Vercel project:** `source-a` · team `the-777-foundation`  
**Production:** https://source-a.vercel.app  
**Commercial landing:** https://source-a.vercel.app/sourcea/start.html  

## Done logged / Vercel

- Latest 48h MVP landing deployed (static 5-question form · `hello@sourcea.app`)
- Domains attached to project `source-a`:
  - `sourcea.app`
  - `www.sourcea.app`

## You add these 2 DNS records in Cloudflare (sourcea.app zone)

Cloudflare → **sourcea.app** → **DNS** → **Add record**

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| **A** | `@` | `76.76.21.21` | **DNS only** (grey cloud) |
| **A** | `www` | `76.76.21.21` | **DNS only** (grey cloud) |

Vercel requires **DNS only** on these records (not orange proxied) for Hobby custom domains.

Then wait 1–5 minutes and verify:

```bash
npx vercel domains verify sourcea.app --scope the-777-foundation
curl -sI https://sourcea.app/ | head -5
curl -sfL https://sourcea.app/ | grep "48 hours"
```

## Smoke (after DNS)

- https://sourcea.app/ → 48h MVP headline
- https://www.sourcea.app/sourcea/start.html → full form
- mailto:hello@sourcea.app in header/footer

## Note

`source.app` (no “a”) is a **different** domain (Webflow product). Commercial plane uses **`sourcea.app`**.
