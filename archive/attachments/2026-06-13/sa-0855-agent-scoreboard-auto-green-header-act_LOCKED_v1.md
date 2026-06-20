# sa-0855 ACT — Validate agent-scoreboard table Auto green column header

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13T23:10Z · **Turn:** ACT · **Worker:** SourceA

## Shipped (scripts only — legacy `/legacy/` scope)

| Piece | Action |
|-------|--------|
| `scripts/validate-agent-scoreboard-auto-green-header-v1.sh` | **NEW** — thead `sc-sb-th-verify` + Auto green label |
| Chains | `validate-scoreboard-auto-green-pill-v1.sh` |

## Validated contract (legacy app.js)

| Check | Proof |
|-------|-------|
| `renderAgentScoreboard()` table | `<th class="sc-sb-th-verify">Auto green</th>` |
| Column pairing | `sc-sb-col-verify` + `renderScoreboardVerifyCell` |
| Stale copy | No `Verify ✓` / `ASF verify` in thead block |
| Fleet live | `fleet_auto_green_count=8` / `agent_count=8` |

## No code diff

`app.js` already implemented (sa-0305/0306) — ACT is validator-only.

## Duplicate chain

Also satisfies **sa-0805** T0 · **sa-0830** T1 · **sa-0880** T3.

## Validators (ACT)

| Validator | Result |
|-----------|--------|
| validate-agent-scoreboard-auto-green-header-v1 | PASS |
| validate-scoreboard-auto-green-pill-v1 | PASS |
| worker_verify_fast_v1 | PASS |

*End sa-0855 ACT*
