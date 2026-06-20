# Hub State API Contract v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Status:** Design + gateway stubs (Track 2 L5)  
**Date:** 2026-06-10  
**Pairs with:** [HUB_LIVE_SYSTEM_DESIGN_v1.md](HUB_LIVE_SYSTEM_DESIGN_v1.md)

## Single-writer law

| Artifact | Canonical writer (target) | Gateway today | Notes |
|----------|---------------------------|---------------|-------|
| `~/.sina/run-inbox-disk-truth-v1.json` | State `:13031` (N2) | Read via `GET /api/live/queue` | Multiple scripts write until N2 |
| `PROGRAM_PROGRESS.json` | State `:13031` | Read-only in hub | Builder reads |
| `~/.sina/factory-now-v1.json` | Agent runtime `:13032` (N3) | Read via `GET /api/live/factory` | Gateway reads |
| `command-data-shell.json` | Rebuild worker `:13030` | Read via `/api/hub-sync` | Worker only |
| `hub-rebuild-queue-v1.jsonl` | `hub_queue_lib_v1.enqueue` | Gateway POST enqueue | Shared contract |
| `hub-live-events-v1.jsonl` | Gateway + worker append | SSE `/api/live/v1` | Append-only |

**Rule:** If two components can write the same file, one of them is wrong.

## Gateway read stubs (`:13020`)

| Route | Method | Returns |
|-------|--------|---------|
| `/api/live/queue` | GET | `sa_id`, `queue_role`, `pos`, `pending`, `generation_id` |
| `/api/live/factory` | GET | `frozen`, `mode`, `factory_now`, `generation_id` |
| `/api/live/v1` | GET (SSE) | Live events from `hub-live-events-v1.jsonl` |

## Staleness contract

- Every slice includes `generation_id` from shell when available.
- Browser ignores slice data when `slice.generation_id < shell.generation_id` (when both present).

## N2 State service (`:13031`) — not started until ASF approves

- Sole writer for queue truth + progress projections.
- Gateway proxies queue mutations to State; returns 202.
- Validator: `validate-hub-state-writers-v1.sh` flags duplicate writers until N2 ships.

## N3 Agent runtime (`:13032`) — after State stable

- Owns FREEZE, IC session spawn, agent-loop factory paths.
- Gateway forwards POSTs; no panel rebuild on request thread.
