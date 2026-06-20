# Prompt OS Core — MVP Build Order (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
## Nine deliverables — implementation under SinaPromptOS

**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-02-013  
**Authority:** `SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md`  
**Root:** `~/Desktop/SinaPromptOS/`  
**Locked:** 2026-06-02

---

## 1. Final folder structure (locked)

```text
SinaPromptOS/                    # Prompt OS Core (= prompt-os-core)
├── main.py                      # one cycle
├── daemon.py                    # → main.py --daemon
├── config/
│   ├── projects.json            # registry + global_priority
│   └── settings.json            # control panel
├── core/
│   ├── orchestrator.py          # central router
│   ├── state_loader.py
│   ├── priority_engine.py
│   ├── task_generator.py
│   ├── prompt_compiler.py
│   ├── validator_gate.py
│   └── sync_engine.py
├── runtime/
│   ├── cursor_executor.py
│   └── event_bus.py
├── daemon/
│   ├── main_daemon.py
│   ├── scheduler.py
│   └── watchdog.py
├── dashboard/
│   ├── backend/server.py
│   └── frontend/
├── projects/                    # pointers — repos stay on Desktop
│   ├── trustfield/project.json
│   ├── noetfield/project.json
│   ├── virelux/project.json
│   ├── seven77/project.json
│   ├── sinaai_mono/project.json
│   └── sina_prompt_os/project.json
├── global/                      # generated each cycle
│   ├── GLOBAL_STATE.json
│   ├── PRIORITY_MAP.json
│   └── SINA_OS_RULES.md
├── data/
│   └── memory.db                # shared memory (SQLite)
├── outputs/                     # last_prompt_*.txt
├── logs/
└── scripts/
    ├── run-day.sh
    ├── run-ui.sh                # Streamlit :8765
    └── run-dashboard.sh         # FastAPI :8766
```

**External repos (unchanged):** `TrustField Technologies`, `VIRLUX`, `SinaaiMonoRepo`, etc.

---

## 2. Central orchestrator architecture

```text
run_cycle():
  state = state_loader.load_global_state()
  priorities = priority_engine.compute_priority(state)
  priority_engine.write_priority_map(priorities)
  tasks = task_generator.generate_tasks(priorities)   # 1 per repo, cap N
  for task in tasks:
    if not validator_gate.validate_task(task): continue
    prompt = prompt_compiler.compile_prompt(task)
    cursor_executor.send_to_cursor(prompt, project_id)
    sync_engine.sync_state(task, verify_passed=False)
  persist execution_log.json + event_bus
```

**Single entry:** `python main.py` or `daemon.py`.

---

## 3. Shared memory architecture

| Store | Path | Holds |
|-------|------|-------|
| **memory.db** | `data/memory.db` | snapshots, suggestions, notes |
| **GLOBAL_STATE.json** | `global/` | last full multi-repo snapshot |
| **PRIORITY_MAP.json** | `global/` | ranked cross-repo view |
| **Per-repo** | `{repo}/os/plan.json` | next_tasks, done, blocked (source of truth for queue) |

**Rule:** `plan.json` in each repo wins for queue; DB wins for history/analytics.

---

## 4. Global priority engine

- Input: all projects from `config/projects.json`  
- Signals: `global_priority` order, weight, blocked count, `next_tasks[0]`, chat activity  
- Output: `PRIORITY_MAP.json` + ranked list for dashboard  
- Code: `core/priority_engine.py` + `core/router.rank_projects`

---

## 5. Per-project OS contract (locked)

Each external repo MUST have:

```text
{repo}/os/
  strategy.md      # execution slice — subordinate to Sina OS + delivery SOT
  plan.json        # queue (ASF maintains on think day)
  prompt-engine.md # optional
  validator.md     # optional
```

**Prompt OS Core reads only** — never moves `os/` into `projects/` folder (pointers only).

---

## 6. Dashboard architecture

| UI | Port | Tech | Role |
|----|------|------|------|
| **Control** | 8766 | FastAPI + static `/ui/` | Priority map, state, logs |
| **Operator** | 8765 | Streamlit | “Give me best prompt”, copy |

**Phase 2:** WebSocket push (not MVP).

---

## 7. Daemon loop

```text
while true:
  watchdog.safe_run(run_cycle)
  sleep(settings.cycle_interval_seconds)  # default 60
```

Start: `python daemon.py` or `python main.py --daemon`  
**Not** installed as systemd until Phase 2.

---

## 8. Migration path (TrustField → multi-project)

| Step | Status |
|------|--------|
| TrustField `os/` template | ✅ Done |
| `config/projects.json` six entries | ✅ Done |
| Router reads external paths | ✅ Done |
| `projects/trustfield/project.json` pointer | ✅ This build order |
| TrustField adapter in sourceB | ✅ Keep |
| Mono `os/`, VIRLUX `os/`, etc. | ✅ Seeded |

**No code move** from TrustField repo.

---

## 9. MVP build order (execute in sequence)

| Phase | Build | Unlocks | Status |
|-------|-------|---------|--------|
| **M0** | Decision + docs §3 hierarchy | No more doc drift | ✅ Locked |
| **M1** | `projects/*.json` pointers + `memory.db` alias | Clear multi-project layout | ✅ Done |
| **M2** | Dashboard shows top 3 + copy buttons | Mon–Fri dashboard flow | Partial |
| **M2T** | Execution Truth Layer v1 (`execution_tracker.py`) | Evidence-based re-rank | ✅ Locked — `SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md` |
| **FB** | Feedback loop + `REPO_STATUS_REPORTS/` | Intent → re-rank | ✅ Done |
| **M3** | `mark-done.sh` + `mark-done-verified.sh` | Memory + evidence | ✅ Done |
| **P2** | AI Control: evaluator + auto-planner + semantic | Guarded intelligence | ✅ v1 — `SINAAI_PHASE2_AI_CONTROLLED_EXECUTION_LOCKED_v1.md` |
| **M4** | Morning Telegram or macOS notification | L1 “no open UI” | Next |
| **M5** | `auto_sync_plan` only with `--verified` flag | L2 safe sync | Next |
| **M6** | launchd plist for morning only (not 24/7 daemon) | Reliable start | Next |
| **M7** | WebSocket dashboard | Live push | Phase 2 |
| **M8** | Cursor SDK / Cloud Agent hook | True execute step | Phase 2 |
| **M9** | Docker + systemd + Redis | “Deployable” pack | Phase 2 |

**Do not start M7–M9 until M3–M4 stable.**

---

## Document control

| Version | Date | seq_id | Change |
|---------|------|--------|--------|
| 1.0 | 2026-06-02 | SA-2026-06-02-013 | Nine deliverables locked |
| 1.1 | 2026-06-02 | SA-2026-06-02-013 | M2T + FB + M3 status; truth layer |
