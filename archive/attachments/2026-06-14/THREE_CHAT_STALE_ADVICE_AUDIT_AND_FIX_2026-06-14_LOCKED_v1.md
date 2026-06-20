# Three-chat stale advice audit + permanent fix (LOCKED v1)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF order · Brain executor  
**Chats:** Brain `58148ac9` · Gov `e54ddfa8` · Worker `fd67502f` (+ alt `85dd7cd4`)  
**Incidents:** INCIDENT-024 · 027 · 028 · AR-2af34431d3

---

## Executive verdict

**Root cause:** Seven memory surfaces not synced — agents fixed law in one file while **injected rules + skills + scripts** still broadcast legacy “Sina Command → Prompt feed” and “Hub → Refresh”.

**Not:** worker memory wiped · not factory broken · not founder wrong on vocabulary.

---

## Mistake inventory (all chats)

| # | Mistake | Chats | Severity | Status |
|---|---------|-------|----------|--------|
| M1 | “Open Sina Command → Prompt feed → Confirm auto-send” | Brain · Gov · Worker | **P0** | **FIXED** gates + rules v5 |
| M2 | **Hub = daily** while also saying **archive monolith** | Brain · Gov | **P0** | **FIXED** terminology + dead-law stubs |
| M3 | “Hub → Refresh / Hub → Track” as daily rhythm | Brain · 85dd7cd4 | P1 | **FIXED** skills + unified brief |
| M4 | Gov Specialist **Worker-class edits** (queue builder, hub) | Gov | P1 | **ROUTED** — Maintainer 2 owns SHIP |
| M5 | TrustField smoke **localhost default** | Gov | P2 | **FIXED** in chat (WEB_BASE env) |
| M6 | “Governance complete / AUTO-RUN P0” hero (Jun 8–9) | Gov archaeology | STALE | **IGNORE** per Judge PAST_STALE_ONLY |
| M7 | `build-sina-daily-bowl.py` “Open Sina Command” | Disk script | P1 | **FIXED** → Super Fast Hub |
| M8 | `agent_system_unified.py` Council = Sina Command daily | Disk script | P1 | **FIXED** → `/` daily · `/legacy/` council |
| M9 | Worker SKILL “Prompt feed shows live next 10” | Skills | P1 | **FIXED** Super Fast Hub only |
| M10 | Legacy hub `command-data.json` hero still says “Hub Track” | Monolith | P2 | **Maintainer** — archive monthly build only |

---

## Auto-heal run (2026-06-14)

| Step | Result |
|------|--------|
| `governance_center_run_v1.py --tier fast` | **PASS** (self_heal · drift · cascade · stairlift · judge · thread) |
| `worker_hub_heal_v1.py` | **PASS** |
| `worker_anti_staleness_heal_v1.py` | **PASS** (no heal needed) |
| `agent_memory_mirror_v1.py --sync --validate` | **PASS** · 0 violations |

---

## Permanent fixes shipped this session

1. `.cursor/rules/000-dead-law-stubs.mdc` — Hub vocabulary + forbid Sina Command Prompt feed
2. `.cursor/rules/prompt-queue.mdc` **v6** · `alwaysApply: true` · Next steps naming
3. `.cursor/rules/brain-founder-closeout-gate.mdc` — mandatory `founder_close_line_gate` before ship
4. Worker SKILLS — repo + **`~/.cursor/skills/` sync on mirror**
5. `scripts/agent_memory_mirror_v1.py` — scan agent-skills · skill sync · NEVER-line skip
6. `scripts/build-sina-daily-bowl.py` · `scripts/agent_system_unified.py` · `AGENT_DESK_START_HERE.md`
7. `BRAIN_KNOWLEDGE_INDEX` Track row → Super Fast Hub Next steps
8. `~/.sina/governance-chat-context-v1.json` — four chat pointers

## Recheck round 2 (2026-06-14)

| Finding | Fix |
|---------|-----|
| **Stale duplicate** `~/.cursor/skills/sina-sourcea-worker/SKILL.md` | **Synced** full 142-line canonical copy |
| Mirror missed user skills path | **`_sync_user_cursor_skills()`** on every `--sync` |
| Skills flagged as violations (NEVER docs) | **SKIP** matches on NEVER/FORBIDDEN lines · SKILL.md detector |
| `prompt-queue.mdc` still mentioned Confirm | **Removed** cosmetic Confirm from close-line |
| Anti-staleness bundle | **38/39 PASS** — `s10-eternal` receipt WARN/FAIL=2 (pre-existing monitor debt) |
 + audit receipt

---

## Correct founder vocabulary (canonical)

| Term | Means |
|------|--------|
| **Hub** / **Sina Command** | Same legacy monolith · `/legacy/` · **archive** |
| **Super Fast Hub** | Daily · `http://127.0.0.1:13020/` |
| **Execution** | Worker `run inbox` · head **sa-0101** |
| **PICKs** | M1 Canvas (2 open) |

---

## Still Maintainer-owned (not Brain)

- Legacy monolith UI copy in `agent-control-panel/app.js` (hub rebuild monthly)
- `FOUNDER_DAILY_OPERATING_MODEL_LOCKED_v1.md` §Essentials glance (archive path)
- H2 `/machines/` route SHIP

---

*End THREE_CHAT_STALE_ADVICE_AUDIT_AND_FIX_2026-06-14_LOCKED_v1*
