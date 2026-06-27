---
updated: 2026-06-27T08:46:57Z
lane: core
source_path: data/sourcea_node_mesh_catalog_v1.json
public: true
kind: json
---

# Sourcea_Node_Mesh_Catalog_V1

- **schema**: sourcea-node-mesh-catalog-v1
- **version**: 1.1.0
- **saved_at**: 2026-06-16T09:45:00Z
- **synestm**: SourceA unified multi-parallel node mesh — not fragmented pipelines
- **graph**: data/sourcea_pipeline_node_graph_v1.json
- **directory_map**: data/sourcea_directory_node_map_v1.json
- **build_plan**: docs/SOURCEA_NODE_MESH_SYNESTM_BUILD_PLAN_LOCKED_v1.md
- **skill**: .cursor/skills/skill-node-architect-agentic-system/SKILL.md
- **topology**: multi-parallel-tier-mesh
## stats
- **active_runner_nodes**: 12
- **logical_nodes**: 11
- **parallel_groups**: 5
- **explicit_edges**: 24
- **planned_nodes**: 24
- **waves**: 5
## parallel_groups
## T0_safety_fanout
- **id**: T0_safety_fanout
- **tier**: T0_safety
- **nodes**: 2
- **command**: python3 scripts/pipeline_node_graph_runner_v1.py --tier T0_safety --json
## T1_truth_fanout
- **id**: T1_truth_fanout
- **tier**: T1_truth_parallel
- **nodes**: 3
- **command**: python3 scripts/pipeline_node_graph_runner_v1.py --tier T1_truth_parallel --json
## T2_fleet_fanout
- **id**: T2_fleet_fanout
- **tier**: T2_fleet_parallel
- **nodes**: 3
- **command**: python3 scripts/pipeline_node_graph_runner_v1.py --tier T2_fleet_parallel --json
## T3_proof_fanout
- **id**: T3_proof_fanout
- **tier**: T3_proof_parallel
- **nodes**: 3
- **command**: python3 scripts/pipeline_node_graph_runner_v1.py --tier T3_proof_parallel --json
## T_lat_orient_fanout
- **id**: T_lat_orient_fanout
- **tier**: T_lat_orient
- **nodes**: 1
- **command**: python3 scripts/pipeline_node_graph_runner_v1.py --tier T_lat_orient --json
#### founder_word_siblings
- orientation_pipeline_v1
- hospital_pipeline_v1
- maze_pipeline_v1
## active_nodes
## sascip_live_wire
- **id**: sascip_live_wire
- **tier**: T0
- **pipeline**: Safety
- **status**: active
- **parallel**: True
## mac_health_probe
- **id**: mac_health_probe
- **tier**: T0
- **pipeline**: Safety
- **status**: active
- **parallel**: True
## disk_live_wire
- **id**: disk_live_wire
- **tier**: T1
- **pipeline**: Truth
- **status**: active
- **parallel**: True
## governance_zero_drift
- **id**: governance_zero_drift
- **tier**: T1
- **pipeline**: Truth
- **status**: active
- **parallel**: True
## crawl_mirror_session
- **id**: crawl_mirror_session
- **tier**: T1
- **pipeline**: Truth
- **status**: active
- **parallel**: True
## agentic_layer_fast
- **id**: agentic_layer_fast
- **tier**: T2
- **pipeline**: Fleet
- **status**: active
- **parallel**: True
## l1_brain_wire
- **id**: l1_brain_wire
- **tier**: T2
- **pipeline**: Fleet
- **status**: active
- **parallel**: True
## hub_dual_heal
- **id**: hub_dual_heal
- **tier**: T2
- **pipeline**: Fleet
- **status**: active
- **parallel**: True
## validate_w10_vocab
- **id**: validate_w10_vocab
- **tier**: T3
- **pipeline**: Proof
- **status**: active
- **parallel**: True
## validate_two_hub
- **id**: validate_two_hub
- **tier**: T3
- **pipeline**: Proof
- **status**: active
- **parallel**: True
## n8n_p0_operational
- **id**: n8n_p0_operational
- **tier**: T3
- **pipeline**: Proof
- **status**: active
- **plane**: RUNTIME_GLUE
- **parallel**: True
## orient_routing_v1
- **id**: orient_routing_v1
- **tier**: T_lat
- **pipeline**: Orient
- **status**: active
- **parallel**: False
- **handler**: scripts/agent_orient_v1.py
- **receipt**: ~/.sina/orient-routing-report-v1.json
## logical_nodes
## session_gate_v1
- **id**: session_gate_v1
- **status**: active
- **wiring_target**: N03 delegate T0-T1 to runner
## pipeline_node_graph_runner_v1
- **id**: pipeline_node_graph_runner_v1
- **status**: active
## worker_inbox_v1
- **id**: worker_inbox_v1
- **status**: active
## hub_projection_v1
- **id**: hub_projection_v1
- **status**: active
## mac_health_guard_v1
- **id**: mac_health_guard_v1
- **status**: active
## program_1000_honest_v1
- **id**: program_1000_honest_v1
- **status**: active
## directory_node_map_v1
- **id**: directory_node_map_v1
- **status**: active
## terminology_2026_v1
- **id**: terminology_2026_v1
- **status**: active
## orientation_pipeline_v1
- **id**: orientation_pipeline_v1
- **status**: active
- **layer**: LAT
- **founder_word**: orientation
- **handler**: scripts/agent_orientation_pipeline_v1.py
- **receipt**: ~/.sina/agent-orientation-receipt-v1.json
## hospital_pipeline_v1
- **id**: hospital_pipeline_v1
- **status**: active
- **layer**: LAT
- **founder_word**: hospital
- **handler**: scripts/agent_hospital_pipeline_v1.py
- **receipt**: ~/.sina/agent-hospital-receipt-v1.json
## maze_pipeline_v1
- **id**: maze_pipeline_v1
- **status**: active
- **layer**: LAT
- **founder_word**: maze
- **handler**: scripts/agent_maze_pipeline_v1.py
- **receipt**: ~/.sina/agent-maze-receipt-v1.json
## planned_nodes
## session_gate_graph_delegate
- **id**: session_gate_graph_delegate
- **build**: N03
- **priority**: P0
- **replaces**: duplicate linear gate steps
## event_spine_emit_v1
- **id**: event_spine_emit_v1
- **build**: N06
- **priority**: P1
#### topics
- spine.bridge
- factory.advance
## hub_node_canvas_v1
- **id**: hub_node_canvas_v1
- **build**: N07
- **priority**: P1
- **surface**: :13020
## hub_run_tier_tap_v1
- **id**: hub_run_tier_tap_v1
- **build**: N08
- **priority**: P1
## crawl_subgraph_c1_c10
- **id**: crawl_subgraph_c1_c10
- **build**: N11
- **priority**: P1
- **count**: 10
## mirror_subgraph_m1_m11
- **id**: mirror_subgraph_m1_m11
- **build**: N12
- **priority**: P1
- **count**: 11
## scheduled_graph_tier_v1
- **id**: scheduled_graph_tier_v1
- **build**: N13
- **priority**: P2
## node_health_dashboard_v1
- **id**: node_health_dashboard_v1
- **build**: N14
- **priority**: P2
- **surface**: :13024
## runreceipt_per_node_v1
- **id**: runreceipt_per_node_v1
- **build**: N15
- **priority**: P2
## portfolio_ya5_node_v1
- **id**: portfolio_ya5_node_v1
- **build**: N10
- **priority**: P2
- **plane**: PORTFOLIO
## portfolio_trustfield_node_v1
- **id**: portfolio_trustfield_node_v1
- **build**: N10
- **priority**: P2
- **plane**: PORTFOLIO
## portfolio_noetfield_node_v1
- **id**: portfolio_noetfield_node_v1
- **build**: N10
- **priority**: P2
- **plane**: PORTFOLIO
## self_heal_runner_v1
- **id**: self_heal_runner_v1
- **build**: N18
- **priority**: P3
## nightly_full_graph_v1
- **id**: nightly_full_graph_v1
- **build**: N19
- **priority**: P3
## mirror_audit_pack_export_v1
- **id**: mirror_audit_pack_export_v1
- **build**: N20
- **priority**: P4
- **commerce**: True
## anti_fragmentation_rules
- New capability = graph node row + directory map row + mesh catalog row
- No orphan validate-* without node id
- Pipelines declare node cluster ids (dual nav)
- Three pipelines (orientation/hospital/maze) = LAT logical nodes · orient_routing_v1 = T_lat runner
- n8n = glue tier only — never law SSOT
- Session gate must delegate to runner (N03) — no duplicate crawl-mirror
- Parallel only within tier — sequential across tiers
## proof_ladder
- bash scripts/validate-pipeline-node-graph-v1.sh
- python3 scripts/pipeline_node_graph_runner_v1.py --dry-run --json
- CART TASK node-mesh
- bash scripts/validate-anti-staleness-vocabulary-gate-v1.sh
