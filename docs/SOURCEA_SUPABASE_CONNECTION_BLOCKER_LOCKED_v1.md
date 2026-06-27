# SourceA Supabase Connection Blocker (LOCKED v1)

**Saved:** 2026-06-27T10:18:00Z  
**Authority:** ASF founder note  
**Supabase tier SSOT:** `data/supabase-portfolio-tiers-v1.json`  
**Project map:** `data/supabase-cloud-project-map-v1.json`  
**Secrets location:** `~/.sourcea-secrets/` only  

---

## Founder Note

The actual blocker last time was not the amount of planning work. The blocker was Supabase access.

Founder did not have the Supabase password, so Cursor/agents could not log in or complete the connection chain from Cloudflare Workers to Cloudflare/Railway cloud workers and Supabase.

SourceA has produced more than 7000 plans across the system, but those plans are not yet reachable from a live database. The team decided to move the plan registry and runtime-readable plan data to Supabase, but the connection failed because founder account access/secrets were not available.

This happened during SourceA Worker work. Future agents should reuse the experience from Hub Pro / cloud worker / SourceA Worker lanes instead of restarting the diagnosis.

---

## Current Blocker

The first blocker was **founder-owned Supabase authentication and secret recovery**, not code.

As of 2026-06-27T10:26:48Z:

- `portfolio-spine` Supabase URL is present and reachable.
- anon key is present.
- service/server key is present.
- local DB password / DB URL / management token is still missing.
- `public.sourcea_plan_registry` does not exist yet.
- `data/all-remaining-plan-backlog-v1.json` loads 23,485 plan rows ready for import.

Agents can prepare schemas, importers, validators, Cloudflare bindings, and Railway env instructions. Agents must not invent or store Supabase passwords, service-role keys, or access tokens in the repo.

---

## Target Project

For SourceA / Forge / plan registry work, use:

- Project: `portfolio-spine`
- Ref: `ldfruywifqnfpwsfgmdl`
- URL: `https://ldfruywifqnfpwsfgmdl.supabase.co`
- Secrets file: `~/.sourcea-secrets/portfolio-spine.env`

Do not resume `virlux-staging` or `the777foundation` for this task. Those are marked paused/never-resume in the Supabase project map.

---

## What Founder Must Do

1. Recover Supabase dashboard access.
   - If password login is used: reset the Supabase password.
   - If GitHub/Google login is used: recover that provider login.
   - Enable MFA/recovery codes after login.

2. Open the SourceA project:
   - `https://supabase.com/dashboard/project/ldfruywifqnfpwsfgmdl`

3. Copy project connection values into local secret files, never into the repo:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - database password or pooled connection string for migrations/imports
   - service-role key only for server/cloud jobs that truly need it

4. Store secrets here:
   - `~/.sourcea-secrets/portfolio-spine.env`
   - `~/.sourcea-secrets/portfolio-spine-db.env` if DB password/connection string is separate

5. Tell the agent:

```text
SourceA Supabase access restored. portfolio-spine env is filled.
```

If the table is still missing, either:

- fill `~/.sourcea-secrets/portfolio-spine-db.env` with `SUPABASE_DB_PASSWORD=...` or `SUPABASE_DB_URL=...`, or
- open Supabase SQL Editor and run `infra/supabase/portfolio-spine/migrations/004_sourcea_plan_registry_v1.sql` manually.

---

## What Agents Do After Access Is Restored

1. Run a light secrets presence check without printing secrets.
2. Verify `portfolio-spine` is reachable.
3. Create/verify `public.sourcea_plan_registry` with RLS.
4. Import existing plan JSON/markdown into Supabase.
6. Add read APIs for Brain / Chat Unify / Hub Pro / cloud workers.
7. Set Cloudflare Worker secrets and Railway environment variables.
8. Run a small read-only smoke:
   - plan count is visible,
   - one plan can be fetched by id,
   - Brain/Hub can read through the intended API,
   - no service-role key is exposed to browser code.

---

## Decision

Reset/recover Supabase access first. Then agents connect the chain:

```text
Supabase portfolio-spine
→ plan registry tables
→ import 23,485 remaining plan rows from `data/all-remaining-plan-backlog-v1.json`
→ Cloudflare Worker / Railway env
→ Hub Pro / Brain / Chat Unify read APIs
→ public or founder-facing retrieval
```

Until founder Supabase access and local secret files are restored, the correct agent action is preparation only, not another code marathon.

