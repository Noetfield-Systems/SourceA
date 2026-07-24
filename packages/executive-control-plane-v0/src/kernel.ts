/**
 * SourceA Executive Control Plane v0 — deterministic kernel.
 * No network. No LLM on decision path. Governor never executes work.
 */

import { pushAudit } from "./audit.ts";
import { hashObject } from "./hash.ts";
import { clock, ids } from "./providers.ts";
import type {
  CanonicalState,
  Commitment,
  ConflictRecord,
  DecisionPolicy,
  DecisionRecord,
  DecisionResult,
  DriftFinding,
  EvidenceReceipt,
  ExecutiveEvent,
  FounderCharter,
  FounderDecisionPacket,
  GoalContract,
  IncidentRecord,
  PlanRecord,
  WorkPacket,
} from "./types.ts";

const CHANGE_POLICY = {
  decision_class: "WEBPAGE_CHANGE",
  policy_version: "webpage_change.v1.live.2f08672f3aaf",
  zone: "GREEN" as const,
  reversible: true,
  body: {
    when: { task_type: "webpage_change", risk: "low_or_medium" },
    select: { workflow: "deterministic_web_change_v1", executor: "cheapest_passing_executor" },
    limits: { max_files: 5, max_attempts: 2, max_fanout: 0 },
    verify: ["build_passes", "target_issue_absent", "unrelated_pages_unchanged", "receipt_written"],
    escalate_when: ["positioning_change_detected", "protected_file_required", "two_distinct_plans_failed"],
  },
};

const REPAIR_POLICY = {
  decision_class: "WEBPAGE_REPAIR",
  policy_version: "webpage_repair.v1.live.185ec3865a14",
  zone: "GREEN" as const,
  reversible: true,
  body: {
    when: { task_type: "webpage_repair", risk: "low_or_medium" },
    select: { workflow: "deterministic_web_repair_v1", executor: "cheapest_passing_executor" },
    limits: { max_files: 5, max_attempts: 2, max_fanout: 0 },
    verify: ["build_passes", "visual_diff_present", "target_issue_absent", "unrelated_pages_unchanged"],
    escalate_when: ["positioning_change_detected", "protected_file_required", "two_distinct_plans_failed"],
  },
};

function clone<T>(v: T): T {
  return structuredClone(v);
}

function policyFromFixture(f: {
  decision_class: string;
  policy_version: string;
  zone: "GREEN" | "AMBER" | "RED";
  reversible: boolean;
  body: DecisionPolicy["body"];
}): DecisionPolicy {
  const now = clock.now();
  return {
    schema: "noetfield.executive.decision_policy.v0",
    policy_id: ids.next("pol"),
    version: "1",
    decision_class: f.decision_class,
    policy_version: f.policy_version,
    zone: f.zone,
    reversible: f.reversible,
    body: f.body,
    created_at: now,
    updated_at: now,
  };
}

export function createInitialState(charter?: Partial<FounderCharter>): CanonicalState {
  const now = clock.now();
  const baseCharter: FounderCharter = {
    schema: "noetfield.executive.founder_charter.v0",
    charter_id: ids.next("chr"),
    version: "1",
    non_negotiables: ["no_unsupervised_redesign", "no_llm_decision_path"],
    red_zone_classes: ["GOVERNANCE_CHANGE", "LEGAL", "LARGE_FINANCE", "POSITIONING"],
    delegation_envelope: {
      max_cost_usd: 5,
      allow_irreversible: false,
      allow_external_commitment: false,
      allow_governance_change: false,
    },
    created_at: now,
    updated_at: now,
    ...charter,
  };
  const state: CanonicalState = {
    schema: "noetfield.executive.canonical_state.v0",
    state_id: ids.next("st"),
    version: "1",
    policy_bundle_version: "ecp-v0.1.0",
    created_at: now,
    updated_at: now,
    charter: baseCharter,
    goals: [],
    policies: [policyFromFixture(CHANGE_POLICY), policyFromFixture(REPAIR_POLICY)],
    decisions: [],
    plans: [],
    commitments: [],
    conflicts: [],
    work_packets: [],
    evidence: [],
    drifts: [],
    incidents: [],
    founder_packets: [],
    human_tax_units: 0,
    failure_signatures: {},
    audit: [],
    last_decision_result: null,
  };
  pushAudit(state, "STATE_CREATED", { state_id: state.state_id });
  return state;
}

export function addGoal(state: CanonicalState, goal: Omit<GoalContract, "schema" | "created_at" | "updated_at" | "source_decision_ids"> & { source_decision_ids?: string[] }): CanonicalState {
  const s = clone(state);
  const now = clock.now();
  const g: GoalContract = {
    schema: "noetfield.executive.goal_contract.v0",
    source_decision_ids: goal.source_decision_ids ?? [],
    created_at: now,
    updated_at: now,
    ...goal,
  };
  s.goals.push(g);
  pushAudit(s, "GOAL_ADDED", { goal_id: g.goal_id });
  return s;
}

/* ---------- GoalController ---------- */

export function activeGoals(state: CanonicalState): GoalContract[] {
  return state.goals.filter((g) => g.status === "ACTIVE");
}

export function goalById(state: CanonicalState, goalId: string): GoalContract | undefined {
  return state.goals.find((g) => g.goal_id === goalId);
}

export function workMapsToActiveGoal(state: CanonicalState, goalId: string | undefined): boolean {
  if (!goalId) return false;
  const g = goalById(state, goalId);
  return !!g && g.status === "ACTIVE";
}

/* ---------- DriftMonitor ---------- */

export function detectDrift(state: CanonicalState): DriftFinding[] {
  return [...state.drifts];
}

function recordDrift(
  state: CanonicalState,
  drift_kind: DriftFinding["drift_kind"],
  goal_id: string | null,
  detail: string,
): DriftFinding {
  const now = clock.now();
  const finding: DriftFinding = {
    schema: "noetfield.executive.drift_finding.v0",
    finding_id: ids.next("drf"),
    version: "1",
    drift_kind,
    goal_id,
    detail,
    created_at: now,
    updated_at: now,
    source_decision_ids: [],
  };
  state.drifts.push(finding);
  pushAudit(state, "DRIFT", { drift_kind, goal_id, detail });
  return finding;
}

/* ---------- IncidentMotor ---------- */

export function recordIncident(
  state: CanonicalState,
  incident: Omit<IncidentRecord, "schema" | "incident_id" | "version" | "created_at" | "updated_at" | "source_decision_ids"> & {
    incident_id?: string;
    version?: string;
    source_decision_ids?: string[];
  },
): CanonicalState {
  const s = clone(state);
  const now = clock.now();
  const row: IncidentRecord = {
    schema: "noetfield.executive.incident_record.v0",
    incident_id: incident.incident_id ?? ids.next("inc"),
    version: incident.version ?? "1",
    reason: incident.reason,
    goal_id: incident.goal_id,
    work_packet_id: incident.work_packet_id,
    detail: incident.detail,
    created_at: now,
    updated_at: now,
    source_decision_ids: incident.source_decision_ids ?? [],
  };
  s.incidents.push(row);
  pushAudit(s, "INCIDENT", { reason: row.reason, incident_id: row.incident_id });
  return s;
}

/* ---------- CommitmentController ---------- */

export function closeCommitment(state: CanonicalState, commitmentId: string): CanonicalState {
  const s = clone(state);
  const c = s.commitments.find((x) => x.commitment_id === commitmentId);
  if (!c) throw new Error(`unknown commitment ${commitmentId}`);
  const hasEvidence = s.evidence.some(
    (e) => e.valid && e.kind === c.required_artifact && s.work_packets.some((w) => w.decision_id === c.decision_id && e.work_packet_id === w.action_id),
  );
  // Also accept evidence tied via work packets for this commitment's decision
  const packets = s.work_packets.filter((w) => w.decision_id === c.decision_id);
  const ok =
    hasEvidence ||
    s.evidence.some((e) => e.valid && e.kind === c.required_artifact && packets.some((p) => p.action_id === e.work_packet_id));
  if (!ok) {
    pushAudit(s, "COMMITMENT_CLOSE_REFUSED", { commitment_id: commitmentId, reason: "missing_evidence" });
    throw new Error("REFUSE: commitment cannot close without required EvidenceReceipt");
  }
  c.status = "CLOSED";
  c.updated_at = clock.now();
  pushAudit(s, "COMMITMENT_CLOSED", { commitment_id: commitmentId });
  return s;
}

export function openCommitments(state: CanonicalState): Commitment[] {
  return state.commitments.filter((c) => c.status === "OPEN" || c.status === "STALLED" || c.status === "OVERDUE");
}

/* ---------- ConflictResolver ---------- */

const PRECEDENCE = [
  "founder_charter",
  "latest_founder_decision",
  "locked_goal_contract",
  "security_legal_financial",
  "active_goal_priority",
  "dependency_order",
  "evidence_strength",
  "reversibility",
  "lower_human_tax",
  "lower_cost",
] as const;

export function detectConflicts(state: CanonicalState): ConflictRecord[] {
  return state.conflicts.filter((c) => !c.resolved);
}

export function resolveConflict(state: CanonicalState, conflictId: string): CanonicalState {
  const s = clone(state);
  const c = s.conflicts.find((x) => x.conflict_id === conflictId);
  if (!c) throw new Error(`unknown conflict ${conflictId}`);

  // Prefer newer founder decision over older policy
  const founderDecisions = s.decisions.filter((d) => d.founder_decision).sort((a, b) => b.created_at.localeCompare(a.created_at));
  if (c.kind === "FOUNDER_VS_POLICY" && founderDecisions.length > 0) {
    c.resolved = true;
    c.resolution = `precedence:latest_founder_decision:${founderDecisions[0]!.decision_id}`;
    c.updated_at = clock.now();
    pushAudit(s, "CONFLICT_RESOLVED", { conflict_id: conflictId, via: PRECEDENCE[1] });
    return s;
  }

  if (c.kind === "UNRESOLVABLE") {
    const packet = createFounderDecisionPacket(s, c);
    s.founder_packets.push(packet);
    c.resolved = false;
    c.resolution = null;
    pushAudit(s, "CONFLICT_RED_ZONE", { conflict_id: conflictId, packet_id: packet.packet_id });
    return s;
  }

  // Default: prefer reversibility / lower risk
  c.resolved = true;
  c.resolution = "precedence:reversibility";
  c.updated_at = clock.now();
  pushAudit(s, "CONFLICT_RESOLVED", { conflict_id: conflictId, via: "reversibility" });
  return s;
}

export function createFounderDecisionPacket(
  state: CanonicalState,
  conflictOrRed: ConflictRecord | { kind: string; detail?: string },
): FounderDecisionPacket {
  const now = clock.now();
  return {
    schema: "noetfield.executive.founder_decision_packet.v0",
    packet_id: ids.next("fdp"),
    version: "1",
    topic: "kind" in conflictOrRed ? String(conflictOrRed.kind) : "RED_ZONE",
    what_changed: "conflict_or_red_zone",
    options: [
      { id: "opt_a", label: "Accept reversible path", risk: "low" },
      { id: "opt_b", label: "Defer until Founder present", risk: "medium" },
    ],
    sg_recommendation: "Choose the lowest-risk reversible option that preserves future authority",
    critic_view: "Policy cannot close this conflict alone",
    risk_if_delayed: "Open commitments may stall",
    safest_interim_action: "Freeze affected work packets; keep monitoring",
    created_at: now,
    updated_at: now,
    source_decision_ids: [],
  };
}

/* ---------- EvidenceVerifier ---------- */

export function recordEvidence(
  state: CanonicalState,
  evidence: Omit<EvidenceReceipt, "schema" | "created_at" | "updated_at" | "version" | "source_decision_ids"> & {
    version?: string;
    source_decision_ids?: string[];
  },
): CanonicalState {
  const s = clone(state);
  const now = clock.now();
  const row: EvidenceReceipt = {
    schema: "noetfield.executive.evidence_receipt.v0",
    evidence_id: evidence.evidence_id,
    version: evidence.version ?? "1",
    work_packet_id: evidence.work_packet_id,
    kind: evidence.kind,
    valid: evidence.valid,
    detail: evidence.detail,
    created_at: now,
    updated_at: now,
    source_decision_ids: evidence.source_decision_ids ?? [],
  };
  s.evidence.push(row);
  pushAudit(s, "EVIDENCE_RECORDED", { evidence_id: row.evidence_id, valid: row.valid });
  return s;
}

export function verifyOutcome(state: CanonicalState, workPacketId: string): CanonicalState {
  const s = clone(state);
  const wp = s.work_packets.find((w) => w.action_id === workPacketId);
  if (!wp) throw new Error(`unknown work packet ${workPacketId}`);
  const required = wp.evidence_required;
  const present = s.evidence.filter((e) => e.work_packet_id === workPacketId && e.valid);
  const kinds = new Set(present.map((e) => e.kind));
  const missing = required.filter((r) => !kinds.has(r));
  if (missing.length > 0) {
    wp.status = "FAILED";
    wp.updated_at = clock.now();
    const next = recordIncident(s, {
      reason: "FALSE_COMPLETION",
      goal_id: wp.goal_id,
      work_packet_id: wp.action_id,
      detail: `missing evidence: ${missing.join(",")}`,
    });
    pushAudit(next, "VERIFY_FAILED", { work_packet_id: workPacketId, missing });
    return next;
  }
  wp.status = "ACCEPTED";
  wp.updated_at = clock.now();
  pushAudit(s, "VERIFY_ACCEPTED", { work_packet_id: workPacketId });
  return s;
}

/* ---------- NextActionCompiler ---------- */

export function compileNextAction(state: CanonicalState, decision: DecisionRecord): { state: CanonicalState; packet: WorkPacket } {
  if (decision.status !== "APPROVED") {
    throw new Error("REFUSE: cannot compile non-approved decision");
  }
  const s = clone(state);
  const goal = goalById(s, decision.goal_id);
  if (!goal || goal.status !== "ACTIVE") {
    throw new Error("REFUSE: no active Goal Contract");
  }
  const policy = s.policies.find((p) => p.decision_class === decision.decision_class && p.policy_version === decision.policy_version);
  const limits = policy?.body.limits ?? goal.budgets;
  const maxFanout = Number(limits.max_fanout ?? goal.budgets.max_fanout ?? 0);
  const now = clock.now();
  const packet: WorkPacket = {
    schema: "noetfield.executive.work_packet.v0",
    action_id: ids.next("act"),
    version: "1",
    goal_id: goal.goal_id,
    decision_id: decision.decision_id,
    plan_step_id: null,
    why_now: "Dependencies satisfied; policy authorized",
    executor_class: policy?.body.select.executor ?? "bounded_executor",
    inputs: [],
    allowed_capabilities: goal.scope_allowlist.map((p) => `write:${p}`),
    forbidden_capabilities: [
      "write:governance/**",
      "deploy:production",
      "spawn:subagents",
      ...goal.forbidden_effects,
    ],
    acceptance_predicates: goal.acceptance_predicates.length
      ? goal.acceptance_predicates
      : policy?.body.verify ?? [],
    evidence_required: goal.evidence_required.length ? goal.evidence_required : ["git_diff", "test_result"],
    budget: {
      max_attempts: Number(limits.max_attempts ?? goal.budgets.max_attempts),
      max_minutes: Number(limits.max_minutes ?? goal.budgets.max_minutes),
      max_cost_usd: Number(limits.max_cost_usd ?? goal.budgets.max_cost_usd),
      max_fanout: maxFanout,
    },
    on_failure: "OPEN_INCIDENT",
    rollback_policy: "revert_scoped_writes",
    status: "OPEN",
    zero_progress_cycles: 0,
    created_at: now,
    updated_at: now,
    source_decision_ids: [decision.decision_id],
  };
  if (maxFanout === 0 && packet.forbidden_capabilities.indexOf("spawn:subagents") < 0) {
    packet.forbidden_capabilities.push("spawn:subagents");
  }
  s.work_packets.push(packet);
  const commitment: Commitment = {
    schema: "noetfield.executive.commitment.v0",
    commitment_id: ids.next("com"),
    version: "1",
    decision_id: decision.decision_id,
    goal_id: goal.goal_id,
    owner: "sourcea",
    due_at: null,
    required_artifact: packet.evidence_required[0] ?? "receipt_written",
    status: "OPEN",
    dependencies: [],
    max_silence_minutes: 60,
    created_at: now,
    updated_at: now,
    source_decision_ids: [decision.decision_id],
  };
  s.commitments.push(commitment);
  pushAudit(s, "WORK_PACKET_COMPILED", { action_id: packet.action_id, max_fanout: maxFanout });
  return { state: s, packet };
}

/* ---------- PolicyEngine + ExecutiveGovernor ---------- */

function classifyZone(
  state: CanonicalState,
  ev: Extract<ExecutiveEvent, { type: "TASK_REQUEST" }>,
): { zone: DecisionResult["zone"]; policy: DecisionPolicy | null; reason: string } {
  if (ev.governance_change || ev.irreversible) {
    return { zone: "RED", policy: null, reason: "irreversible_or_governance" };
  }
  if (state.charter.red_zone_classes.includes(ev.decision_class)) {
    return { zone: "RED", policy: null, reason: "red_zone_class" };
  }
  const policy = state.policies.find((p) => p.decision_class === ev.decision_class) ?? null;
  if (!policy) {
    return { zone: "RED", policy: null, reason: "unknown_decision_class" };
  }
  if (!policy.reversible || policy.zone === "AMBER") {
    return { zone: "AMBER", policy, reason: "amber_or_non_reversible_policy" };
  }
  return { zone: "GREEN", policy, reason: "known_green_policy" };
}

function decisionHash(input: {
  event: ExecutiveEvent;
  policy_version: string;
  policy_bundle_version: string;
}): string {
  return hashObject({
    event: input.event,
    policy_version: input.policy_version,
    policy_bundle_version: input.policy_bundle_version,
  });
}

export function selectNextDecision(state: CanonicalState): DecisionResult | null {
  return state.last_decision_result;
}

export function reconcileState(state: CanonicalState): CanonicalState {
  const s = clone(state);
  // Mark overdue commitments by due_at if present (deterministic)
  for (const c of s.commitments) {
    if (c.status === "OPEN" && c.due_at && c.due_at < clock.now()) {
      c.status = "OVERDUE";
      c.updated_at = clock.now();
    }
  }
  pushAudit(s, "RECONCILE", { open_commitments: openCommitments(s).length });
  return s;
}

export function ingestEvent(state: CanonicalState, event: ExecutiveEvent): CanonicalState {
  let s = reconcileState(state);

  if (event.type === "PLAN_PROPOSAL") {
    // Untrusted: store plan only; never mutate goals/policies/decisions from proposal content
    const now = clock.now();
    const plan: PlanRecord = {
      schema: "noetfield.executive.plan_record.v0",
      plan_id: event.plan.plan_id,
      version: event.plan.version ?? "1",
      goal_id: event.plan.goal_id,
      untrusted: true,
      assumptions: event.plan.assumptions,
      candidate_actions: event.plan.candidate_actions,
      risks: event.plan.risks,
      success_predicates: event.plan.success_predicates,
      founder_decisions_required: event.plan.founder_decisions_required,
      created_at: now,
      updated_at: now,
      source_decision_ids: event.plan.source_decision_ids ?? [],
    };
    s.plans.push(plan);
    pushAudit(s, "PLAN_PROPOSAL_STORED", { plan_id: plan.plan_id, untrusted: true });
    return s;
  }

  if (event.type === "FOUNDER_DECISION") {
    const now = clock.now();
    const d: DecisionRecord = {
      schema: "noetfield.executive.decision_record.v0",
      decision_id: event.decision.decision_id,
      version: event.decision.version ?? "1",
      zone: event.decision.zone,
      goal_id: event.decision.goal_id,
      decision_class: event.decision.decision_class,
      policy_version: event.decision.policy_version,
      status: event.decision.status,
      action_summary: event.decision.action_summary,
      created_at: now,
      updated_at: now,
      source_decision_ids: event.decision.source_decision_ids ?? [],
      founder_decision: true,
    };
    s.decisions.push(d);
    pushAudit(s, "FOUNDER_DECISION", { decision_id: d.decision_id });
    return s;
  }

  if (event.type === "CONFLICT_RAISED") {
    const now = clock.now();
    const c: ConflictRecord = {
      schema: "noetfield.executive.conflict_record.v0",
      conflict_id: ids.next("cnf"),
      version: "1",
      kind: event.kind,
      left_ref: event.left_ref,
      right_ref: event.right_ref,
      resolved: false,
      resolution: null,
      created_at: now,
      updated_at: now,
      source_decision_ids: [],
    };
    s.conflicts.push(c);
    pushAudit(s, "CONFLICT_RAISED", { conflict_id: c.conflict_id, kind: c.kind });
    return s;
  }

  if (event.type === "EVIDENCE_SUBMITTED") {
    return recordEvidence(s, event.evidence);
  }

  if (event.type === "EXECUTOR_CLAIM_DONE") {
    const wp = s.work_packets.find((w) => w.action_id === event.work_packet_id);
    if (!wp) throw new Error(`unknown work packet ${event.work_packet_id}`);
    if (event.claim_only !== false) {
      // claim without evidence → reject
      return recordIncident(s, {
        reason: "FALSE_COMPLETION",
        goal_id: wp.goal_id,
        work_packet_id: wp.action_id,
        detail: "executor claim without evidence",
      });
    }
    return verifyOutcome(s, event.work_packet_id);
  }

  if (event.type === "FAILURE_OBSERVED") {
    const sig = event.signature;
    s.failure_signatures[sig] = (s.failure_signatures[sig] ?? 0) + 1;
    const wp = s.work_packets.find((w) => w.action_id === event.work_packet_id);
    if ((s.failure_signatures[sig] ?? 0) >= 2) {
      s = recordIncident(s, {
        reason: "REPEATED_FAILURE",
        goal_id: wp?.goal_id ?? null,
        work_packet_id: event.work_packet_id,
        detail: `signature=${sig} count=${s.failure_signatures[sig]}`,
      });
    }
    pushAudit(s, "FAILURE_OBSERVED", { signature: sig, count: s.failure_signatures[sig] });
    return s;
  }

  if (event.type === "PROGRESS_CHECK") {
    const wp = s.work_packets.find((w) => w.action_id === event.work_packet_id);
    if (!wp) throw new Error(`unknown work packet ${event.work_packet_id}`);
    if (!event.verified_progress) {
      wp.zero_progress_cycles += 1;
      wp.updated_at = clock.now();
      if (wp.zero_progress_cycles >= 2) {
        wp.status = "STOPPED";
        s = recordIncident(s, {
          reason: "ZERO_PROGRESS",
          goal_id: wp.goal_id,
          work_packet_id: wp.action_id,
          detail: "two cycles with zero verified progress",
        });
      }
    } else {
      wp.zero_progress_cycles = 0;
      wp.updated_at = clock.now();
    }
    pushAudit(s, "PROGRESS_CHECK", { work_packet_id: wp.action_id, cycles: wp.zero_progress_cycles });
    return s;
  }

  if (event.type === "HUMAN_TAX") {
    s.human_tax_units += event.units;
    const goal = event.goal_id ? goalById(s, event.goal_id) : activeGoals(s)[0];
    if (goal && s.human_tax_units > goal.budgets.max_human_tax_units) {
      goal.status = "FROZEN";
      goal.updated_at = clock.now();
      for (const wp of s.work_packets.filter((w) => w.goal_id === goal.goal_id && w.status === "OPEN")) {
        wp.status = "FROZEN";
        wp.updated_at = clock.now();
      }
      s = recordIncident(s, {
        reason: "HUMAN_TAX_BREACH",
        goal_id: goal.goal_id,
        work_packet_id: null,
        detail: `human_tax_units=${s.human_tax_units} max=${goal.budgets.max_human_tax_units}`,
      });
    }
    pushAudit(s, "HUMAN_TAX", { units: event.units, total: s.human_tax_units });
    return s;
  }

  if (event.type === "OUT_OF_SCOPE_MUTATION") {
    const goal = goalById(s, event.goal_id);
    recordDrift(s, "AUTHORITY_DRIFT", event.goal_id, `path=${event.path}`);
    if (goal) {
      goal.status = "FROZEN";
      goal.updated_at = clock.now();
    }
    for (const wp of s.work_packets.filter((w) => w.goal_id === event.goal_id && w.status === "OPEN")) {
      wp.status = "FROZEN";
      wp.updated_at = clock.now();
    }
    s = recordIncident(s, {
      reason: "OUT_OF_SCOPE",
      goal_id: event.goal_id,
      work_packet_id: null,
      detail: `out of scope path ${event.path}`,
    });
    return s;
  }

  if (event.type === "SPAWN_SUBAGENTS_ATTEMPT") {
    const wp = s.work_packets.find((w) => w.action_id === event.work_packet_id);
    if (!wp) throw new Error(`unknown work packet ${event.work_packet_id}`);
    if (wp.budget.max_fanout === 0 || wp.forbidden_capabilities.includes("spawn:subagents")) {
      s = recordIncident(s, {
        reason: "UNAUTHORIZED_CAPABILITY",
        goal_id: wp.goal_id,
        work_packet_id: wp.action_id,
        detail: "spawn:subagents forbidden when max_fanout=0",
      });
    }
    return s;
  }

  if (event.type === "TASK_REQUEST") {
    // No active goal mapping
    if (!workMapsToActiveGoal(s, event.goal_id)) {
      if (event.goal_id && goalById(s, event.goal_id) === undefined) {
        // task names a missing goal
        s = recordIncident(s, {
          reason: "NO_ACTIVE_GOAL",
          goal_id: event.goal_id ?? null,
          work_packet_id: null,
          detail: "task with no active Goal Contract",
        });
        const result: DecisionResult = {
          schema: "noetfield.executive.decision_result.v0",
          result_id: ids.next("res"),
          zone: "RED",
          status: "REJECTED",
          decision_hash: decisionHash({
            event,
            policy_version: "none",
            policy_bundle_version: s.policy_bundle_version,
          }),
          policy_version: "none",
          rationale: "no_active_goal_contract",
          decision: null,
          founder_packet_id: null,
          created_at: clock.now(),
        };
        s.last_decision_result = result;
        pushAudit(s, "DECISION", { status: result.status, rationale: result.rationale });
        return s;
      }
      // work unrelated to active goals → GOAL_DRIFT
      recordDrift(s, "GOAL_DRIFT", event.goal_id ?? null, `intent=${event.intent}`);
      s = recordIncident(s, {
        reason: "REJECTED_TASK",
        goal_id: event.goal_id ?? null,
        work_packet_id: null,
        detail: "work item unrelated to active goal",
      });
      const result: DecisionResult = {
        schema: "noetfield.executive.decision_result.v0",
        result_id: ids.next("res"),
        zone: "RED",
        status: "REJECTED",
        decision_hash: decisionHash({
          event,
          policy_version: "none",
          policy_bundle_version: s.policy_bundle_version,
        }),
        policy_version: "none",
        rationale: "goal_drift_unrelated_work",
        decision: null,
        founder_packet_id: null,
        created_at: clock.now(),
      };
      s.last_decision_result = result;
      return s;
    }

    const { zone, policy, reason } = classifyZone(s, event);
    const policyVersion = policy?.policy_version ?? "none";
    const dHash = decisionHash({
      event,
      policy_version: policyVersion,
      policy_bundle_version: s.policy_bundle_version,
    });

    if (zone === "RED") {
      const packet = createFounderDecisionPacket(s, { kind: reason });
      s.founder_packets.push(packet);
      const result: DecisionResult = {
        schema: "noetfield.executive.decision_result.v0",
        result_id: ids.next("res"),
        zone: "RED",
        status: "RED_ZONE_REQUIRED",
        decision_hash: dHash,
        policy_version: policyVersion,
        rationale: reason,
        decision: null,
        founder_packet_id: packet.packet_id,
        created_at: clock.now(),
      };
      s.last_decision_result = result;
      pushAudit(s, "DECISION", { status: result.status, zone, rationale: reason });
      return s;
    }

    if (zone === "AMBER") {
      // Require plan + critic evidence before finalize
      const hasPlan = s.plans.some((p) => p.goal_id === event.goal_id);
      const hasCritic = s.evidence.some((e) => e.kind === "critic_review" && e.valid);
      if (!hasPlan || !hasCritic) {
        const result: DecisionResult = {
          schema: "noetfield.executive.decision_result.v0",
          result_id: ids.next("res"),
          zone: "AMBER",
          status: "REJECTED",
          decision_hash: dHash,
          policy_version: policyVersion,
          rationale: "amber_missing_plan_or_critic",
          decision: null,
          founder_packet_id: null,
          created_at: clock.now(),
        };
        s.last_decision_result = result;
        return s;
      }
    }

    // GREEN (or AMBER with evidence): finalize
    const now = clock.now();
    const decision: DecisionRecord = {
      schema: "noetfield.executive.decision_record.v0",
      decision_id: ids.next("dec"),
      version: "1",
      zone,
      goal_id: event.goal_id!,
      decision_class: event.decision_class,
      policy_version: policyVersion,
      status: "APPROVED",
      action_summary: `authorize ${event.decision_class} for ${event.intent}`,
      created_at: now,
      updated_at: now,
      source_decision_ids: [],
    };
    s.decisions.push(decision);
    const result: DecisionResult = {
      schema: "noetfield.executive.decision_result.v0",
      result_id: ids.next("res"),
      zone,
      status: "APPROVED",
      decision_hash: dHash,
      policy_version: policyVersion,
      rationale: reason,
      decision,
      founder_packet_id: null,
      created_at: now,
    };
    s.last_decision_result = result;
    pushAudit(s, "DECISION", {
      status: result.status,
      zone,
      policy_version: policyVersion,
      decision_id: decision.decision_id,
      decision_hash: dHash,
    });
    return s;
  }

  return s;
}

/** ExecutiveGovernor: state + event → exactly one DecisionResult (via ingest). */
export function executiveDecide(state: CanonicalState, event: ExecutiveEvent): { state: CanonicalState; result: DecisionResult | null } {
  const next = ingestEvent(state, event);
  return { state: next, result: next.last_decision_result };
}
