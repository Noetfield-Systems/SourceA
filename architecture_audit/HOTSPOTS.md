# HOTSPOTS.md

Ranked performance offenders (investigation mode — no fixes applied).

## Tier S — Catastrophic (minutes, blocks hub)

| Rank | Hotspot | Location | Why | Est. runtime |
|------|---------|----------|-----|--------------|
| S1 | `POST /refresh` | server + `run_refresh_pipeline` | 4 subprocesses + full `build_payload` + HTML write | 60–230s |
| S2 | `hub_after_mutation()` on ~28 POST routes | `sina-command-server.py` | Full rebuild per button click | 15–60s each |
| S3 | `build-sina-command-panel.py` strict | CI path | build + 40 validators | 2–10 min |
| S4 | Concurrent E2E + refresh + find_critical_bugs | process overlap | SIGKILL 137, lock contention | unpredictable |

## Tier A — Severe (seconds–minutes)

| Rank | Hotspot | Location | Why |
|------|---------|----------|-----|
| A1 | `build_payload()` monolith | `sina_command_lib.py:3503` | ~50 synchronous module calls + subprocess per request |
| A2 | `GET /api/hub-sync` | server:159 | Calls `build_payload()` in request thread on every auto-sync |
| A3 | `goal1_auto_run_payload()` inside build | subprocess broker poll embedded in every rebuild |
| A4 | `healthy-drain-orchestrator status` subprocess | inside `build_payload` | 15s timeout per build |
| A5 | `validate-hub-p0-no-autorun-v1.sh` | inside `hub_after_mutation` | Up to 90s after every mutation |
| A6 | JSON serialize 2.7MB | `write_panel_outputs` | CPU + disk thrash on every T2 mutation |

## Tier B — Moderate (was worse before L0 fix)

| Rank | Hotspot | Location | Why |
|------|---------|----------|-----|
| B1 | IC `clear_session` was calling `hub_after_mutation` | server (pre-fix) | 15s per clear — **partially fixed to T0** |
| B2 | IC dry `chat` was calling `hub_after_mutation` | server (pre-fix) | **partially fixed to T0** |
| B3 | `ecosystem_subjects.ecosystem_payload(refresh=True)` | build_payload when refresh | Full ecosystem rescan |
| B4 | `founder_threads_payload(refresh_scan=True)` | refresh path | Thread rescan |

## Tier C — Structural complexity

| Rank | Pattern | Impact |
|------|---------|--------|
| C1 | O(modules) per build — ~50 imports/calls | Linear in hub feature count |
| C2 | No incremental payload merge — always full dict | O(payload size) write every mutation |
| C3 | ThreadingHTTPServer + `_HUB_LOCK` | Concurrent requests queue on lock; stale cache reads |
| C4 | `applyPayload` shallow merge in UI | Stale nested objects after partial API responses |
| C5 | Duplicate queue truth readers | REGISTRY + truth + factory-now + healthy-queue |

## Disk thrashing

| Pattern | Files touched per `/refresh` |
|---------|---------------------------|
| Pipeline | PROGRAM_PROGRESS, bowl/state, MASTER_ORDERS, fleet registry |
| Panel | command-data.json, command-data-shell.json, index.html |
| Module mutations | + per-action SSOT files before rebuild |

**Estimated writes per founder session (heavy use):** 10–50 full JSON rewrites.

## Blocking operations

| Operation | Blocks |
|-----------|--------|
| `hub_after_mutation` | HTTP response until complete |
| `POST /refresh` | Browser 120s AbortController |
| `fcntl` E2E lock | Second E2E instance (cancelled) |
| `factory_validation_lock` | Strict build vs E2E |

## Long polling

| Mechanism | Interval | Cost |
|-----------|----------|------|
| Advisor track `setInterval` | 5s | GET discussion API |
| Goal1 "auto-refresh 25s" | UI copy | hub-sync implied |
| `hubAutoSync` silent | on error/recovery | GET hub-sync → build_payload |

No WebSocket — all HTTP.

## Heavy serialization

- `command-data.json` ~2.7MB `json.dumps` per `write_panel_outputs`
- Shell strip pass reads full dict again
- Browser `JSON.parse` on full load after shell

## Recursive / circular refresh risk

```
[MITIGATED] update-progress → bowl → panel nested build (env skips)
[ACTIVE] hub-sync poll → build_payload while mutation holds lock
[CANCELLED] E2E POST /refresh during audits
```

## O(N²) / O(N³) candidates

| Candidate | Mechanism |
|-----------|-----------|
| O(modules²) risk | If payload modules cross-call each other during build (ecosystem + threads + commitments overlap) |
| O(agents × rebuild) | 8 agents scoreboard verify → 8 full rebuilds if founder clicks each |
| O(tabs × full load) | Lazy load helps but `applyPayload` after `/refresh` loads everything |

## Worst offender summary

**#1 Root cause:** `hub_after_mutation()` is the default success handler for nearly every POST — coupling all UI mutations to a monolithic ~50-module synchronous rebuild and multi-MB disk write.

**#2 Aggravator:** `GET /api/hub-sync` still calls `build_payload()` — background polling rebuilds in memory even when founder did nothing.

**#3 Historical:** Backend E2E required `POST /refresh` inside audit — multiplied contention (now cancelled).
