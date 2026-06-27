# SourceA Forge Terminal v3 Swarm Blackboard (LOCKED v1)

**Saved:** 2026-06-25T02:30:00Z  
**Version:** 1.0 — LOCKED  
**App version:** 3.1.0+ · port **13029**  
**Parent:** `SOURCEA_FORGE_TERMINAL_L2_SELF_IMPROVE_LOCKED_v1.md` · `SOURCEA_FORGE_TERMINAL_LIVING_DESKTOP_E2E_LOCKED_v1.md`

---

## One law

> **v3 parallel swarm uses a shared blackboard for planner/critic coordination, Mac founder sessions default `dry_run=true`, and real LLM swarm execution routes through cloud dispatch only.**

---

## Blackboard schema: `forge-swarm-blackboard-v1`

Path: `~/.sina/forge-swarm-blackboard-v1.json`

| Field | Type | Rule |
|-------|------|------|
| `goal` | string | Primary founder goal |
| `goals` | string[] | Goal stack (replan appends) |
| `tasks` | object[] | `{ type, text, priority }` merged from parallel planners |
| `artifacts` | object[] | Builder step summaries per task |
| `repo_state` | object | Code intel / file list snapshot |
| `repo_graph` | object | `{ nodes[], edges[] }` dependency graph |
| `planner_votes` | object[] | Per-planner task proposals |
| `critic_verdicts` | object[] | Parallel critic outputs |
| `logs` | string[] | Round + replan audit trail |
| `round` | int | Current replan round (max 2) |

Helpers: `scripts/forge_swarm_blackboard_v1.py` — `merge_plans`, `aggregate_critic_verdicts`, `build_repo_graph_light`.

---

## Swarm receipt schema: `forge-agent-kernel-swarm-v3`

Path: `~/.sina/forge-agent-kernel-swarm-v3.json`

Required keys: `schema`, `swarm_id`, `goal`, `state`, `parallel`, `blackboard`, `task_runs`, `critic_aggregate`, `verify_harness`, `at`.

Optional v3.1+: `repair_runs`, `optimizer_notes`, `replan_rounds`, `repo_graph`, `parallel_build`.

---

## Agent roles

| Role | Count | Function |
|------|-------|----------|
| Planner | 3 | Parallel task decomposition → `merge_plans` |
| Builder | 1–5 | Patch/apply per task |
| Critic | 3 | Majority vote → `aggregate_critic_verdicts` |
| Repair | on-demand | Targeted fix hints before replan |
| Optimizer | 1 | ROI model tier + skip redundant tasks |

Kernel: `scripts/forge_agent_kernel_v3_swarm.py` — `run_swarm_loop`.

---

## API

```json
POST /api/forge-terminal/v1
{ "action": "agent_swarm_run", "goal": "…", "dry_run": true, "parallel": true }

POST /api/forge-terminal/v1
{ "action": "advisor_run", "goal": "…", "swarm": true, "cloud": false }
```

Cloud dispatch: `scripts/forge_swarm_cloud_dispatch_v1.py` when `cloud: true` or live execution armed.

---

## Mac control plane

- Founder session: `dry_run=true` default — stub swarm, no local LLM marathon.
- Real swarm body: Railway/FBE via cloud dispatch receipt `~/.sina/forge-swarm-cloud-dispatch-latest-v1.json`.
- No Redis queue on Mac. No TypeScript monorepo on Mac.
- Light E2E only (INCIDENT-039).

---

## Proof

```bash
python3 scripts/forge_terminal_living_ui_e2e_verify_v1.py
```

Receipt must include `swarm blackboard`, `parallel swarm`, `agent_swarm_run api` checks.
