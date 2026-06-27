# SourceA Forge Terminal v4 Civilization (LOCKED v1)

**Saved:** 2026-06-25T03:00:00Z  
**Version:** 1.0 — LOCKED (alpha)  
**App version:** 4.0.0-alpha · port **13029**  
**Parent:** `SOURCEA_FORGE_TERMINAL_V3_SWARM_BLACKBOARD_LOCKED_v1.md`

---

## One law

> **v4 civilization accumulates persistent memory, agent identity, and task economy lite — all auditable logged; cloud executes live swarm body; Mac remains control plane.**

---

## Constitution (immutable rules)

1. No unlimited cost execution (`max_cost_per_task` = 10.0)
2. All actions must be traceable (`forge-civilization-memory-v1.json` event log)
3. No destructive system operations without approval
4. Every deployment must pass verification (critic aggregate + harness)
5. Memory must be auditable (disk receipts + optional labs-sandbox Supabase)

---

## Civilization memory

Path: `~/.sina/forge-civilization-memory-v1.json`

| Field | Rule |
|-------|------|
| `event_log` | Append after every swarm/advisor/L2/L3 run |
| `task_history` | goal → verdict → cost |
| `failure_patterns` | Critic issues from failed runs |
| `graph_snapshot` | Latest repo graph |

Module: `scripts/forge_civilization_memory_v1.py`

---

## Agent registry

Path: `~/.sina/forge-agent-registry-v1.json`

- Seed: 3 planners, 5 builders, 3 critics, 1 repair, 1 optimizer
- Reputation: +0.1 success, -0.15 failure
- Evolution: cost_efficiency boost when reputation > 0.8

Module: `scripts/forge_agent_registry_v1.py`

---

## Task economy lite

- `estimate_task_value` / `estimate_task_cost` on blackboard
- `select_agent_for_task` — lowest cost × highest reputation bid
- No v5 credits, tax, or digital-nation layer

Module: `scripts/forge_swarm_blackboard_v1.py`

---

## Civilization loop

Path: `~/.sina/forge-civilization-tick-latest-v1.json`

- Backlog: L3 queue + memory failures
- Tick wired in `scripts/cloud_auto_runtime_v1.py`
- LangGraph bridge: `run_civilization_gate()` in factory-runtime-spike

Module: `scripts/forge_civilization_loop_v1.py`

---

## Mac vs cloud

| Action | Mac | Cloud |
|--------|-----|-------|
| Civilization memory write | Local JSON | Optional Supabase labs-sandbox |
| Live swarm LLM | No (dry_run stub) | Yes via cloud dispatch |
| Civilization tick | dry_run stub | Live when auto-proceed armed |

---

## Proof

```bash
python3 scripts/forge_terminal_living_ui_e2e_verify_v1.py
```

Target: **60+** checks · version **4.0.0-alpha**
