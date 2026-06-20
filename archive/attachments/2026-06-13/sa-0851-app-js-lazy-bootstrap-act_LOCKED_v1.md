# sa-0851 ACT — Validate app.js lazy load __COMMAND_DATA_LAZY shell bootstrap

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13T22:05Z · **Turn:** ACT · **Queue pos:** 11 · **Worker:** SourceA

## Shipped (scripts only — legacy `/legacy/` scope)

| Piece | Action |
|-------|--------|
| `scripts/validate-app-js-lazy-bootstrap-v1.sh` | **NEW** — static app.js bootstrap contract |
| Chains | `validate-command-data-lazy-shell-v1.sh` (index + shell size) |

## Validated contract (legacy app.js)

| Check | Proof |
|-------|-------|
| Shell-first boot | `loadCommandData()` → `loadCommandDataShell()` |
| Lazy flag | sets `__COMMAND_DATA_LAZY = true` on shell; false on full |
| Deferred full | `loadCommandDataFull()` fetches `command-data.json` on demand |
| Heavy tabs | `tabNeedsFullLoad` + `HEAVY_TAB_KEYS` |
| No idle prefetch | `scheduleIdleFullPrefetch` noop (HUB-LITE 0.1) |
| Shell payload | 403344 bytes ≤ 512000 |

## Out of scope (hub law)

- **Worker Hub** `/` — no `__COMMAND_DATA_LAZY`; `validate-super-fast-hub-v1` covers daily path
- **No** `app.js` edits · **no** full panel build

## Duplicate chain

Validator also satisfies **sa-0801** T0 · sa-0826 · sa-0876 (same title).

## Validators (ACT)

| Validator | Result |
|-----------|--------|
| validate-app-js-lazy-bootstrap-v1 | PASS |
| validate-command-data-lazy-shell-v1 | PASS |
| validate-super-fast-hub-v1 | PASS |

*End sa-0851 ACT*
