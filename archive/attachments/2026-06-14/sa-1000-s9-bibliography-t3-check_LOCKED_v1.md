# sa-1000 CHECK — Phase s9 research index bibliography (T3 dedup audit)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14T11:08Z · **Turn:** CHECK · **Worker:** SourceA · **Tier:** T3 research only

## Duplicate title audit

| SA | Tier | REGISTRY | Receipt | Canonical? |
|----|------|----------|---------|--------------|
| sa-0975 | T2 | **done** | `receipts/sa-0975-receipt.json` | **YES** — primary s9 bibliography index research |
| sa-1000 | T3 | backlog | — | **NO** — cite sa-0975; no re-research |

**Same title** (slot 24 repeats). `SOURCEA-1000-LOCK.md` bibliography shipped by sa-0975 ACT. Canonical doc also lists duplicates **sa-0925**, **sa-0950**.

## Canonical research (read-only)

**Path:** `archive/attachments/2026-06-14/sa-0975-phase-s9-research-index-sourcea-1000-lock-bibliography_LOCKED_v1.md`

**Verdict (unchanged at 676/1000):** SOURCEA-1000-LOCK lacked bibliography — sa-0975 appended phase-s9 canonical index (22 rows) + `validate-sourcea-1000-s9-bibliography-v1`; duplicate-tier titles cite T2 rows only.

## ACT spec (next turn · 155/156)

| Piece | Action |
|-------|--------|
| `archive/attachments/2026-06-14/sa-1000-s9-bibliography-t3-crossref_LOCKED_v1.md` | T3 stub: `canonical_sa: sa-0975` |
| `scripts/validate-s9-bibliography-crossref-v1.sh` | Assert cross-ref cites sa-0975; no duplicate matrix |
| `SOURCEA-PRIORITY.md` | Evidence row on ACT |

## Verdict

**CHECK PASS** — duplicate detected; ACT = cross-ref + validator only.

*End sa-1000 CHECK*
