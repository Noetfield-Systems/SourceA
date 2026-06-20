# Hub Unify Upgrade Proposal v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Type:** Research + upgrade proposal (no implementation in this doc)  
**Date:** 2026-06-10  
**Context:** Track 1 (v5.1) shipped — server request thread is clean. UI and E2E remain fragmented.  
**Goal:** One app mental model, one live client, one gate runner — less duplication, simpler E2E.

---

## 1. Research summary — what’s fragmented today

### 1.1 Browser app (`app.js` ~9,170 lines)

| Problem | Evidence |
|---------|----------|
| **Many independent poll loops** | 9× `setInterval` (advisor, autoFeed, loop, intelligence, ping 20s, hub-sync 45s, goal1 4s, prompt-feed 5s) |
| **Monolith payload mindset** | `applyPayload()` used 20+ times; expects full `command-data` shape |
| **hub-sync contract drift** | Server returns shell fields at top level; `hubAutoSync` still checks `json.data` → **auto-sync often no-ops** |
| **Duplicate fetches** | Same tab data via shell, hub-sync, per-tab GET, and post-mutation `json.data` |
| **No live push** | No SSE/WebSocket on hub; Monitor has separate `/api/live-ongoing-prompts` on :13021 |
| **No app map in code** | `HEAVY_TAB_KEYS` is implicit; no `TAB_REGISTRY` linking tab → API → slice keys |

### 1.2 Queue / state duplication (backend)

| Reader / writer | File / lib |
|-----------------|------------|
| Execution queue head | `~/.sina/run-inbox-disk-truth-v1.json` → `queue.sa_id` |
| Pick helper | `queue_sa_pick_lib_v1.py` |
| Healthy queue pack | `healthy_queue_ssot_lib.py` + `healthy-queue-30-active.json` |
| Factory mirror | `factory-now-v1.json` |
| CI receipt | `REPO_EXECUTION_LOGS/sourcea/latest.yaml` |
| Panel embed | `command-data-shell.json` → `factory_now`, nav |

**Five surfaces, one concept (“what task is live?”)** — validators each re-check a subset.

### 1.3 E2E / validator sprawl

| Layer | Count | Notes |
|-------|-------|-------|
| `validate-*.sh` scripts | **~270** | Many one-off, overlapping SSOT checks |
| `find_critical_bugs` CRITICAL shell chain | **~47** validators | ~83–120s typical |
| Python audits in `find_critical_bugs` | 3 | essentials nav, hub alignment, governance |
| Hub HTTP E2E variants | **6+** | light, full, standard, playbook, preflight, goal1, live-prompt-feed |
| Stabilization wrapper | `validate-hub-stabilization-e2e-light-v1.sh` | chains 4 scripts **then** light E2E |

**Pain:** No single manifest; CI and founder run different subsets; duplicate hub health checks; heavy path still exists beside light path.

### 1.4 Rebuild path duplication (partially fixed)

| Path | Status |
|------|--------|
| Request thread → `hub_after_mutation` | **Removed** (v5.1) |
| `hub_rebuild_worker_v1.py` + queue | **Active** (:13030) |
| `hub_projection_sync_v1.py` | **Still exists** — can trigger align/build outside worker |
| `build-sina-command-panel.py` strict CI | Separate full build + 40 validators |

---

## 2. Proposed upgrade — “Hub Surface + Live Client + Gate Ladder”

Three products, one map:

```
┌─────────────────────────────────────────────────────────────┐
│  HUB SURFACE API (:13020)                                     │
│  • /api/live/v1          SSE (generation, freeze, queue)    │
│  • /api/surface/v1       one JSON: nav + chips + generation │
│  • /api/slice/<domain>   per-tab read (replaces blob merge) │
│  • POST mutations        202 + enqueue (unchanged v5.1)     │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  HUB LIVE CLIENT (new app.js module ~400 lines)               │
│  • one EventSource → invalidates slices by key                │
│  • replaces 9 setInterval loops                               │
│  • TAB_REGISTRY: tabId → sliceUrl → renderFn                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  GATE LADDER (new scripts/gate_ladder_v1.py)                  │
│  • one manifest: gates/manifest-v1.yaml                       │
│  • tiers: smoke (30s) · daily (2m) · ci (find_critical) · full│
│  • find_critical_bugs imports manifest — no duplicate lists   │
└─────────────────────────────────────────────────────────────┘
```

**Ports unchanged:** `:13020` gateway, `:13030` worker. State service deferred to `:13031+`.

---

## 3. Upgrade phases (UNIFY U0–U5)

### U0 — Contract repair (1 session, P0)

**Problem:** `hubAutoSync` expects `json.data`; server sends flat shell.

**Fix:** Either:
- A) Server adds `"data": shell` wrapper for backward compat, **or**
- B) `hubAutoSync` merges top-level shell fields into `D` (preferred — moves toward slices)

**Gate:** `hubAutoSync` updates `D.built_at` / `generation_id` on every 45s poll.

---

### U1 — Live feed (1 session)

**Add:** `GET /api/live/v1` SSE on `:13020` (design in `HUB_LIVE_SYSTEM_DESIGN_v1.md`)

**Events:** `hub.generation`, `factory.freeze`, `queue.head`, `rebuild.status`

**Gate:** `curl -N --max-time 5 :13020/api/live/v1` prints `data:` lines.

**No app.js yet** — prove server stream first.

---

### U2 — Hub Live Client (2 sessions)

**New file:** `agent-control-panel/assets/hub-live-client-v1.js`

```javascript
// Responsibilities only:
// - EventSource /api/live/v1
// - hold surfaceState { generation_id, freeze_status, queue_sa_id }
// - on generation change → HubSlices.refreshStale()
// - reconnect with backoff
```

**Replace in `app.js`:**
- Remove 4× bottom `setInterval` hub-sync loops
- Keep tab-specific polls only until slices exist (advisor, loop, IC)

**Gate:** Browser Network tab shows **one** long-lived EventSource; hub-sync polling stops.

---

### U3 — Tab registry + slices (3–4 sessions)

**New:** `agent-control-panel/assets/tab-registry-v1.js`

| tabId | slice GET | keys in D |
|-------|-----------|-----------|
| command | `/api/hub-sync` (surface) | nav, factory_now, freeze |
| goal1-auto-run | `/api/goal1-auto-run-status` | goal1_auto_run |
| intelligence | `/api/intelligence-circle` | intelligence_circle |
| agent-loop | `/api/agent-loop` | agent_loop |
| prompt-feed | `/api/prompt-queue` | prompt_queue |

**New server route (optional consolidate):**

`GET /api/surface/v1` → `{ generation_id, freeze_status, queue_sa_id, nav, built_at }`  
Single call for header chips (queue, freeze banner, sync time).

**Deprecate over time:** full `command-data.json` load on boot for non-heavy tabs.

**Gate:** Opening 5 main tabs never downloads full 9MB JSON.

---

### U4 — State read unification (2 sessions, backend)

**New:** `scripts/state_read_lib_v1.py` — **read-only** facade:

```python
def queue_head() -> str:      # queue.sa_id via truth file
def factory_mode() -> str:   # FREEZE / RUN from factory-now
def generation() -> int:     # from shell
def progress_valid_yes() -> int:
```

**Migrate:** validators and hub-sync/SSE to use this lib — **one field path** (`C-H10` enforced in code).

**Gate:** `grep queue_sa.json` → 0; `grep t.get("queue_sa")` → 0 in scripts.

---

### U5 — Unified E2E gate ladder (2 sessions)

**New manifest:** `gates/manifest-v1.yaml`

```yaml
tiers:
  smoke:
    budget_s: 30
    gates:
      - id: hub-health
        run: curl -sf :13020/health
      - id: hub-light-e2e
        run: python3 scripts/audit_backend_e2e_light_v1.py
      - id: four-rule-static
        run: python3 scripts/validate-hub-four-rule-v1.py
  daily:
    budget_s: 120
    extends: smoke
    gates:
      - id: anti-staleness
        run: bash scripts/validate-anti-staleness-bundle-v1.sh
      - id: ecosystem-safety
        run: bash scripts/validate-ecosystem-safety-v1.sh
  ci:
    extends: daily
    gates:
      - id: find-critical-manifest
        run: python3 scripts/gate_ladder_v1.py --tier ci
  full:
    requires_env: SINA_E2E_FORCE=1
    gates:
      - id: audit-backend-e2e-heavy
        run: python3 scripts/audit_backend_e2e.py
```

**New runner:** `scripts/gate_ladder_v1.py`
- Loads manifest
- Runs gates with timeouts, single hub/worker preflight
- JSON report to `~/.sina/gate-ladder-last-v1.json`

**Refactor:** `find_critical_bugs.py` → `gate_ladder_v1.py --tier ci` (manifest is SSOT; delete duplicate `SHELL_VALIDATORS` list over time in slices)

**Collapse wrappers:** `validate-hub-stabilization-e2e-light-v1.sh` becomes thin alias to `--tier smoke`.

**Gate:** `gate_ladder_v1.py --tier smoke` < 30s PASS; `find_critical_bugs` runs same tier + governance audits only.

---

## 4. E2E simplification — before vs after

| Today | After U5 |
|-------|----------|
| 47 critical validators inline in Python | Manifest tiers; CI tier = ~15 gates |
| 6+ E2E script names | 1 runner, 4 tiers |
| Light E2E prefight chains 4 bash scripts | Runner does one preflight block |
| Heavy E2E opt-in via `SINA_E2E_FORCE=1` | `tier: full` in manifest only |
| Founder unclear what to run | `gate_ladder_v1.py --tier smoke` always |

**Founder commands (proposed):**

```bash
python3 scripts/gate_ladder_v1.py --tier smoke   # 30s — before any commit
python3 scripts/gate_ladder_v1.py --tier daily   # 2m — before batch
python3 scripts/find_critical_bugs.py            # CI (manifest tier ci)
SINA_E2E_FORCE=1 python3 scripts/gate_ladder_v1.py --tier full
```

---

## 5. App simplification — before vs after

| Today | After U2–U3 |
|-------|-------------|
| 9 poll timers | 1 SSE + tab-local fetch on invalidate |
| `applyPayload` god-merge | Per-slice merge into `D[key]` |
| Implicit tab/API map | `TAB_REGISTRY` one file |
| Stale sync (json.data bug) | `generation_id` driven refresh |
| “Is it live?” → hammer Refresh | SSE pushes rebuild done |

---

## 6. What we do NOT do in this upgrade

- Split microservices (Phase N stays deferred)
- Rewrite all 270 validators at once (manifest wraps existing scripts)
- Delete `command-data.json` (CI/strict build still uses it)
- Merge conduct / INBOX desync into hub gates
- Drain factory while FREEZE ON

---

## 7. Recommended execution order

| Priority | Phase | Effort | User-visible win |
|----------|-------|--------|------------------|
| **P0** | U0 contract fix | 1h | Auto-sync works again |
| **P1** | U1 SSE | 2h | Server ready for live |
| **P1** | U2 Live Client | 1 day | Stops poll storm |
| **P2** | U3 Tab registry | 2–3 days | Faster tabs, clear map |
| **P2** | U5 Gate ladder (smoke+daily) | 1 day | Simple E2E story |
| **P3** | U4 state_read_lib | 1 day | Less validator drift |
| **P3** | U5 migrate find_critical_bugs | 2 days | CI uses manifest |

**Parallel:** Update `docs/ARCHITECTURE.md` with one-page app map (link TAB_REGISTRY + ports).

---

## 8. Success metrics (unify upgrade done)

**App**
- ≤1 SSE connection + ≤2 tab-local polls (down from 9 timers)
- `TAB_REGISTRY` documents every founder tab
- Boot without full `command-data.json` for default tabs

**E2E**
- One manifest, one runner, four tiers
- `smoke` < 30s, `daily` < 120s
- `find_critical_bugs` no longer maintains 47-entry duplicate list

**Duplication**
- Queue head: one read lib, one field path
- Hub rebuild: worker only (deprecate ad-hoc `hub_projection_sync` from hot paths)

---

## 9. Approval phrases (proposed)

| Phase | Phrase |
|-------|--------|
| U0 | `ASF: UNIFY U0 — hub-sync contract` |
| U1 | `ASF: UNIFY U1 — SSE live feed` |
| U2 | `ASF: UNIFY U2 — live client` |
| U3 | `ASF: UNIFY U3 — tab registry` |
| U4 | `ASF: UNIFY U4 — state read lib` |
| U5 | `ASF: UNIFY U5 — gate ladder` |

---

## 10. One-line pitch

**Unify Upgrade** turns the hub from “one giant JSON + 270 validators + 9 poll loops” into **one live stream, one tab map, one gate ladder** — without undoing v5.1 stabilization.
