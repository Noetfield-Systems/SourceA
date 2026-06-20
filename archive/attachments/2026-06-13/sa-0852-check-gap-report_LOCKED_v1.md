# sa-0852 CHECK — Measure command-data-shell.json size — target under 500KB

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13T22:10Z · **Turn:** CHECK · **Worker:** SourceA  
**Tier:** T2 quarterly (duplicate: sa-0802 T0 · sa-0877 T3)

## Task (read-only)

Measure `command-data-shell.json` size — confirm under **500 KB** cap.

## Hub law context

| Surface | Uses shell JSON? |
|---------|------------------|
| **Legacy** `/legacy/` | **Yes** — lazy bootstrap fetches `command-data-shell.json` |
| **Worker Hub** `/` | **No** — `/api/worker-hub/v1` (~2–4 KB) |

Law: `HUB_WORKER_ONLY_ARCHIVED_MONOLITH_LOCKED_v1.md` · `SHELL_MAX_BYTES` in `sina_command_lib.py`

## Live measurement (CHECK 2026-06-13)

| Signal | Value |
|--------|-------|
| Path | `agent-control-panel/command-data-shell.json` |
| **Bytes** | **403344** |
| **KB** | **393.9 KB** |
| Cap (`SHELL_MAX_BYTES`) | **512000** (500 × 1024) |
| **Under target** | **YES** — ~106 KB headroom |
| `built_at` | 2026-06-13T21:20:44Z |

## Existing enforcement (partial coverage)

| Piece | Role |
|-------|------|
| `validate-command-data-lazy-shell-v1.sh` | **PASS** — size + heavy-key leak check |
| `validate-ui-wiring-v1.sh` | 500KB assert (sa-0016) |
| `build-sina-command-panel.py` / `sina_command_lib` | Write-time fail if shell > cap |
| `audit_hub_source_alignment.py` | Shell cap audit |

**No** dedicated `validate-command-data-shell-size-v1.sh` with explicit measure receipt for sa-0852.

## Duplicate prompt chain

| SA | Tier | Status |
|----|------|--------|
| sa-0802 | T0 P0 | backlog |
| **sa-0852** | T2 P2 | backlog (this CHECK) |
| sa-0877 | T3 | backlog |

## Gaps vs task (ACT scope)

| ID | Gap | Severity | ACT fix |
|----|-----|----------|---------|
| **GAP-1** | No sa-0852-specific measure validator/receipt | medium | `validate-command-data-shell-size-v1.sh` — report bytes/KB + assert ≤ cap |
| **GAP-2** | No PRIORITY evidence row for shell size | medium | Append row on VERIFY |
| **GAP-3** | Size already green — no builder trim needed | informational | Doc-only ACT sufficient |
| **GAP-4** | Duplicate sa-0802/sa-0877 | low | One validator closes chain |
| **GAP-5** | Worker Hub health=critical (super-fast-hub exit 52) | informational | Unrelated to shell size task |

## Recommended ACT (minimal)

1. Ship `validate-command-data-shell-size-v1.sh` — thin measure + cap assert (may delegate to `SHELL_MAX_BYTES`)
2. Crosswalk attachment with live bytes/KB table
3. **No** panel build trim · **no** shell JSON edit unless rebuild pushes over cap

## Preflight validators (CHECK)

| Validator | Result |
|-----------|--------|
| validate-command-data-lazy-shell-v1 | **PASS** · 403344 ≤ 512000 |
| validate-app-js-lazy-bootstrap-v1 | PASS |
| validate-super-fast-hub-v1 | **FAIL** exit 52 — health=critical (out of scope) |
| find_critical_bugs (FCB fast) | not re-run (shell validators sufficient) |

## Verdict

**CHECK complete** — shell **under 500KB** on disk; gap = **dedicated measure validator + evidence row**. **STOP** — no implement · no closeout.

*End sa-0852 CHECK*
