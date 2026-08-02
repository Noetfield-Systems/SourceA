import type { BlueprintGraph } from "../types.ts";

/** Golden slice-1 blueprint: live L0 webpage-repair mesh path (semantic only). */
export const WEBPAGE_REPAIR_L0_BLUEPRINT: BlueprintGraph = {
  blueprint_id: "webpage_repair_l0_v1",
  version: "1.0.0",
  title: "Webpage Repair L0 (Executive Mesh vertical slice)",
  nodes: [
    { id: "n_event", node_kind: "EventIngest", manifest_version: "1.0.0", config: { event_type: "webpage_repair_request" } },
    { id: "n_sg", node_kind: "RolePod_SG", manifest_version: "1.0.0" },
    { id: "n_mem", node_kind: "RolePod_MemorySteward", manifest_version: "1.0.0" },
    { id: "n_plan", node_kind: "RolePod_Planner", manifest_version: "1.0.0" },
    { id: "n_critic", node_kind: "RolePod_Critic", manifest_version: "1.0.0" },
    { id: "n_gov", node_kind: "Governor", manifest_version: "1.0.0", config: { human_tax_visible: true } },
    {
      id: "n_exec",
      node_kind: "Executor_RunwayGoalKernel",
      manifest_version: "1.0.0",
      config: { executor_class: "RUNWAY_GOAL_KERNEL", human_tax_visible: true },
    },
    { id: "n_verify", node_kind: "IndependentVerifier", manifest_version: "1.0.0" },
    { id: "n_commit", node_kind: "CanonicalCommit", manifest_version: "1.0.0" },
    { id: "n_digest", node_kind: "Digest", manifest_version: "1.0.0" },
  ],
  edges: [
    { id: "e1", from_node: "n_event", from_port: "event", to_node: "n_sg", to_port: "event" },
    { id: "e2", from_node: "n_event", from_port: "event", to_node: "n_mem", to_port: "event" },
    { id: "e3", from_node: "n_sg", from_port: "packet", to_node: "n_mem", to_port: "sg_packet" },
    { id: "e4", from_node: "n_sg", from_port: "packet", to_node: "n_plan", to_port: "sg_packet" },
    { id: "e5", from_node: "n_mem", from_port: "context", to_node: "n_plan", to_port: "context" },
    { id: "e6", from_node: "n_plan", from_port: "plan", to_node: "n_critic", to_port: "plan" },
    { id: "e7", from_node: "n_plan", from_port: "plan", to_node: "n_gov", to_port: "plan" },
    { id: "e8", from_node: "n_critic", from_port: "packet", to_node: "n_gov", to_port: "critic" },
    { id: "e9", from_node: "n_gov", from_port: "work", to_node: "n_exec", to_port: "work" },
    { id: "e10", from_node: "n_exec", from_port: "execution", to_node: "n_verify", to_port: "execution" },
    { id: "e11", from_node: "n_verify", from_port: "evidence", to_node: "n_commit", to_port: "evidence" },
    { id: "e12", from_node: "n_commit", from_port: "commit", to_node: "n_digest", to_port: "commit" },
  ],
};

/** Required ordered kinds for mesh webpage-repair topology match */
export const WEBPAGE_REPAIR_REQUIRED_KINDS = [
  "EventIngest",
  "RolePod_SG",
  "RolePod_MemorySteward",
  "RolePod_Planner",
  "RolePod_Critic",
  "Governor",
  "Executor_RunwayGoalKernel",
  "IndependentVerifier",
  "CanonicalCommit",
  "Digest",
] as const;
