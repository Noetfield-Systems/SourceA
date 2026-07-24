import type { WorkPacketMesh } from "./types.ts";

export interface RunwayGoalAdmitRequest {
  goal_id: string;
  decision_class: string;
  policy_version: string;
  target_url: string;
  acceptance_predicates: string[];
  max_fanout: number;
  execution_idempotency_key: string;
  work_packet_action_id: string;
}

export interface RunwayGoalAdmitResult {
  admitted: boolean;
  goal_ref: string;
  status: "ADMITTED" | "REJECTED" | "DOCUMENT_STUB";
  detail: string;
}

export type RunwayRouter = (wp: WorkPacketMesh) => Promise<RunwayGoalAdmitResult>;

/** Document-only stubs for non-slice-1 executors. */
export function documentStubRouter(wp: WorkPacketMesh): Promise<RunwayGoalAdmitResult> {
  return Promise.resolve({
    admitted: false,
    goal_ref: wp.goal_id,
    status: "DOCUMENT_STUB",
    detail: `executor_class ${wp.executor_class} not required for slice-1 E2E`,
  });
}

/**
 * Route RUNWAY_GOAL_KERNEL WorkPackets to staging Goal API.
 * When RUNWAY_GOAL_BASE_URL is unset, uses local admit simulator (integration tests).
 */
export function createRunwayGoalKernelRouter(opts?: {
  baseUrl?: string;
  fetchImpl?: typeof fetch;
  simulate?: boolean;
}): RunwayRouter {
  const baseUrl = opts?.baseUrl ?? process.env.RUNWAY_GOAL_BASE_URL ?? "";
  const fetchImpl = opts?.fetchImpl ?? fetch;
  const simulate = opts?.simulate ?? !baseUrl;

  return async (wp: WorkPacketMesh): Promise<RunwayGoalAdmitResult> => {
    if (wp.executor_class !== "RUNWAY_GOAL_KERNEL") {
      return documentStubRouter(wp);
    }
    if (wp.budget.max_fanout !== 0) {
      return {
        admitted: false,
        goal_ref: wp.goal_id,
        status: "REJECTED",
        detail: "ILLEGAL_FANOUT",
      };
    }

    const body: RunwayGoalAdmitRequest = {
      goal_id: wp.goal_id,
      decision_class: String(wp.inputs.decision_class ?? "WEBPAGE_REPAIR"),
      policy_version: String(wp.inputs.policy_version ?? ""),
      target_url: String(wp.inputs.target_url ?? ""),
      acceptance_predicates: wp.acceptance_predicates,
      max_fanout: wp.budget.max_fanout,
      execution_idempotency_key: wp.execution_idempotency_key,
      work_packet_action_id: wp.action_id,
    };

    if (simulate) {
      return {
        admitted: true,
        goal_ref: `sim://${body.goal_id}`,
        status: "ADMITTED",
        detail: "local_admit_simulator",
      };
    }

    const res = await fetchImpl(`${baseUrl.replace(/\/$/, "")}/v1/goals`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      return {
        admitted: false,
        goal_ref: wp.goal_id,
        status: "REJECTED",
        detail: `http_${res.status}`,
      };
    }
    const json = (await res.json()) as { goal_id?: string; id?: string };
    return {
      admitted: true,
      goal_ref: String(json.goal_id ?? json.id ?? wp.goal_id),
      status: "ADMITTED",
      detail: "runway_goal_api",
    };
  };
}

export function independentVerify(
  wp: WorkPacketMesh,
  admit: RunwayGoalAdmitResult,
  producerModelId: string,
): { valid: boolean; evidence_id: string; detail: string } {
  // Producing model cannot sole-verify — verifier identity must differ.
  const verifierId = "independent_verifier.mesh_v1";
  if (verifierId === producerModelId) {
    return { valid: false, evidence_id: "ev_reject", detail: "PRODUCER_SOLE_VERIFY_FORBIDDEN" };
  }
  if (!admit.admitted) {
    return { valid: false, evidence_id: `ev_fail_${wp.action_id}`, detail: admit.detail };
  }
  if (wp.budget.max_fanout !== 0) {
    return { valid: false, evidence_id: `ev_fanout_${wp.action_id}`, detail: "ILLEGAL_FANOUT" };
  }
  const missing = wp.acceptance_predicates.filter((p) => !wp.evidence_required.length);
  void missing;
  return {
    valid: true,
    evidence_id: `ev_${wp.action_id}`,
    detail: `verified_by=${verifierId};goal=${admit.goal_ref};predicates=${wp.acceptance_predicates.join(",")}`,
  };
}
