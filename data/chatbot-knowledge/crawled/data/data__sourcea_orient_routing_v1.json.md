---
updated: 2026-06-30T12:42:32Z
lane: core
source_path: data/sourcea_orient_routing_v1.json
public: true
kind: json
---

# Sourcea_Orient_Routing_V1

- **schema**: sourcea-orient-routing-v1
- **version**: 1.1.0
- **saved_at**: 2026-06-16T09:45:00Z
- **human**: docs/SOURCEA_ORIENTATION_AND_ROUTING_LOCKED_v1.md
- **law**: AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md
- **mesh_catalog**: data/sourcea_node_mesh_catalog_v1.json
- **node_graph**: data/sourcea_pipeline_node_graph_v1.json
- **report_receipt**: ~/.sina/orient-routing-report-v1.json
## commands
- **orient**: python3 scripts/agent_orient_v1.py --json
- **orient_routing_validate**: bash scripts/validate-orient-routing-v1.sh
- **orientation_pipeline**: python3 scripts/agent_three_pipelines_router_v1.py orientation --json
- **hospital_pipeline**: python3 scripts/agent_three_pipelines_router_v1.py hospital --json
- **maze_pipeline**: python3 scripts/agent_three_pipelines_router_v1.py maze --json
- **node_graph_lat**: python3 scripts/pipeline_node_graph_runner_v1.py --tier T_lat_orient --json
- **session_gate**: python3 scripts/agent_session_gate_run_v1.py --role <role> --json
- **session_start_rule**: agent_session_gate_run_v1.py ONLY — not orientation/hospital/maze
## graph_tiers
### session
- T0_safety
- T1_truth_parallel
- T2_fleet_parallel
- T3_proof_parallel
### lat
- T_lat_orient
### all_runner
- T0_safety
- T1_truth_parallel
- T2_fleet_parallel
- T3_proof_parallel
- T_lat_orient
## pipeline_nodes
### orientation
- **node_id**: orientation_pipeline_v1
- **tier**: 1
- **layer**: LAT
- **trigger**: orientation
- **handler**: scripts/agent_orientation_pipeline_v1.py
- **receipt**: ~/.sina/agent-orientation-receipt-v1.json
- **founder_word_only**: True
### hospital
- **node_id**: hospital_pipeline_v1
- **tier**: 2
- **layer**: LAT
- **trigger**: hospital
- **handler**: scripts/agent_hospital_pipeline_v1.py
- **receipt**: ~/.sina/agent-hospital-receipt-v1.json
- **founder_word_only**: True
### maze
- **node_id**: maze_pipeline_v1
- **tier**: 3
- **layer**: LAT
- **trigger**: maze
- **handler**: scripts/agent_maze_pipeline_v1.py
- **receipt**: ~/.sina/agent-maze-receipt-v1.json
- **founder_word_only**: True
- **quarantine**: True
### orient_routing
- **node_id**: orient_routing_v1
- **tier**: T_lat_orient
- **layer**: LAT
- **handler**: scripts/agent_orient_v1.py
- **receipt**: ~/.sina/orient-routing-report-v1.json
- **runner_tier**: T_lat_orient
- **founder_word_only**: False
## orientation_station_nodes
- **O1**: session_gate_v1
- **O2**: governance_zero_drift
- **O6**: agentic_layer_fast
- **O8**: orientation_pipeline_v1
- **O15**: orient_routing_v1
- **O16**: pipeline_node_graph_runner_v1
- **O17**: directory_node_map_v1
- **O18**: agentic_layer_fast
- **O19**: orient_routing_v1
- **O20**: pipeline_node_graph_runner_v1
- **orientation_stations_ssot**: data/sourcea_agentic_unified_bundle_v1.json
- **unified_bundle**: data/sourcea_agentic_unified_bundle_v1.json
## founder_word_routing
### orientation
- **tier**: 1
- **node_id**: orientation_pipeline_v1
- **router**: agent_three_pipelines_router_v1.py orientation
- **receipt**: ~/.sina/agent-orientation-receipt-v1.json
- **authority**: False
### hospital
- **tier**: 2
- **node_id**: hospital_pipeline_v1
- **router**: agent_three_pipelines_router_v1.py hospital
- **receipt**: ~/.sina/agent-hospital-receipt-v1.json
- **authority**: False
### maze
- **tier**: 3
- **node_id**: maze_pipeline_v1
- **router**: agent_three_pipelines_router_v1.py maze
- **receipt**: ~/.sina/agent-maze-receipt-v1.json
- **authority**: False
- **quarantine**: True
## role_routing
### brain
- **daily**: Route · pick · handoff · quote factory_now_line
- **session_start**: agent_session_gate_run_v1.py --role brain
- **build**: False
- **orient_hint**: Pick ONE branch from gate_tree · no sa-* implementation
- **next_tap**: Worker chat RUN INBOX or role handoff
- **skill**: agent-skills/sourcea_brain/SKILL.md
### worker
- **daily**: RUN INBOX · one sa-* · validators PASS
- **session_start**: agent_session_gate_run_v1.py --role worker
- **build**: True
- **orient_hint**: H1 glance optional · disk queue SSOT
- **next_tap**: RUN INBOX
- **skill**: agent-skills/sourcea_worker/SKILL.md
### governance
- **daily**: Advise · audit · poison track checkcart
- **session_start**: agent_session_gate_run_v1.py --role any
- **build**: False
- **orient_hint**: Receipt cascade · no product build
- **next_tap**: CART TASK poison-track if open
- **skill**: agent-skills/shared/conscious-recovery/SKILL.md
### any
- **daily**: Session gate · quote factory_now_line · role scope
- **session_start**: agent_session_gate_run_v1.py --role any
- **orient_hint**: Say worker or brain for lane-specific routing
## orient_chain
## start_here
- **step**: 1
- **id**: start_here
- **path**: brain-os/law/entry/START_HERE_LOCKED_v1.md
- **why**: Law front door · pick role
## orient_routing
- **step**: 2
- **id**: orient_routing
- **path**: docs/SOURCEA_ORIENTATION_AND_ROUTING_LOCKED_v1.md
- **why**: Routing + receipt cascade
## foundational_index
- **step**: 3
- **id**: foundational_index
- **path**: docs/SOURCEA_FOUNDATIONAL_AGENTIC_SYSTEMS_INDEX_LOCKED_v1.md
- **why**: Skill load order
## node_mesh_plan
- **step**: 4
- **id**: node_mesh_plan
- **path**: docs/SOURCEA_NODE_MESH_SYNESTM_BUILD_PLAN_LOCKED_v1.md
- **why**: Parallel node mesh · synestm
## three_pipelines
- **step**: 5
- **id**: three_pipelines
- **path**: AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md
- **why**: Founder word triggers
## layer_stack
- **step**: 6
- **id**: layer_stack
- **path**: SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md
- **why**: L0–L3 roles
## node_graph
- **step**: 7
- **id**: node_graph
- **path**: data/sourcea_pipeline_node_graph_v1.json
- **why**: 12 nodes · 5 tiers · LAT orient
## directory_map
- **step**: 8
- **id**: directory_map
- **path**: data/sourcea_directory_node_map_v1.json
- **why**: Folder → node wiring
## live_surfaces
- **step**: 9
- **id**: live_surfaces
- **path**: ~/.sina/agent-live-surfaces-v1.json
- **why**: factory_now_line inject
## session_gate_receipt
- **step**: 10
- **id**: session_gate_receipt
- **path**: ~/.sina/agent_session_gate_receipt_v1.json
- **why**: Session proof
## session_gate_step_nodes
- **anti_staleness_auto_wire**: disk_live_wire
- **memory_mirror_sync**: disk_live_wire
- **daily_duty_card**: session_gate_v1
- **truth_bundle**: disk_live_wire
- **rules_loop**: governance_zero_drift
- **agentic_pipeline_v2**: agentic_layer_fast
- **stranger_agent_safety_live_wire**: sascip_live_wire
- **governance_zero_drift_live_wire**: governance_zero_drift
- **sourcea_crawl_mirror_pipeline**: crawl_mirror_session
- **conduct**: session_gate_v1
## validator_check_nodes
- **validate-disk-live-wire-v1**: disk_live_wire
- **validate-crawl-mirror-v1**: crawl_mirror_session
- **validate-stranger-agent-safety-v1**: sascip_live_wire
- **validate-stranger-agent-safety-live-wire-v1**: sascip_live_wire
- **validate-anti-staleness-vocabulary-gate-v1**: validate_w10_vocab
- **validate-pipeline-node-graph-v1**: pipeline_node_graph_runner_v1
- **validate-two-hub-v1**: validate_two_hub
- **validate-n8n-p0-operational-v1**: n8n_p0_operational
- **validate-orient-routing-v1**: orient_routing_v1
- **validate-agent-three-pipelines-v1**: orientation_pipeline_v1
- **find_critical_bugs**: validate_w10_vocab
## daily_pipeline_to_node
### brain
- **entry**: brain-session-start.sh
#### nodes
- session_gate_v1
- disk_live_wire
- l1_brain_wire
- brain_governance_wire_v1
- **execute**: route handoff only — never implement sa
### worker
- **entry**: worker_turn_entry_v1.sh
#### nodes
- session_gate_v1
- worker_inbox_v1
- goal1_lane_broker
- outbound_post_ship_v1
- **execute**: RUN INBOX head only — queue_pos>1 preview not bound
### governance
- **entry**: l1_agent_pipeline_wire_v1.py
#### nodes
- l1_brain_wire
- governance_zero_drift
### commercial
- **entry**: l1_agent_pipeline_wire_v1.py
#### nodes
- l1_brain_wire
- commercial_command_pulse
### brief
- **entry**: l1_agent_pipeline_wire_v1.py
#### nodes
- l1_brain_wire
- research_acquisitor
## receipt_cascade_sources
## session_gate
- **id**: session_gate
- **path**: ~/.sina/agent_session_gate_receipt_v1.json
- **step_key**: steps
## graph_run
- **id**: graph_run
- **path**: ~/.sina/pipeline-node-graph-receipt-v1.json
- **tier_key**: tiers
## critical_bugs
- **id**: critical_bugs
- **path**: ~/.sina/find-bugs/last-run.json
- **field**: critical_count
## live_surfaces
- **id**: live_surfaces
- **path**: ~/.sina/agent-live-surfaces-v1.json
- **field**: factory_now_line
## orientation
- **id**: orientation
- **path**: ~/.sina/agent-orientation-receipt-v1.json
- **node_id**: orientation_pipeline_v1
- **only_if_exists**: True
## hospital
- **id**: hospital
- **path**: ~/.sina/agent-hospital-receipt-v1.json
- **node_id**: hospital_pipeline_v1
- **only_if_exists**: True
## maze
- **id**: maze
- **path**: ~/.sina/agent-maze-receipt-v1.json
- **node_id**: maze_pipeline_v1
- **only_if_exists**: True
## orient_report
- **id**: orient_report
- **path**: ~/.sina/orient-routing-report-v1.json
- **node_id**: orient_routing_v1
- **field**: cascade_ok
- **invert**: True
## investigator_judge
- **id**: investigator_judge
- **path**: ~/.sina/investigator-judge-unified-receipt-v1.json
- **node_id**: investigator_judge_unified_v1
- **only_if_exists**: True
## daily_routing_ladder
## session_gate
- **order**: 1
- **id**: session_gate
- **handler**: agent_session_gate_run_v1.py
- **node_id**: session_gate_v1
- **enhance**: False
## live_surfaces
- **order**: 2
- **id**: live_surfaces
- **handler**: agent-live-surfaces-v1.json
- **node_id**: disk_live_wire
- **enhance**: False
## run_inbox
- **order**: 3
- **id**: run_inbox
- **handler**: healthy_prompt_turn_v1.py
- **node_id**: worker_inbox_v1
- **enhance**: False
## node_graph_pulse
- **order**: 4
- **id**: node_graph_pulse
- **handler**: pipeline_node_graph_runner_v1.py
- **node_id**: pipeline_node_graph_runner_v1
- **enhance**: False
## orient_cascade
- **order**: 5
- **id**: orient_cascade
- **handler**: agent_orient_v1.py
- **node_id**: orient_routing_v1
- **enhance**: False
## hub_glance
- **order**: 6
- **id**: hub_glance
- **handler**: http://127.0.0.1:13020/
- **skip_if**: hub_down
- **node_id**: hub_projection_v1
