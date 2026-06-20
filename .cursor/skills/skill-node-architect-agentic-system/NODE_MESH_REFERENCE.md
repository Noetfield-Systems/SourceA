# SourceA — Node Mesh Reference

**Unified bundle:** `data/sourcea_agentic_unified_bundle_v1.json`  
**Catalog machine:** `data/sourcea_node_mesh_catalog_v1.json` v1.1  
**Graph:** `data/sourcea_pipeline_node_graph_v1.json` v1.3  
**Directory map:** `data/sourcea_directory_node_map_v1.json` v1.1  
**Orient routing:** `data/sourcea_orient_routing_v1.json` v1.1  
**Build plan:** `docs/SOURCEA_NODE_MESH_SYNESTM_BUILD_PLAN_LOCKED_v1.md`

---

## Active mesh (12 runner nodes · 5 tiers)

| Tier | Node id | Pipeline | Parallel group |
|------|---------|----------|----------------|
| T0 | `sascip_live_wire` | Safety | T0_safety_fanout |
| T0 | `mac_health_probe` | Safety | T0_safety_fanout |
| T1 | `disk_live_wire` | Truth | T1_truth_fanout |
| T1 | `governance_zero_drift` | Truth | T1_truth_fanout |
| T1 | `crawl_mirror_session` | Truth | T1_truth_fanout |
| T2 | `agentic_layer_fast` | Fleet | T2_fleet_fanout |
| T2 | `l1_brain_wire` | Fleet | T2_fleet_fanout |
| T2 | `hub_dual_heal` | Fleet | T2_fleet_fanout |
| T3 | `validate_w10_vocab` | Proof | T3_proof_fanout |
| T3 | `validate_two_hub` | Proof | T3_proof_fanout |
| T3 | `n8n_p0_operational` | Proof (glue) | T3_proof_fanout |
| **T_lat** | **`orient_routing_v1`** | **Orient** | **T_lat_orient_fanout** |

## LAT pipelines (founder word · logical nodes)

| Node id | Trigger | Receipt |
|---------|---------|---------|
| `orientation_pipeline_v1` | **orientation** | `~/.sina/agent-orientation-receipt-v1.json` |
| `hospital_pipeline_v1` | **hospital** | `~/.sina/agent-hospital-receipt-v1.json` |
| `maze_pipeline_v1` | **maze** | `~/.sina/agent-maze-receipt-v1.json` |

## Other logical nodes

`session_gate_v1` · `pipeline_node_graph_runner_v1` · `worker_inbox_v1` · `hub_projection_v1` · `mac_health_guard_v1` · `program_1000_honest_v1` · `directory_node_map_v1` · `terminology_2026_v1`

## Planned (N03–N20 — see build plan)

Session gate delegate · Event spine · Hub canvas · Crawl C1–C10 · Mirror M1–M11 · Portfolio planes · Self-heal · Nightly tier

## Commands

```bash
bash scripts/validate-agentic-unified-bundle-v1.sh
python3 scripts/agent_orient_v1.py --role worker --json
python3 scripts/pipeline_node_graph_runner_v1.py --tier T_lat_orient --json
bash scripts/validate-orient-routing-v1.sh
bash scripts/validate-pipeline-node-graph-v1.sh
```

**Report:** `~/.sina/orient-routing-report-v1.json`

---

**END NODE_MESH_REFERENCE**
