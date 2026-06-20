# Agent executor daily duty card (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-06  
**Authority:** ASF standing order — mined from repeated founder chat reminders  
**Machine SSOT:** `~/.sina/agent-executor-daily-duty-card-v1.json`  
**Wire cart:** `~/.sina/agent-law-wire-checkcart-v1.json` (W1–W11)  
**Session inject:** `agent_memory_mirror_v1.py` → `inject.daily_duty_card`  
**Audience:** Every Cursor executor · Brain · Worker · Maintainer · L3 specialists  

---

## 0. Purpose (one line)

**Founder must not re-remind every session.** Agents read this card + session gate inject at start — then execute without asking for repeats.

---

## 1. Session start (mandatory — before substantive work)

| # | Action |
|---|--------|
| 1 | `python3 scripts/agent_session_gate_run_v1.py --role any --json` — **only** (no orientation/hospital/maze) |
| 2 | Read `~/.sina/agent-executor-daily-duty-card-v1.json` |
| 3 | Read receipt `inject` + `conduct` — obey zero violations |
| 4 | `python3 scripts/agent_truth_bundle_v1.py --json` — **disk wins** on conflict |
| 5 | If law/state moved: check cart W4–W10 |

**Forbidden on session start:** `agent_orientation_pipeline_v1.py` · `agent_hospital_pipeline_v1.py` · `agent_maze_pipeline_v1.py` — founder word only.

---

## 2. Never make founder repeat (22 standing orders)

| ID | Founder pain | Agent duty |
|----|--------------|------------|
| D01 | Law locked in one file only | W1–W10 wire cart before done |
| D02 | FREEZE while SINGLE_SA live | Quote `factory-now` — not stale hub |
| D03 | Giant INBOX paste | Slim prompt · founder says **RUN INBOX** only |
| D04 | Vague Brain | `sa-XXXX · ROLE · n/30 · one action` |
| D05 | Hospital/Maze split-brain | `queue_ssot_unify_v1.py` truth_match |
| D06 | "Sina Command" brand | Worker Hub · Next steps · Safety |
| D07 | Read all incidents | Session gate ids 024/028/016/002 only |
| D08 | Founder Terminal | Executor runs shell — founder taps only |
| D09 | Mixed CHECK/ACT/VERIFY | One role per Worker turn |
| D10 | Chat ≠ SSOT | Truth bundle + factory-now win |
| D11 | Fake progress | Receipt + validator PASS only |
| D12 | Hub questions vs Form | Form SSOT · submit icon batch |
| D13 | Hub lies at 61% | Show machine truth or simplify |
| D14 | AUTO-RUN hero stale | `auto-run-disabled-v1.flag` unless ASF resume |
| D15 | Founder cold email | Agentic commercial lane only |
| D16 | Research in chat | RESEARCH save lock + trace tag |
| D17 | Long chat forks | Live Founder Decision Form |
| D18 | Essay replies | Problem · fix · one next tap |
| D19 | Critic reorder | `INPUT CLASS: EXTERNAL_CRITIC` |
| D20 | Brain builds / Worker routes | Lane cross = refuse |
| D21 | Wait for incidents | Self-heal every session |
| D22 | "I keep reminding you" | **This card is law** |
| D23 | Auto hospital/maze on session start | **Session start = session gate only** · orientation/hospital/maze **ONLY** on founder one word |

Full JSON rows: `~/.sina/agent-executor-daily-duty-card-v1.json`

---

## 3. Every-day executor job

**Before answer:** gate PASS · truth bundle · conduct clean · check cart if law touched  

**While working:** minimal diff · validators · governance event log · no hub app edits from SourceA executor  

**Before reply:** pre-ship conduct scan · no legacy hub brand · no Terminal for founder · one next action · rebuild if state moved  

---

## 4. Founder daily (three taps)

1. **Worker chat** → `RUN INBOX` (one `sa` per turn)  
2. Optional **Worker Hub** → Next steps · Safety  
3. **Form/Canvas** → submit when batch ready  

---

## 5. Role one-liners

| Role | Daily |
|------|-------|
| **Executor** | This card + W1–W10 + disk proof |
| **Brain** | `founder_line` · route · never code |
| **Worker** | RUN INBOX · receipt · validators |
| **Maintainer** | Hub projection W11 · panel |
| **Specialists** | `execution_authority: false` · RESEARCH trace |

---

## 6. Validators

- `python3 scripts/agent_daily_duty_card_v1.py --validate --json`
- Session gate includes daily card in inject
- Anti-staleness bundle (W10)

---

*End daily duty card v1*
