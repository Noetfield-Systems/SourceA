# sa-0853 CHECK — Fix refresh pipeline total time under 360s for audit E2E

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13T22:25Z · **Turn:** CHECK · **Worker:** SourceA  
**Tier:** T2 (duplicate: sa-0803 T0 · sa-0828 T1 · sa-0878 T3)

## Task (read-only)

Ensure refresh pipeline completes within **360s** for `audit_backend_e2e` / related E2E gates.

## Hub law context

| Path | Behavior |
|------|----------|
| **Worker Hub daily** | `POST /refresh` `{mode:"light"}` — **~1s** (Super Fast Hub) |
| **Legacy full rebuild** | `POST /refresh` `{mode:"full"}` — async worker queue · **minutes** |
| **Default POST `/refresh` `{}`** | **light** → HTTP **200** (live probe: **634ms**) |

Law: `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` · `HUB_WORKER_ONLY_ARCHIVED_MONOLITH_LOCKED_v1.md`

## Live disk (CHECK 2026-06-13)

| Signal | Value |
|--------|-------|
| `POST /refresh {}` status | **200** (light) — not 202 |
| `run_refresh_pipeline()` | fleet 180s cap + jobs 300s each (3 jobs) — **worst-case >360s** if all timeout |
| Dedupe env | `SINA_SKIP_NESTED_BOWL` · `SINA_SKIP_PANEL_BUILD` · `SINA_SKIP_FLEET_SCAN` (sa-0205) |
| `audit_backend_e2e.py` refresh | expects **202** async + 30s poll (60×0.5s) |
| `audit_backend_e2e_light_v1.py` | expects **202** on `refresh-async` — **stale vs light default** |
| `validate-refresh-pipeline-360-v1.sh` | **absent** |

## Prior prompts (same theme)

| SA | Tier | Status | Note |
|----|------|--------|------|
| sa-0204–0279 | hub-build-ci | **done** | "POST /refresh timeout 360s" — receipt only |
| sa-0803 | T0 | backlog | same title as sa-0853 |
| **sa-0853** | T2 | backlog | **this CHECK** |

## Gaps vs task (ACT scope)

| ID | Gap | Severity | ACT fix |
|----|-----|----------|---------|
| **GAP-1** | E2E expects 202 async refresh; hub default is 200 light | **high** | Align `audit_backend_e2e` + light E2E: light path OR `mode:full` with 360s wait |
| **GAP-2** | No explicit 360s budget constant / validator | **high** | `REFRESH_E2E_BUDGET_SEC=360` + `validate-refresh-pipeline-360-v1.sh` |
| **GAP-3** | Poll loop max ~30s — insufficient for full worker rebuild | medium | Extend wait to 360s when testing `mode:full` |
| **GAP-4** | Pipeline per-step timeouts can exceed 360s combined | medium | Document/tighten caps or skip steps under audit profile |
| **GAP-5** | No PRIORITY evidence row for sa-0853 | low | VERIFY append |
| **GAP-6** | Full `audit_backend_e2e.py` not run on CHECK (slow) | informational | ACT/VERIFY timed probe |

## Recommended ACT (minimal)

1. Patch `audit_backend_e2e.py` refresh block — dual contract:
   - **light:** accept 200 + generation_id bump (<2s)
   - **full audit profile:** `POST /refresh` `{mode:"full"}` + poll ≤360s
2. Ship `validate-refresh-pipeline-360-v1.sh` — static budget + optional timed light refresh
3. Sync `audit_backend_e2e_light_v1.py` `refresh-async` expect to light reality
4. Crosswalk attachment — Worker Hub daily vs full rebuild audit paths

**Out of scope:** forcing full rebuild on Worker Hub default route.

## Preflight validators (CHECK)

| Validator | Result |
|-----------|--------|
| validate-command-data-shell-size-v1 | PASS · 403344 B |
| validate-super-fast-hub-v1 | PASS |
| find_critical_bugs (FCB fast) | **critical 0** |
| `POST /refresh` live probe | **200** in 634ms |

## Verdict

**CHECK complete** — **E2E refresh contract stale** vs Super Fast Hub; **360s budget unenforced**. **STOP** — no implement · no closeout.

*End sa-0853 CHECK*
