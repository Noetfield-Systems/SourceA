# sa-0801 CHECK — Validate app.js lazy load __COMMAND_DATA_LAZY shell bootstrap

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13T21:50Z · **Turn:** CHECK · **Worker:** SourceA  
**Note:** Registry head after sa-0800 is **phase-s8-hub-ui-ux** (not phase-s7).

## Task (read-only)

Validate legacy `app.js` lazy-load bootstrap for `__COMMAND_DATA_LAZY` + `command-data-shell.json` path.

## Hub law context (2026-06-13)

| Surface | Role |
|---------|------|
| **Worker Hub** `/` | **Daily default** — `GET /api/worker-hub/v1` · no `__COMMAND_DATA_LAZY` |
| **Legacy monolith** `/legacy/` | **Archived** — `app.js` lazy bootstrap applies here only |

**Law:** `HUB_WORKER_ONLY_ARCHIVED_MONOLITH_LOCKED_v1.md` · `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md`

sa-0801 scope = **legacy maintenance proof** — not Worker Hub daily ops.

## Live disk (CHECK 2026-06-13)

| Piece | Status |
|-------|--------|
| `index.html` `__COMMAND_DATA_LAZY=true` | **present** |
| `command-data-shell.json` | **403454 bytes** (≤ 512000) |
| `app.js` `loadCommandDataShell()` | **present** (L154–167) |
| `app.js` `loadCommandDataFull()` | **present** (L134–152) |
| `app.js` `tabNeedsFullLoad()` + `HEAVY_TAB_KEYS` | **present** |
| `scheduleIdleFullPrefetch()` | **disabled** (HUB-LITE Phase 0.1) |
| `validate-command-data-lazy-shell-v1.sh` | **PASS** — index + shell only |
| `validate-app-js-lazy-bootstrap-v1.sh` | **absent** |

## Gaps vs task (ACT scope)

| ID | Gap | Severity | ACT fix |
|----|-----|----------|---------|
| **GAP-1** | No app.js-specific validator (sa-0801) | **high** | `validate-app-js-lazy-bootstrap-v1.sh` — static grep/parse of bootstrap fns |
| **GAP-2** | Existing validator covers index/shell only (sa-0041/0091) | medium | Extend or sibling validator — do not duplicate shell size check |
| **GAP-3** | Task verify line = full panel build + FCB | **blocker for naive VERIFY** | Use `worker_verify_fast_v1` + lazy validators per `WORKER_NO_SLOW_VERIFY_SHELL` |
| **GAP-4** | Worker cannot edit `agent-control-panel/` | informational | ACT = scripts validator only · Maintainer for app.js fixes |
| **GAP-5** | Duplicate titles sa-0826/sa-0851/sa-0876 | low | sa-0801 T0 is authoritative |

## Recommended ACT (minimal)

1. Ship `scripts/validate-app-js-lazy-bootstrap-v1.sh` — assert app.js contains:
   - `__COMMAND_DATA_LAZY`
   - `loadCommandDataShell` fetches `command-data-shell.json`
   - `loadCommandDataFull` deferred (not on boot)
   - no idle 9MB prefetch
2. Crosswalk attachment — legacy-only scope + Worker Hub supersession
3. **No** app.js edits · **no** full panel build on VERIFY

## Preflight validators (CHECK)

| Validator | Result |
|-----------|--------|
| validate-command-data-lazy-shell-v1 | PASS · shell 403454 B |
| validate-super-fast-hub-v1 | PASS · Worker Hub default |
| validate-dispatch-policy-v1 | PASS |
| find_critical_bugs (FCB fast) | **critical 0** |

## Verdict

**CHECK complete** — lazy bootstrap **implemented** on legacy disk; **missing app.js validator**. Worker Hub daily path **out of scope**. **STOP** — no implement · no closeout.

*End sa-0801 CHECK*
