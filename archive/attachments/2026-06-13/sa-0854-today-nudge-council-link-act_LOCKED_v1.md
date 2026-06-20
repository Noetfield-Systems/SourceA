# sa-0854 ACT — Validate Today tab nudge banner links to council-room tab

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13T22:45Z · **Turn:** ACT · **Worker:** SourceA

## Shipped (scripts only — legacy `/legacy/` scope)

| Piece | Action |
|-------|--------|
| `scripts/validate-today-nudge-council-link-v1.sh` | **NEW** — Today + banner + `data-tab="council-room"` |
| Chains | `validate-essay-nudge-banner-v1.sh` |

## Validated contract (legacy app.js)

| Check | Proof |
|-------|-------|
| `renderToday()` | calls `renderEssayNudgeBanner()` |
| Banner HTML | `data-tab="council-room"` + `sc-goto-tab` |
| Essay nudges | **0** in the repository — banner hidden; link wiring static PASS |

## No code diff

`app.js` already implemented (sa-0307) — ACT is validator-only.

## Duplicate chain

Also satisfies **sa-0804** T0 · **sa-0829** · **sa-0879**.

## Validators (ACT)

| Validator | Result |
|-----------|--------|
| validate-today-nudge-council-link-v1 | PASS |
| validate-essay-nudge-banner-v1 | PASS |

*End sa-0854 ACT*
