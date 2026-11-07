import { classifyGoalOutcome, type GoalOutcome } from "./goal-outcome.ts";
import type { WorkPacketMesh } from "./types.ts";

export interface RunwayGoalAdmitResult {
  admitted: boolean;
  goal_ref: string;
  status: "ADMITTED" | "REJECTED" | "DOCUMENT_STUB";
  detail: string;
  snapshot?: Record<string, unknown>;
}

export type RunwayRouter = (wp: WorkPacketMesh) => Promise<RunwayGoalAdmitResult>;

export interface RunwayVerificationResult {
  valid: boolean;
  pending?: boolean;
  evidence_id: string;
  detail: string;
  goal_status?: string;
  outcome?: GoalOutcome;
  receipt_id?: string;
  receipt_hash?: string;
}

/** Document-only stubs for non-slice-1 executors. */
export function documentStubRouter(wp: WorkPacketMesh): Promise<RunwayGoalAdmitResult> {
  return Promise.resolve({
    admitted: false,
    goal_ref: wp.goal_id,
    status: "DOCUMENT_STUB",
    detail: `executor_class ${wp.executor_class} not required for slice-1 E2E`,
  });
}

/** Map mesh WorkPacket → live Goal API contract (title + objective required). */
export function toRunwayGoalBody(wp: WorkPacketMesh): Record<string, unknown> {
  const url = String(wp.inputs.target_url ?? "");
  const decisionClass = String(wp.inputs.decision_class ?? "WEBPAGE_REPAIR");
  return {
    title: `Executive Mesh ${decisionClass}`.slice(0, 80),
    objective: `Repair webpage ${url} under ${decisionClass} policy ${String(wp.inputs.policy_version ?? "")}; acceptance: ${wp.acceptance_predicates.join(", ")}`,
    project_id: `mesh_${wp.action_id}`.replace(/[^a-zA-Z0-9_]/g, "_").slice(0, 40),
    force_repair_once: true,
    approved_for_runtime: false,
    sleep_seconds: 30,
    priority: 50,
    mesh: {
      work_packet_action_id: wp.action_id,
      decision_id: wp.decision_id,
      commitment_id: wp.commitment_id,
      decision_class: decisionClass,
      policy_version: wp.inputs.policy_version,
      target_url: url,
      max_fanout: wp.budget.max_fanout,
      execution_idempotency_key: wp.execution_idempotency_key,
      acceptance_predicates: wp.acceptance_predicates,
    },
  };
}

/**
 * Route one WorkPacket to Runway, then start Runway's existing durable Goal
 * Pursuit Workflow. Admission is not completion. The returned Goal is tracked
 * until PASSED + ACCEPTED_ARTIFACT + all required predicates + receipt verify.
 */
export function createRunwayGoalKernelRouter(opts?: {
  baseUrl?: string;
  fetchImpl?: typeof fetch;
  simulate?: boolean;
  tenantId?: string;
}): RunwayRouter {
  const baseUrl = opts?.baseUrl ?? process.env.RUNWAY_GOAL_BASE_URL ?? "";
  const fetchImpl = opts?.fetchImpl ?? fetch;
  const simulate = opts?.simulate ?? !baseUrl;
  const tenantId = opts?.tenantId ?? process.env.RUNWAY_TENANT_ID ?? "tenant-runway-staging";

  return async (wp: WorkPacketMesh): Promise<RunwayGoalAdmitResult> => {
    if (wp.executor_class !== "RUNWAY_GOAL_KERNEL") return documentStubRouter(wp);
    if (wp.budget.max_fanout !== 0) {
      return {
        admitted: false,
        goal_ref: wp.goal_id,
        status: "REJECTED",
        detail: "ILLEGAL_FANOUT",
      };
    }
    const body = toRunwayGoalBody(wp);
    if (simulate) {
      return {
        admitted: true,
        goal_ref: `sim://${wp.goal_id}`,
        status: "ADMITTED",
        detail: "local_admit_simulator_only_not_execution",
      };
    }

    const base = baseUrl.replace(/\/$/, "");
    const headers = { "content-type": "application/json", "x-tenant-id": tenantId };
    const res = await fetchImpl(`${base}/v1/goals`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      return {
        admitted: false,
        goal_ref: wp.goal_id,
        status: "REJECTED",
        detail: `http_${res.status}:${errText.slice(0, 200)}`,
      };
    }
    const json = (await res.json()) as Record<string, unknown>;
    const goalId = String(json.goal_id ?? json.id ?? "");
    if (!goalId) {
      return {
        admitted: false,
        goal_ref: wp.goal_id,
        status: "REJECTED",
        detail: "GOAL_ID_MISSING",
      };
    }

    const started = await fetchImpl(`${base}/v1/goals/${encodeURIComponent(goalId)}/start`, {
      method: "POST",
      headers,
    });
    if (!started.ok) {
      const detail = await started.text().catch(() => "");
      try {
        await fetchImpl(`${base}/v1/goals/${encodeURIComponent(goalId)}/kill`, {
          method: "POST",
          headers: { "x-tenant-id": tenantId },
        });
      } catch {
        // Preserve original start failure. A failed cleanup is not acceptance.
      }
      return {
        admitted: false,
        goal_ref: goalId,
        status: "REJECTED",
        detail: `GOAL_START_FAILED:${started.status}:${detail.slice(0, 160)}`,
      };
    }
    const startSnapshot = await started.json().catch(() => ({})) as Record<string, unknown>;
    return {
      admitted: true,
      goal_ref: goalId,
      status: "ADMITTED",
      detail: "runway_goal_api+goal_pursuit_started",
      snapshot: startSnapshot,
    };
  };
}

/** Independent live verification. Goal presence/READY/HTTP 200 is never PASS. */
export async function independentVerifyLive(
  wp: WorkPacketMesh,
  admit: RunwayGoalAdmitResult,
  producerModelId: string,
  opts?: { baseUrl?: string; fetchImpl?: typeof fetch; tenantId?: string },
): Promise<RunwayVerificationResult> {
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

  const baseUrl = opts?.baseUrl ?? process.env.RUNWAY_GOAL_BASE_URL ?? "";
  if (!baseUrl || admit.goal_ref.startsWith("sim://")) {
    return {
      valid: false,
      pending: true,
      evidence_id: `ev_pending_${wp.action_id}`,
      goal_status: "SIMULATED",
      detail: "SIMULATION_CANNOT_PROVE_EXECUTION",
    };
  }

  const fetchImpl = opts?.fetchImpl ?? fetch;
  const tenantId = opts?.tenantId ?? process.env.RUNWAY_TENANT_ID ?? "tenant-runway-staging";
  const headers = { "x-tenant-id": tenantId };
  const res = await fetchImpl(`${baseUrl.replace(/\/$/, "")}/v1/goals/${encodeURIComponent(admit.goal_ref)}`, {
    headers,
  });
  if (!res.ok) {
    return {
      valid: false,
      evidence_id: `ev_live_fail_${wp.action_id}`,
      detail: `live_get_http_${res.status}`,
    };
  }
  const snap = await res.json();
  const outcome = classifyGoalOutcome(snap, admit.goal_ref);
  if (outcome.kind === "PENDING") {
    return {
      valid: false,
      pending: true,
      evidence_id: `ev_pending_${wp.action_id}`,
      goal_status: outcome.goal_status,
      detail: outcome.detail,
      outcome,
    };
  }
  if (outcome.kind !== "ACCEPTED_ARTIFACT") {
    return {
      valid: false,
      evidence_id: `ev_terminal_fail_${wp.action_id}`,
      goal_status: outcome.goal_status,
      detail: "reason" in outcome ? outcome.reason : outcome.kind,
      outcome,
    };
  }

  const receiptVerify = await fetchImpl(
    `${baseUrl.replace(/\/$/, "")}/v1/goals/${encodeURIComponent(admit.goal_ref)}/verify`,
    { method: "POST", headers },
  );
  if (!receiptVerify.ok) {
    return {
      valid: false,
      evidence_id: `ev_receipt_fail_${wp.action_id}`,
      goal_status: outcome.goal_status,
      detail: `receipt_verify_http_${receiptVerify.status}`,
      outcome,
    };
  }
  const verified = (await receiptVerify.json()) as Record<string, unknown>;
  const valid = verified.passed === true && verified.receipt_id === outcome.receipt_id;
  return {
    valid,
    evidence_id: valid ? `ev_live_${wp.action_id}` : `ev_receipt_fail_${wp.action_id}`,
    goal_status: outcome.goal_status,
    receipt_id: outcome.receipt_id,
    receipt_hash: outcome.receipt_hash,
    detail: valid
      ? `verified_by=${verifierId};goal=${admit.goal_ref};receipt=${outcome.receipt_id}`
      : "RUNWAY_RECEIPT_VERIFY_FAILED",
    outcome,
  };
}

/** Legacy offline verifier retained for diagnostics only. */
export function independentVerify(
  wp: WorkPacketMesh,
  admit: RunwayGoalAdmitResult,
  producerModelId: string,
): { valid: boolean; evidence_id: string; detail: string } {
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
  return {
    valid: false,
    evidence_id: `ev_pending_${wp.action_id}`,
    detail: "GOAL_ADMISSION_IS_NOT_COMPLETION",
  };
}
