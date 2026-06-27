# SourceA Plan Registry Read Contract (LOCKED v1)

**Saved:** 2026-06-27T10:57:00Z  
**Table:** `public.sourcea_plan_registry`  
**Rows imported:** `23,485`  
**Client:** `scripts/sourcea_plan_registry_client_v1.py`  
**FBE/Railway route:** `/api/sourcea/plan-registry/v1`  
**Cloudflare proxy:** `/plan-registry`

---

## One Law

Plan rows are read through public-safe APIs. Browser-facing consumers never receive service-role keys, DB passwords, or raw Supabase credentials.

---

## Query Contract

### Count / Next Rows

```text
GET /api/sourcea/plan-registry/v1?limit=20&offset=0
GET /api/sourcea/plan-registry/v1?status=open&lane=sourcea-site&limit=20
```

Returns:

```json
{
  "ok": true,
  "rows": [],
  "count": 20,
  "total": 23485,
  "filters": {
    "limit": "20",
    "offset": "0"
  },
  "contract": "sourcea-plan-registry-read-v1"
}
```

### Plan By ID

```text
GET /api/sourcea/plan-registry/v1?plan_id=sa-score-0001
```

Returns:

```json
{
  "ok": true,
  "plan_id": "sa-score-0001",
  "found": true,
  "rows": [
    {
      "plan_id": "sa-score-0001",
      "title": "..."
    }
  ]
}
```

---

## Consumer Rules

### Hub Pro

Hub Pro may show:

- total plan count
- next open plans by lane
- plan by id
- source registry and prompt path

Hub Pro must not expose service keys or DB connection strings.

### Chat Unify

Chat Unify may use the endpoint for:

- “next action” suggestions
- audit trail references
- plan id lookup
- lane-scoped work queue previews

It must not dump full plan backlog into chat context.

### Brain

Brain may query only narrowly:

- by exact `plan_id`
- by small `limit`
- by lane/status filters

Brain must summarize relevant rows and keep public voice clean. It must not paste internal paths unless the page or founder context is explicitly internal.

### Cloudflare Worker

Cloudflare `/plan-registry` proxies to FBE/Railway:

```text
GET /plan-registry?limit=20
GET /plan-registry?plan_id=sa-score-0001
```

The Worker forwards `FBE_INTERNAL_SECRET` only server-to-server.

---

## Allowed Public Fields

- `plan_id`
- `title`
- `status`
- `tier`
- `lane`
- `phase`
- `workstream`
- `priority`
- `priority_rank`
- `source_registry`
- `prompt_path`
- `updated_at`
- `payload` only on exact `plan_id` detail calls

---

## Forbidden In Responses

- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_DB_PASSWORD`
- `DATABASE_URL`
- `POSTGRES_URL`
- JWT/key material
- raw server env dumps

