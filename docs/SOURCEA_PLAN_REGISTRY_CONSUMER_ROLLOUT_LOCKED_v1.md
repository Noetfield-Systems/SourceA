# SourceA Plan Registry Consumer Rollout (LOCKED v1)

**Saved:** 2026-06-27T11:12:44Z  
**Upstream contract:** `docs/SOURCEA_PLAN_REGISTRY_READ_CONTRACT_LOCKED_v1.md`  
**Supabase table:** `public.sourcea_plan_registry`  
**Current row floor:** `23485`

---

## One Law

Consumers read narrow slices from the plan registry. No consumer dumps the full backlog into UI state, Brain prompt context, or Chat Unify chat context.

---

## Brain Adapter Boundary

Brain may use a future retrieval adapter only after explicit Brain-runtime approval.

Allowed reads:

- exact `plan_id`
- `lane` plus `status` with `limit <= 5`
- count/health summaries

Forbidden:

- loading all `23485+` plans into the prompt
- exposing service-role keys, DB URLs, or server env names
- treating internal `prompt_path` as public website copy

Adapter shape:

```text
visitor question
→ classify whether plan registry is relevant
→ query /plan-registry with exact id or tiny lane/status filter
→ summarize 1-5 rows in public-safe language
→ cite sourcea.app public routes only when available
```

---

## Hub Pro Contract

Hub Pro may show:

- total plan count
- next rows by optional lane filter
- exact plan lookup
- source registry/prompt path for internal founder operations

Hub Pro uses local H1 route:

```text
GET /api/sourcea/plan-registry/v1?limit=5
GET /api/sourcea/plan-registry/v1?lane=<lane>&limit=5
GET /api/sourcea/plan-registry/v1?plan_id=<plan_id>
GET /api/sourcea/plan-registry/status/v1
```

---

## Chat Unify Contract

Chat Unify exposes a read-only machine:

```json
{
  "action": "plan_registry",
  "plan_id": "cu-score-0001"
}
```

or:

```json
{
  "action": "plan_registry",
  "lane": "chat_unify",
  "status": "open",
  "limit": 5
}
```

Hard limits:

- `limit <= 10`
- no writes
- no secret-bearing fields
- summarized use only
- next-action suggestions are advisory; execution routes back to Hub/FBE machines with receipts

---

## Brain Adapter Contract

Brain uses the public Cloudflare plan registry proxy as a live tool only when a visitor asks for a plan id or a small plan-registry slice.

Allowed:

- exact plan id such as `cu-score-0001`
- tiny list mode with `limit <= 5`
- public-safe summary fields only: `plan_id`, `title`, `status`, `lane`, `priority`

Forbidden:

- full backlog dumps
- service-role writes
- exposing `prompt_path`, DB URLs, service keys, or internal filesystem paths as public copy

---

## Noetfield / TrustField Split Decision

Current policy:

- TrustField ownership is `noetfield`; SourceA may temporarily keep legacy `lane=trustfield` registry mirror rows only for consumer read-back continuity.
- Do not prune legacy mirrored `lane=trustfield` rows from the SourceA plan registry during this slice.
- SourceA keeps the product-graduation export pack at `archive/sourcea-product-graduation-20260628/` as the versioned handoff record.
- Noetfield / TrustField own active imports, migrations, legal/entity docs, deploy config, and product-specific scripts outside SourceA active storage.
- Authority pointer: `data/supabase-portfolio-tiers-v1.json` → `supabase_repo_split_v1`.

Decision gate before pruning:

1. Noetfield Supabase table exists.
2. Product-owned import count and sample read-back are green in the Noetfield / TrustField process.
3. Hub/Chat Unify can still query SourceA-owned and TrustField-owned rows by lane.
4. Founder approves mirror vs Noetfield-only ownership.

---

## Future Receipt Write Path

Execution receipts should be attached by FBE/Railway only, using server-side service role.

Target future shape:

```text
plan_id + run_id + receipt_path + status + completed_at
```

Implemented server-side route:

```text
POST /api/sourcea/plan-registry/receipt-link/v1
```

Supported proof mode:

```json
{
  "plan_id": "cu-score-0001",
  "run_id": "example-run",
  "receipt_path": "~/.sina/example.json",
  "status": "dry_run",
  "dry_run": true
}
```

Browser/UI consumers remain read-only.

---

## Golden Queue Proof Rule

After Railway/FBE deploy, `/health` is not sufficient proof. Proof must also include:

- `/api/cloud-forge-run/queue/v1`
- current queue head or observed queue row
- `batch_id`
- no `mock_only` head unless explicitly marked as preview/recovery

If queue head is `mock_only`, the correct recovery is skip head or fix Railway dependencies. Do not redeploy repeatedly to solve a queue data problem.

---

## Eval And Monitoring

Light checks must cover:

- Supabase count is `>= 23485`
- known plan lookup works
- Hub route returns JSON
- Chat Unify action returns JSON
- no response contains secret-like values
- Brain adapter docs exist before Brain runtime edits
- queue proof route returns a `batch_id`
- receipt linkback dry-run returns a would-update payload without writing

Operational monitoring belongs in Hub Pro first:

- plan count
- last read status
- lookup result
- upstream read error

