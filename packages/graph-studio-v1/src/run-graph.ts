import type { CompiledExecutionPlan, NodeRunStatus, RunGraph, RunGraphNode } from "./types.ts";

export interface MeshRunSnapshot {
  run_id: string;
  status: string;
  terminal: string | null;
  audit: Array<{ at: string; kind: string; detail?: Record<string, unknown> }>;
}

const KIND_TO_AUDIT: Record<string, string[]> = {
  EventIngest: ["RECEIVED", "SNAPSHOT_LOCKED"],
  RolePod_SG: ["ROLE_DELIBERATION", "SG"],
  RolePod_MemorySteward: ["CONTEXT_PACK", "MEMORY"],
  RolePod_Planner: ["PLANNER", "ROLE_DELIBERATION"],
  RolePod_Critic: ["CRITIC"],
  Governor: ["GOVERNOR", "GOVERNOR_DECIDED", "ACTION_COMPILED"],
  Executor_RunwayGoalKernel: ["EXECUTING", "EXECUTOR"],
  IndependentVerifier: ["VERIFY", "VERIFYING"],
  CanonicalCommit: ["COMMIT", "CANONICAL"],
  Digest: ["DIGEST", "FINALIZE"],
};

function statusFromMesh(
  nodeKind: string,
  mesh: MeshRunSnapshot,
  orderIndex: number,
  total: number,
): NodeRunStatus {
  const terminalFail =
    mesh.terminal === "BOUNDED_FAILURE" ||
    mesh.terminal === "INCIDENT" ||
    mesh.terminal === "DEFERRED_BY_POLICY" ||
    mesh.terminal === "FOUNDER_DECISION_REQUIRED";

  if (mesh.terminal === "ACCEPTED") return "PASSED";

  const auditKinds = new Set(mesh.audit.map((a) => a.kind.toUpperCase()));
  const markers = (KIND_TO_AUDIT[nodeKind] ?? []).map((m) => m.toUpperCase());
  const hit = markers.some((m) => [...auditKinds].some((k) => k.includes(m)));

  if (terminalFail) {
    // nodes that already ran → PASSED; current → FAILED; later → SKIPPED
    if (hit) return "PASSED";
    // approximate: if mesh status name matches this stage, FAILED
    const st = mesh.status.toUpperCase();
    if (markers.some((m) => st.includes(m))) return "FAILED";
    // order heuristic vs progress
    const progress = Math.min(mesh.audit.length, total);
    if (orderIndex < progress) return "PASSED";
    if (orderIndex === progress) return "FAILED";
    return "SKIPPED";
  }

  if (hit) return "PASSED";
  const st = mesh.status.toUpperCase();
  if (markers.some((m) => st.includes(m))) return "RUNNING";
  const progress = Math.min(mesh.audit.length, total);
  if (orderIndex < progress) return "PASSED";
  if (orderIndex === progress) return "RUNNING";
  return "PENDING";
}

/** Project mesh run status + audit onto per-node Run Graph statuses. */
export function projectRunGraph(
  plan: CompiledExecutionPlan,
  mesh: MeshRunSnapshot | null,
  graphRunId: string,
): RunGraph {
  const sorted = [...plan.nodes].sort((a, b) => a.order - b.order);
  const nodes: RunGraphNode[] = sorted.map((n, i) => {
    if (!mesh) {
      return { id: n.id, node_kind: n.node_kind, status: "PENDING" };
    }
    return {
      id: n.id,
      node_kind: n.node_kind,
      status: statusFromMesh(n.node_kind, mesh, i, sorted.length),
    };
  });

  const child_runs = (mesh?.audit ?? [])
    .filter((a) => a.kind.toUpperCase().includes("ROLE") || a.detail?.role_run_id)
    .map((a, idx) => ({
      child_id: String(a.detail?.role_run_id ?? `child_${idx}`),
      parent_node_id: sorted.find((n) => n.node_kind.startsWith("RolePod_"))?.id ?? sorted[0]?.id ?? "",
      status: "VISIBLE",
    }));

  return {
    run_id: graphRunId,
    plan_hash: plan.plan_hash,
    mesh_run_id: mesh?.run_id ?? null,
    status: mesh?.status ?? "PENDING",
    nodes,
    child_runs,
  };
}
