# Sinaai — Phase 2: AI-Controlled Execution OS (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
## Human supervisor · system = junior execution CTO (guarded)

**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-02-015  
**Classification:** INTERNAL ONLY  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/SourceA/SINAAI_PHASE2_AI_CONTROLLED_EXECUTION_LOCKED_v1.md`  
**Authority:** Subordinate to `SINA_OS_SSOT_LOCKED.md` v3, `SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md`  
**Implementation:** `~/Desktop/SinaPromptOS/core/ai_control/`  
**Locked:** 2026-06-02  
**Maintainer:** ASF

---

## 0. Phase 1 — CLOSED (do not extend)

| Layer | Status |
|-------|--------|
| Sina OS law | ✅ |
| Parallel Prompt OS + plan.json queues | ✅ |
| Ecosystem publish + feedback | ✅ |
| Execution Truth (reports + logs) | ✅ |

**Phase 1 name (locked):** *Deterministic multi-repo Execution OS* — not autonomous AI.

**Stop:** new architecture docs, new prompt packs, new SSOT merges.

---

## 1. Phase 2 goal (locked)

Move from:

```text
ASF = brain · system = calculator
```

To:

```text
system = guarded junior CTO · ASF = supervisor (approve / reject)
```

**Not in Phase 2 v1:** unsupervised ship, auto-edit Source A, auto registry, full Cursor API autonomy.

---

## 2. Three modules (build order)

| # | Module | Code | Output |
|---|--------|------|--------|
| **P2-M1** | Task Completion Intelligence | `task_evaluator.py` | `DONE` / `NOT_DONE` / `PARTIAL` + confidence + risk |
| **P2-M2** | Auto-Planner (guarded) | `auto_planner.py` | next micro-step or `NEEDS_ASF` |
| **P2-M3** | Semantic Progress | `semantic_progress.py` | meaning-based progress 0–100 per repo |

**Bridge:** `ai_control/orchestrator_bridge.py` → writes `SourceA/PHASE2_EVALUATIONS.json`, `SEMANTIC_PROGRESS.json`

---

## 3. Data flow (locked)

```text
SINA OS (law)
     ↓
Execution Truth (logs + reports)     ← Phase 1
     ↓
AI Control Core (Phase 2)          ← NEW
  ├─ task_definition.json (per repo os/)
  ├─ Task Evaluator
  ├─ Auto-Planner (confidence gate)
  └─ Semantic Progress
     ↓
Prompt OS (prompts, ≤3 parallel)
     ↓
Cursor → VERIFY → EXECUTION LOG
     ↓
(loop)
```

---

## 4. Per-repo `os/task_definition.json` (locked schema)

```json
{
  "version": 1,
  "active_task": "<matches plan.json next_tasks[0]>",
  "definitions": {
    "<task name>": {
      "acceptance_criteria": ["string", "..."],
      "verify_commands": ["npm test", "curl -f .../health"]
    }
  }
}
```

If missing → evaluator uses **rule-only** mode (execution log + plan.json).

---

## 5. Task Evaluator contract (P2-M1)

**Input:** `project_id`, `task`, execution log, optional `task_definition.json`, repo state  
**Output:**

```yaml
verdict: DONE | NOT_DONE | PARTIAL
confidence: 0.0-1.0
risk: LOW | MEDIUM | HIGH
next_micro_step: <string or empty>
reasons: [<string>]
mode: rules | rules+llm
```

**Rules (always):**

- `status: done` + `verify_passed: false` → `NOT_DONE`
- `tests.status: failed` → `NOT_DONE`
- `verify_passed: true` + tests passed + commit present → `DONE` (high confidence)
- Report `completed[]` without matching log → lowers confidence

**LLM (optional):** `OPENROUTER_API_KEY` + `phase2.task_evaluator_llm: true`

---

## 6. Auto-Planner contract (P2-M2)

```text
if evaluator.confidence >= phase2.auto_planner_threshold:
    propose next_tasks[0] from plan.json (or split micro-step)
else:
    verdict = NEEDS_ASF
```

**Default:** `auto_plan_apply: false` — proposals only in JSON; ASF applies via `mark-done-verified.sh`.

---

## 7. Semantic Progress (P2-M3)

Combines (no embeddings in v1):

- plan.json done vs queue depth  
- STATUS REPORT `progress`  
- execution log success rate  
- evaluator verdict history  

Writes: `SourceA/SEMANTIC_PROGRESS.json`

**v2 (later):** embeddings per repo — not Phase 2 v1.

---

## 8. Commands

```bash
cd ~/Desktop/SinaPromptOS && source .venv/bin/activate

# Evaluate one repo after execution log submitted
./scripts/run-phase2-eval.sh trustfield

# All repos + refresh semantic progress
python main.py --phase2-cycle

# Full day still:
./scripts/run-day.sh morning
```

**Settings:** `config/settings.json` → `"phase2": { "enabled": true, ... }`

---

## 9. Relation to M4–M9

| MVP | When |
|-----|------|
| M4 notification | After P2-M1 stable with real logs |
| M5 auto_sync | After evaluator `DONE` + `--verified` |
| M6 launchd | After M4 |
| M8 Cursor API | Phase 2b |

---

## 10. Handoff

Full status + open issues + daily commands:  
`SINAAI_ECOSYSTEM_FINAL_STATE_AND_NEXT_PLAN_LOCKED_v1.md`

---

## Document control

| Version | Date | seq_id | Change |
|---------|------|--------|--------|
| 1.0 | 2026-06-02 | SA-2026-06-02-015 | Lock Phase 2 three modules + Phase 1 closed |
| 1.1 | 2026-06-02 | SA-2026-06-02-015 | Handoff pointer §10 |
