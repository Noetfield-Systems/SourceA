/**
 * Bridge: mesh Governor wraps ECP v0 for commit legality (GREEN/AMBER/RED).
 * Role Pods recommend; only Governor + ECP kernel authorize commit.
 */

import {
  addGoal,
  createInitialState,
  executiveDecide,
  resetProviders,
  type DecisionResult,
  type GoalContract,
} from "../../executive-control-plane-v0/src/index.ts";

function repairGoal(goalId: string, targetUrl: string): Omit<
  GoalContract,
  "schema" | "created_at" | "updated_at" | "source_decision_ids"
> {
  return {
    goal_id: goalId,
    version: "1",
    authority_hash: `auth_${goalId}`,
    intent: `Repair webpage ${targetUrl}`,
    decision_class: "WEBPAGE_REPAIR",
    status: "ACTIVE",
    scope_allowlist: ["apps/**", "sites/**"],
    forbidden_effects: ["write:governance/**", "positioning_change", "fanout"],
    acceptance_predicates: [
      "build_passes",
      "visual_diff_present",
      "target_issue_absent",
      "unrelated_pages_unchanged",
    ],
    evidence_required: ["build_log", "visual_diff", "target_issue_absent"],
    budgets: {
      max_attempts: 2,
      max_minutes: 30,
      max_cost_usd: 5,
      max_fanout: 0,
      max_human_tax_units: 5,
    },
  };
}

export function ecpLegalityForWebpageRepair(input: {
  goal_id: string;
  target_url: string;
  correlation_id: string;
}): { zone: "GREEN" | "AMBER" | "RED"; reason_codes: string[]; ecp_result: DecisionResult | null } {
  resetProviders();
  let state = createInitialState();
  state = addGoal(state, repairGoal(input.goal_id, input.target_url));
  const { result } = executiveDecide(state, {
    type: "TASK_REQUEST",
    goal_id: input.goal_id,
    decision_class: "WEBPAGE_REPAIR",
    intent: `repair ${input.target_url}`,
    reversible: true,
    scope_paths: ["apps/**"],
  });

  if (!result || result.status !== "APPROVED" || result.zone === "RED") {
    return {
      zone: "RED",
      reason_codes: ["ECP_V0_REJECT", result?.status ?? "NO_RESULT"],
      ecp_result: result,
    };
  }
  if (result.zone === "AMBER") {
    return { zone: "AMBER", reason_codes: ["ECP_V0_AMBER"], ecp_result: result };
  }
  return {
    zone: "GREEN",
    reason_codes: ["ECP_V0_WRAP_OK", result.policy_version],
    ecp_result: result,
  };
}
