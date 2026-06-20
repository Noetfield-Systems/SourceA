# ASF Full Day Execution Playbook (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
## One day think · five days execute — hour-by-hour operating manual

**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-02-010  
**Classification:** INTERNAL ONLY — never commit to public git  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/SourceA/ASF_FULL_DAY_EXECUTION_PLAYBOOK_LOCKED_v1.md`  
**Authority:** Subordinate to `SINA_OS_SSOT_LOCKED.md` v3 and `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md`  
**Implementation:** `~/Desktop/SinaPromptOS/scripts/run-day.sh`  
**Locked:** 2026-06-02  
**Maintainer:** ASF

---

> **What this document is.**  
> The **missing piece** ASF asked for: a **complete full day of work** — not scattered bullets in chat.  
> **Morning → execution blocks → evening** with exact commands, files, and time budgets.  
> **Not implemented elsewhere before this file** — only summarized in Prompt OS §4 (Farsi) and unified blueprint §1.2 / §5.7.

---

## 0. Where this lived before (honest map)

| Location | What was there | Gap |
|----------|----------------|-----|
| Chat / brainstorming | «۱ روز فکر · ۵ روز اجرا» + صبح/روز/شب | Not a standalone doc |
| `SINA_PROMPT_OS_SYSTEM_LOCKED_v1.md` §4 | ۳ خط فارسی صبح/شب | No timetable, no commands |
| `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT` §1.2, §4, §5.7 | Model + loop one-liner | No **full day** playbook |
| `SinaPromptOS` | UI + `daily-snapshot.sh` | No **day runner** until `run-day.sh` |

**This file + `run-day.sh` = canonical full-day reference.**

---

## 1. Weekly rhythm (locked)

| Day type | ASF thinking | System |
|----------|--------------|--------|
| **Think day** (≈1 day / week) | Adjust `projects.json` priority, one note in UI, approve structural items only | Read SSOT + unified blueprint |
| **Execute days** (≈5 days) | **No** re-reading all repos — follow this playbook | Prompt OS only |

---

## 2. Full execute day — timeline (default)

Assume **6–8 hours** available. Scale blocks up/down.

### Block A — Morning start (15–20 min) — «صبح»

**Goal:** Know what to do without opening six repos.

| Step | Action | Command / file |
|------|--------|----------------|
| A1 | Run morning pack | `~/Desktop/SinaPromptOS/scripts/run-day.sh morning` |
| A2 | Read top project + 2 alternates | `data/day/YYYY-MM-DD/morning-summary.md` |
| A3 | Copy **primary** prompt to clipboard | auto in morning script, or UI button |
| A4 | Optional: 1-line week focus | UI **Save note** or edit `config/projects.json` |

**Output files created:**

```text
SinaPromptOS/data/day/2026-06-02/
  morning-summary.md      # human-readable priorities
  prompt-trustfield.txt   # example — one file per top-3 project
  snapshot.json           # machine state
```

**Do NOT:** read full SSOT, all READMEs, or old Cursor threads — snapshot already did.

---

### Block B — Execution sprint 1 (90–120 min) — «اجرا ۱»

| Step | Action |
|------|--------|
| B1 | Open **one** Cursor workspace (path in prompt header) |
| B2 | Paste **one** prompt from morning pack |
| B3 | Let Cursor finish **one task only** |
| B4 | Run VERIFY command from prompt |
| B5 | Agent → **EXECUTION LOG** YAML (§J in notice prompts) |
| B6 | `./scripts/submit-execution-log.sh <repo> log.yaml` |
| B7 | `./scripts/mark-done-verified.sh <repo> log.yaml` (or `mark-done.sh` + manual log) |

**Rule:** If task > 2 hours → split in `plan.json` tonight (Block E), do not expand scope in Cursor.

---

### Block C — Midday check (5 min) — optional

```bash
~/Desktop/SinaPromptOS/scripts/run-day.sh now
```

- Refreshes ranking after `plan.json` updates  
- Copy **next** prompt if primary project blocked or done  

---

### Block D — Execution sprint 2 (90–120 min) — «اجرا ۲»

Same as Block B for:

- **Same project** if still blocked on revenue (e.g. TrustField gates), OR  
- **Second project** from morning alternates (max **2 active DELIVERY** repos per day)

**Hard cap:** Max **3 Cursor prompts** per execute day (quality > quantity).

---

### Block E — Evening close (15–20 min) — «شب»

| Step | Action | Command |
|------|--------|---------|
| E1 | Evening pack | `run-day.sh evening` |
| E2 | Review `evening-summary.md` | blocked count, unfinished tasks |
| E3 | For each project touched: confirm `plan.json` updated | manual |
| E4 | Set tomorrow hint | optional note in UI or `global_priority` tweak |

**Output:**

```text
data/day/YYYY-MM-DD/evening-summary.md
```

**Weekly think day only:** edit Source A / registry — **not** every evening.

---

## 3. The eternal loop (every block)

```text
Read state → Decide (router) → Prompt(s) parallel ≤3 → Cursor → Verify → Execution log → Truth cycle → plan.json
```

Law: `SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md`

This is the **full day** broken into **time blocks** — same loop, three times max per day.

---

## 4. Command reference (implementation)

| Intent | Command |
|--------|---------|
| Truth + feedback cycle | `./scripts/run-feedback-cycle.sh` |
| Submit execution evidence | `./scripts/submit-execution-log.sh <repo> log.yaml` |
| Verified done | `./scripts/mark-done-verified.sh <repo> log.yaml` |
| Full morning pack | `./scripts/run-day.sh morning` |
| Next prompt now | `./scripts/run-day.sh now` |
| Evening reflection | `./scripts/run-day.sh evening` |
| All three | `./scripts/run-day.sh full` |
| UI equivalent | `Sina Prompt OS.command` → tab **Now** |

From repo root:

```bash
cd ~/Desktop/SinaPromptOS
source .venv/bin/activate
./scripts/run-day.sh morning
```

---

## 5. Think day playbook (≈1 day / week)

| Block | Duration | ASF | Documents |
|-------|----------|-----|-----------|
| T1 | 30 min | Read law only | `SINA_OS_SSOT_LOCKED.md` |
| T2 | 30 min | Agents/automation | `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md` |
| T3 | 30 min | Set priorities | `SinaPromptOS/config/projects.json` |
| T4 | 30 min | Per-project queue | each `*/os/plan.json` — **only** `next_tasks` / `blocked` |
| T5 | 15 min | Sign conflicts / phase | SSOT gaps, registry if needed |

**No Cursor coding on think day** unless emergency DELIVERY gate.

---

## 6. Role clarity (one table)

| Role | Full-day job |
|------|----------------|
| **Sina OS** | Already read on think day — embedded in every prompt |
| **Prompt OS** | Morning/evening packs + midday `now` |
| **ASF** | Paste, verify, update `plan.json`; structural edits think day only |
| **Cursor** | Execute one task per prompt |
| **Runtime** (`:8000`) | Separate — Telegram PAIOS, not this Cursor day loop |

---

## 7. فارسی — خلاصه یک روز اجرا

| بلوک | زمان | کار تو |
|------|------|--------|
| **صبح** | ۱۵ دقیقه | `run-day.sh morning` → خلاصه + پرامپت |
| **اجرا ۱** | ۱.۵–۲ ساعت | Cursor → یک تسک → verify → plan.json |
| **ظهر** | ۵ دقیقه | `run-day.sh now` در صورت نیاز |
| **اجرا ۲** | ۱.۵–۲ ساعت | پروژه دوم یا ادامه همان |
| **شب** | ۱۵ دقیقه | `run-day.sh evening` → فردا |

**تو فکر نمی‌کنی «چه پروژه‌ای»** — سیستم گفته. **تو فکر می‌کنی «آیا verify سبز شد»** — آن هم کوتاه.

---

## 8. Never-do on execute days

1. Open all six Cursor workspaces at once  
2. Skip `plan.json` update after a sprint  
3. Redesign architecture from Cursor chat  
4. More than 3 prompts/day without ASF explicit push  
5. TrustField **new features** under freeze (ops/gates only)  

---

## Document control

| Version | Date | sequence_id | Change |
|---------|------|-------------|--------|
| 1.0 | 2026-06-02 | SA-2026-06-02-010 | Initial lock — full day playbook + run-day.sh binding |

**ASF approval:** ___________________ **Date:** __________
