# Forge Production MVP — local runtime

Execution loop: **POST /tasks → BullMQ → governance → executor → state → GET /tasks/:id**

## Quick start (no Docker)

```bash
cd ~/Desktop/SourceA
bash infra/forge-mvp/start-local.sh --smoke
```

Exit after smoke (don't keep services running):

```bash
bash infra/forge-mvp/start-local.sh --smoke --smoke-only
```

## Validate all phases

```bash
cd ~/Desktop/SourceA
bash infra/forge-mvp/validate.sh --smoke
```

## Docker (all services)

```bash
cd ~/Desktop/SourceA
docker compose -f infra/forge-mvp/docker-compose.yml up --build
bash infra/forge-mvp/smoke.sh
```

Requires Docker + `~/.sina/secrets.env` mounted for LLM keys.

## API contract

**POST /tasks**
```json
{ "goal": "build settings page", "provider": "openai" }
```
Response: `{ "task_id": "tsk_...", "status": "queued" }`

**GET /tasks/:id** — `{ task_id, status, created_at, result? }`

**GET /state/:id** — `{ task_id, created_at, status, result? }`

## Package layout

| Package | Path |
|---------|------|
| Core domain | `apps/forge-core/src/{types,state,registry,tasks}/` |
| API | `apps/forge-core-api/src/{routes,services}/` |
| Worker | `apps/forge-worker/src/{queue,executor,governance}/` |
| Governance | `apps/forge-governance/src/service/` |

## Manual (three terminals)

**Terminal 1 — Redis:**
```bash
cd ~/Desktop/SourceA/apps/forge-core && npm run ensure-redis
```

**Terminal 2 — Worker:**
```bash
export SOURCEA_ROOT="$HOME/Desktop/SourceA" FORGE_EMBEDDED_REDIS=0
cd ~/Desktop/SourceA/apps/forge-worker && npm run dev
```

**Terminal 3 — API + smoke:**
```bash
export SOURCEA_ROOT="$HOME/Desktop/SourceA" FORGE_EMBEDDED_REDIS=0
cd ~/Desktop/SourceA/apps/forge-core-api && npm run dev
```
```bash
cd ~/Desktop/SourceA && bash infra/forge-mvp/smoke.sh
```

Keys load from `~/.sina/secrets.env` automatically.
