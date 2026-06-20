# Hub Live System Design v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Status:** Design (ASF-approved direction)  
**Date:** 2026-06-10  
**Supersedes:** Fragmented “one JSON blob” mental model  
**Pairs with:** `HUB_STABILIZATION_v5.1_FINAL.md` (Track 1 — usable this week)

---

## Two tracks (both required)

| Track | Timeline | Outcome |
|-------|----------|---------|
| **Track 1 — Stabilize** | This week | Clicks &lt;1s, no request-thread rebuilds (v5.1 Phases A→B→C→E) |
| **Track 2 — Live system** | 4–8 weeks after Track 1 green | Clean map, single writers, real-time UI, no duplication |

Track 1 does **not** replace Track 2. Track 1 makes the current panel usable while Track 2 is built beside it.

---

## What “clean + live” means

| Today (broken) | Target (live) |
|----------------|---------------|
| 9MB `command-data.json` loaded/polled | Per-domain slices + shell nav only |
| 6+ `setInterval` polls in `app.js` | One SSE stream + on-demand tab fetch |
| Every mutation → full rebuild | Mutation → state write → event → coalesced rebuild |
| Queue truth in 4 readers | One State API owns queue/progress/factory |
| No app map | One diagram, one owner per box |
| “Refresh” = 230s block | “Refresh” = 202 + live `generation_id` bump on wire |

---

## Target app map (one page)

```
┌─────────────────────────────────────────────────────────────────┐
│  BROWSER  agent-control-panel/                                  │
│  • Shell layout (nav, freeze banner, queue chip)                  │
│  • Tab views fetch ONLY their slice                               │
│  • SSE client: /api/live/v1 (generation_id, freeze, queue, alerts)│
└────────────────────────────┬────────────────────────────────────┘
                             │ :13020
┌────────────────────────────▼────────────────────────────────────┐
│  GATEWAY  sina-command-server.py (thin)                           │
│  READ:  proxy GET /api/<domain>  OR serve cached slice            │
│  WRITE: POST /api/<domain> → forward to owner, return 202         │
│  LIVE:  GET /api/live/v1 → SSE (hub_generation, queue, freeze)    │
│  NEVER: build_payload, write panel JSON, validators, refresh pipe │
└─────┬──────────────────┬──────────────────┬─────────────────────┘
      │                  │                  │
      ▼                  ▼                  ▼
┌───────────────┐    ┌───────────────┐    ┌─────────────────┐
│ STATE         │    │ AGENT RUNTIME │    │ PANEL BUILDER   │
│ :13031+       │    │ :13032+       │    │ (external       │
│ (future N2)   │    │ (future N3)   │    │  worker :13030) │
│ SSOT only     │    │ factory FREEZE│    │                 │
│ queue         │    │ IC sessions   │    │ command-data-   │
│ progress      │    │ agent loop    │    │ shell.json      │
│ factory       │    │ spawn gate    │    │ command-data.json│
│ inbox         │    │               │    │ index.html      │
└───────┬───────┘    └───────┬───────┘    └────────▲────────┘
        │                    │                     │
        └──────────┬─────────┴─────────────────────┘
                   ▼
        ~/.sina/hub-rebuild-queue-v1.jsonl
        ~/.sina/hub-live-events-v1.jsonl   ← SSE feed source
                   │
                   ▼
        ┌─────────────────────┐
        │ REBUILD WORKER (1)  │  hub_rebuild_worker_v1.py · :13030
        │ coalesce · fcntl    │  → build_payload OFF request thread
        │ bump generation_id  │
        └─────────────────────┘
                 │
                 ▼
      ┌─────────────────────┐
      │ VALIDATOR (CLI)     │  find_critical_bugs / light E2E
      │ read-only           │  never in request path
      └─────────────────────┘
```

**Port rule:** `:13020` stays browser entry forever. `:13030+` only after `lsof` + ASF approval. Never `:13021–13023`.

---

## Single-writer table (eliminates duplication)

| Artifact | Only writer | Readers |
|----------|-------------|---------|
| `~/.sina/run-inbox-disk-truth-v1.json` | State service (Phase N) / scripts until then | Gateway, Monitor, validators |
| `PROGRAM_PROGRESS.json` | State service | Builder, Gateway slices |
| `factory-now-v1.json` | Agent runtime | Gateway, freeze banner |
| `command-data-shell.json` | Panel builder (worker) | Gateway hub-sync, browser boot |
| `command-data.json` | Panel builder (worker) | Lazy tab load, CI only |
| `hub-rebuild-queue-v1.jsonl` | `hub_queue_lib_v1.enqueue` | Worker |
| `hub-live-events-v1.jsonl` | Gateway + worker (append) | SSE broadcaster |

**Law:** If two components can write the same file, one of them is wrong.

---

## Real-time layer (SSE first, not WebSocket)

Why SSE over WebSocket for v1 live:
- One-way server→browser fits “state changed, repaint slice”
- Works through `ThreadingHTTPServer` with a small handler
- No new port; path `GET /api/live/v1`

### Event types on the wire

```json
{"type":"hub.generation", "generation_id": 42, "built_at": "..."}
{"type":"factory.freeze",   "frozen": true}
{"type":"queue.head",       "sa_id": "sa-0778", "pos": 2}
{"type":"rebuild.status",   "state": "running|done|error", "job_id": "..."}
{"type":"tab.invalidate",   "keys": ["agent_loop", "intelligence_circle"]}
```

### Browser behavior

1. On load: shell JSON + open SSE
2. On `hub.generation` change: refetch only stale tabs (not full 9MB)
3. On `tab.invalidate`: refetch that tab’s `GET /api/<domain>`
4. Remove redundant `setInterval` hubAutoSync loops (keep one SSE reconnect)

### Staleness contract

- Every slice response includes `generation_id`
- UI ignores slice if `generation_id < shell.generation_id`
- Worker bumps `generation_id` once per coalesced rebuild (v5.1 Phase C)

---

## Domain slices (replace monolith payload)

| Tab / concern | GET slice | POST owner | Notes |
|---------------|-----------|------------|-------|
| Nav + freeze | shell (disk) | — | &lt;50KB |
| Queue / YOU ARE HERE | `/api/live/queue` → State | — | sa_id from `queue.sa_id` |
| Goal1 | `/api/goal1-auto-run-status` | Agent runtime | already exists |
| Intelligence | `/api/intelligence-circle` | IC module | L0 cheap actions |
| Agent loop | `/api/agent-loop` | loop module | |
| Factory | slice from factory-now | Agent runtime | FREEZE banner |
| Bowl / todos | `/api/commitments` or bowl slice | respective SSOT | |
| Refresh | `POST /refresh` → 202 | enqueue only | worker rebuilds |

**Deprecate:** `GET /api/hub-sync` returning full built payload.  
**Replace with:** shell read + SSE + per-tab APIs.

---

## Migration path (both tracks)

### Week 1 — Track 1 (v5.1)

| Step | Approval | Result |
|------|----------|--------|
| A | `ASF: EDIT ALLOWED — Phase A only` | hub-sync &lt;200ms, refresh 202 |
| B | `ASF: Phase B approved` | no sync rebuild in handlers |
| C | `ASF: Phase C approved` | worker + four NEVER rules |
| E | `ASF: Phase E approved` | light E2E green |

### Weeks 2–4 — Track 2 foundation

| Step | Deliverable |
|------|-------------|
| L1 | `GET /api/live/v1` SSE + `hub-live-events-v1.jsonl` |
| L2 | `app.js`: one SSE client; kill duplicate poll timers |
| L3 | `hub-sync` → shell + `generation_id` only (already in A) |
| L4 | Tab loader: fetch slice if `generation_id` stale |
| L5 | Extract `hub_queue_lib_v1` consumers → document State API contract |

### Weeks 4–8 — Track 2 services (Phase N)

| Service | Port | Extract when |
|---------|------|--------------|
| Rebuild worker | 13030 | **Shipped (N1)** — queue consumer only |
| State | 13031 | After Track 2 L5 green + `lsof` + ASF N2 |
| Agent runtime | 13032 | After State stable + ASF N3 |
| Panel builder | daemon | Already worker on `:13030` |
| Validator | CLI | Already separate |

Gateway on `:13020` shrinks to proxy + SSE only.

---

## Success criteria (final system)

**Responsive (Track 1):**
- clear_session &lt;1s · refresh 202 &lt;1s · hub-sync &lt;200ms

**Live (Track 2):**
- UI updates within 2s of worker rebuild without manual Refresh
- Zero full `command-data.json` loads in normal browsing
- One SSE connection replaces N poll loops
- One writer per SSOT file
- App map fits on one page (this doc)

**Machine proof:**
- Four NEVER rules in request thread
- `audit_backend_e2e_light_v1.py` PASS
- `find_critical_bugs` critical 0

---

## What we deliberately do NOT do

- Microservices before Track 1 green
- WebSocket before SSE proves value
- Rewrite all 9k lines of `app.js` in week 1
- Merge conduct / INBOX desync into hub gates
- Drain factory while FREEZE ON

---

## Implementation status (2026-06-10)

| Step | Status |
|------|--------|
| Track 1 v5.1 A–E + N1 + P1–P10 | DONE |
| L1 SSE + `hub-live-events-v1.jsonl` | DONE |
| L2 SSE client + poll reduction | DONE (`app.js`) |
| L3 slim hub-sync contract | DONE |
| L4 tab slice loaders | DONE (agent-loop, IC, live/queue) |
| L5 State API contract + stubs | DONE |
| N2 State `:13031` scaffold | DONE (optional serve) |
| N3 Agent runtime `:13032` scaffold | DONE (optional serve) |

## Next action

1. **Founder:** Hard refresh hub (`Cmd+Shift+R`) — SSE live updates after Refresh  
2. **N2 full extract:** `ASF: Phase N2 approved` + empty `lsof :13031`  
3. **N3 full extract:** after State stable 1 week + `ASF: Phase N3 approved`
