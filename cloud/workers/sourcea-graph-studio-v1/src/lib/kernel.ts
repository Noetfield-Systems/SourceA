/**
 * Worker-local Graph Studio kernel (Web Crypto hash).
 * Mirrors packages/graph-studio-v1 — Node package remains unit-test SSOT.
 */

export type RuntimeBinding =
  | "EVENT_INGEST"
  | "MESH_POD"
  | "MESH_GOVERNOR"
  | "MESH_EXECUTOR"
  | "MESH_VERIFIER"
  | "MESH_COMMIT"
  | "DIGEST";

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
  type: string;
  required?: boolean;
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
  authority: string;
  budget: Record<string, unknown>;
  verifier_required: boolean;
  composite: { max_subflow_depth: number; max_fanout: number } | null;
}

export interface BlueprintNode {
  id: string;
  node_kind: NodeKind;
  manifest_version: string;
  config?: Record<string, unknown>;
}

export interface BlueprintEdge {
  id: string;
  from_node: string;
  from_port: string;
  to_node: string;
  to_port: string;
  explicit_loop?: boolean;
}

export interface BlueprintGraph {
  blueprint_id: string;
  version: string;
  title: string;
  nodes: BlueprintNode[];
  edges: BlueprintEdge[];
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

export interface CompileError {
  code: string;
  message: string;
  node_id?: string;
  edge_id?: string;
}

export type CompileResult =
  | { ok: true; plan: CompiledExecutionPlan }
  | { ok: false; errors: CompileError[] };

export function stableStringify(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map((v) => stableStringify(v)).join(",")}]`;
  const obj = value as Record<string, unknown>;
  const keys = Object.keys(obj).sort();
  return `{${keys.map((k) => `${JSON.stringify(k)}:${stableStringify(obj[k])}`).join(",")}}`;
}

export async function hashObject(value: unknown): Promise<string> {
  const data = new TextEncoder().encode(stableStringify(value));
  const buf = await crypto.subtle.digest("SHA-256", data);
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

const emptyConfig = { type: "object", additionalProperties: false, properties: {} };

function pod(
  kind: NodeKind,
  title: string,
  ports_in: PortDef[],
  ports_out: PortDef[],
): NodeManifest {
  return {
    node_kind: kind,
    version: "1.0.0",
    title,
    description: `${title} Role Pod`,
    ports_in,
    ports_out,
    config_schema: emptyConfig,
    runtime_binding: "MESH_POD",
    authority: "deliberate",
    budget: { max_attempts: 1, max_fanout: 0 },
    verifier_required: false,
    composite: null,
  };
}

export const SLICE1_MANIFESTS: NodeManifest[] = [
  {
    node_kind: "EventIngest",
    version: "1.0.0",
    title: "Event Ingest",
    description: "Admit EventEnvelope",
    ports_in: [],
    ports_out: [{ name: "event", type: "EventEnvelope", required: true }],
    config_schema: emptyConfig,
    runtime_binding: "EVENT_INGEST",
    authority: "ingest",
    budget: {},
    verifier_required: false,
    composite: null,
  },
  pod("RolePod_SG", "SG Pod", [{ name: "event", type: "EventEnvelope", required: true }], [
    { name: "packet", type: "RoleDecisionPacket", required: true },
  ]),
  pod(
    "RolePod_MemorySteward",
    "Memory Steward",
    [
      { name: "event", type: "EventEnvelope", required: true },
      { name: "sg_packet", type: "RoleDecisionPacket", required: true },
    ],
    [{ name: "context", type: "ContextPack", required: true }],
  ),
  pod(
    "RolePod_Planner",
    "Strategic Planner",
    [
      { name: "context", type: "ContextPack", required: true },
      { name: "sg_packet", type: "RoleDecisionPacket", required: true },
    ],
    [{ name: "plan", type: "PlanGraphPacket", required: true }],
  ),
  pod("RolePod_Critic", "Critic", [{ name: "plan", type: "PlanGraphPacket", required: true }], [
    { name: "packet", type: "RoleDecisionPacket", required: true },
  ]),
  {
    node_kind: "Governor",
    version: "1.0.0",
    title: "Executive Governor",
    description: "Sole committer",
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
      properties: { human_tax_visible: { type: "boolean", default: true } },
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
    description: "RUNWAY_GOAL_KERNEL",
    ports_in: [{ name: "work", type: "WorkPacket", required: true }],
    ports_out: [{ name: "execution", type: "Any", required: true }],
    config_schema: emptyConfig,
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
    description: "Decides reality",
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
    description: "Supabase SSOT write",
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
    description: "Run digest",
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
    description: "Bounded nested shell",
    ports_in: [{ name: "in", type: "Any", required: true }],
    ports_out: [{ name: "out", type: "Any", required: true }],
    config_schema: emptyConfig,
    runtime_binding: "MESH_POD",
    authority: "deliberate",
    budget: { max_fanout: 0 },
    verifier_required: false,
    composite: { max_subflow_depth: 1, max_fanout: 0 },
  },
];

const BY_KIND = new Map(SLICE1_MANIFESTS.map((m) => [m.node_kind, m]));

export function getManifest(kind: NodeKind, version?: string): NodeManifest | undefined {
  const m = BY_KIND.get(kind);
  if (!m) return undefined;
  if (version && m.version !== version) return undefined;
  return m;
}

export const WEBPAGE_REPAIR_L0_BLUEPRINT: BlueprintGraph = {
  blueprint_id: "webpage_repair_l0_v1",
  version: "1.0.0",
  title: "Webpage Repair L0",
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

const REQUIRED = [
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

const LAYOUT_KEYS = new Set(["x", "y", "color", "position", "positions", "layout", "style"]);

function hasLayoutPollution(value: unknown, path = ""): string | null {
  if (value === null || typeof value !== "object") return null;
  if (Array.isArray(value)) {
    for (let i = 0; i < value.length; i++) {
      const hit = hasLayoutPollution(value[i], `${path}[${i}]`);
      if (hit) return hit;
    }
    return null;
  }
  for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
    if (LAYOUT_KEYS.has(k)) return `${path}.${k}`;
    const hit = hasLayoutPollution(v, `${path}.${k}`);
    if (hit) return hit;
  }
  return null;
}

export function stripLayout(graph: BlueprintGraph): BlueprintGraph {
  return {
    blueprint_id: graph.blueprint_id,
    version: graph.version,
    title: graph.title,
    nodes: graph.nodes.map((n) => ({
      id: n.id,
      node_kind: n.node_kind,
      manifest_version: n.manifest_version,
      ...(n.config ? { config: n.config } : {}),
    })),
    edges: graph.edges.map((e) => ({
      id: e.id,
      from_node: e.from_node,
      from_port: e.from_port,
      to_node: e.to_node,
      to_port: e.to_port,
      ...(e.explicit_loop ? { explicit_loop: true } : {}),
    })),
  };
}

function topoOrder(graph: BlueprintGraph, errors: CompileError[]): string[] {
  const ids = new Set(graph.nodes.map((n) => n.id));
  const indeg = new Map<string, number>();
  const adj = new Map<string, string[]>();
  for (const id of ids) {
    indeg.set(id, 0);
    adj.set(id, []);
  }
  for (const e of graph.edges) {
    if (e.explicit_loop) continue;
    if (!ids.has(e.from_node) || !ids.has(e.to_node)) {
      errors.push({ code: "EDGE_UNKNOWN_NODE", message: `Edge ${e.id} bad`, edge_id: e.id });
      continue;
    }
    adj.get(e.from_node)!.push(e.to_node);
    indeg.set(e.to_node, (indeg.get(e.to_node) ?? 0) + 1);
  }
  const q = [...ids].filter((id) => (indeg.get(id) ?? 0) === 0).sort();
  const order: string[] = [];
  while (q.length) {
    const n = q.shift()!;
    order.push(n);
    for (const m of adj.get(n) ?? []) {
      const d = (indeg.get(m) ?? 1) - 1;
      indeg.set(m, d);
      if (d === 0) {
        q.push(m);
        q.sort();
      }
    }
  }
  if (order.length !== ids.size) {
    errors.push({ code: "CYCLE_WITHOUT_EXPLICIT_LOOP", message: "Cycle without Explicit Loop" });
  }
  return order;
}

export async function compileBlueprint(raw: BlueprintGraph): Promise<CompileResult> {
  const errors: CompileError[] = [];
  const pollution = hasLayoutPollution(raw);
  if (pollution) {
    errors.push({ code: "LAYOUT_POLLUTION", message: `Layout field: ${pollution}` });
  }
  const graph = stripLayout(raw);
  if (!graph.blueprint_id || !graph.version || !graph.nodes?.length) {
    errors.push({ code: "SCHEMA", message: "blueprint_id, version, nodes required" });
  }
  const nodeById = new Map(graph.nodes.map((n) => [n.id, n]));
  if (nodeById.size !== graph.nodes.length) {
    errors.push({ code: "DUPLICATE_NODE_ID", message: "Duplicate node ids" });
  }
  for (const n of graph.nodes) {
    if (!getManifest(n.node_kind, n.manifest_version)) {
      errors.push({
        code: "UNKNOWN_NODE_KIND",
        message: `${n.node_kind}@${n.manifest_version}`,
        node_id: n.id,
      });
    }
  }
  for (const e of graph.edges) {
    const from = nodeById.get(e.from_node);
    const to = nodeById.get(e.to_node);
    if (!from || !to) continue;
    const fromM = getManifest(from.node_kind, from.manifest_version);
    const toM = getManifest(to.node_kind, to.manifest_version);
    if (!fromM || !toM) continue;
    const outPort = fromM.ports_out.find((p) => p.name === e.from_port);
    const inPort = toM.ports_in.find((p) => p.name === e.to_port);
    if (!outPort || !inPort) {
      errors.push({ code: "PORT_UNKNOWN", message: `Bad ports on ${e.id}`, edge_id: e.id });
    } else if (outPort.type !== "Any" && inPort.type !== "Any" && outPort.type !== inPort.type) {
      errors.push({
        code: "PORT_TYPE_MISMATCH",
        message: `${outPort.type}→${inPort.type}`,
        edge_id: e.id,
      });
    }
  }
  const order = topoOrder(graph, errors);
  const kinds = graph.nodes.map((n) => n.node_kind);
  for (const k of REQUIRED) {
    if (!kinds.includes(k as NodeKind)) {
      errors.push({ code: "TOPOLOGY_MISMATCH", message: `Missing ${k}` });
    }
  }
  const executors = graph.nodes.filter((n) => getManifest(n.node_kind)?.runtime_binding === "MESH_EXECUTOR");
  const verifiers = graph.nodes.filter((n) => getManifest(n.node_kind)?.runtime_binding === "MESH_VERIFIER");
  for (const ex of executors) {
    const m = getManifest(ex.node_kind)!;
    if (!m.verifier_required) continue;
    const covered = graph.edges.some((e) => e.from_node === ex.id && verifiers.some((v) => v.id === e.to_node));
    if (!covered) {
      errors.push({ code: "VERIFIER_COVERAGE", message: `Executor ${ex.id} needs verifier`, node_id: ex.id });
    }
  }
  if (errors.length) return { ok: false, errors };

  const compiledNodes: CompiledNode[] = order.map((id, i) => {
    const n = nodeById.get(id)!;
    const m = getManifest(n.node_kind, n.manifest_version)!;
    return {
      id: n.id,
      node_kind: n.node_kind,
      manifest_version: n.manifest_version,
      runtime_binding: m.runtime_binding,
      config: n.config ?? {},
      verifier_required: m.verifier_required,
      order: i,
    };
  });
  const compiledEdges: CompiledEdge[] = graph.edges.map((e) => ({
    id: e.id,
    from_node: e.from_node,
    from_port: e.from_port,
    to_node: e.to_node,
    to_port: e.to_port,
    explicit_loop: Boolean(e.explicit_loop),
  }));
  const body = {
    plan_schema: "graph_studio_compiled_plan_v1" as const,
    blueprint_id: graph.blueprint_id,
    blueprint_version: graph.version,
    topology: "webpage_repair_l0_v1" as const,
    nodes: compiledNodes,
    edges: compiledEdges,
    executor_ids: executors.map((e) => e.id).sort(),
    verifier_ids: verifiers.map((v) => v.id).sort(),
  };
  const plan_hash = await hashObject(body);
  return { ok: true, plan: { ...body, plan_hash } };
}

export type NodeRunStatus = "PENDING" | "RUNNING" | "PASSED" | "FAILED" | "SKIPPED";

export function projectRunGraph(
  plan: CompiledExecutionPlan,
  mesh: { run_id: string; status: string; terminal: string | null } | null,
  graphRunId: string,
): {
  run_id: string;
  plan_hash: string;
  mesh_run_id: string | null;
  status: string;
  nodes: Array<{ id: string; node_kind: NodeKind; status: NodeRunStatus }>;
  child_runs: Array<{ child_id: string; parent_node_id: string; status: string }>;
} {
  const sorted = [...plan.nodes].sort((a, b) => a.order - b.order);
  const allPassed = mesh?.terminal === "ACCEPTED";
  const failed = Boolean(mesh?.terminal && mesh.terminal !== "ACCEPTED");
  return {
    run_id: graphRunId,
    plan_hash: plan.plan_hash,
    mesh_run_id: mesh?.run_id ?? null,
    status: mesh?.status ?? "PENDING",
    nodes: sorted.map((n) => ({
      id: n.id,
      node_kind: n.node_kind,
      status: (allPassed ? "PASSED" : failed ? "FAILED" : mesh ? "RUNNING" : "PENDING") as NodeRunStatus,
    })),
    child_runs: [],
  };
}
