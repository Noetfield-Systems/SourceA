# sa-0851 CHECK — Validate app.js lazy load __COMMAND_DATA_LAZY shell bootstrap

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13T22:00Z · **Turn:** CHECK · **Queue pos:** 10 · **Worker:** SourceA  
**Tier:** T2 quarterly hardening (same title as sa-0801 T0 · sa-0826 · sa-0876)

## Task (read-only)

Validate legacy `app.js` lazy-load bootstrap for `__COMMAND_DATA_LAZY` + shell path.

## Hub law (unchanged)

| Surface | Lazy bootstrap |
|---------|----------------|
| **Worker Hub** `/` | **Out of scope** — `/api/worker-hub/v1` |
| **Legacy** `/legacy/` | **In scope** — frozen `app.js` maintenance proof |

Law: `HUB_WORKER_ONLY_ARCHIVED_MONOLITH_LOCKED_v1.md` · `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md`

## Duplicate prompt chain

| SA | Tier | Status | CHECK |
|----|------|--------|-------|
| sa-0801 | T0 P0 | backlog | CHECK done 2026-06-13 — gaps documented |
| **sa-0851** | T2 P2 | backlog | **this CHECK** |
| sa-0826 | T1 | backlog | — |
| sa-0876 | T3 | backlog | — |

**Same substance** — one validator (`validate-app-js-lazy-bootstrap-v1.sh`) can close all tiers; sa-0801 T0 is earlier authoritative slot.

## Live disk (CHECK 2026-06-13)

| Piece | Status |
|-------|--------|
| `index.html` `__COMMAND_DATA_LAZY=true` | present |
| `command-data-shell.json` | **403325 bytes** (≤ 512000) |
| `app.js` bootstrap | present — `loadCommandDataShell` · `loadCommandDataFull` · `tabNeedsFullLoad` |
| Idle 9MB prefetch | disabled (`scheduleIdleFullPrefetch` noop) |
| `validate-command-data-lazy-shell-v1` | **PASS** (index/shell) |
| `validate-app-js-lazy-bootstrap-v1` | **absent** |
| `audit_backend_e2e.py` lazy path | **none** — sa-0851 verify line won't prove app.js bootstrap |

## Gaps vs task (ACT scope)

| ID | Gap | Severity | ACT fix |
|----|-----|----------|---------|
| **GAP-1** | No app.js-specific validator | **high** | `validate-app-js-lazy-bootstrap-v1.sh` |
| **GAP-2** | sa-0801 T0 same task — ACT not shipped | medium | Ship once · idempotent close sa-0851 after |
| **GAP-3** | `audit_backend_e2e` has no lazy/bootstrap probe | medium | Optional e2e sub-step or rely on static validator |
| **GAP-4** | Task verify = e2e + spine — not lazy-specific | informational | VERIFY uses fast lane + lazy validators |
| **GAP-5** | Worker cannot edit `agent-control-panel/` | informational | Scripts validator only |

## Recommended ACT

1. Ship `validate-app-js-lazy-bootstrap-v1.sh` (if sa-0801 ACT not yet done — same diff)
2. Crosswalk attachment `sa-0851-…_LOCKED_v1.md` — legacy-only · duplicate-chain note
3. **No** app.js edits · **no** full panel build

## Preflight validators (CHECK)

| Validator | Result |
|-----------|--------|
| validate-command-data-lazy-shell-v1 | PASS · shell 403325 B |
| validate-super-fast-hub-v1 | PASS |
| validate-spine-bridge-founder-v1 | PASS |
| find_critical_bugs (FCB fast) | **critical 0** |

## Verdict

**CHECK complete** — implementation on legacy disk; **validator gap** same as sa-0801. **STOP** — no implement · no closeout.

*End sa-0851 CHECK*
