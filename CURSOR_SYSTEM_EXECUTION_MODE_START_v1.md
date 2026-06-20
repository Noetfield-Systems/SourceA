# START SYSTEM EXECUTION MODE — Master Prompt (v1)
## Paste into correct workspace ONLY — see table below

**Date:** 2026-06-02  
**Status:** ACTIVE — operational, not new architecture  
**Handoff:** `SINAAI_ECOSYSTEM_FINAL_STATE_AND_NEXT_PLAN_LOCKED_v1.md`

---

## WHO builds WHAT (read first)

| Role | Where | Does | Does NOT |
|------|-------|------|----------|
| **SinaPromptOS** | `~/Desktop/SinaPromptOS/` | orchestrator, publish, rank, write `outputs/last_prompt_*.txt` | Build TrustField/VIRLUX/777 product code |
| **Repo Cursor agent** | Each repo workspace | ONE task from `outputs/last_prompt_<repo>.txt` | Orchestrate other repos, edit Source A |
| **SinaaiMonoRepo agent** | `~/Desktop/SinaaiMonoRepo/` | **Only** Mono tasks (`last_prompt_sinaai_mono.txt`) | TrustField, VIRLUX, 777, full ecosystem |
| **This chat (wrong root)** | Empty `SinaaiDataBase` shell | Avoid for delivery | — |

**Answer:** Do **not** use MonoRepo agent to build everything. Use **6 workspace agents** + **terminal SinaPromptOS** for brain.

---

## A) TERMINAL — run brain (ASF or any agent in SinaPromptOS folder)

```bash
cd ~/Desktop/SinaPromptOS && source .venv/bin/activate
./scripts/run-full-cycle.sh
python main.py
ls -la outputs/last_prompt_*.txt
```

No code changes in SinaPromptOS unless `last_prompt_sina_prompt_os.txt` is your active lane.

---

## B) PER-REPO — paste AFTER awareness (§A+repo from CURSOR_REPO_AGENT_NOTICE_PROMPTS_v1.md)

Then paste **only** the matching block from:
`~/Desktop/SinaPromptOS/outputs/last_prompt_<project_id>.txt`

| Repo | Workspace | Prompt file |
|------|-----------|-------------|
| TrustField | `TrustField Technologies/` | `last_prompt_trustfield.txt` |
| VIRLUX | `VIRLUX/` | `last_prompt_virlux.txt` |
| MonoRepo | `SinaaiMonoRepo/` | `last_prompt_sinaai_mono.txt` |
| Noetfield | `.../noetfield/` | `last_prompt_noetfield.txt` |
| 777 | `The 777 Foundation/` | `last_prompt_seven77.txt` |
| Prompt OS | `SinaPromptOS/` | `last_prompt_sina_prompt_os.txt` |

---

## C) UNIVERSAL IMPLEMENT PROMPT (every repo — after B)

```text
START SYSTEM EXECUTION MODE — IMPLEMENT (one task only)

You are in ONE repo lane of a parallel multi-project system. No redesign. No new architecture.

READ (in order):
1. /Users/sinakazemnezhad/Desktop/SourceA/SINA_OS_SSOT_LOCKED.md
2. /Users/sinakazemnezhad/Desktop/SourceA/SINAAI_ECOSYSTEM_FINAL_STATE_AND_NEXT_PLAN_LOCKED_v1.md
3. /Users/sinakazemnezhad/Desktop/SourceA/ECOSYSTEM_STATUS.md
4. /Users/sinakazemnezhad/Desktop/SourceA/GLOBAL_PRIORITY.json
5. /Users/sinakazemnezhad/Desktop/SourceA/SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md
6. /Users/sinakazemnezhad/Desktop/SourceA/SINAAI_PHASE2_AI_CONTROLLED_EXECUTION_LOCKED_v1.md
7. This repo: os/strategy.md, os/plan.json, os/task_definition.json

RULES:
- Execute ONLY the SINGLE TASK in the Prompt OS prompt below (or next_tasks[0] if aligned).
- TrustField: DELIVERY freeze — ops/gates/E2E only unless ASF lifted freeze.
- Noetfield: docs/spec only unless ASF activated code.
- Do NOT edit Desktop/SourceA/ from this repo.
- Do NOT touch other repos.

VERIFY:
- Run command named in task, repo VERIFY.md, or reports/.
- Paste full VERIFY output.

AFTER VERIFY — reply with EXECUTION LOG YAML (§J in CURSOR_REPO_AGENT_NOTICE_PROMPTS_v1.md).
ASF will run: submit-execution-log.sh + mark-done-verified.sh

OUTPUT:
1) Changes made
2) VERIFY output
3) plan.json diff
4) EXECUTION LOG YAML block
```

Then paste contents of `last_prompt_<this_repo>.txt` below the line:
`--- PROMPT OS TASK ---`

---

## D) First cycle results (2026-06-02 — generated)

**Full cycle:** feedback + truth + phase2 ✅  
**Orchestrator:** 3 parallel prompts (settings max_tasks_per_cycle=3) ✅  
**All 6 prompt files:** generated in `SinaPromptOS/outputs/`

**Ranked order:**
1. trustfield — postgres validation / production readiness (score 118)
2. virlux — staging smoke test (79.6)
3. sinaai_mono — runtime health check (79)
4. seven77 — homepage content pass (66.5)
5. noetfield — spec section 3 review (45)
6. sina_prompt_os — daily snapshot (25)

**Lanes this cycle (top 3):** TrustField, VIRLUX, MonoRepo  
**Lanes 4–6:** use prompt files + run second wave same day if ASF has capacity

---

## E) After all lanes today

```bash
cd ~/Desktop/SinaPromptOS
./scripts/run-full-cycle.sh
./scripts/run-day.sh evening
```
