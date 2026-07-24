import type { CompiledExecutionPlan } from "./types.ts";
import { assertPlanHash } from "./compiler.ts";

export interface MeshEventLike {
  event_id: string;
  event_type: string;
  schema_version: string;
  organization_id: string;
  correlation_id: string;
  causation_id: string | null;
  idempotency_key: string;
  producer: string;
  produced_at: string;
  payload: Record<string, unknown>;
  canonical_state_version?: number;
}

export interface MeshPipelineLike {
  ingest(raw: MeshEventLike): Promise<{
    run_id: string;
    status: string;
    terminal: string | null;
    audit: Array<{ at: string; kind: string; detail: Record<string, unknown> }>;
    digest?: Record<string, unknown> | null;
  }>;
}

export interface PinnedPlanStore {
  getPlan(plan_hash: string): CompiledExecutionPlan | undefined;
}

/**
 * Load frozen plan by hash, assert integrity + webpage-repair topology,
 * then invoke Executive Mesh ingest. Does not interpret a generic graph.
 */
export async function executePinnedPlan(
  plan_hash: string,
  event: MeshEventLike,
  opts: { store: PinnedPlanStore; mesh: MeshPipelineLike },
): Promise<{
  ok: boolean;
  plan_hash: string;
  mesh_run_id: string | null;
  status: string;
  terminal: string | null;
  detail?: string;
  audit?: Array<{ at: string; kind: string; detail: Record<string, unknown> }>;
  digest?: Record<string, unknown> | null;
}> {
  const plan = opts.store.getPlan(plan_hash);
  if (!plan) {
    return {
      ok: false,
      plan_hash,
      mesh_run_id: null,
      status: "BOUNDED_FAILURE",
      terminal: "BOUNDED_FAILURE",
      detail: "PLAN_NOT_FOUND",
    };
  }
  if (plan.plan_hash !== plan_hash || !assertPlanHash(plan)) {
    return {
      ok: false,
      plan_hash,
      mesh_run_id: null,
      status: "BOUNDED_FAILURE",
      terminal: "BOUNDED_FAILURE",
      detail: "PLAN_HASH_MISMATCH",
    };
  }
  if (plan.topology !== "webpage_repair_l0_v1") {
    return {
      ok: false,
      plan_hash,
      mesh_run_id: null,
      status: "BOUNDED_FAILURE",
      terminal: "BOUNDED_FAILURE",
      detail: "TOPOLOGY_NOT_SUPPORTED",
    };
  }

  const run = await opts.mesh.ingest(event);
  return {
    ok: run.terminal === "ACCEPTED",
    plan_hash,
    mesh_run_id: run.run_id,
    status: run.status,
    terminal: run.terminal,
    audit: run.audit,
    digest: run.digest ?? null,
  };
}

export class MemoryPlanStore implements PinnedPlanStore {
  private plans = new Map<string, CompiledExecutionPlan>();

  put(plan: CompiledExecutionPlan): void {
    this.plans.set(plan.plan_hash, { ...plan, frozen_at: plan.frozen_at ?? new Date().toISOString() });
  }

  getPlan(plan_hash: string): CompiledExecutionPlan | undefined {
    return this.plans.get(plan_hash);
  }
}
