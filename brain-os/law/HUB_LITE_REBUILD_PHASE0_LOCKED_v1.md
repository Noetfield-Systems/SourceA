# HUB-LITE-REBUILD Phase 0 — LOCKED v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**PICK:** `HUB-LITE-REBUILD A` (ASF five-step, 2026-06-05)  
**Effect:** Emergency lite hub this week · Phase 1 surface API next · monolith deprecated · **Refresh = light by default** · commercial 11.x not blocked

## Phase 0 shipped behaviors

| # | Behavior | Implementation |
|---|----------|----------------|
| 0.1 | No idle 9MB prefetch | `app.js` `scheduleIdleFullPrefetch` no-op |
| 0.2 | Shell-only boot | `loadCommandDataShell` — no `command-data.json` fallback |
| 0.3 | Throttled polls | Goal1: 120s when SSE; Home skips goal1 poll when SSE connected |
| 0.4 | Light Refresh default | `POST /refresh` body `{mode:"light"}` → `hub_light_refresh()` |
| 0.5 | Tab slices | `GET /api/slice/<domain>` + `loadTabSlice()` on heavy tabs |
| 0.6 | Maintainer law | `hub_self_refresh` / align only; `build-sina-command-panel` ASF strict-hub only |

## Full refresh (founder rare path)

`POST /refresh` with `{ "mode": "full" }` — queues worker rebuild when `:13030` healthy.

## Phase 1 (next, not blocking commercial)

- `/api/surface/v1` header chips SSOT
- SSE-driven slice invalidation
- Deprecate `command-data.json` for all tabs

## Commercial

PLAN-300 / 11.01–11.03 execution **not blocked** by hub lite work.

**Receipt:** `~/.sina/hub-lite-rebuild-five-step-pick-v1.json`
