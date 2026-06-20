# Automation Converge Program (LOCKED v1)

**Saved:** 2026-06-10T11:58:40Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-07  
**Today plan:** `TODAY_AUTORUN_50_PLAN_LOCKED_v1.md` — **SUPERSEDED 2026-06-10** (see `FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md`)  
**Cursor AUTO-RUN:** not P0 — next automation path per founder law 2026-06-10  
**Authority:** ASF — four-brain convergence (Cursor Brain, Claude Pro, GPT, Old Brain)  
**Parent:** `GOAL_HIERARCHY_LOCKED_v1.md` · `BRAIN_FULL_SYSTEM_MAP_LOCKED_v1.md` · `GOAL_EXECUTION_ACTIVE_LOCKED_v1.md`  
**Prompt pack:** `brain-os/plan-registry/automation-fast-track-100/` (`ft-0001` … `ft-0100`) — **100 unique, zero duplication** (retired `automation-converge-1000` tier mirrors)

---

## 0. North star (one sentence)

> **SUPERSEDED 2026-06-10 for founder P0:** Cursor AUTO-RUN is **rejected**. Factory default = **FREEZE** · **Safety** · **RUN INBOX when Brain routes**.

**One Hub tap → headless queue → Worker executes → broker syncs → repeat — no paste, no Terminal, no advisor archaeology.**

Full automation (A+B+C) = that pattern on **SourceA drain**, **multi-repo dispatch**, and **Hub↔Cursor** — in that order.

---

## 1. DROP (immediate — not throughput)

| Drop | Why |
|------|-----|
| MANIFEST.yaml builds | Structural debt — post Phase 1 |
| Path drift cleanup sweeps | E2E noise — not runtime failure |
| E2E score chasing | `audit_backend_e2e` PASS is enough |
| FORGE probe before ship | FORGE green in `forge/` — ship first |
| Multi-brain compare ceremonies | Act on disk + validators only |
| Dual rails (healthy pack + pick 1) | **One rail:** `pick 1` + autoloop until Phase 1 exit |
| Manual Worker paste per turn | Use headless path |

---

## 2. Tonight — founder (Hub only, no Terminal) — SUPERSEDED 2026-06-10

**See:** `FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md`

| # | Action | Owner |
|---|--------|-------|
| ~~1~~ | ~~Hub → AUTO-RUN 50~~ | **DEPRIORITIZED** — not a goal |
| 1 | Hub Actions → ship / validate (executor) | ASF taps only |
| 2 | Agentic outreach + demo booking | **Agents** — founder never email/call |
| 3 | Voice/outbound lane when wired | Agents + employees |

**Executor:** monitors `~/.sina/goal1-worker-batch-latest.log` — not founder.

---

## 3. Phase 1 exit criteria (then Loop B)

- [ ] **50** autoloop turns with **`broker=yes`** streak (≥95%)
- [ ] **s1 backlog < 40** (from ~66 at lock time)
- [ ] **FORGE** live on Vercel
- [ ] **`dispatch_ready=true`** on hub (honest)
- [ ] Optional: TrustField demo booked

**Morning check (executor):**

```bash
grep -c 'broker=yes' ~/.sina/goal1-worker-batch-latest.log
python3 scripts/goal-progress-v1.py
python3 scripts/brain_validate_goal1_v1.py --json
```

---

## 4. Three loops (never confuse)

| Loop | Full = | Blocker today |
|------|--------|---------------|
| **A** — REGISTRY / healthy drain | `goal1_auto_loop` unattended · activate PASS · broker yes | Manual paste habit |
| **B** — SinaPromptOS | `dispatch-day` scheduled · no daily paste | `auto_sync_plan=false` |
| **C** — Hub 10-round | Auto submit-round · no clipboard | Auto-paste incident lock |

**Phase 2 (after exit):** Loop B — `auto_sync_plan=true` **only** with **m5 verified-only** (`m5_sync.py`).  
**Phase 3:** Loop C — Cursor SDK M8b + incident unlock checklist.

---

## 5. Automation levels

| Level | Meaning | Status at lock |
|-------|---------|----------------|
| **L1** | Hub + pick 1 + optional autoloop | **NOW** |
| **L2** | eval live + `dispatch_ready=true` + dispatch Phase 2b | eval ✅ · dispatch founder gate |
| **L3** | Zero-human — 7 blockers in `BRAIN_FULL_SYSTEM_MAP` §L3 | **Not shipped** |

**Law:** Never claim L3 until blockers close. Speed = **turns/day**, not new architecture.

---

## 6. Throughput truth

| Mode | s1 (~66 tasks) |
|------|----------------|
| 1 manual turn/day | ~2 months |
| 10 autoloop/day | < 1 week |
| 50 autoloop/day | ~2 days |

**Locked law:** Phase-first drain — cannot skip s1 for s4. Work inside it at maximum speed.

---

## 7. Spine (collapse everything)

```text
INPUT (pick 1 / queue state) → QUEUE (INBOX + broker) → EXECUTOR (headless turn) → VALIDATE+SYNC → repeat
```

---

## 8. Prompt pack law (fast track — no games)

> **SUPERSEDED 2026-06-10:** **Hub ▶ AUTO-RUN** is legacy — use **RUN INBOX** + **Brain sync** under FREEZE.

- **Pack id:** `automation-fast-track-100-locked`
- **IDs:** `ft-0001` … `ft-0100` — **one unique task each**, no T0/T1 mirrors
- **Pick:** `bash scripts/plan-automation-fast-track-run.sh pick 1`
- **Runtime default:** **Hub ▶ AUTO-RUN 50** (`goal1_auto_loop_v1.py`) — **not** 100 manual pastes
- **Daemon:** `goal1_run_loop_v1.py` already exists — **do not** build `autoloop_daemon.py`
- **Forbidden:** pick 30 · tier duplication · MANIFEST · drift hunts during Phase 1

---

*End AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1*
