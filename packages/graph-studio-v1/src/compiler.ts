import { WEBPAGE_REPAIR_REQUIRED_KINDS } from "./blueprints/webpage_repair_l0_v1.ts";
import { hashObject } from "./hash.ts";
import { getManifest } from "./registry/slice1.ts";
import type {
  BlueprintGraph,
  CompileError,
  CompileResult,
  CompiledEdge,
  CompiledExecutionPlan,
  CompiledNode,
  NodeKind,
} from "./types.ts";

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
      errors.push({ code: "EDGE_UNKNOWN_NODE", message: `Edge ${e.id} references unknown node`, edge_id: e.id });
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
    errors.push({
      code: "CYCLE_WITHOUT_EXPLICIT_LOOP",
      message: "Graph has a cycle; only Explicit Loop edges may form cycles",
    });
  }
  return order;
}

function assertWebpageRepairTopology(kinds: NodeKind[], errors: CompileError[]): void {
  const required = [...WEBPAGE_REPAIR_REQUIRED_KINDS];
  for (const k of required) {
    if (!kinds.includes(k as NodeKind)) {
      errors.push({
        code: "TOPOLOGY_MISMATCH",
        message: `Slice-1 webpage-repair requires node_kind ${k}`,
      });
    }
  }
  const extras = kinds.filter((k) => !(required as readonly string[]).includes(k) && k !== "CompositeRolePod");
  if (extras.length) {
    errors.push({
      code: "TOPOLOGY_EXTRA",
      message: `Slice-1 rejects extra kinds: ${extras.join(",")}`,
    });
  }
}

function subflowDepth(node: BlueprintGraph["nodes"][number], depth: number, errors: CompileError[]): void {
  if (!node.subflow) return;
  if (depth > 1) {
    errors.push({
      code: "COMPOSITE_DEPTH",
      message: "max_subflow_depth=1 exceeded",
      node_id: node.id,
    });
    return;
  }
  for (const child of node.subflow.nodes) {
    subflowDepth(child, depth + 1, errors);
  }
}

/** Strip any accidental layout keys before compile (defense in depth). */
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
      ...(n.subflow ? { subflow: stripLayout(n.subflow) } : {}),
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

export function compileBlueprint(raw: BlueprintGraph): CompileResult {
  const errors: CompileError[] = [];
  const pollution = hasLayoutPollution(raw);
  if (pollution) {
    errors.push({
      code: "LAYOUT_POLLUTION",
      message: `Layout/visual field not allowed in Blueprint Graph: ${pollution}`,
    });
  }

  const graph = stripLayout(raw);
  if (!graph.blueprint_id || !graph.version || !graph.nodes?.length) {
    errors.push({ code: "SCHEMA", message: "blueprint_id, version, and nodes are required" });
  }

  const nodeById = new Map(graph.nodes.map((n) => [n.id, n]));
  if (nodeById.size !== graph.nodes.length) {
    errors.push({ code: "DUPLICATE_NODE_ID", message: "Duplicate node ids" });
  }

  for (const n of graph.nodes) {
    const manifest = getManifest(n.node_kind, n.manifest_version);
    if (!manifest) {
      errors.push({
        code: "UNKNOWN_NODE_KIND",
        message: `Unknown node_kind/version: ${n.node_kind}@${n.manifest_version}`,
        node_id: n.id,
      });
      continue;
    }
    if (n.node_kind === "CompositeRolePod") {
      const bounds = manifest.composite;
      if (!bounds) {
        errors.push({ code: "COMPOSITE_BOUNDS", message: "Composite missing bounds", node_id: n.id });
      }
      subflowDepth(n, 0, errors);
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
    if (!outPort) {
      errors.push({
        code: "PORT_UNKNOWN",
        message: `Unknown out port ${e.from_port} on ${from.node_kind}`,
        edge_id: e.id,
      });
    }
    if (!inPort) {
      errors.push({
        code: "PORT_UNKNOWN",
        message: `Unknown in port ${e.to_port} on ${to.node_kind}`,
        edge_id: e.id,
      });
    }
    if (outPort && inPort && outPort.type !== "Any" && inPort.type !== "Any" && outPort.type !== inPort.type) {
      errors.push({
        code: "PORT_TYPE_MISMATCH",
        message: `${outPort.type} → ${inPort.type} on edge ${e.id}`,
        edge_id: e.id,
      });
    }
  }

  const order = topoOrder(graph, errors);
  const kinds = graph.nodes.map((n) => n.node_kind);
  assertWebpageRepairTopology(kinds, errors);

  const executors = graph.nodes.filter((n) => getManifest(n.node_kind)?.runtime_binding === "MESH_EXECUTOR");
  const verifiers = graph.nodes.filter((n) => getManifest(n.node_kind)?.runtime_binding === "MESH_VERIFIER");

  for (const ex of executors) {
    const manifest = getManifest(ex.node_kind)!;
    if (!manifest.verifier_required) continue;
    const covered = graph.edges.some(
      (e) => e.from_node === ex.id && verifiers.some((v) => v.id === e.to_node),
    );
    if (!covered) {
      errors.push({
        code: "VERIFIER_COVERAGE",
        message: `Executor ${ex.id} requires IndependentVerifier on outbound edge`,
        node_id: ex.id,
      });
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

  const plan_hash = hashObject(body);
  const plan: CompiledExecutionPlan = { ...body, plan_hash };
  return { ok: true, plan };
}

export function assertPlanHash(plan: CompiledExecutionPlan): boolean {
  const { plan_hash: _h, frozen_at: _f, ...body } = plan;
  return hashObject(body) === plan.plan_hash;
}
