# @noetfield/auth-core

Shared Supabase Auth helpers for **SourceA**, **Noetfield**, and **TrustField** Next.js apps.

**SSOT:** `data/cross-domain-auth-surfaces-v1.json`  
**Identity project:** portfolio_spine (`ldfruywifqnfpwsfgmdl`)

## Install (consumer repo)

```bash
npm install @supabase/ssr @supabase/supabase-js
```

Copy or link this package, then:

```ts
import { createBrowserClient } from "@noetfield/auth-core/browser";
import { createServerClient } from "@noetfield/auth-core/server";
import { authMiddleware } from "@noetfield/auth-core/middleware";
```

## Env

```
NEXT_PUBLIC_SUPABASE_URL=https://ldfruywifqnfpwsfgmdl.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=...
```

## Routes (each venture app)

- `/auth/sign-in`
- `/auth/sign-up`
- `/auth/callback` — PKCE `exchangeCodeForSession`
- `/auth/sign-out`

Register all callback URLs in Supabase Dashboard → Authentication → URL configuration.

## Server protection

Use `getClaims()` in middleware — not `getSession()` alone. See `src/middleware.ts`.
