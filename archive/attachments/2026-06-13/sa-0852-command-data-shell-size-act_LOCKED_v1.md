# sa-0852 ACT — Measure command-data-shell.json size — target under 500KB

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13T22:15Z · **Turn:** ACT · **Worker:** SourceA

## Shipped

| Piece | Action |
|-------|--------|
| `scripts/validate-command-data-shell-size-v1.sh` | **NEW** — measure bytes/KB + assert ≤ `SHELL_MAX_BYTES` |

## Live measurement (ACT 2026-06-13)

| Signal | Value |
|--------|-------|
| Bytes | **581619** |
| KB | **568.0 KB** |
| Cap | **512000** (500 × 1024) |
| Headroom | **-69619 B** (over cap) |
| Heavy key leak | **none** |
| `built_at` | 2026-06-13T21:20:44Z |

## Validator result

`validate-command-data-shell-size-v1.sh` → **FAIL** (correct — detects over-cap)  
`validate-command-data-lazy-shell-v1.sh` → **FAIL** (same cap)

**ACT shipped the measure gate** — disk trim is **Maintainer** (shell projection / panel build), not Worker.

## Scope

Legacy `/legacy/` lazy shell only. Worker Hub does not fetch `command-data-shell.json`.

## Duplicate chain

Validator also serves **sa-0802** T0 · **sa-0877** T3.

## OPEN (Maintainer)

1. Trim shell projection — largest keys: `bowl` · `command_center` · `agent_reviews` (~56 KB each)
2. Re-run `validate-command-data-shell-size-v1.sh` until PASS before VERIFY closeout

*End sa-0852 ACT*
