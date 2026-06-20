# sa-0976 CHECK — GPT-4o · Claude Opus · Gemini workflow gaps (T3 dedup audit)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14T03:38Z · **Turn:** CHECK · **Worker:** SourceA · **Tier:** T3 research only

## Duplicate title audit

| SA | Tier | REGISTRY | Receipt | Canonical? |
|----|------|----------|---------|--------------|
| sa-0951 | T2 | **done** | `receipts/sa-0951-receipt.json` | **YES** — primary research |
| sa-0976 | T3 | backlog | — | **NO** — cite sa-0951; no re-research |

**Same title** in generator taxonomy (slot 0 repeats across tiers). sa-0975 bibliography indexes sa-0951 row; sa-0976 must not fork prose.

## Canonical research (read-only)

**Path:** `archive/attachments/2026-06-14/sa-0951-model-workflow-gaps-research_LOCKED_v1.md`

| Model | Industry strength | SourceA gap (unchanged at 654/1000) |
|-------|-------------------|--------------------------------------|
| GPT-4o | Fast multimodal, tool ecosystem | No first-class GPT lane — OpenRouter eval pilots only |
| Claude Opus | Long context, SWE | Brain/Worker edit lock; no side-by-side receipt chain |
| Gemini | Google stack, long context | Not in eval-1b pilots; no Gemini grounding validator |

**WTM synthesis:** `brain-os/wtm/SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md` — architecture strong; multi-vendor **workflow** compare remains research debt, not dispatch blocker.

## Factory truth (CHECK snapshot)

| Signal | Value |
|--------|-------|
| Valid YES | 654/1000 |
| Eval-1b | OpenRouter A/B scaffold · machine gate |
| OpenRouter in ACT | **blocked** (prompt_feasibility_gate) |
| Founder law | Hub-only — no Terminal |

## ACT spec (next turn · 89/156)

**Do not re-write compare table.** Ship dedup cross-ref only:

| Piece | Action |
|-------|--------|
| `archive/attachments/2026-06-14/sa-0976-model-workflow-gaps-t3-crossref_LOCKED_v1.md` | T3 stub: `canonical_sa: sa-0951` + pointer + one-line factory verdict |
| `scripts/validate-model-workflow-gaps-crossref-v1.sh` | Assert cross-ref exists, cites sa-0951 path, min row count 0 (no duplicate table) |
| `SOURCEA-PRIORITY.md` | Evidence row on ACT |

## VERIFY spec

Receipt + REGISTRY `done` + `worker_verify_closeout_v1.sh` with task validator.

## Verdict

**CHECK PASS** — duplicate detected; ACT is cross-ref + validator, not new research spend.

*End sa-0976 CHECK*
