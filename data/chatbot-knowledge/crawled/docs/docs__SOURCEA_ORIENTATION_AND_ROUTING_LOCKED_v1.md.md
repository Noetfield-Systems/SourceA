---
lane: core
updated: 2026-06-30T12:42:32Z
source_path: docs/SOURCEA_ORIENTATION_AND_ROUTING_LOCKED_v1.md
public: true
---

# SourceA — Orientation & Routing LOCKED v1.1

**Version:** 1.1.0 LOCKED · **Saved:** 2026-06-16T09:45:00Z  
**Machine SSOT:** `data/sourcea_orient_routing_v1.json` v1.1  
**Unified bundle:** `data/sourcea_agentic_unified_bundle_v1.json`  
**Library:** `scripts/orient_routing_v1.py`  
**Command:** `python3 scripts/agent_orient_v1.py --json`  
**Report:** `~/.sina/orient-routing-report-v1.json`  
**Law:** `AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md`  
**Wil parity:** `~/Desktop/YA5/.cursor/governance/ORIENTATION_ROUTING.md` (read-only)

> **Session start = session gate only.** Orientation · hospital · maze = **founder word** via router.

---

## Daily routing ladder

| Order | Route | Handler | Skip |
|-------|-------|---------|------|
| 1 | Session gate | `agent_session_gate_run_v1.py` | never |
| 2 | Live surfaces | `agent-live-surfaces-v1.json` | never |
| 3 | RUN INBOX | `healthy_prompt_turn_v1.py` | never |
| 4 | Node graph pulse | `pipeline_node_graph_runner_v1.py` | `pipeline_node_graph_runner_v1` | optional |
| 5 | Orient cascade | `agent_orient_v1.py` | `orient_routing_v1` | optional |
| 6 | Hub glance | `:13020` Next steps | `hub_projection_v1` | `hub_down` |

---

## Founder word routing

| Word | Tier | Router | Receipt | Authority |
|------|------|--------|---------|-----------|
| **orientation** | 1 Atlas | `orientation_pipeline_v1` | `agent_three_pipelines_router_v1.py orientation` | `agent-orientation-receipt-v1.json` | false |
| **hospital** | 2 Clinic | `hospital_pipeline_v1` | `… hospital` | `agent-hospital-receipt-v1.json` | false |
| **maze** | 3 Quarantine | `maze_pipeline_v1` | `… maze` | `agent-maze-receipt-v1.json` | false |

**Never** auto-run orientation/hospital/maze on session start. **`orient_routing_v1`** runs on graph tier `T_lat_orient` or via `agent_orient_v1.py`.

---

## Pipeline ↔ node map (v1.1)

| Pipeline | Node id | Graph tier | Founder word? |
|----------|---------|------------|---------------|
| Orientation Atlas | `orientation_pipeline_v1` | LAT logical | yes · **orientation** |
| Hospital Clinic | `hospital_pipeline_v1` | LAT logical | yes · **hospital** |
| Maze Quarantine | `maze_pipeline_v1` | LAT logical | yes · **maze** |
| Orient cascade | `orient_routing_v1` | **T_lat_orient** runner | no · anytime |

**Graph v1.3:** 12 runner nodes · 5 tiers (T0–T3 + T_lat) · founder-word pipelines feed orient cascade on receipt FAIL.

---

## Role routing

| Role | Daily | Build? | Next tap |
|------|-------|--------|----------|
| **Brain** | Route · pick · handoff | No | Worker RUN INBOX |
| **Worker** | RUN INBOX · one sa-* | Yes | RUN INBOX |
| **Governance** | Audit · advise | No | CART poison-track if open |
| **any** | Session gate · quote disk | scope-dependent | Say worker or brain |

---

## Orient read chain (10 steps)

1. `brain-os/law/entry/START_HERE_LOCKED_v1.md`  
2. **`docs/SOURCEA_ORIENTATION_AND_ROUTING_LOCKED_v1.md`** (this doc)  
3. `docs/SOURCEA_FOUNDATIONAL_AGENTIC_SYSTEMS_INDEX_LOCKED_v1.md`  
4. `docs/SOURCEA_NODE_MESH_SYNESTM_BUILD_PLAN_LOCKED_v1.md`  
5. `AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md`  
6. `SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md`  
7. `data/sourcea_pipeline_node_graph_v1.json`  
8. `data/sourcea_directory_node_map_v1.json`  
9. `~/.sina/agent-live-surfaces-v1.json`  
10. `~/.sina/agent_session_gate_receipt_v1.json`  

---

## Receipt cascade (Wave 1 — node ids on FAIL)

When a verify report FAILs, orient maps failure → **node id**:

| Source | Example | Node id |
|--------|---------|---------|
| session_gate | `crawl_mirror` step | `crawl_mirror_session` |
| session_gate | SASCIP step | `sascip_live_wire` |
| graph_run | tier node FAIL | node id from graph |
| orientation | receipt ok=false | `orientation_pipeline_v1` |
| hospital | receipt ok=false | `hospital_pipeline_v1` |
| maze | receipt ok=false | `maze_pipeline_v1` |
| critical_bugs | critical_count > 0 | `validate_w10_vocab` |
| live_surfaces | missing factory line | `disk_live_wire` |

**Orient output:**

```text
── Receipt cascade ──
  FAIL crawl_mirror_session ← session_gate.sourcea_crawl_mirror_pipeline
  nodes: crawl_mirror_session
```

**JSON:** `receipt_cascade` in `agent_orient_v1.py --json`  
**Brief line:** `cascade_line` in report

Mapping SSOT: `data/sourcea_orient_routing_v1.json` → `session_gate_step_nodes` · `validator_check_nodes`

---

## Session gate step → node map

| Gate step | Node id |
|-----------|---------|
| anti_staleness_auto_wire | disk_live_wire |
| stranger_agent_safety_live_wire | sascip_live_wire |
| governance_zero_drift_live_wire | governance_zero_drift |
| sourcea_crawl_mirror_pipeline | crawl_mirror_session |
| agentic_pipeline_v2 | agentic_layer_fast |

Full map in machine SSOT.

---

## Commands

```bash
cd [REDACTED]
python3 scripts/agent_orient_v1.py --role worker --json
bash scripts/validate-orient-routing-v1.sh
python3 scripts/agent_three_pipelines_router_v1.py orientation --role worker --json
python3 scripts/pipeline_node_graph_runner_v1.py --tier T_lat_orient --json
python3 scripts/agent_session_gate_run_v1.py --role worker --json
```

---

## Orient bundle fields

| Field | Content |
|-------|---------|
| `factory_now_line` | Live queue truth |
| `receipt_cascade` | FAIL rows with node_id |
| `cascade_line` | One-line cascade brief |
| `role_routing` | Role-specific next tap |
| `node_mesh_brief` | Active nodes · tiers · edges · synestm |
| `pipeline_nodes_brief` | Four pipelines · receipt ok per node |
| `hints` | Actionable fixes with node prefix |

---

## Agent rules

1. **Session start** — gate only · not orientation pipeline  
2. **Founder says orientation** — router → Tier 1 Atlas · read-only  
3. **FAIL in cascade** — cite node id · run fix command · not chat-only  
4. **Brain** — orient for routing · Worker for INBOX  
5. **Validate** — `validate-orient-routing-v1.sh` before claiming orient upgrade DONE  

---

## Related

| Doc | Role |
|-----|------|
| `docs/SOURCEA_NODE_MESH_SYNESTM_BUILD_PLAN_LOCKED_v1.md` | Parallel node mesh |
| `data/sourcea_orient_routing_v1.json` | Machine routing SSOT |
| `.cursor/skills/skill-node-architect-agentic-system/SKILL.md` | Node architect |
| `~/.sina/cart-tasks/tasks/orient-routing-cart-v1.json` | Checklist |

---

**END LOCKED v1.1.0 · SOURCEA_ORIENTATION_AND_ROUTING_LOCKED_v1.md**
