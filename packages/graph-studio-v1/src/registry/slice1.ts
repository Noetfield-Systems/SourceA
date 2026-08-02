import type { NodeKind, NodeManifest } from "../types.ts";

const emptyConfig = {
  type: "object",
  additionalProperties: false,
  properties: {},
};

function pod(
  kind: NodeKind,
  title: string,
  mesh_role: NonNullable<NodeManifest["mesh_role"]>,
  ports_in: NodeManifest["ports_in"],
  ports_out: NodeManifest["ports_out"],
): NodeManifest {
  return {
    node_kind: kind,
    version: "1.0.0",
    title,
    description: `${title} Role Pod (L0 deliberation; recommend only)`,
    ports_in,
    ports_out,
    config_schema: emptyConfig,
    runtime_binding: "MESH_POD",
    authority: "deliberate",
    budget: { max_attempts: 1, max_fanout: 0 },
    verifier_required: false,
    composite: null,
    mesh_role,
  };
}

export const SLICE1_MANIFESTS: NodeManifest[] = [
  {
    node_kind: "EventIngest",
    version: "1.0.0",
    title: "Event Ingest",
    description: "Admit EventEnvelope into the pinned plan",
    ports_in: [],
    ports_out: [{ name: "event", type: "EventEnvelope", required: true }],
    config_schema: {
      type: "object",
      additionalProperties: false,
      properties: {
        event_type: { type: "string" },
      },
    },
    runtime_binding: "EVENT_INGEST",
    authority: "ingest",
    budget: {},
    verifier_required: false,
    composite: null,
  },
  pod(
    "RolePod_SG",
    "SG Pod",
    "SG",
    [{ name: "event", type: "EventEnvelope", required: true }],
    [{ name: "packet", type: "RoleDecisionPacket", required: true }],
  ),
  pod(
    "RolePod_MemorySteward",
    "Memory Steward",
    "MEMORY_STEWARD",
    [
      { name: "event", type: "EventEnvelope", required: true },
      { name: "sg_packet", type: "RoleDecisionPacket", required: true },
    ],
    [{ name: "context", type: "ContextPack", required: true }],
  ),
  pod(
    "RolePod_Planner",
    "Strategic Planner",
    "STRATEGIC_PLANNER",
    [
      { name: "context", type: "ContextPack", required: true },
      { name: "sg_packet", type: "RoleDecisionPacket", required: true },
    ],
    [{ name: "plan", type: "PlanGraphPacket", required: true }],
  ),
  pod(
    "RolePod_Critic",
    "Critic",
    "CRITIC",
    [{ name: "plan", type: "PlanGraphPacket", required: true }],
    [{ name: "packet", type: "RoleDecisionPacket", required: true }],
  ),
  {
    node_kind: "Governor",
    version: "1.0.0",
    title: "Executive Governor",
    description: "Sole committer of DecisionRecord and WorkPacket",
    ports_in: [
      { name: "plan", type: "PlanGraphPacket", required: true },
      { name: "critic", type: "RoleDecisionPacket", required: true },
    ],
    ports_out: [
      { name: "decision", type: "DecisionRecord", required: true },
      { name: "work", type: "WorkPacket", required: true },
    ],
    config_schema: {
      type: "object",
      additionalProperties: false,
      properties: {
        human_tax_visible: { type: "boolean", default: true },
      },
    },
    runtime_binding: "MESH_GOVERNOR",
    authority: "commit",
    budget: { human_tax_visible: true, max_fanout: 0 },
    verifier_required: false,
    composite: null,
  },
  {
    node_kind: "Executor_RunwayGoalKernel",
    version: "1.0.0",
    title: "Runway Goal Kernel Executor",
    description: "Admit WorkPacket to RUNWAY_GOAL_KERNEL (no second Railway heavy executor)",
    ports_in: [{ name: "work", type: "WorkPacket", required: true }],
    ports_out: [{ name: "execution", type: "Any", required: true }],
    config_schema: {
      type: "object",
      additionalProperties: false,
      properties: {
        executor_class: { type: "string", const: "RUNWAY_GOAL_KERNEL" },
        human_tax_visible: { type: "boolean", default: true },
      },
    },
    runtime_binding: "MESH_EXECUTOR",
    authority: "execute",
    budget: { max_attempts: 2, max_fanout: 0, human_tax_visible: true },
    verifier_required: true,
    composite: null,
  },
  {
    node_kind: "IndependentVerifier",
    version: "1.0.0",
    title: "Independent Verifier",
    description: "Decides reality (ACCEPTED / FAILED / INCIDENT)",
    ports_in: [{ name: "execution", type: "Any", required: true }],
    ports_out: [{ name: "evidence", type: "EvidenceReceipt", required: true }],
    config_schema: emptyConfig,
    runtime_binding: "MESH_VERIFIER",
    authority: "verify",
    budget: {},
    verifier_required: false,
    composite: null,
  },
  {
    node_kind: "CanonicalCommit",
    version: "1.0.0",
    title: "Canonical Commit",
    description: "Write terminal run to Supabase SSOT",
    ports_in: [{ name: "evidence", type: "EvidenceReceipt", required: true }],
    ports_out: [{ name: "commit", type: "CanonicalCommit", required: true }],
    config_schema: emptyConfig,
    runtime_binding: "MESH_COMMIT",
    authority: "record",
    budget: {},
    verifier_required: false,
    composite: null,
  },
  {
    node_kind: "Digest",
    version: "1.0.0",
    title: "Digest",
    description: "Emit run digest for observers",
    ports_in: [{ name: "commit", type: "CanonicalCommit", required: true }],
    ports_out: [{ name: "digest", type: "Digest", required: true }],
    config_schema: emptyConfig,
    runtime_binding: "DIGEST",
    authority: "observe",
    budget: {},
    verifier_required: false,
    composite: null,
  },
  {
    node_kind: "CompositeRolePod",
    version: "1.0.0",
    title: "Composite Role Pod",
    description: "Bounded nested Role Pod shell (max_subflow_depth=1)",
    ports_in: [{ name: "in", type: "Any", required: true }],
    ports_out: [{ name: "out", type: "Any", required: true }],
    config_schema: {
      type: "object",
      additionalProperties: false,
      properties: {
        label: { type: "string" },
      },
    },
    runtime_binding: "MESH_POD",
    authority: "deliberate",
    budget: { max_fanout: 0 },
    verifier_required: false,
    composite: { max_subflow_depth: 1, max_fanout: 0 },
  },
  {
    node_kind: "ExplicitLoop",
    version: "1.0.0",
    title: "Explicit Loop",
    description: "Allowed cycle marker (not used in slice-1 webpage-repair)",
    ports_in: [{ name: "in", type: "Any", required: true }],
    ports_out: [{ name: "out", type: "Any", required: true }],
    config_schema: emptyConfig,
    runtime_binding: "MESH_POD",
    authority: "deliberate",
    budget: { max_attempts: 3, max_fanout: 0 },
    verifier_required: false,
    composite: null,
  },
];

const BY_KIND = new Map(SLICE1_MANIFESTS.map((m) => [m.node_kind, m]));

export function getManifest(kind: NodeKind, version?: string): NodeManifest | undefined {
  const m = BY_KIND.get(kind);
  if (!m) return undefined;
  if (version && m.version !== version) return undefined;
  return m;
}

export function listRegistry(): NodeManifest[] {
  return [...SLICE1_MANIFESTS];
}
