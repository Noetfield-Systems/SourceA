import assert from "node:assert/strict";
import { test, beforeEach } from "node:test";
import {
  addGoal,
  closeCommitment,
  compileNextAction,
  createFounderDecisionPacket,
  createInitialState,
  detectConflicts,
  detectDrift,
  ingestEvent,
  recordEvidence,
  resetProviders,
  resolveConflict,
  verifyOutcome,
} from "../src/index.ts";
import type { GoalContract } from "../src/types.ts";

function baseGoal(overrides: Partial<GoalContract> = {}): Omit<
  GoalContract,
  "schema" | "created_at" | "updated_at" | "source_decision_ids"
> {
  return {
    goal_id: "goal_18",
    version: "1",
    authority_hash: "auth_goal_18",
    intent: "Repair one webpage",
    decision_class: "WEBPAGE_REPAIR",
    status: "ACTIVE",
    scope_allowlist: ["apps/site/page-x/**"],
    forbidden_effects: ["write:governance/**"],
    acceptance_predicates: ["target issue removed", "build passes"],
    evidence_required: ["git_diff", "test_result"],
    budgets: {
      max_attempts: 2,
      max_minutes: 30,
      max_cost_usd: 1.5,
      max_fanout: 0,
      max_human_tax_units: 5,
    },
    ...overrides,
  };
}

beforeEach(() => {
  resetProviders();
});

test("1. same state event policy version produce same decision hash", () => {
  let s = createInitialState();
  s = addGoal(s, baseGoal());
  const event = {
    type: "TASK_REQUEST" as const,
    goal_id: "goal_18",
    decision_class: "WEBPAGE_REPAIR",
    intent: "repair page",
    reversible: true,
  };
  const a = ingestEvent(s, event);
  const b = ingestEvent(s, event);
  assert.ok(a.last_decision_result);
  assert.ok(b.last_decision_result);
  assert.equal(a.last_decision_result!.decision_hash, b.last_decision_result!.decision_hash);
  assert.equal(a.last_decision_result!.status, "APPROVED");
});

test("2. task with no active Goal Contract is rejected", () => {
  const s0 = createInitialState();
  const s = ingestEvent(s0, {
    type: "TASK_REQUEST",
    goal_id: "goal_missing",
    decision_class: "WEBPAGE_REPAIR",
    intent: "orphan task",
  });
  assert.equal(s.last_decision_result!.status, "REJECTED");
  assert.ok(s.incidents.some((i) => i.reason === "NO_ACTIVE_GOAL"));
});

test("3. work unrelated to active goal creates GOAL_DRIFT", () => {
  let s = createInitialState();
  s = addGoal(s, baseGoal());
  s = ingestEvent(s, {
    type: "TASK_REQUEST",
    goal_id: "goal_other",
    decision_class: "WEBPAGE_REPAIR",
    intent: "unrelated redesign",
  });
  // goal_other does not exist → NO_ACTIVE_GOAL; force drift path by inactive goal
  s = createInitialState();
  s = addGoal(s, baseGoal({ status: "ACHIEVED" }));
  s = ingestEvent(s, {
    type: "TASK_REQUEST",
    goal_id: "goal_18",
    decision_class: "WEBPAGE_REPAIR",
    intent: "work on achieved goal",
  });
  assert.ok(detectDrift(s).some((d) => d.drift_kind === "GOAL_DRIFT"));
});

test("4. known low-risk reversible task produces GREEN WorkPacket", () => {
  let s = createInitialState();
  s = addGoal(s, baseGoal({ decision_class: "WEBPAGE_CHANGE", intent: "edit page copy" }));
  s = ingestEvent(s, {
    type: "TASK_REQUEST",
    goal_id: "goal_18",
    decision_class: "WEBPAGE_CHANGE",
    intent: "edit page copy",
    reversible: true,
  });
  assert.equal(s.last_decision_result!.zone, "GREEN");
  assert.equal(s.last_decision_result!.status, "APPROVED");
  const { state, packet } = compileNextAction(s, s.last_decision_result!.decision!);
  assert.equal(packet.schema, "noetfield.executive.work_packet.v0");
  assert.equal(packet.budget.max_fanout, 0);
  assert.ok(packet.forbidden_capabilities.includes("spawn:subagents"));
  assert.ok(state.work_packets.length >= 1);
});

test("5. irreversible or governance-changing task produces RED_ZONE_REQUIRED", () => {
  let s = createInitialState();
  s = addGoal(s, baseGoal());
  s = ingestEvent(s, {
    type: "TASK_REQUEST",
    goal_id: "goal_18",
    decision_class: "WEBPAGE_REPAIR",
    intent: "rewrite positioning",
    irreversible: true,
    governance_change: true,
  });
  assert.equal(s.last_decision_result!.status, "RED_ZONE_REQUIRED");
  assert.ok(s.last_decision_result!.founder_packet_id);
});

test("6. model proposal cannot mutate canonical state directly", () => {
  let s = createInitialState();
  s = addGoal(s, baseGoal());
  const beforeGoals = JSON.stringify(s.goals);
  const beforePolicies = JSON.stringify(s.policies);
  s = ingestEvent(s, {
    type: "PLAN_PROPOSAL",
    plan: {
      plan_id: "plan_204",
      goal_id: "goal_18",
      assumptions: ["x"],
      candidate_actions: ["mutate_goal_intent"],
      risks: [],
      success_predicates: [],
      founder_decisions_required: [],
      source_decision_ids: [],
    },
  });
  assert.equal(JSON.stringify(s.goals), beforeGoals);
  assert.equal(JSON.stringify(s.policies), beforePolicies);
  assert.equal(s.plans.length, 1);
  assert.equal(s.plans[0]!.untrusted, true);
});

test("7. commitment cannot close without required EvidenceReceipt", () => {
  let s = createInitialState();
  s = addGoal(s, baseGoal({ decision_class: "WEBPAGE_CHANGE" }));
  s = ingestEvent(s, {
    type: "TASK_REQUEST",
    goal_id: "goal_18",
    decision_class: "WEBPAGE_CHANGE",
    intent: "edit",
    reversible: true,
  });
  const compiled = compileNextAction(s, s.last_decision_result!.decision!);
  s = compiled.state;
  const com = s.commitments[0]!;
  assert.throws(() => closeCommitment(s, com.commitment_id), /REFUSE/);
});

test("8. executor completion claim without evidence is rejected", () => {
  let s = createInitialState();
  s = addGoal(s, baseGoal({ decision_class: "WEBPAGE_CHANGE" }));
  s = ingestEvent(s, {
    type: "TASK_REQUEST",
    goal_id: "goal_18",
    decision_class: "WEBPAGE_CHANGE",
    intent: "edit",
    reversible: true,
  });
  const compiled = compileNextAction(s, s.last_decision_result!.decision!);
  s = compiled.state;
  s = ingestEvent(s, {
    type: "EXECUTOR_CLAIM_DONE",
    work_packet_id: compiled.packet.action_id,
    claim_only: true,
  });
  assert.ok(s.incidents.some((i) => i.reason === "FALSE_COMPLETION"));
});

test("9. two identical semantic failures create repeated-failure incident", () => {
  let s = createInitialState();
  s = addGoal(s, baseGoal({ decision_class: "WEBPAGE_CHANGE" }));
  s = ingestEvent(s, {
    type: "TASK_REQUEST",
    goal_id: "goal_18",
    decision_class: "WEBPAGE_CHANGE",
    intent: "edit",
    reversible: true,
  });
  const compiled = compileNextAction(s, s.last_decision_result!.decision!);
  s = compiled.state;
  s = ingestEvent(s, {
    type: "FAILURE_OBSERVED",
    work_packet_id: compiled.packet.action_id,
    signature: "build_fail:TS2322",
  });
  s = ingestEvent(s, {
    type: "FAILURE_OBSERVED",
    work_packet_id: compiled.packet.action_id,
    signature: "build_fail:TS2322",
  });
  assert.ok(s.incidents.some((i) => i.reason === "REPEATED_FAILURE"));
});

test("10. two zero-progress cycles stop the work packet", () => {
  let s = createInitialState();
  s = addGoal(s, baseGoal({ decision_class: "WEBPAGE_CHANGE" }));
  s = ingestEvent(s, {
    type: "TASK_REQUEST",
    goal_id: "goal_18",
    decision_class: "WEBPAGE_CHANGE",
    intent: "edit",
    reversible: true,
  });
  const compiled = compileNextAction(s, s.last_decision_result!.decision!);
  s = compiled.state;
  s = ingestEvent(s, {
    type: "PROGRESS_CHECK",
    work_packet_id: compiled.packet.action_id,
    verified_progress: false,
  });
  s = ingestEvent(s, {
    type: "PROGRESS_CHECK",
    work_packet_id: compiled.packet.action_id,
    verified_progress: false,
  });
  const wp = s.work_packets.find((w) => w.action_id === compiled.packet.action_id)!;
  assert.equal(wp.status, "STOPPED");
  assert.ok(s.incidents.some((i) => i.reason === "ZERO_PROGRESS"));
});

test("11. human-tax breach freezes affected work and creates incident", () => {
  let s = createInitialState();
  s = addGoal(s, baseGoal({ decision_class: "WEBPAGE_CHANGE", budgets: {
    max_attempts: 2, max_minutes: 30, max_cost_usd: 1.5, max_fanout: 0, max_human_tax_units: 3,
  }}));
  s = ingestEvent(s, {
    type: "TASK_REQUEST",
    goal_id: "goal_18",
    decision_class: "WEBPAGE_CHANGE",
    intent: "edit",
    reversible: true,
  });
  const compiled = compileNextAction(s, s.last_decision_result!.decision!);
  s = compiled.state;
  s = ingestEvent(s, { type: "HUMAN_TAX", units: 4, goal_id: "goal_18" });
  assert.equal(s.goals[0]!.status, "FROZEN");
  assert.ok(s.incidents.some((i) => i.reason === "HUMAN_TAX_BREACH"));
  assert.ok(s.work_packets.some((w) => w.status === "FROZEN"));
});

test("12. newer Founder decision beats older policy in conflict", () => {
  let s = createInitialState();
  s = addGoal(s, baseGoal());
  s = ingestEvent(s, {
    type: "FOUNDER_DECISION",
    decision: {
      decision_id: "dec_founder_1",
      zone: "GREEN",
      goal_id: "goal_18",
      decision_class: "WEBPAGE_REPAIR",
      policy_version: "founder.override.v1",
      status: "APPROVED",
      action_summary: "founder override",
      source_decision_ids: [],
    },
  });
  s = ingestEvent(s, {
    type: "CONFLICT_RAISED",
    kind: "FOUNDER_VS_POLICY",
    left_ref: "dec_founder_1",
    right_ref: "webpage_repair.v1.live.185ec3865a14",
  });
  const c = detectConflicts(s)[0]!;
  s = resolveConflict(s, c.conflict_id);
  const resolved = s.conflicts.find((x) => x.conflict_id === c.conflict_id)!;
  assert.equal(resolved.resolved, true);
  assert.match(resolved.resolution ?? "", /latest_founder_decision/);
});

test("13. unresolvable conflict produces Founder Decision Packet", () => {
  let s = createInitialState();
  s = ingestEvent(s, {
    type: "CONFLICT_RAISED",
    kind: "UNRESOLVABLE",
    left_ref: "a",
    right_ref: "b",
  });
  const c = detectConflicts(s)[0]!;
  s = resolveConflict(s, c.conflict_id);
  assert.ok(s.founder_packets.length >= 1);
  const packet = createFounderDecisionPacket(s, c);
  assert.equal(packet.schema, "noetfield.executive.founder_decision_packet.v0");
});

test("14. webpage-edit work packet cannot spawn subagents when max_fanout is zero", () => {
  let s = createInitialState();
  s = addGoal(s, baseGoal({ decision_class: "WEBPAGE_CHANGE" }));
  s = ingestEvent(s, {
    type: "TASK_REQUEST",
    goal_id: "goal_18",
    decision_class: "WEBPAGE_CHANGE",
    intent: "edit",
    reversible: true,
  });
  const compiled = compileNextAction(s, s.last_decision_result!.decision!);
  assert.equal(compiled.packet.budget.max_fanout, 0);
  s = compiled.state;
  s = ingestEvent(s, {
    type: "SPAWN_SUBAGENTS_ATTEMPT",
    work_packet_id: compiled.packet.action_id,
  });
  assert.ok(s.incidents.some((i) => i.reason === "UNAUTHORIZED_CAPABILITY"));
});

test("15. out-of-scope mutation creates AUTHORITY_DRIFT and freezes the task", () => {
  let s = createInitialState();
  s = addGoal(s, baseGoal({ decision_class: "WEBPAGE_CHANGE" }));
  s = ingestEvent(s, {
    type: "TASK_REQUEST",
    goal_id: "goal_18",
    decision_class: "WEBPAGE_CHANGE",
    intent: "edit",
    reversible: true,
  });
  const compiled = compileNextAction(s, s.last_decision_result!.decision!);
  s = compiled.state;
  s = ingestEvent(s, {
    type: "OUT_OF_SCOPE_MUTATION",
    goal_id: "goal_18",
    path: "governance/locks/secret.md",
  });
  assert.ok(detectDrift(s).some((d) => d.drift_kind === "AUTHORITY_DRIFT"));
  assert.equal(s.goals[0]!.status, "FROZEN");
  assert.ok(s.incidents.some((i) => i.reason === "OUT_OF_SCOPE"));
});

test("evidence path: valid evidence allows verify and commitment close", () => {
  let s = createInitialState();
  s = addGoal(s, baseGoal({
    decision_class: "WEBPAGE_CHANGE",
    evidence_required: ["git_diff"],
  }));
  s = ingestEvent(s, {
    type: "TASK_REQUEST",
    goal_id: "goal_18",
    decision_class: "WEBPAGE_CHANGE",
    intent: "edit",
    reversible: true,
  });
  const compiled = compileNextAction(s, s.last_decision_result!.decision!);
  s = compiled.state;
  s = recordEvidence(s, {
    evidence_id: "ev_1",
    work_packet_id: compiled.packet.action_id,
    kind: "git_diff",
    valid: true,
    detail: "diff present",
  });
  s = verifyOutcome(s, compiled.packet.action_id);
  assert.equal(s.work_packets.find((w) => w.action_id === compiled.packet.action_id)!.status, "ACCEPTED");
  const com = s.commitments[0]!;
  s = closeCommitment(s, com.commitment_id);
  assert.equal(s.commitments[0]!.status, "CLOSED");
});
