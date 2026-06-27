# Add source.app to Cloudflare Pages (one-time)

**Project:** `sourcea-com` · **Account:** `0d0b967b77e2e5535455d39ff3dae72c`

Wrangler v4 removed `pages project domain add` — use dashboard:

1. [Cloudflare Dashboard](https://dash.cloudflare.com/) → **Workers & Pages** → **sourcea-com**
2. **Custom domains** → **Set up a custom domain**
3. Add **`source.app`** and **`www.source.app`**
4. If `source.app` zone is on this account, DNS records auto-configure
5. Smoke: `curl -sI https://source.app/sourcea/start.html` → 200

**DNS manual (if needed):**

| Type | Name | Target |
|------|------|--------|
| CNAME | @ | `sourcea-com.pages.dev` |
| CNAME | www | `sourcea-com.pages.dev` |

**Until DNS propagates:** https://sourcea-com.pages.dev/sourcea/start.html
