# Sinaai — Execution Truth Layer (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
## Phase 2: intent + evidence → re-rank (not autonomous execution)

**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-02-014  
**Classification:** INTERNAL ONLY  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/SourceA/SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md`  
**Authority:** Subordinate to `SINA_OS_SSOT_LOCKED.md` v3 and `SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md`  
**Implementation:** `~/Desktop/SinaPromptOS/core/execution_tracker.py` + `ecosystem_feedback.py`  
**Locked:** 2026-06-02  
**Maintainer:** ASF

---

## 1. What this layer is (locked)

| Phase | Name | Status |
|-------|------|--------|
| **1** | Ecosystem Coordination OS | ✅ Built |
| **2** | **Execution Truth Layer v1** | ✅ **Locked + built** |
| **3** | Semi-autonomous execution (auto-finish, daily loop) | ❌ Not yet — after real logs |

**Problem solved:** Prompt OS understood **intent** (STATUS REPORT) but not **reality**.  
**Solution:** Every finished task must leave an **execution log** with evidence before the system trusts `done`.

```text
REPO_STATUS_REPORTS/     → intent (what agent claims)
REPO_EXECUTION_LOGS/     → evidence (what actually happened)
         ↓
execution_tracker + ecosystem_feedback
         ↓
EXECUTION_TRUTH.json + FEEDBACK_AGGREGATE.json
         ↓
ECOSYSTEM_STATUS.md + GLOBAL_PRIORITY.json (re-published)
```

**No architecture change.** Same parallel model: **N lanes per cycle** (default 3), **1 task per repo per cycle**.

---

## 2. Source A paths (canonical)

| Path | Role |
|------|------|
| `REPO_STATUS_REPORTS/<repo>.yaml` | Agent status (health, next, needs) |
| `REPO_EXECUTION_LOGS/<repo>/*.yaml` | Per-task evidence logs |
| `REPO_EXECUTION_LOG_TEMPLATE.yaml` | Paste template for Cursor §J |
| `REPO_STATUS_REPORT_TEMPLATE.yaml` | Paste template for Cursor §I |
| `EXECUTION_TRUTH.json` | Report vs log verification aggregate |
| `FEEDBACK_AGGREGATE.json` | Full re-rank snapshot |

Generated (do not hand-edit): `ECOSYSTEM_STATUS.md`, `GLOBAL_PRIORITY.json`, `GLOBAL_BLOCKERS.json`, `ECOSYSTEM_GRAPH.json`

---

## 3. Execution log schema (locked v1)

```yaml
repo: <project_id>                    # trustfield | sinaai_mono | virlux | noetfield | seven77 | sina_prompt_os
task: <string>                        # must match plan.json task finished
status: done | failed | blocked | in_progress
verify_passed: true | false          # REQUIRED true for trusted done
evidence:
  commit: <git hash>
  files_changed: [<paths>]
  diff_summary: <optional>
tests:
  status: passed | failed | skipped
  command: <command run>
  output_snippet: <output>
real_output: <what works now>
reporter: cursor | asf
```

**Rule T1:** `status: done` without `verify_passed: true` → **not trusted** for ranking.  
**Rule T2:** STATUS REPORT `completed[]` without matching verified log → **penalty** on re-rank.  
**Rule T3:** Product repos **do not** write Source A files — ASF submits via scripts.

---

## 4. Commands (locked)

```bash
cd ~/Desktop/SinaPromptOS && source .venv/bin/activate

# Submit evidence
./scripts/submit-execution-log.sh <project_id> log.yaml

# Verified close (log + plan.json + re-publish)
./scripts/mark-done-verified.sh <project_id> log.yaml

# Full truth + feedback cycle
./scripts/run-feedback-cycle.sh
# alias: python main.py --feedback-cycle

# Morning / evening (playbook)
./scripts/run-day.sh morning
./scripts/run-day.sh evening
```

**Settings** (`config/settings.json`):

| Key | Default | Meaning |
|-----|---------|---------|
| `execution_validation_enabled` | `true` | Use logs in ranking |
| `require_execution_log_for_mark_done` | `false` | If `true`, `mark-done.sh` requires `--log` |
| `auto_sync_plan` | `false` | M5 — not active |

---

## 5. Cursor agent contract (locked)

| Step | Notice section | Mode |
|------|----------------|------|
| Session start | A + repo block | AWARENESS — YAML only |
| After awareness | I | STATUS REPORT — YAML only |
| After IMPLEMENT + VERIFY | J | EXECUTION LOG — YAML only |
| Execute task | H | IMPLEMENT — one task |

Doc: `CURSOR_REPO_AGENT_NOTICE_PROMPTS_v1.md` §I, §J

---

## 6. Parallel loop (locked — full day)

```text
Sunday:   ASF adjusts projects.json + all os/plan.json queues
Daily:    publish → parallel prompts (≤3) → Cursor per lane → VERIFY
          → EXECUTION LOG → submit → feedback/truth cycle → evening pack
```

**ASF is not choosing “one company”** — system emits up to **3 prompts** per cycle from **global parallel ranking**.

---

## 7. What is NOT in v1 (honest)

- Auto-read git diff / run tests inside Prompt OS  
- Auto `mark-done` without ASF submit  
- Cursor API autonomous execute (M8)  
- Full daily loop with only “start” (Phase 3)

**Next build after real logs:** M5 `auto_sync_plan` with `--verified` + Auto-Finish Engine (Phase 2b).

---

## 8. MVP alignment

| MVP | Item | Status |
|-----|------|--------|
| M1 | Multi-project pointers | ✅ |
| M2 | Dashboard / UI | Partial |
| **M2T** | **Execution Truth Layer v1** | ✅ **This doc** |
| M3 | `mark-done.sh` | ✅ |
| M3v | `mark-done-verified.sh` | ✅ |
| FB | Feedback loop + reports | ✅ |
| M4 | Morning notification | Next |
| M5 | Safe auto-sync | Next |
| M6 | launchd morning | Next |

---

## Document control

| Version | Date | seq_id | Change |
|---------|------|--------|--------|
| 1.0 | 2026-06-02 | SA-2026-06-02-014 | Lock Execution Truth Layer v1 + paths + schema + commands |
