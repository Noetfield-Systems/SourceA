# sa-0854 CHECK — Validate Today tab nudge banner links to council-room tab

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13T22:40Z · **Turn:** CHECK · **Worker:** SourceA  
**Tier:** T2 (duplicate: sa-0804 T0 · sa-0829 T1 · sa-0879 T3)

## Task (read-only)

Validate **Today** tab essay nudge banner button navigates to **council-room** tab.

## Hub law context

| Surface | Today + nudge banner |
|---------|----------------------|
| **Legacy** `/legacy/` `app.js` | **In scope** — `renderToday()` + `renderEssayNudgeBanner()` |
| **Worker Hub** `/` | **Out of scope** — no Today tab |

Law: `HUB_WORKER_ONLY_ARCHIVED_MONOLITH_LOCKED_v1.md`

## Live disk (CHECK 2026-06-13)

| Piece | Status |
|-------|--------|
| `renderEssayNudgeBanner()` | present · `data-tab="council-room"` on Council → button (L7839) |
| `renderToday()` | calls `renderEssayNudgeBanner(data().essayDiscourse)` (L9239) |
| `renderCouncilRoom()` | also embeds banner (L8041/L8174) |
| Essay nudges logged | **0** — banner hidden at runtime (no missing agents) |
| `validate-essay-nudge-banner-v1` | **PASS** — sa-0307/0317/0357 (function + class) |
| `validate-today-nudge-council-link-v1` | **absent** — no explicit Today→council-room link assert |

## Partial coverage (existing)

`validate-essay-nudge-banner-v1.sh` checks:
- `renderEssayNudgeBanner` exists
- Council/Today call sites
- `sc-essay-nudge-banner` class

**Does not** assert `data-tab="council-room"` inside banner HTML or Today-specific wiring.

## Gaps vs task (ACT scope)

| ID | Gap | Severity | ACT fix |
|----|-----|----------|---------|
| **GAP-1** | No sa-0854-specific link validator | **high** | `validate-today-nudge-council-link-v1.sh` |
| **GAP-2** | Prior validator incomplete on council-room `data-tab` | medium | Extend or sibling script |
| **GAP-3** | 0 nudges — runtime banner not visible | informational | Validator is static; OK when nudges=0 |
| **GAP-4** | Worker Hub has no Today tab | informational | Legacy maintenance only |
| **GAP-5** | Duplicate sa-0804/sa-0829/sa-0879 | low | One validator closes chain |

## Recommended ACT (minimal)

1. Ship `validate-today-nudge-council-link-v1.sh`:
   - `renderToday` contains `renderEssayNudgeBanner`
   - `renderEssayNudgeBanner` contains `data-tab="council-room"`
   - `sc-goto-tab` handler binds `data-tab` (smoke grep)
2. Crosswalk attachment — legacy scope note
3. **No** `app.js` edits unless grep fails (disk shows **implemented**)

## Preflight validators (CHECK)

| Validator | Result |
|-----------|--------|
| validate-essay-nudge-banner-v1 | PASS · 0 nudges |
| validate-essay-nudges-council-v1 | PASS |
| validate-refresh-pipeline-360-v1 | PASS |
| find_critical_bugs (FCB fast) | **critical 0** |

## Verdict

**CHECK complete** — **link implemented** on legacy disk; gap = **dedicated Today→council-room validator**. **STOP** — no implement · no closeout.

*End sa-0854 CHECK*
