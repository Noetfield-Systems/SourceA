# sa-0977 CHECK — Cursor vs Devin vs SWE-agent verify gates (T3 dedup audit)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14T03:46Z · **Turn:** CHECK · **Worker:** SourceA · **Tier:** T3 research only

## Duplicate title audit

| SA | Tier | REGISTRY | Receipt | Canonical? |
|----|------|----------|---------|--------------|
| sa-0952 | T2 | **done** | `receipts/sa-0952-receipt.json` | **YES** — primary spike |
| sa-0977 | T3 | backlog | — | **NO** — cite sa-0952; no re-research |

**Same title** (slot 1 repeats across tiers). sa-0975 bibliography row for sa-0952; sa-0977 must not fork compare matrix.

## Canonical research (read-only)

**Path:** `archive/attachments/2026-06-14/sa-0952-agent-verify-gates-spike_LOCKED_v1.md`

| Runtime | SourceA fit |
|---------|-------------|
| **Cursor Worker** | Canonical — broker + receipts + `worker_verify_closeout_v1` |
| **Devin** | Partial — no factory adapter / no REGISTRY law |
| **SWE-agent** | Research benchmark only — no spine |

**Verdict (unchanged at 655/1000):** Cursor Worker is the only runtime wired to honest factory closeout today.

## Factory truth (CHECK snapshot)

| Signal | Value |
|--------|-------|
| Valid YES | 655/1000 |
| OpenRouter in ACT | **blocked** |
| Related | sa-0972 hub-only vs terminal-first · sa-0957 WTM agent-os |

## ACT spec (next turn · 92/156)

**Do not re-write compare matrix.** Ship dedup cross-ref only:

| Piece | Action |
|-------|--------|
| `archive/attachments/2026-06-14/sa-0977-agent-verify-gates-t3-crossref_LOCKED_v1.md` | T3 stub: `canonical_sa: sa-0952` + pointer |
| `scripts/validate-agent-verify-gates-crossref-v1.sh` | Assert cross-ref cites sa-0952; no duplicate Devin/SWE table |
| `SOURCEA-PRIORITY.md` | Evidence row on ACT |

## VERIFY spec

Receipt + REGISTRY `done` + `worker_verify_closeout_v1.sh` with task validator.

## Verdict

**CHECK PASS** — duplicate detected; ACT = cross-ref + validator only.

*End sa-0977 CHECK*
