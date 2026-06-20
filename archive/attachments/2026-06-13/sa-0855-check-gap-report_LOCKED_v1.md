# sa-0855 CHECK — Validate agent-scoreboard table Auto green column header

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13T23:00Z · **Turn:** CHECK · **Worker:** SourceA  
**Tier:** T2 (duplicate: sa-0805 T0 · sa-0830 T1 · sa-0880 T3)

## Task (read-only)

Validate **agent-scoreboard** table second-column header reads **Auto green** (machine auto-pass — not ASF Verify).

## Hub law context

| Surface | Scoreboard table |
|---------|------------------|
| **Legacy** `/legacy/` `app.js` | **In scope** — `renderAgentScoreboard()` table `<thead>` |
| **Worker Hub** `/` | **Out of scope** — scoreboard tab lives in legacy panel |

Law: `HUB_WORKER_ONLY_ARCHIVED_MONOLITH_LOCKED_v1.md` · `AGENT_SCOREBOARD_LOCKED_v1.md` (§1 column 2 — **doc drift**, see GAP-5)

## Live disk (CHECK 2026-06-13)

| Piece | Status |
|-------|--------|
| `renderAgentScoreboard()` table header | `<th class="sc-sb-th-verify">Auto green</th>` (L7929) |
| Column cells | `sc-sb-col-verify` + `renderScoreboardVerifyCell(r)` (L7905) |
| Auto-pass pill | `sc-sb-auto-pill` · `aria-label="Auto green"` (L7855) |
| CSS header class | `.sc-sb-th-verify` width/center (app.css L4871) |
| API live | `fleet_auto_green_count=8` · `agent_count=8` |
| `validate-scoreboard-auto-green-pill-v1` | **PASS** — sa-0306/0356 cell pill |
| `validate-render-agent-scoreboard-v1` | **PASS** — sa-0305 hero/gaps (no thead assert) |
| `validate-fleet-auto-green-count-v1` | **PASS** — fleet_auto_green_count=8 |
| `validate-agent-scoreboard-auto-green-header-v1` | **absent** — no dedicated column-header validator |

## Partial coverage (existing)

| Validator | Covers |
|-----------|--------|
| `validate-scoreboard-auto-green-pill-v1.sh` | `renderScoreboardVerifyCell` auto_pass pill; no Verify button |
| `validate-render-agent-scoreboard-v1.sh` | Hero tagline · gap banners · fleet_auto_green_count meta |
| `validate-batch-sa-0318-0424` sa-0319 | `"Auto green" in APP_S` globally — not thead-specific |

**Does not** assert:
- `sc-sb-th-verify` class on `<th>`
- Header text **Auto green** inside `renderAgentScoreboard` table block
- Header/cell column pairing (`sc-sb-th-verify` ↔ `sc-sb-col-verify`)

## Gaps vs task (ACT scope)

| ID | Gap | Severity | ACT fix |
|----|-----|----------|---------|
| **GAP-1** | No sa-0855-specific column-header validator | **high** | `validate-agent-scoreboard-auto-green-header-v1.sh` |
| **GAP-2** | Prior validators omit thead `sc-sb-th-verify` assert | medium | Extend or sibling script |
| **GAP-3** | Law doc still says "Verified ✓" / ASF verify (§1 §4) | informational | Doc drift — UI already Auto green |
| **GAP-4** | Worker Hub has no scoreboard table | informational | Legacy maintenance only |
| **GAP-5** | Duplicate sa-0805/sa-0830/sa-0880 | low | One validator closes chain |

## Recommended ACT (minimal)

1. Ship `validate-agent-scoreboard-auto-green-header-v1.sh`:
   - `renderAgentScoreboard` contains `sc-sb-table` + `<thead>`
   - `<th class="sc-sb-th-verify">Auto green</th>` inside scoreboard function block
   - Table body uses `sc-sb-col-verify` (column pairing)
   - Reject stale copy: no `Verify ✓` / `ASF verify` in thead
2. Chain: `validate-scoreboard-auto-green-pill-v1.sh` (cell contract)
3. Crosswalk attachment — legacy scope note
4. **No** `app.js` edits unless grep fails (disk shows **implemented**)

## Preflight validators (CHECK)

| Validator | Result |
|-----------|--------|
| validate-scoreboard-auto-green-pill-v1 | PASS |
| validate-render-agent-scoreboard-v1 | PASS |
| validate-fleet-auto-green-count-v1 | PASS · fleet_auto_green_count=8 |
| validate-agent-scoreboard-auto-verify-v1 | PASS · 8 auto_pass rows |
| worker_verify_fast_v1 | PASS (L1) |
| Live POST /api/agent-scoreboard list | PASS · ok=true |

## Verdict

**CHECK complete** — **column header implemented** on legacy disk (`Auto green` + `sc-sb-th-verify`); gap = **dedicated thead validator**. **STOP** — no implement · no closeout.

*End sa-0855 CHECK*
