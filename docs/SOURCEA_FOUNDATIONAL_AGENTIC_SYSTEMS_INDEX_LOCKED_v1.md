# SourceA — Foundational Agentic Systems — Index LOCKED v1.2

**Version:** 1.2.0 LOCKED · **Saved:** 2026-06-16T10:00:00Z  
**Path:** `~/Desktop/SourceA/docs/SOURCEA_FOUNDATIONAL_AGENTIC_SYSTEMS_INDEX_LOCKED_v1.md`  
**Purpose:** Single human index — skills · SSOT · pipelines · nodes · carts

**Machine unified bundle:** `data/sourcea_agentic_unified_bundle_v1.json` — version pins for all agentic SSOT

---

## One tap — daily

| Step | Command / action |
|------|------------------|
| Session start | `python3 scripts/agent_session_gate_run_v1.py --role worker --json` |
| Orient + cascade | `python3 scripts/agent_orient_v1.py --role worker --json` |
| Build | Worker chat **RUN INBOX** |
| Validate stack | `bash scripts/validate-agentic-unified-bundle-v1.sh` |

---

## Skills (load order)

| Order | Skill | Path |
|-------|-------|------|
| **0** | **Foundational agentic systems** | `.cursor/skills/skill-foundational-agentic-systems/SKILL.md` v2.0 |
| 1 | **Node architect SYNESTM** | `.cursor/skills/skill-node-architect-agentic-system/SKILL.md` v2.1 + NODE_* refs |
| 2 | Architecting pipelines PRO | `.cursor/skills/skill-architecting-pipelines-pro/SKILL.md` |
| 3 | Conscious recovery | `.cursor/skills/sina-conscious-recovery/SKILL.md` |
| 4 | SourceA Brain | `.cursor/skills/sina-sourcea-brain/SKILL.md` |
| 5 | SourceA Worker | `.cursor/skills/sina-sourcea-worker/SKILL.md` |
| 6 | Anti-staleness machine | `.cursor/skills/anti-staleness-machine/SKILL.md` |

**Founder mirrors:** `~/.cursor/skills/sina-foundational-agentic-systems/` · `sina-node-architect-agentic-system/` · `sina-architecting-pipelines-pro/`

---

## Locked SSOT (unified v1.2)

| Topic | Human | Machine | Version |
|-------|-------|---------|---------|
| **Unified bundle** | this index | `data/sourcea_agentic_unified_bundle_v1.json` | 1.0.0 |
| Orient routing | `docs/SOURCEA_ORIENTATION_AND_ROUTING_LOCKED_v1.md` | `data/sourcea_orient_routing_v1.json` | 1.1.0 |
| Node graph | build plan + mesh ref | `data/sourcea_pipeline_node_graph_v1.json` | **1.3.0** |
| Mesh catalog | synestm build plan | `data/sourcea_node_mesh_catalog_v1.json` | 1.1.0 |
| Directory map | `docs/SOURCEA_DIRECTORY_NODE_MAP_LOCKED_v1.md` | `data/sourcea_directory_node_map_v1.json` | 1.1.0 |
| Three pipelines | `AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md` | router + lib | v2 body |
| Entry | `entry/START_HERE_LOCKED_v1.md` | — | — |
| Layer stack | `SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md` | — | v2 |
| SASCIP defense | `docs/SOURCEA_STRANGER_AGENT_DEFENSE_IN_DEPTH_FOUNDER_GUIDE_LOCKED_v1.md` | SASCIP v1.2 | — |
| Synestm build | `docs/SOURCEA_NODE_MESH_SYNESTM_BUILD_PLAN_LOCKED_v1.md` | N01–N20 | — |
| Node charter | `docs/SOURCEA_NODE_ARCHITECT_AGENTIC_AUTONOMOUS_SYSTEM_LOCKED_v1.md` | — | — |
| Terminology 2026 | `docs/SOURCEA_TERMINOLOGY_AND_COMMERCIAL_TUNE_2026_LOCKED_v1.md` | — | — |
| n8n glue | `SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md` | manifest | glue only |

---

## Graph + pipelines (single picture)

**12 runner nodes · 5 tiers:** T0 safety · T1 truth · T2 fleet · T3 proof · **T_lat orient**

| Pipeline | Node id | Trigger |
|----------|---------|---------|
| Orientation Atlas | `orientation_pipeline_v1` | founder **orientation** |
| Hospital Clinic | `hospital_pipeline_v1` | founder **hospital** |
| Maze Quarantine | `maze_pipeline_v1` | founder **maze** |
| Orient cascade | `orient_routing_v1` | `agent_orient_v1.py` / graph tier T_lat |

**Orientation stations O1–O20:** canonical list in `sourcea_agentic_unified_bundle_v1.json` → `orientation_stations`

---

## Cart tasks

| Slug | File |
|------|------|
| node-mesh | `~/.sina/cart-tasks/tasks/node-mesh-cart-v1.json` |
| orient-routing | `~/.sina/cart-tasks/tasks/orient-routing-cart-v1.json` |

---

## Sync command

```bash
cd ~/Desktop/SourceA
bash scripts/sync-cursor-agent-skills.sh
bash scripts/validate-agentic-unified-bundle-v1.sh
```

---

**END LOCKED v1.2.0**
