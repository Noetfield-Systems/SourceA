# VIRLUX Worker Blueprint — Supabase RLS harden (staging)

**Saved:** 2026-06-09T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**trace_id:** `governance_goal_specialist-20260609-005`  
**parent_trace:** `governance_goal_specialist-20260609-004`  
**worker_lane:** `virlux` (portfolio) · **execution_authority:** false (advocate blueprint — Brain assigns `sa-XXXX`)  
**project:** `virlux-staging` · ref `bueoakgiisvufxfbdvoa`  
**urgency:** P0 portfolio security (parallel to SourceA factory — do not block AUTO-RUN)

---

## Brain routing header (paste into Worker INBOX)

```
PLAN WITH NO ASF — VIRLUX ONE TURN — Supabase staging RLS harden (revoke + deny policies + verify)

Parent: governance_goal_specialist-20260609-004 · Supabase email 2026-06-08 CRITICAL
Project: virlux-staging (bueoakgiisvufxfbdvoa)
Repo: ~/Desktop/VIRLUX only — NEVER edit SourceA

Pre-flight:
  - Read os/agents/auto-virlux-delivery/MEMORY.md + INCIDENTS.md
  - Read apps/api/prisma/migrations/20250608000000_enable_rls/migration.sql (already enables RLS, 0 policies)
  - Secrets: ~/.sina/secrets.env (Tier 3) — VIRLUX_STAGING_DB_PASSWORD, never commit keys

Deliverables (all required):
  1) New Prisma migration: revoke anon/authenticated grants + explicit deny-all policies on all 13 public tables
  2) Apply to staging DB (prisma migrate deploy with DIRECT_URL)
  3) Post-deploy proof: anon PostgREST cannot SELECT User/RefreshToken; Prisma API login/smoke still PASS
  4) Incident closeout in ~/.sina/agent-workspaces/virlux/INCIDENT_REPORT_ALWAYS.md
  5) Receipt: docs/receipts/sa-XXXX-virlux-supabase-rls-harden.md

Closeout: WORKER_ROUND_REPORT → broker submit · one sa only
```

---

## Context (disk truth — do not re-debate)

| Fact | Value |
|------|-------|
| RLS enabled | All 13 `public` tables — migration `20250608000000_enable_rls` |
| Policies | 0 per table — deny-by-default for JWT roles, but linter WARN |
| Grants | `anon` + `authenticated` still have SELECT/INSERT/UPDATE/DELETE on all tables |
| Sensitive cols | `User.passwordHash`, `RefreshToken.tokenHash`, `KycSubmission.documentNumber`, `Partner.webhookSecret`, `TeamInvite.token` |
| App access path | Prisma via `DATABASE_URL` (postgres / virlux_api) — **not** supabase-js in apps |
| Email Jun 8 | Valid if sent before RLS migration; live advisor now INFO `rls_enabled_no_policy` |

**Goal:** Defense in depth — REVOKE Data API grants + explicit deny policies + verification receipt. Optional: rotate anon/publishable keys in Supabase dashboard (founder/executor documents; keys in Vercel env only).

---

## Tables (all must be covered)

`Organization` · `User` · `TelegramLink` · `RefreshToken` · `Wallet` · `Quote` · `Transaction` · `PaymentIntent` · `KycSubmission` · `LedgerEntry` · `AuditLog` · `TeamInvite` · `Partner`

---

## Implementation spec

### 1) Create migration `apps/api/prisma/migrations/20250609000000_supabase_api_lockdown/migration.sql`

```sql
-- VIRLUX: Lock down Supabase Data API (anon/authenticated) on application tables.
-- Prisma API uses DATABASE_URL (postgres/virlux_api) and bypasses these roles.
-- Law: governance_goal_specialist-20260609-004

-- Belt 1: explicit deny policies (satisfies Supabase linter; documents intent)
DO $$
DECLARE
  t text;
BEGIN
  FOREACH t IN ARRAY ARRAY[
    'Organization','User','TelegramLink','RefreshToken','Wallet','Quote',
    'Transaction','PaymentIntent','KycSubmission','LedgerEntry','AuditLog',
    'TeamInvite','Partner'
  ]
  LOOP
    EXECUTE format(
      'CREATE POLICY "block_data_api_%s" ON %I FOR ALL TO anon, authenticated USING (false) WITH CHECK (false)',
      lower(t), t
    );
  END LOOP;
END $$;

-- Belt 2: revoke table privileges from JWT roles
REVOKE ALL ON TABLE
  "Organization","User","TelegramLink","RefreshToken","Wallet","Quote",
  "Transaction","PaymentIntent","KycSubmission","LedgerEntry","AuditLog",
  "TeamInvite","Partner"
FROM anon, authenticated;

-- Ensure RLS stays on (idempotent)
ALTER TABLE "Organization" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "User" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "TelegramLink" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "RefreshToken" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Wallet" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Quote" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Transaction" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "PaymentIntent" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "KycSubmission" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "LedgerEntry" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "AuditLog" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "TeamInvite" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Partner" ENABLE ROW LEVEL SECURITY;
```

**Note:** If `CREATE POLICY` fails because policy exists, drop `block_data_api_*` first or use `IF NOT EXISTS` pattern via DO block check.

### 2) Apply staging

```bash
cd ~/Desktop/VIRLUX
# Load DB URLs from secrets — executor only
bash scripts/staging-supabase-db-url.sh   # writes/prints pooler + direct URLs
cd apps/api
npx prisma migrate deploy
```

Use `DIRECT_URL` for migrations per existing VIRLUX staging scripts.

### 3) Verify (executor — record output in receipt)

**A. SQL checks (Supabase SQL editor or psql)**

```sql
SELECT tablename, policyname FROM pg_policies WHERE schemaname='public' ORDER BY tablename;
SELECT grantee, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE table_schema='public' AND grantee IN ('anon','authenticated')
ORDER BY table_name;
-- Expect: zero rows for anon/authenticated after REVOKE
```

**B. PostgREST anon probe (must NOT return passwordHash rows)**

```bash
# Use staging anon key from Supabase dashboard — NEVER paste into git
curl -s "https://bueoakgiisvufxfbdvoa.supabase.co/rest/v1/User?select=id,email" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY"
# Expect: [] or permission error — NOT user rows with sensitive fields
```

**C. App path still works**

```bash
cd ~/Desktop/VIRLUX
npm run deploy:smoke
# or minimal: curl staging API health/login if available
```

**D. Supabase Security Advisors** — refresh; CRITICAL `rls_disabled_in_public` and `sensitive_columns_exposed` should clear or downgrade.

### 4) Optional key rotation (founder dashboard — document in receipt)

1. Supabase → Settings → API → rotate anon + publishable keys  
2. Update Vercel env for api/app/web staging projects only  
3. Confirm no `NEXT_PUBLIC_SUPABASE_*` in repo grep

---

## Acceptance criteria (PASS/FAIL)

| # | Criterion |
|---|-----------|
| 1 | Migration committed under `apps/api/prisma/migrations/` |
| 2 | `pg_policies` has `block_data_api_*` on all 13 tables |
| 3 | `anon`/`authenticated` have **no** table grants on public app tables |
| 4 | Anon REST probe returns no `User`/`RefreshToken` data |
| 5 | `npm run deploy:smoke` (or documented API login) PASS |
| 6 | `INCIDENT_REPORT_ALWAYS.md` appended with closeout + trace ids |
| 7 | No secrets in git diff |

---

## Incident closeout template (append to virlux workspace)

```markdown
## Supabase RLS harden — YYYY-MM-DD
- Alert: Supabase email CRITICAL rls_disabled / sensitive_columns (virlux-staging)
- Parent trace: governance_goal_specialist-20260609-004
- Worker trace: governance_goal_specialist-20260609-005 / sa-XXXX
- Action: migration 20250609000000_supabase_api_lockdown — revoke + deny policies
- Verify: anon REST blocked · deploy:smoke PASS · advisors refreshed
- Keys rotated: yes/no
- Status: CLOSED / PARTIAL
```

---

## Brain registry suggestion

| Field | Value |
|-------|-------|
| Title | VIRLUX staging Supabase RLS harden — revoke grants + deny policies + verify |
| Phase | phase-v0-verify-gates or security-hotfix |
| Priority | P0 portfolio security |
| Depends | None — parallel to GOAL-AUTH-LIVE |
| Blocks | VIRLUX pilot demos with real KYC/users until PASS |

---

## Governance constraints (non-negotiable)

- **FILE_STORAGE:** secrets Tier 3 only (`~/.sina/secrets.env`, Vercel env)  
- **No SourceA edits**  
- **Founder:** Supabase dashboard clicks for key rotation — no Terminal  
- **TrustField money flow:** unchanged — VIRLUX infra separate from TF/NF MSB posture  

---

*End blueprint — Brain routes to VIRLUX Worker as next portfolio `sa-XXXX`.*
