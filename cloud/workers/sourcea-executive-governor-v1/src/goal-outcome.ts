export type GoalOutcome =
  | { kind: "PENDING"; goal_status: string; detail: string }
  | {
      kind: "ACCEPTED_ARTIFACT";
      goal_status: "PASSED";
      receipt_id: string;
      receipt_hash: string;
      passed_criteria: string[];
    }
  | { kind: "BOUNDED_FAILURE"; goal_status: string; reason: string }
  | { kind: "FOUNDER_DECISION_REQUIRED"; goal_status: "PARTIAL_PASS"; reason: string }
  | { kind: "INCIDENT"; goal_status: string; reason: string };

type GoalSnapshotLike = {
  goal_id?: unknown;
  status?: unknown;
  work_packet_terminal?: unknown;
  receipt_id?: unknown;
  receipt_hash?: unknown;
  acceptance_criteria?: unknown;
  acceptance_results?: unknown;
};

const PENDING_GOAL_STATES = new Set([
  "DRAFT",
  "READY",
  "RUNNING",
  "CHECKPOINTING",
  "WAITING_FOR_APPROVAL",
  "WAITING_FOR_EXTERNAL_EVENT",
  "BLOCKED",
  "PAUSED",
  "SLEEPING",
  "VERIFYING",
]);

const FAILED_GOAL_STATES = new Set([
  "FAILED",
  "BUDGET_EXHAUSTED",
  "TIME_EXHAUSTED",
  "CANCELLED",
]);

/**
 * Classify a canonical Runway Goal snapshot.
 *
 * A Goal's existence, READY state, workflow id, or HTTP 200 is not completion.
 * Success requires the Runway terminal, its accepted-artifact terminal, a
 * receipt identity/hash, and PASS for every required acceptance criterion.
 */
export function classifyGoalOutcome(
  value: unknown,
  expectedGoalId: string,
): GoalOutcome {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return { kind: "INCIDENT", goal_status: "UNKNOWN", reason: "goal_snapshot_invalid" };
  }

  const snapshot = value as GoalSnapshotLike;
  const goalId = typeof snapshot.goal_id === "string" ? snapshot.goal_id : "";
  const status = typeof snapshot.status === "string" ? snapshot.status : "UNKNOWN";

  if (!goalId || goalId !== expectedGoalId) {
    return { kind: "INCIDENT", goal_status: status, reason: "goal_identity_mismatch" };
  }

  if (status === "PASSED") {
    if (snapshot.work_packet_terminal !== "ACCEPTED_ARTIFACT") {
      return { kind: "INCIDENT", goal_status: status, reason: "accepted_artifact_terminal_missing" };
    }

    const receiptId = typeof snapshot.receipt_id === "string" ? snapshot.receipt_id : "";
    const receiptHash = typeof snapshot.receipt_hash === "string" ? snapshot.receipt_hash : "";
    if (!receiptId || !/^([a-f0-9]{64}|sha256:[a-f0-9]{64})$/i.test(receiptHash)) {
      return { kind: "INCIDENT", goal_status: status, reason: "verified_receipt_missing" };
    }

    if (!Array.isArray(snapshot.acceptance_criteria) || !Array.isArray(snapshot.acceptance_results)) {
      return { kind: "INCIDENT", goal_status: status, reason: "acceptance_evidence_missing" };
    }

    const required = snapshot.acceptance_criteria.filter(
      (criterion: unknown) =>
        Boolean(criterion) &&
        typeof criterion === "object" &&
        (criterion as { required?: unknown }).required === true,
    ) as Array<{ id?: unknown }>;

    if (required.length === 0) {
      return { kind: "INCIDENT", goal_status: status, reason: "required_acceptance_criteria_missing" };
    }

    const passedIds = new Set(
      snapshot.acceptance_results
        .filter(
          (result: unknown) =>
            Boolean(result) &&
            typeof result === "object" &&
            (result as { status?: unknown }).status === "PASS",
        )
        .map((result: unknown) => (result as { id?: unknown }).id)
        .filter((id: unknown): id is string => typeof id === "string"),
    );

    const missing = required
      .map((criterion) => criterion.id)
      .filter((id: unknown) => typeof id !== "string" || !passedIds.has(id));

    if (missing.length > 0) {
      return {
        kind: "INCIDENT",
        goal_status: status,
        reason: "required_acceptance_criteria_not_passed:" + missing.map(String).join(","),
      };
    }

    return {
      kind: "ACCEPTED_ARTIFACT",
      goal_status: "PASSED",
      receipt_id: receiptId,
      receipt_hash: receiptHash,
      passed_criteria: required.map((criterion) => String(criterion.id)),
    };
  }

  if (status === "PARTIAL_PASS") {
    return {
      kind: "FOUNDER_DECISION_REQUIRED",
      goal_status: "PARTIAL_PASS",
      reason: "partial_pass_requires_founder_decision",
    };
  }

  if (FAILED_GOAL_STATES.has(status)) {
    return { kind: "BOUNDED_FAILURE", goal_status: status, reason: "runway_goal_terminal_failure" };
  }

  if (PENDING_GOAL_STATES.has(status) || status === "UNKNOWN") {
    return { kind: "PENDING", goal_status: status, detail: "goal_not_terminal" };
  }

  return { kind: "PENDING", goal_status: status, detail: "unrecognized_goal_state_fail_closed" };
}
