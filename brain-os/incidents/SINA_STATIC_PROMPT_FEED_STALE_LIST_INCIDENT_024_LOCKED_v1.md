# INCIDENT-024 — Static Prompt feed stale 10-pack (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Subject:** `PROMPT_FEED_LIVE` · `INCIDENT_SUBJECT_INDEX` SUBJ-PROMPT  
**Date:** 2026-06-10  
**Status:** remediated  

## What broke

Prompt feed tab showed OpenRouter `prompt-queue.json` static batch until founder re-confirmed. Queue cursor could move 106→107 while UI still listed old 10-pack.

## Root cause

Two SSOTs: `prompt_direction.py` (AI invention) vs `healthy-queue-state-v1.json` (machine). UI wired to wrong source; `worker-drain-next-10` deduped by sa_id not queue turns.

## Remediation

- `SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md`
- `scripts/live_ongoing_prompts_v1.py` — 10 consecutive turns
- `scripts/validate-next-prompt-pack-live-v1.py` — machine gate
- Hub `renderPromptFeed` — live poll 5s
- `prompt_direction.confirm` — commentary only, not execution queue

## Verify

`bash scripts/validate-live-prompt-feed-e2e-v1.sh`
