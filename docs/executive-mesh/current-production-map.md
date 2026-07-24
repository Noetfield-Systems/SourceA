# SourceA Executive Mesh — Current Production Map

**decision_id:** `NF-EXECUTIVE-MESH-V1`  
**As of:** 2026-07-24  
**Purpose:** Inventory before vertical slice. Reuse, do not replace.

| Component | Path / surface | Responsibility | Authoritative data owner | Integration boundary | Missing for Mesh | Migrate? |
|-----------|----------------|----------------|--------------------------|----------------------|------------------|----------|
| ECP v0 kernel | `packages/executive-control-plane-v0` | Deterministic Governor API | Package in-memory / callers | Pure TS; no CF | Role Pods, DO host | N — wrap |
| Brain chat | `cloud/workers/sourcea-brain-chat-v1` | Public chat + Workers AI | KV/AI bindings | Edge chat only | Not Authority | N |
| Loop specialist | `cloud/workers/loop-specialist-tick-v1` | Cron → Railway FBE dispatch | Secrets `FBE_CLOUD_WORKER_URL` | CF→Railway HTTP | Not Governor | N — pattern reuse |
| Cloud auto runtime | `cloud/workers/cloud-auto-runtime-tick-v1` | Cycle tick → FBE | Same | CF→Railway | — | N |
| Deadman | `cloud/workers/sourcea-deadman-v1` | Loop staleness | Supabase `loop_registry` | CF→Supabase | Pulse watch for mesh | N — reuse |
| FBE Railway | `scripts/fbe_cloud_worker_http_v1.py` | Heavy forge/bay executor | Railway service | HTTP API | Not webpage repair | N — later slices |
| Forge BullMQ | `apps/forge-core` + Redis | Task queue | Redis hot only | Local/Railway forge | Not executive SSOT | N |
| Supabase spine | `infra/supabase/portfolio-spine` | Receipts, loops, truth_log | Postgres + RLS | Service role writes | executive_runs tables | Y — add migration |
| Context packet | `scripts/pre_llm/context_packet` | Pre-LLM context | Files/scripts | Python | Mesh ContextPack TS | Extend concepts |
| Governed work packet | `scripts/lib/governed_work_packet_v1.py` | HTU + terminals | SourceA schemas | Python | — | N — reuse vocab |
| Decision capacity | SG live policies + SourceA scripts | Policy coverage | SG SSOT | GATED promote | — | N |
| Runway Goal Kernel | `noetfield-runway-live-staging` | GoalDO + HDIR webpage repair | DO SQLite + HDIR | `/v1/goals` | Slice-1 executor | N — consume |
| HDIR | `NOETFIELD-RUNWAY/noetfield-hdir` | webpage-build-deploy | HDIR runtime | Service binding | — | N |
| GHA deploy | `.github/workflows/deploy-sourcea-buyer-surfaces-v1.yml` | Buyer surface deploy | GitHub | Wrangler | Blueprint promote later | N |

## Gaps closed by slice-1

1. CF Durable Object Governor Worker wrapping ECP v0 — live: `https://sourcea-executive-governor-v1.sina-kazemnezhad-ca.workers.dev` (`MESH_SIMULATE=0`)
2. Four Role Pods (SG · Memory · Planner · Critic) at L0 — `packages/executive-mesh-v1`
3. Supabase executive_* tables applied (migration `015`) — apply receipt in `receipts/executive/`
4. WorkPacket route `RUNWAY_GOAL_KERNEL` → live staging `/v1/goals` + independent GET verify + canonical SSOT write 

## Explicit non-migrate

- Do not replace FBE with a second heavy executor  
- Do not put Goal state in Supabase (Runway DO remains goal host)  
- Do not add a second vector DB in slice-1  
