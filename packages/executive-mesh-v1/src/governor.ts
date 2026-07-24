import { ecpLegalityForWebpageRepair } from "./ecp-bridge.ts";
import { hashObject } from "./hash.ts";
import type { ExecutiveRun, PlanGraphPacket, RoleDecisionPacket, WorkPacketMesh } from "./types.ts";
import { WEBPAGE_REPAIR_POLICY } from "./types.ts";

export type GovernorVerdict = "GREEN" | "AMBER" | "RED";

export interface GovernorCommitResult {
  verdict: GovernorVerdict;
  decision_id: string;
  decision_hash: string;
  reason_codes: string[];
}

/**
 * Wrap ECP v0 legality: GREEN only when Critic PASS, SG RECOMMEND, snapshot matches,
 * ECP kernel APPROVED/GREEN, and plan uses RUNWAY_GOAL_KERNEL with max_fanout 0.
 */
export function governorCommit(
  run: Pick<
    ExecutiveRun,
    "run_id" | "snapshot_version" | "role_packets" | "plan" | "stale_rejected" | "event" | "correlation_id"
  >,
  packets: RoleDecisionPacket[],
  plan: PlanGraphPacket | null,
  offeredSnapshot: number,
): GovernorCommitResult {
  const reasons: string[] = [];
  if (run.stale_rejected || offeredSnapshot !== run.snapshot_version) {
    reasons.push("STALE_SNAPSHOT");
  }
  const sg = packets.find((p) => p.role === "SG");
  const critic = packets.find((p) => p.role === "CRITIC");
  if (!sg || sg.conclusion !== "RECOMMEND") reasons.push("SG_NOT_RECOMMEND");
  if (!critic || critic.conclusion !== "PASS") reasons.push("CRITIC_NOT_PASS");
  if (!plan || plan.critic_status !== "PASSED") reasons.push("PLAN_NOT_CLEARED");
  if (plan && plan.recommended_runway !== "RUNWAY_GOAL_KERNEL") reasons.push("BAD_EXECUTOR");
  if (WEBPAGE_REPAIR_POLICY.body.limits.max_fanout !== 0) reasons.push("ILLEGAL_FANOUT_POLICY");
  for (const p of packets) {
    if (p.snapshot_version !== run.snapshot_version) reasons.push("STALE_PACKET");
  }

  const goalId = String(run.event.payload.goal_id ?? `goal_${run.run_id}`);
  const targetUrl = String(run.event.payload.target_url ?? run.event.payload.url ?? "");
  const ecp = ecpLegalityForWebpageRepair({
    goal_id: goalId,
    target_url: targetUrl,
    correlation_id: run.correlation_id,
  });
  if (ecp.zone !== "GREEN") {
    reasons.push("ECP_V0_NOT_GREEN", ...ecp.reason_codes);
  }

  if (reasons.length > 0) {
    return {
      verdict: "RED",
      decision_id: `dec_reject_${run.run_id}`,
      decision_hash: hashObject({ run_id: run.run_id, reasons }),
      reason_codes: reasons,
    };
  }

  const body = {
    run_id: run.run_id,
    snapshot_version: run.snapshot_version,
    decision_class: "WEBPAGE_REPAIR",
    policy_version: WEBPAGE_REPAIR_POLICY.policy_version,
    action: "COMPILE_WORK_PACKET",
    packet_hashes: packets.map((p) => p.packet_hash),
    ecp_decision_hash: ecp.ecp_result?.decision_hash ?? null,
  };
  return {
    verdict: "GREEN",
    decision_id: `dec_${run.run_id}`,
    decision_hash: hashObject(body),
    reason_codes: ["GOVERNOR_COMMIT_OK", ...ecp.reason_codes],
  };
}

export function compileNextAction(
  runId: string,
  decisionId: string,
  commitmentId: string,
  eventPayload: Record<string, unknown>,
  plan: PlanGraphPacket,
): WorkPacketMesh {
  const url = String(eventPayload.target_url ?? eventPayload.url ?? "");
  const goalId = String(eventPayload.goal_id ?? `goal_${runId}`);
  const limits = WEBPAGE_REPAIR_POLICY.body.limits;
  return {
    action_id: `wp_${runId}`,
    goal_id: goalId,
    decision_id: decisionId,
    commitment_id: commitmentId,
    why_now: plan.target_outcome,
    executor_class: "RUNWAY_GOAL_KERNEL",
    inputs: {
      target_url: url,
      workflow: WEBPAGE_REPAIR_POLICY.body.select.workflow,
      decision_class: "WEBPAGE_REPAIR",
      policy_version: WEBPAGE_REPAIR_POLICY.policy_version,
      acceptance_predicates: plan.acceptance_predicates,
    },
    allowed_capabilities: ["webpage_repair", "hdir_webpage_build_deploy"],
    forbidden_capabilities: ["fanout", "positioning_change", "protected_file_write"],
    acceptance_predicates: plan.acceptance_predicates,
    evidence_required: ["build_log", "visual_diff", "target_issue_absent"],
    budget: {
      max_attempts: limits.max_attempts,
      max_minutes: 30,
      max_cost_usd: 5,
      max_fanout: limits.max_fanout,
    },
    rollback_policy: "pre_deploy_checkpoint",
    failure_policy: "INCIDENT_THEN_BOUNDED_FAILURE",
    execution_idempotency_key: `exec_${runId}_${goalId}`,
  };
}
