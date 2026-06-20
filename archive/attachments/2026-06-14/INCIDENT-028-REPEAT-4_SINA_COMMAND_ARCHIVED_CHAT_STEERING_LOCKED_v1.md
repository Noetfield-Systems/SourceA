# INCIDENT-028 repeat #4 — Agent steered founder to archived Sina Command (LOCKED v1)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Reporter:** SourceA Worker session `fd67502f`  
**Severity:** High (founder trust · wrong daily UI · repeat after disk fix)  
**Parent:** `brain-os/incidents/SINA_WORKER_STALE_PROMPT_FEED_AUTOSEND_INCIDENT_028_LOCKED_v1.md`  
**Related:** INCIDENT-031 (`no_hub`) · `000-dead-law-stubs.mdc` · `prompt-queue.mdc` v6

---

## What broke (this session)

Worker ended **multiple** substantive replies (sa-0975 ACT/VERIFY, sa-0976 CHECK, AUTO HEAL) with variants of:

- "Open **Sina Command** → **Prompt feed**"
- "review the 10 steps and tap **Confirm**"
- `curl` to `/api/prompt-direction` presented as founder path

ASF correction: **Sina Command is ARCHIVED. We are not using that for daily ops.**

---

## Disk truth (who wins — chat memory loses)

| Surface | Status | Daily? |
|---------|--------|--------|
| **Sina Command** / legacy monolith | `http://127.0.0.1:13020/legacy/` | **NO — archive only** |
| **Super Fast Hub (H1)** | `http://127.0.0.1:13020/` | **YES — daily** |
| **Machine Hub (H2)** | `http://127.0.0.1:13020/machines/` | Maintainer depth only |
| **Execution order** | `run inbox` + `~/.sina/live-ongoing-prompts-next-10-v1.json` | Machine SSOT |
| **Founder UI for queue** | Super Fast Hub → **Next steps** | Never "Prompt feed" |

**Law already correct on disk:** `prompt-queue.mdc` v6 · `000-dead-law-stubs.mdc` · `SOURCEA_FOUNDER_MACHINE_TERMINOLOGY_DICTIONARY_LOCKED_v1.md` §3.

---

## Root cause (effect attribution)

| Rank | Cause | Fix |
|------|-------|-----|
| 1 | **Chat / summary memory** carried pre-028 close-line template | Session gate + mirror before reply |
| 2 | **Stale `agent-loop.mdc`** still says "founder clicks in Sina Command" | Patched this session |
| 3 | Agent ran `prompt-direction` curl then **parroted legacy UI name** in close-line | Executor-only API; never name legacy UI to founder |
| 4 | Skipped `agent_memory_mirror_v1.py --validate` on founder-facing close | Mandatory before ship |

**Not root cause:** Hub engine down · queue broken · Valid YES drift — factory was honest at 654/1000.

---

## Remediation (this session)

| # | Action |
|---|--------|
| 1 | This incident receipt |
| 2 | `agent-loop.mdc` — Super Fast Hub / Worker-only; legacy paths marked archive |
| 3 | `agent_memory_mirror_v1.py --sync --validate` |
| 4 | Backlog `agent-review` submit |

---

## FORBIDDEN close-lines (instant STALE)

- Sina Command → anything
- Prompt feed (daily name)
- Confirm auto-send / review 10 steps tap Confirm
- Hub → Refresh / rebuild / Track as daily path

## CORRECT close-lines

- **Worker:** `RUN INBOX` when ready — one sa per turn; disk queue is SSOT
- **Daily glance (optional):** Super Fast Hub → **Next steps** — live next-10 on disk
- **Safety:** Super Fast Hub → **Safety** if staleness alarm
- **Never** ask founder to open Terminal, legacy monolith, or Confirm gate

---

## Agent tips (operating procedure)

1. **Session start:** `python3 scripts/agent_session_gate_run_v1.py --role worker --json` — read mirror F10–F13
2. **Before every founder-facing paragraph:** grep mental check — did I say Sina Command or Prompt feed? → rewrite
3. **Conflict resolver:** `agent_truth_bundle_v1.py --json` beats chat memory
4. **Close-line template:** `Next: RUN INBOX → sa-XXXX ROLE` + factory-now line from disk JSON only
5. **prompt-direction API:** executor background only — **do not** tell founder to open any UI for it
6. **INCIDENT-031:** no hub rebuild steering; light worker heal only

---

*End INCIDENT-028-REPEAT-4*
