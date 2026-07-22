
**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
[MAINTAINER_AGENT_REF · sinaai_maintainer · MAINT-REF-INCIDENT-028-001]

| Field | Value |
|-------|-------|
| **ref_tag** | `MAINT-REF-INCIDENT-028-001` |
| **trace_id** | `MAINT-REF-2026-06-12-INCIDENT-028-001` |
| **sequence_id** | SA-2026-06-12-INCIDENT-028 |
| **Subject** | `PROMPT_FEED_LIVE` · `AGENT_CHAT_STALE_LAW` |
| **Date** | 2026-06-12 |
| **Severity** | High (founder trust / wrong operating instructions) |
| **Reporter** | SourceA Worker |
| **Backlog** | AR-ede028c43c |
| **Related** | INCIDENT-024 (remediated 2026-06-10) · INCIDENT-013 · INCIDENT-027 |

# INCIDENT-028 — Worker stale prompt-feed auto-send advice (LOCKED v1)

## Executive summary

On 2026-06-12, SourceA Worker told ASF three times to open Prompt feed and **"tap Confirm — auto-send 10 prompts."** That instruction is **obsolete on disk** since INCIDENT-024. Auto-send of OpenRouter-generated execution prompts was superseded by machine-owned live queue turns. Worker followed a **stale Cursor injected rule snapshot**, not current disk law.

**Verdict:** STALE AGENT — not stale hub engine, not stale queue. Stale agent law source + incomplete 024 UI/doc scrub.

## What broke

| What Worker said | Disk law today | Match? |
|------------------|----------------|--------|
| "Tap Confirm — auto-send 10 prompts" | Forbidden in `.cursor/rules/prompt-queue.mdc` §4 | NO |
| Confirm gates delivery | Confirm = cosmetic stamp only — never blocks | NO |
| OpenRouter propose = execution order | Machine SSOT = `live-ongoing-prompts-next-10-v1.json` | NO |
| Prompt feed drives run inbox | Execution = run inbox + `validate-next-prompt-pack-live` | NO |

**Execution unaffected:** `prompt_direction.confirm` returns `auto_feed: false`; machine queue at cursor_pos 1 remained healthy.

## Root causes (effect attribution)

| Rank | Cause | % |
|------|-------|---|
| 1 | Stale Cursor injected workspace rule (pre-024 prompt-queue text) | 30% |
| 2 | Agent skipped disk-first read before founder-facing output | 26% |
| 3 | Incomplete INCIDENT-024 remediation — stale UI/doc surfaces | 20% |
| 4 | Agent conflated propose with execution | 12% |
| 5 | INCIDENT-024 not in Worker session-start mandatory read | 7% |
| 6 | `prompt-queue.mdc` alwaysApply: false — correct law optional in session | 5% |

## Remediation (Maintainer P0 — 2026-06-12)

| # | Fix | Status |
|---|-----|--------|
| 1 | This LOCKED body + registry row 028 | shipped |
| 2 | Scrub hub UI "auto-send" (`app.js`) | shipped |
| 3 | Fix `founder_commitments.py` copy | shipped |
| 4 | Fix `sync_founder_missed_actions_v1.py` nudge | shipped |
| 5 | Fix `SINA_CURSOR_PROMPT_QUEUE_ORDER_v1.md` confirm row | shipped |
| 6 | Fix `prompt_direction.py` docstring + propose message | shipped |
| 7 | Wire 024/028 into `MANDATORY_READ_BY_ROLE` §Worker | shipped |
| 8 | `validate-prompt-feed-no-autosend-copy-v1.sh` | shipped |

## Correct law (effective after 024)

**Execution:** `healthy-queue-state` → `live-ongoing-prompts-next-10` → run inbox → INBOX. Gate: `validate-next-prompt-pack-live-v1.py`.

**Display + optional (never gates):** Prompt feed UI polls live ongoing JSON. OpenRouter propose = AI commentary outline only. Confirm = cosmetic `founder_confirmed_at` stamp.

**Agent close-line:** Prompt feed shows live next 10 from machine queue. Optional big-picture commentary. Execution = run inbox — **never** "confirm auto-send."

## Verify

```bash
bash scripts/validate-prompt-feed-no-autosend-copy-v1.sh
bash scripts/validate-live-prompt-feed-e2e-v1.sh
```

**END INCIDENT-028** — SA-2026-06-12-INCIDENT-028 · **MAINT-REF-INCIDENT-028-001**
