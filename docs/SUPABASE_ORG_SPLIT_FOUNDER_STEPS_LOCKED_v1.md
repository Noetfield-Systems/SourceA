# Supabase org split — founder steps — LOCKED v1

**Saved:** 2026-06-20T22:20:00Z · **Authority:** ASF · **URGENT:** free org = **2 active projects max**  
**Map:** `data/supabase-cloud-project-map-v1.json`

Your org has **3 projects**. Free tier allows **2 active** at once. **Pause or delete** VIRLUX + 777 first — then unpause SourceA.

---

## Do this now (order matters)

### 1. Pause **virlux-staging** (`bueoakgiisvufxfbdvoa`)

1. Open: **https://supabase.com/dashboard/project/bueoakgiisvufxfbdvoa/settings/general**
2. Scroll to **Pause project** → confirm **Pause**
3. Wait until dashboard shows **Paused**

*(Or **Delete project** at bottom if you want permanent removal — repos already hold schema.)*

### 2. Pause **the777foundation** (`mmdhnktybjpwlwdczgbq`)

1. Open: **https://supabase.com/dashboard/project/mmdhnktybjpwlwdczgbq/settings/general**
2. **Pause project** → confirm
3. Wait until **Paused**

*(Migrations safe in `~/Desktop/The 777 Foundation/supabase/migrations/`.)*

### 3. Unpause **SourceA** (`kazemnezhadsina144-dot's Project`)

1. Org home → click **kazemnezhadsina144-dot's Project** (currently paused)
2. **Restore project** / **Unpause**
3. **Settings → API** → copy URL + anon key → `~/.sourcea-secrets/portfolio-spine.env`

Tell the agent: **“Both paused + SourceA up”**

---

## Why pause first (not delete)

- **Pause** frees your **2 active project** slots immediately (paused projects don’t count).
- **Delete** is permanent — only if you’re sure exports aren’t needed.
- VIRLUX + 777 **repo copies are already the truth** — cloud was optional.

---

## What you had (from your dashboard)

| Dashboard name | Region | Status | Keep? |
|----------------|--------|--------|-------|
| **kazemnezhadsina144-dot's Project** | us-west-2 | **Paused** | **YES — unpause (SourceA)** |
| **virlux-staging** | ca-central-1 | NANO | **NO — export then pause** |
| **the777foundation** | ca-central-1 | NANO | **NO — export then pause** |

---

## Step A — Bring SourceA up (do this first)

1. Supabase dashboard → click **`kazemnezhadsina144-dot's Project`**
2. Click **Restore project** / **Unpause** (wording varies)
3. Wait until status is **Active** (not paused)
4. **Settings → API** → copy:
   - Project URL  
   - `anon` public key  
5. Open **`~/.sourcea-secrets/portfolio-spine.env`** and paste:

   ```
   SUPABASE_URL=https://YOUR_REF.supabase.co
   SUPABASE_ANON_KEY=eyJ...
   SOURCEA_SUPABASE_TIER=portfolio-spine
   ```

6. Tell the agent: **“SourceA Supabase unpaused + keys pasted”**

---

## Step B — VIRLUX out of Supabase (keep repo updates)

**Already on disk (nothing lost if you pause cloud):**

- Migrations pointer: `SourceA/infra/supabase/labs-sandbox/`
- Receipts: `VIRLUX/.virlux-receipts/` + `receipt-store.ts` (disk is primary)
- Prisma schema: `VIRLUX/apps/api/prisma/schema.prisma`

**Before pause (optional — only if you care about cloud-only rows):**

1. Open **`virlux-staging`** project → **Storage** → bucket `virlux-receipts` → download any files  
2. Save into: **`~/Desktop/VIRLUX/data/supabase-export/`** (create folder)  
3. **Table Editor** → export any tables with data → same folder  

**Then:**

4. **Project Settings → General → Pause project** (or delete after export if you are sure)

**After pause:** VIRLUX keeps shipping on Vercel. Receipts stay in repo / `.virlux-receipts`. No Supabase URL needed in production env.

Tell the agent: **“VIRLUX Supabase paused — repo-native”**

---

## Step C — 777 Foundation out of Supabase (keep repo updates)

**Already on disk (nothing lost if you pause cloud):**

- All migrations: **`~/Desktop/The 777 Foundation/supabase/migrations/`** (001–014)  
- Manifest: **`supabase/production.project.json`** (ref `mmdhnktybjpwlwdczgbq`)

**Before pause (export live user data once):**

1. Open **`the777foundation`** project → **Table Editor**
2. Export CSV (or SQL dump) for tables that matter:
   - `path_progress` · `launch_waitlist` · `profiles` · `contribution_ledger` · `session_artifacts` (if they have rows)
3. Save into: **`~/Desktop/The 777 Foundation/supabase/seed/export/`** (create folder — **do not commit secrets**)

**Then:**

4. **Pause project** on dashboard

**After pause:** Public site still works. Path progress falls back to **localStorage** (already built). Admin/auth features that need DB stay off until you re-link or move to portfolio-spine later.

Tell the agent: **“777 Supabase paused — export in seed/export”**

---

## Step D — Verify (agent runs)

```bash
bash ~/Desktop/SourceA/scripts/run-portfolio-supabase-daily-v1.sh
```

You want: **portfolio-spine green** · VIRLUX/777 **not required** in daily ping.

---

## One sentence

**Unpause SourceA project + paste keys → export 777 + VIRLUX data into their repos → pause those two projects.** Repos keep all structure; cloud was optional runtime.
