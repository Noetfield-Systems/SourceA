# sa-0978 CHECK — RAGAS vs Eval-1b (T3 dedup audit)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14T03:48Z · **Turn:** CHECK · **Worker:** SourceA · **Tier:** T3 research only

## Duplicate title audit

| SA | Tier | REGISTRY | Receipt | Canonical? |
|----|------|----------|---------|--------------|
| sa-0953 | T2 | **done** | `receipts/sa-0953-receipt.json` | **YES** — primary internal note |
| sa-0978 | T3 | backlog | — | **NO** — cite sa-0953; no re-research |

**Same title** (slot 2 repeats across tiers). sa-0975 bibliography indexes sa-0953 row.

## Canonical research (read-only)

**Path:** `archive/attachments/2026-06-14/sa-0953-ragas-vs-eval1b-research_LOCKED_v1.md`

**Verdict (unchanged at 656/1000):** Eval-1b is the enforcement-linked behavioral gate; RAGAS would be a deferred third metric layer — not a replacement.

## Factory truth (CHECK snapshot)

| Signal | Value |
|--------|-------|
| Valid YES | 656/1000 |
| Eval-1b | `eval_packet_v1b_report.json` · dispatch gate |
| OpenRouter in ACT | **blocked** |

## ACT spec (next turn · 95/156)

**Do not re-write RAGAS compare matrix.** Ship dedup cross-ref only:

| Piece | Action |
|-------|--------|
| `archive/attachments/2026-06-14/sa-0978-ragas-eval1b-t3-crossref_LOCKED_v1.md` | T3 stub: `canonical_sa: sa-0953` |
| `scripts/validate-ragas-eval1b-crossref-v1.sh` | Assert cross-ref cites sa-0953; no duplicate RAGAS table |
| `SOURCEA-PRIORITY.md` | Evidence row on ACT |

## Verdict

**CHECK PASS** — duplicate detected; ACT = cross-ref + validator only.

*End sa-0978 CHECK*
