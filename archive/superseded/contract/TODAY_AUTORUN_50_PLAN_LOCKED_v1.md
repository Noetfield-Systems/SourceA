# Today plan — AUTO-RUN 50 (LOCKED v1)

**Saved:** 2026-06-10T11:58:22Z · **Retrofit:** doc-datetime-law batch retrofit
> **SUPERSEDED 2026-06-10** — Founder rejected Cursor AUTO-RUN as P0. Use `FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md` + FREEZE factory-now. Historical reference only.

**Locked:** 2026-06-07 · **Authority:** ASF four-brain convergence  
**Parent:** `AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md` · `AUTOMATION-FAST-TRACK-100-LOCK.md`  
**Scope:** **Today only** — reach 50 headless autoloop turns with `broker=yes` streak

---

## Disk at lock

| Signal | Value |
|--------|--------|
| REGISTRY | 284/1000 (28.4%) |
| LIVE_PICK | sa-0131 |
| Loop chain | inject · validate · activate · sync **PASS** |
| eval_1b_gate_ok | true |
| dispatch_ready | false (founder unlock today if Hub offers) |
| broker=yes (historical log) | 14 — **target 50 tonight** |

---

## Today north star (one line)

> **Hub ▶ AUTO-RUN 50 — no Worker paste — morning proves 50 broker=yes.**

---

## Founder — tonight (Hub only, ~5 min)

| # | Action | Required |
|---|--------|----------|
| 1 | **Refresh** | yes |
| 2 | **▶ AUTO-RUN 50** (Goal 1 loop / `/api/run-goal1-auto-loop`) | **P0** |
| 3 | **Actions → ship FORGE** (Vercel) | yes |
| 4 | **Confirm `dispatch_ready=true`** (eval already green) | yes if Hub shows |

**Forbidden today:** Terminal · manual Worker paste per turn · healthy pack parallel rail · brain compare sessions · MANIFEST · path drift

---

## Executor — tonight (not founder)

| # | Action |
|---|--------|
| 1 | Confirm `goal1_auto_loop_v1.py --prepare-only --turns 1 --json` → deliver ok |
| 2 | If Hub button unavailable: `python3 scripts/goal1_auto_loop_v1.py --turns 50` |
| 3 | Tail `~/.sina/goal1-worker-batch-latest.log` for `AGENT DONE` + `broker=yes` |
| 4 | On `broker=no` + `sa_mismatch`: fix YAML `sa_focus` = INBOX `sa_id` only — no scope creep |
| 5 | Stop after 3 consecutive `broker=no` via `stop_goal1_loop_v1.py` — report blocker |

**Daemon:** `goal1_run_loop_v1.py` — **do not** build new autoloop file.

---

## Morning check — today success

```bash
grep -c 'broker=yes' ~/.sina/goal1-worker-batch-latest.log   # target ≥ 50 new tonight
python3 scripts/goal-progress-v1.py                          # done count moved
python3 scripts/brain_validate_goal1_v1.py --json            # activate still PASS
```

| Pass | Fail |
|------|------|
| broker=yes count **≥ 50** (or ≥36 new if 14 baseline) | broker=no streak ≥ 3 unattended |
| activate **PASS** | activate FAIL |
| goal-progress **done count up** | zero movement + broker=no |

---

## Today exit criteria (all required)

- [ ] **AUTO-RUN 50** started from Hub (one tap)
- [ ] Batch log shows **50** `broker=yes` turns (cumulative ≥ 50 acceptable)
- [ ] `brain_validate` **activate PASS** after batch
- [ ] FORGE ship attempted (Hub Action)
- [ ] `dispatch_ready=true` if founder confirm available
- [ ] **No** manual Worker paste turns (except single debug if autoloop hard-fails)

---

## If autoloop breaks (curriculum only)

Use **one** fast-track prompt — not 100 pastes:

| Issue | ft-id |
|-------|-------|
| deliver/prepare fail | ft-0001 |
| broker sa_mismatch | ft-0005 |
| validate before scale | ft-0003 |
| 3× broker fail stop | ft-0006 |
| inbox/queue drift | ft-0010 |

Pick: `bash scripts/plan-automation-fast-track-run.sh pick 1`

---

## Drop today (explicit)

MANIFEST · path drift · E2E full suite · FORGE probe · ac-1000 pack · dual queue rails · advisor archaeology

---

## After today (not today)

Loop B scheduler · Loop C SDK · s1 full drain · ft-0041+ — **only after** AUTO-RUN 50 gate passes.

---

*End TODAY_AUTORUN_50_PLAN_LOCKED_v1*
