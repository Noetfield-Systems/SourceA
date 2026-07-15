# Hub Unify + Proof UX — Master Plan v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Status:** Shipped logged (2026-06-10) — Track 2 live system + HUB-P0-1/2/3 proof UX  
**Date:** 2026-06-10  
**Authority:** ASF — `execution_authority: false` for proof UX; gates stay logged  
**Implementers:** SourceA scripts · SinaaiDataBase Hub UI (per locked spec)

---

## 0. One sentence (unified)

> **One live Hub Surface (proof + queue + freeze), one event export contract, one gate ladder — plain English on Home, honest numbers from disk, no duplicate polls or E2E scripts.**

---

## 1. Deep analysis — Hub Proof UX P0 vs disk today

### 1.1 Build status matrix

| Build ID | Spec says | Disk today | Gap |
|----------|-----------|------------|-----|
| **HUB-P0-1** Honest counter §1 | `proof_counter` from `program-1000-honest-status-v1.py` | `hub_home_founder_view_v1.py` + Home §1 UI (`sc-home-founder-proof`) | **DONE** — `verified_done`, kill RED/GREEN, `honest_progress` alias kept |
| **HUB-P0-2** Event chain export | `event_chain_export_v1.py` + `GET /api/event-chain-export-v1` | CLI + API + `founder-export-event-chain` action | **DONE** — `WORKER_STARTED` checked via `has_worker_started` meta |
| **HUB-P0-3** Overnight verify | `founder-overnight-verify-readonly` button | `overnight_verify_readonly_v1.py` + Home button | **DONE** — 5 disk CHECK turns · semi-auto copy on RED |

### 1.2 What already works (reuse, don’t rewrite)

| Asset | Location | Reuse for |
|-------|----------|-----------|
| `renderHomeFounderView()` | `app.js` ~5877 | Hub Home §1 UI shell |
| `hub_home_founder_view_v1.py` | `build_payload` → `home_founder_view` | Proof slice builder |
| `program-1000-honest-status-v1.py` | writes `~/.sina/PROGRAM_1000_HONEST_STATUS.json` | **Canonical honest SSOT** (spec intent) |
| `EVENT_CONTRACT.yaml` | `brain-os/system/` | Export field names |
| `execution_event_log_v1.py` | `~/.sina/events/{date}.jsonl` | Primary event log |
| `validate-hub-home-founder-view-v1.sh` | CI gate | Extend for proof_counter |

### 1.3 Fragmentation proof UX hits today

**Four event stores** (home merges 2, export needs all relevant):

| Store | Path | Used by |
|-------|------|---------|
| Daily contract log | `~/.sina/events/{YYYY-MM-DD}.jsonl` | `execution_event_log_v1`, home `_daily_events` |
| Broker mirror | `~/.sina/goal1-lane-broker-events.jsonl` | home `_merge_events` |
| Legacy bus | `~/.sina/events_v1.jsonl` | imported in hub_home, **not merged** |
| Rebuild queue | `~/.sina/hub-rebuild-queue-v1.jsonl` | v5.1 worker (different domain) |

**Honest count duplication:**

| Source | Value class |
|--------|-------------|
| `registry_honest_lib_v1.audit_registry_done()` | UI home today (596) |
| `program-1000-honest-status-v1.py` | Spec SSOT (596 honest, unproven_done, drift) |
| `run-inbox-disk-truth.progress` | 595 valid_yes / 596 receipt_done |
| REGISTRY raw `done` | **Must never show alone** (spec law) |

**UI sync gap (unify + proof):**

- `hubAutoSync` expects `json.data`; hub-sync returns flat shell → Home may not refresh after worker rebuild unless full panel reload.

---

## 2. Unified architecture — “Hub Surface + Proof Slice + Gate Ladder”

```
┌──────────────────────────────────────────────────────────────────┐
│  HUB HOME (command tab) — plain English                           │
│  §1 proof_counter · §2 status · §3 actions · §4 event export    │
└────────────────────────────┬─────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
  GET /api/surface/v1   GET /api/slice/home    GET /api/live/v1 (SSE)
  (chips: gen, freeze,  (home_founder_view +   (generation, queue,
   queue, proof_counter)  proof_counter)        freeze, rebuild)
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
              ┌──────────────────────────────┐
              │  state_read_lib_v1 (read)     │
              │  · queue.sa_id                │
              │  · PROGRAM_1000_HONEST_STATUS │
              │  · factory FREEZE             │
              └──────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
  event_chain_export_v1   hub_queue_lib      gate_ladder_v1
  (one sa_id JSONL)       (rebuild queue)    (smoke/daily/ci)
```

**Proof UX is not a separate app** — it is the **first slice** on the unified Hub Surface.

---

## 3. Enhanced data contracts

### 3.1 `proof_counter` (replaces ambiguous `honest_progress`)

Built in `hub_home_founder_view_v1.py` from **`program-1000-honest-status-v1.py`** (read cache file or call `build_status()`):

```json
{
  "verified_done": 596,
  "total": 1000,
  "pct": 59.6,
  "unproven_done": 0,
  "drift": 0,
  "kill": "GREEN",
  "kill_reason": "",
  "label": "596 verified receipts · not REGISTRY done alone",
  "ssot": "~/.sina/PROGRAM_1000_HONEST_STATUS.json",
  "at": "2026-06-10T..."
}
```

**Kill rules (plain English):**

| Condition | `kill` | Copy |
|-----------|--------|------|
| `unproven_done > 0` or `drift > 0` | RED | "Semi-auto blocked — unproven closes logged" |
| FREEZE + stop receipt | RED | "Factory FROZEN — founder-gated resume only" |
| else | GREEN | "Receipt-bound progress only" |

Keep `honest_progress` as **deprecated alias** for one release (UI reads `proof_counter` first).

### 3.2 Event chain export (HUB-P0-2 enhanced)

**Single module:** `scripts/event_chain_export_v1.py`

```python
# Input: sa_id, optional customer=1 (strip internal fields)
# Sources (in order):
#   1. ~/.sina/events/*.jsonl (filter trace_id / data.sa_id)
#   2. goal1-lane-broker-events.jsonl
#   3. execution spine / closeout receipts if sa match
# Output: JSONL stream or file; contract = EVENT_CONTRACT.yaml event_types
# Demo-grade gate: must include WORKER_STARTED for sa_id
```

**API:** `GET /api/event-chain-export-v1?sa_id=sa-0778&customer=1`

- Read-only; no `build_payload`; stream response `application/x-ndjson`
- **Unified with gate ladder:** smoke tier includes `event_chain_export_v1.py --sa_id <queue.sa_id> --check`

### 3.3 Overnight verify (HUB-P0-3 enhanced)

**`action_id`:** `founder-overnight-verify-readonly`

| Property | Value |
|----------|-------|
| Model | Haiku CHECK/VERIFY |
| Turns | max 5 |
| Writes | **none** (read-only) |
| FREEZE | Must not drain; enqueue only if report JSON |
| UX | Button on Home §3: "Overnight check (read-only)" |
| Kill copy | "Semi-auto · founder-gated" when RED |

**Output:** `~/.sina/overnight-verify-report-v1.json` + plain summary in Actions log.

---

## 4. Unified build order (Proof + Unify)

Phases are **sequenced** to avoid duplicate work.

| Order | ID | Delivers | Unify link | Proof link |
|-------|-----|----------|------------|------------|
| **1** | U0 | hub-sync ↔ app.js contract + `generation_id` merge | U0 | Enables live Home refresh |
| **2** | **HUB-P0-1** | `proof_counter` §1 on Home | U3 slice `/api/slice/home` | **GOAL-HUB-P0-1** |
| **3** | U1 | SSE `/api/live/v1` | Live backbone | Pushes proof_counter bump |
| **4** | **HUB-P0-2** | `event_chain_export_v1` + API | Surface read-only route | **GOAL-HUB-P0-2** |
| **5** | U2 | `hub-live-client-v1.js` — kill Home poll loops | Tab registry seed: `command` | Home updates on SSE |
| **6** | **HUB-P0-3** | overnight verify action + button | L2 enqueue if needed | **GOAL-HUB-P0-3** |
| **7** | U4 | `state_read_lib_v1.py` | One queue/honest read path | proof_counter uses lib |
| **8** | U5 | `gate_ladder_v1.py` + manifest | Unified E2E | **proof smoke gates** |
| **9** | U3 | Full tab registry + `/api/surface/v1` | Complete map | Export button on Home |

**Mandatory spec order preserved:** P0-1 → P0-2 → P0-3, interleaved with unify prerequisites.

---

## 5. Hub Home UI — § layout (locked mapping)

| Section | Content | Data source |
|---------|---------|-------------|
| **§1 Proof** | Verified counter, RED/GREEN kill, unproven badge | `proof_counter` |
| **§2 Status** | FROZEN/Ready headline, queue chip | `status` + `state_read_lib.queue_head()` |
| **§3 Actions** | Safety, Refresh (202), **Export chain**, **Overnight verify** | `actions` + new ids |
| **§4 Events** | Last 10 plain-English rows | `recent_events` via unified `event_read_lib` |
| **§5 Technical** | Collapsed sa/pos (founder opt-in) | `technical_detail` |

**UI file:** `app.js` `renderHomeFounderView()` — add §1 block reading `hfv.proof_counter` before score hero.

**Workspace split (per locked spec):**

- SourceA: payload, export CLI, API routes, branch actions, gates
- SinaaiDataBase: §1/§3 UI polish if mirrored workspace — **single SSOT remains SourceA shell**

---

## 6. Unified E2E — proof + stabilization in one ladder

Add to `gates/manifest-v1.yaml`:

```yaml
smoke:
  budget_s: 35
  gates:
    - hub-health
    - hub-four-rule-static
    - hub-light-e2e
    - hub-home-founder-view          # existing validator
    - proof-counter-present          # NEW: shell has proof_counter.verified_done
    - event-chain-export-queue-head    # NEW: export sa-0778 includes WORKER_STARTED or explicit skip reason

daily:
  extends: smoke
  gates:
    - program-1000-honest-status       # program-1000-honest-status-v1.py --write
    - anti-staleness-bundle
    - ecosystem-safety

ci:
  extends: daily
  gates:
    - find-critical-manifest-slice     # replaces 47-entry duplicate list over time
```

**Collapse these into smoke:**

- `validate-hub-stabilization-e2e-light-v1.sh` → `gate_ladder_v1.py --tier smoke`
- Separate proof validators → manifest entries, not new top-level scripts

**Founder one-liner:**

```bash
python3 scripts/gate_ladder_v1.py --tier smoke   # hub + proof in <35s
```

---

## 7. Eliminate duplication (explicit)

| Before | After unified |
|--------|----------------|
| `honest_progress` + REGISTRY + monitor counts | `proof_counter` ← `PROGRAM_1000_HONEST_STATUS.json` only |
| 4 event JSONL locations | `event_read_lib_v1` for UI; `event_chain_export_v1` for download |
| Home Refresh → sync `build_payload` | Refresh → 202; SSE `generation_id` refresh |
| 9 `setInterval` + manual Refresh | 1 SSE + tab invalidate |
| Proof E2E + hub E2E + 47 validators | `gate_ladder_v1` tiers |
| `_merge_events` ad-hoc | `event_read_lib.recent_plain(n=10)` shared with export |

---

## 8. Real-time + proof (how they connect)

```
Worker rebuild completes
  → bumps shell generation_id
  → SSE: { type: "hub.generation", generation_id: N }
  → hub-live-client refetches GET /api/slice/home
  → §1 proof_counter updates (if PROGRAM_1000_HONEST_STATUS changed)
```

No separate “proof poll loop.”

---

## 9. Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Honest count 595 vs 596 confusion | `proof_counter` shows `verified_done` + footnote `valid_yes` from truth file |
| Export missing `WORKER_STARTED` | Gate fails smoke with plain message; customer=1 strips internals |
| Overnight verify drains factory | `execution_authority: false`; readonly branch; FREEZE check in handler |
| SinaaiDataBase / SourceA drift | Single payload SSOT; UI reads slice API only |
| hub-sync regression for Goal1 | `/api/surface/v1` includes goal1 chip OR client polls `/api/goal1-auto-run-status` on SSE |

---

## 10. Approval phrases (extended)

| Phase | Phrase |
|-------|--------|
| U0 | `ASF: UNIFY U0 — hub-sync contract` |
| HUB-P0-1 | `ASF: HUB-P0-1 — proof counter` |
| U1 | `ASF: UNIFY U1 — SSE live feed` |
| HUB-P0-2 | `ASF: HUB-P0-2 — event chain export` |
| HUB-P0-3 | `ASF: HUB-P0-3 — overnight verify` |
| U2–U5 | `ASF: UNIFY U2` … `U5` (per prior master plan) |

---

## 11. Success definition (unified)

**Proof UX:**
- Home §1 shows `proof_counter.verified_done` / 1000 with RED/GREEN kill
- Export downloads one-sa JSONL with contract field names
- Overnight verify button returns read-only report in &lt;30s wall time

**Unify:**
- ≤1 SSE; no request-thread builds; `gate_ladder smoke` &lt;35s PASS

**One map:**
- This doc + `TAB_REGISTRY` (U3) + `gates/manifest-v1.yaml` (U5)

---

## 12. References

- `HUB_PROOF_UX_P0_LOCKED_v1.md` — ASF locked goals (unchanged intent)
- `HUB_UNIFY_UPGRADE_PROPOSAL_v1.md` — technical unify phases
- `HUB_LIVE_SYSTEM_DESIGN_v1.md` — SSE + surface API
- `brain-os/system/HUB_HOME_REDESIGN_SPEC_LOCKED_v1.md` — Home layout law
- `brain-os/system/EVENT_CONTRACT.yaml` — export contract

---

*End Hub Unify + Proof Master v1*
