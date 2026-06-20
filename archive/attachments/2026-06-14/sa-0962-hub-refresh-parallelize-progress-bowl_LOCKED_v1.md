# sa-0962 — Hub refresh parallelize progress+bowl — perf research note

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Tier:** T2 research only · **No D-modules · No pipeline implement**

## One-line verdict

> **Dedupe is shipped; parallelization is not.** `run_refresh_pipeline()` runs fleet → progress → bowl → master-orders **sequentially**. Bowl **depends** on `PROGRAM_PROGRESS.json` from progress — true progress‖bowl parallel needs a dependency split. This note is **perf research only** — defer code until ASF orders + INCIDENT-031 lift.

---

## Current pipeline (disk truth)

`scripts/sina_command_lib.py` → `run_refresh_pipeline()`:

| Step | Script | Timeout | Env guards |
|------|--------|---------|------------|
| 1 Fleet scan | `scan-cursor-agent-fleet.py` | 180s | once per pipeline |
| 2 Program progress | `update-program-progress.py` | 300s | `SINA_SKIP_NESTED_BOWL=1` |
| 3 Daily bowl | `build-sina-daily-bowl.py` | 300s | `SINA_SKIP_PANEL_BUILD=1` · `SINA_SKIP_FLEET_SCAN=1` |
| 4 Master orders | `export-master-orders-json.py` | 300s | same |
| 5 Panel + KPI | `build_payload()` | (in caller) | full rebuild |

**Dedupe shipped (sa-0205/0206/0222):** nested bowl-in-progress and panel-in-bowl eliminated — **O(n) duplicate builds removed**, not wall-clock parallelized.

---

## Perf baseline

| Path | Duration | Source |
|------|----------|--------|
| `POST /refresh` full strict | **~230s** | SOURCEA-PRIORITY sa-0217 |
| Light `hub_self_refresh` / hub-sync | **~0.6s** | sa-0853 · `validate-refresh-pipeline-360-v1` |
| `build_payload()` monolith | 15–60s per mutation | HOTSPOTS A1 |
| External rebuild worker | Coalesce 3s settle | `hub_rebuild_worker_v1.py` :13030 |

**Bottleneck #1 (HOTSPOTS):** `hub_after_mutation()` + full `build_payload()` — dominates refresh after pipeline steps complete.

---

## Dependency graph (why progress‖bowl is hard)

```text
fleet_scan → AGENT_FLEET_REGISTRY.json
update-program-progress → PROGRAM_PROGRESS.json (+ command center MD)
build-sina-daily-bowl → reads PROGRAM_PROGRESS.json (locks, parallel_plans, drift)
export-master-orders → reads bowl/state + progress signals
build_payload → reads all above
```

**Hard edge:** bowl step **must** see progress output. Running progress and bowl in parallel without refactor → **stale bowl** or race on `PROGRAM_PROGRESS.json`.

---

## Safe parallel options (research — not built)

| # | Option | Est. savings | Risk | Defer until |
|---|--------|--------------|------|-------------|
| **P1** | Parallel **fleet scan** + **progress pre-reads** (architect, semantic, wire) inside progress script | Low–med | Low if fleet write finishes before bowl | Maintainer refactor progress internals |
| **P2** | After progress completes: parallel **bowl** + **master-orders** (if orders export reads only committed progress) | Med | Medium — verify export deps | Validator proves no cross-write |
| **P3** | Split progress into **fast path** (locks/todos) + **slow path** (fleet, mergepack) — bowl waits fast only | Med–high | Schema contract | Law amend on PROGRAM_PROGRESS |
| **P4** | **Do not** parallelize progress‖bowl without P3 | — | **High** stale UI | Never without split |
| **P5** | Keep **light sync** default; full `/refresh` founder-only | N/A | INCIDENT-031 / no_hub | Current law |

---

## What already helps (do not re-litigate)

| Shipped | Effect |
|---------|--------|
| `SINA_SKIP_*` env chain | Removed nested rebuild loops |
| Hub rebuild worker :13030 | Coalesced enqueue — fewer full rebuilds |
| `hub_self_refresh --quick` | Agent sync without 230s refresh |
| Lazy shell / canonical projection | Smaller founder payload |
| `validate-refresh-pipeline-360-v1` | Budget guard on E2E refresh |

---

## Duplicate sa titles

Same task at **sa-0912**, **sa-0937**, **sa-0962**. This doc is canonical for sa-0962 VERIFY closeout.

---

## Verdict

**Parallelizing progress+bowl in one shot is unsafe** without splitting `update-program-progress` outputs. **Real win** is P2 (bowl‖master-orders after progress) + continued light-sync default — not rewriting `run_refresh_pipeline` in this research sa.

**One-line:** Dedupe done; parallel needs dependency split — perf note only, no implement.
