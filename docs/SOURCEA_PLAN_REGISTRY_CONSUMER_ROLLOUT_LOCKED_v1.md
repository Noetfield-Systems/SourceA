# SourceA Plan Registry Consumer Rollout (LOCKED v1)

**Saved:** 2026-06-27T11:04:00Z  
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

---

## Noetfield / TrustField Split Decision

Current policy:

- Keep TrustField rows mirrored in SourceA with `lane=trustfield` until Noetfield import and read-back are confirmed.
- Do not prune TrustField rows from `portfolio-spine` during this slice.
- Noetfield can receive a separate import from `scripts/noetfield_trustfield_plan_registry_import_v1.py`.

Decision gate before pruning:

1. Noetfield Supabase table exists.
2. Import count and sample read-back are green.
3. Hub/Chat Unify can still query SourceA-owned and TrustField-owned rows by lane.
4. Founder approves mirror vs Noetfield-only ownership.

---

## Future Receipt Write Path

Execution receipts should be attached by FBE/Railway only, using server-side service role.

Target future shape:

```text
plan_id + run_id + receipt_path + status + completed_at
```

Browser/UI consumers remain read-only.

---

## Eval And Monitoring

Light checks must cover:

- Supabase count is `>= 23485`
- known plan lookup works
- Hub route returns JSON
- Chat Unify action returns JSON
- no response contains secret-like values
- Brain adapter docs exist before Brain runtime edits

Operational monitoring belongs in Hub Pro first:

- plan count
- last read status
- lookup result
- upstream read error

