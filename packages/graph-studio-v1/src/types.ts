/** Graph Studio v1 — domain types (NF-GRAPH-STUDIO-V1) */

export type RuntimeBinding =
  | "EVENT_INGEST"
  | "MESH_POD"
  | "MESH_GOVERNOR"
  | "MESH_EXECUTOR"
  | "MESH_VERIFIER"
  | "MESH_COMMIT"
  | "DIGEST";

export type PortType =
  | "EventEnvelope"
  | "ContextPack"
  | "RoleDecisionPacket"
  | "PlanGraphPacket"
  | "DecisionRecord"
  | "WorkPacket"
  | "EvidenceReceipt"
  | "CanonicalCommit"
  | "Digest"
  | "Any";

export type NodeKind =
  | "EventIngest"
  | "RolePod_SG"
  | "RolePod_MemorySteward"
  | "RolePod_Planner"
  | "RolePod_Critic"
  | "Governor"
  | "Executor_RunwayGoalKernel"
  | "IndependentVerifier"
  | "CanonicalCommit"
  | "Digest"
  | "CompositeRolePod"
  | "ExplicitLoop";

export interface PortDef {
  name: string;
  type: PortType;
  required?: boolean;
}

export interface CompositeBounds {
  max_subflow_depth: number;
  max_fanout: number;
}

export interface NodeManifest {
  node_kind: NodeKind;
  version: string;
  title: string;
  description: string;
  ports_in: PortDef[];
  ports_out: PortDef[];
  config_schema: Record<string, unknown>;
  runtime_binding: RuntimeBinding;
  authority: "deliberate" | "commit" | "execute" | "verify" | "record" | "ingest" | "observe";
  budget: {
    max_attempts?: number;
    max_fanout?: number;
    human_tax_visible?: boolean;
  };
  verifier_required: boolean;
  composite: CompositeBounds | null;
  mesh_role?: "SG" | "MEMORY_STEWARD" | "STRATEGIC_PLANNER" | "CRITIC";
}

export interface BlueprintNode {
  id: string;
  node_kind: NodeKind;
  manifest_version: string;
  config?: Record<string, unknown>;
  /** Nested subflow for CompositeRolePod only */
  subflow?: BlueprintGraph;
}

export interface BlueprintEdge {
  id: string;
  from_node: string;
  from_port: string;
  to_node: string;
  to_port: string;
  explicit_loop?: boolean;
}

/** Semantic graph only — no layout */
export interface BlueprintGraph {
  blueprint_id: string;
  version: string;
  title: string;
  nodes: BlueprintNode[];
  edges: BlueprintEdge[];
}

/** Studio-only; never hashed into plan */
export interface BlueprintLayout {
  blueprint_id: string;
  version: string;
  positions: Record<string, { x: number; y: number; color?: string }>;
}

export interface CompiledNode {
  id: string;
  node_kind: NodeKind;
  manifest_version: string;
  runtime_binding: RuntimeBinding;
  config: Record<string, unknown>;
  verifier_required: boolean;
  order: number;
}

export interface CompiledEdge {
  id: string;
  from_node: string;
  from_port: string;
  to_node: string;
  to_port: string;
  explicit_loop: boolean;
}

export interface CompiledExecutionPlan {
  plan_schema: "graph_studio_compiled_plan_v1";
  blueprint_id: string;
  blueprint_version: string;
  topology: "webpage_repair_l0_v1";
  nodes: CompiledNode[];
  edges: CompiledEdge[];
  executor_ids: string[];
  verifier_ids: string[];
  plan_hash: string;
  frozen_at?: string;
}

export type NodeRunStatus = "PENDING" | "RUNNING" | "PASSED" | "FAILED" | "SKIPPED";

export interface RunGraphNode {
  id: string;
  node_kind: NodeKind;
  status: NodeRunStatus;
  detail?: string;
}

export interface RunGraph {
  run_id: string;
  plan_hash: string;
  mesh_run_id: string | null;
  status: string;
  nodes: RunGraphNode[];
  child_runs: Array<{ child_id: string; parent_node_id: string; status: string }>;
}

export interface CompileError {
  code: string;
  message: string;
  node_id?: string;
  edge_id?: string;
}

export type CompileResult =
  | { ok: true; plan: CompiledExecutionPlan }
  | { ok: false; errors: CompileError[] };
