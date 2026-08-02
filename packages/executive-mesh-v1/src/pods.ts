import { hashObject } from "./hash.ts";
import type {
  ContextPack,
  EventEnvelope,
  PlanGraphPacket,
  RoleDecisionPacket,
  RoleId,
} from "./types.ts";
import { WEBPAGE_REPAIR_POLICY } from "./types.ts";

const BLUEPRINT = "role_blueprint.v1.slice1";
const MODEL_ROUTE_L0 = "deliberation.L0.deterministic.v1";

function basePacket(
  role: RoleId,
  parentRunId: string,
  snapshotVersion: number,
  question: string,
  conclusion: RoleDecisionPacket["conclusion"],
  recommended: string,
  extras: Partial<RoleDecisionPacket> = {},
): RoleDecisionPacket {
  const body = {
    role,
    parent_run_id: parentRunId,
    snapshot_version: snapshotVersion,
    conclusion,
    recommended_action: recommended,
    ...extras.body,
  };
  return {
    role,
    role_run_id: `rr_${role.toLowerCase()}_${parentRunId}`,
    parent_run_id: parentRunId,
    snapshot_version: snapshotVersion,
    blueprint_version: BLUEPRINT,
    model_route_version: MODEL_ROUTE_L0,
    decision_question: question,
    conclusion,
    recommended_action: recommended,
    confidence: extras.confidence ?? 0.9,
    assumptions: extras.assumptions ?? [],
    evidence_refs: extras.evidence_refs ?? [],
    policy_refs: extras.policy_refs ?? [WEBPAGE_REPAIR_POLICY.policy_version],
    objections: extras.objections ?? [],
    unresolved_uncertainties: extras.unresolved_uncertainties ?? [],
    hard_vetoes: extras.hard_vetoes ?? [],
    dissent: extras.dissent ?? [],
    artifact_refs: extras.artifact_refs ?? [],
    packet_hash: "",
    body,
  };
}

export function sealPacket(p: RoleDecisionPacket): RoleDecisionPacket {
  const { packet_hash: _h, ...rest } = p;
  return { ...p, packet_hash: hashObject(rest) };
}

/** SG Pod L0 — agenda from event + live Decision Capacity. */
export function runSgPod(event: EventEnvelope, runId: string, snapshotVersion: number): RoleDecisionPacket {
  const taskType = String(event.payload.task_type ?? event.event_type);
  const url = String(event.payload.target_url ?? event.payload.url ?? "");
  const isRepair = taskType === "webpage_repair" || event.event_type === "webpage.repair.requested";
  return sealPacket(
    basePacket(
      "SG",
      runId,
      snapshotVersion,
      "What is the executive agenda for this event?",
      isRepair ? "RECOMMEND" : "REQUEST_EVIDENCE",
      isRepair
        ? `Admit WEBPAGE_REPAIR for ${url} under ${WEBPAGE_REPAIR_POLICY.policy_version}`
        : "Insufficient Decision Capacity for event type",
      {
        assumptions: ["Live Decision Capacity covers WEBPAGE_REPAIR"],
        body: {
          agenda: {
            decision_class: isRepair ? "WEBPAGE_REPAIR" : "UNKNOWN",
            target_url: url,
            priority: "P1",
            policy_version: WEBPAGE_REPAIR_POLICY.policy_version,
          },
        },
      },
    ),
  );
}

/** Memory Steward — versioned ContextPack. */
export function runMemorySteward(
  event: EventEnvelope,
  runId: string,
  snapshotVersion: number,
  sg: RoleDecisionPacket,
): { packet: RoleDecisionPacket; context: ContextPack } {
  const context: ContextPack = {
    snapshot_version: snapshotVersion,
    role: "MEMORY_STEWARD",
    founder_charter_slice: ["NF-EXECUTIVE-MESH-V1", "NF-EXECUTIVE-CONTROL-PLANE-V0", "NF-DECISION-CAPACITY-V1"],
    active_goal_contracts: [
      {
        goal_id: String(event.payload.goal_id ?? `goal_${event.idempotency_key}`),
        target_url: event.payload.target_url ?? event.payload.url,
      },
    ],
    applicable_policies: [WEBPAGE_REPAIR_POLICY as unknown as Record<string, unknown>],
    open_decisions: [],
    open_commitments: [],
    recent_incidents: [],
    graph_neighborhood: [{ event_type: event.event_type, producer: event.producer }],
    retrieved_evidence: [{ ref: `event:${event.event_id}`, hash: event.payload_hash }],
    contradictions: [],
    excluded_material: ["L2_council", "vector_retrieval"],
    provenance_manifest: [sg.packet_hash, event.payload_hash],
    context_hash: "",
  };
  context.context_hash = hashObject({ ...context, context_hash: "" });

  const packet = sealPacket(
    basePacket(
      "MEMORY_STEWARD",
      runId,
      snapshotVersion,
      "What context is admissible for this run?",
      "PASS",
      `ContextPack v${snapshotVersion} sealed`,
      {
        artifact_refs: [`context:${context.context_hash}`],
        body: { context_hash: context.context_hash },
      },
    ),
  );
  return { packet, context };
}

/** Strategic Planner L0 — PlanGraph from WEBPAGE_REPAIR policy. */
export function runPlannerPod(
  event: EventEnvelope,
  runId: string,
  snapshotVersion: number,
  context: ContextPack,
): { packet: RoleDecisionPacket; plan: PlanGraphPacket } {
  const url = String(event.payload.target_url ?? event.payload.url ?? "");
  const plan: PlanGraphPacket = {
    packet_type: "PlanGraphPacket",
    target_outcome: `Repair webpage ${url} to acceptance predicates`,
    milestones: ["admit_goal", "hdir_webpage_build_deploy", "independent_verify", "commit_canonical"],
    dependencies: ["decision_capacity:WEBPAGE_REPAIR", "runway_goal_kernel"],
    parallel_groups: [],
    acceptance_predicates: [...WEBPAGE_REPAIR_POLICY.body.verify],
    rollback_points: ["pre_deploy", "pre_canonical_commit"],
    assumptions: ["Executor class RUNWAY_GOAL_KERNEL", "max_fanout=0"],
    risks: ["protected_file_required", "positioning_change_detected"],
    founder_decisions_required: [],
    recommended_runway: "RUNWAY_GOAL_KERNEL",
    critic_status: "PENDING",
  };

  const packet = sealPacket(
    basePacket(
      "STRATEGIC_PLANNER",
      runId,
      snapshotVersion,
      "What plan advances the target under policy limits?",
      "RECOMMEND",
      plan.target_outcome,
      {
        confidence: 0.88,
        assumptions: plan.assumptions,
        artifact_refs: [`plan:${hashObject(plan)}`, `context:${context.context_hash}`],
        body: { plan },
      },
    ),
  );
  return { packet, plan };
}

/** Critic — independent route from Planner. */
export function runCriticPod(
  runId: string,
  snapshotVersion: number,
  plan: PlanGraphPacket,
  planner: RoleDecisionPacket,
): { packet: RoleDecisionPacket; plan: PlanGraphPacket } {
  const illegalFanout = plan.parallel_groups.some((g) => g.length > 1);
  const policyFanout = WEBPAGE_REPAIR_POLICY.body.limits.max_fanout;
  const vetoes: string[] = [];
  const objections: string[] = [];

  if (illegalFanout || policyFanout !== 0) {
    if (illegalFanout) vetoes.push("ILLEGAL_FANOUT");
  }
  if (plan.recommended_runway !== "RUNWAY_GOAL_KERNEL") {
    objections.push("NON_CANONICAL_EXECUTOR");
  }
  if (!plan.acceptance_predicates.includes("unrelated_pages_unchanged")) {
    objections.push("MISSING_ACCEPTANCE_PREDICATE");
  }

  const passed = vetoes.length === 0 && objections.length === 0;
  const updated: PlanGraphPacket = { ...plan, critic_status: passed ? "PASSED" : "FAILED" };

  const packet = sealPacket(
    basePacket(
      "CRITIC",
      runId,
      snapshotVersion,
      "Does the plan violate policy, fanout, or acceptance law?",
      passed ? "PASS" : "VETO",
      passed ? "Plan cleared for Governor" : `Blocked: ${[...vetoes, ...objections].join(",")}`,
      {
        confidence: 0.95,
        objections,
        hard_vetoes: vetoes,
        dissent: passed ? [] : ["Planner recommendation opposed"],
        // Critic must not share planner model route identity beyond L0 label — independent deliberation id
        evidence_refs: [`planner_packet:${planner.packet_hash}`, `plan:${hashObject(plan)}`],
        body: {
          independent_route: true,
          critic_route_id: `critic_independent_${runId}`,
          planner_route_id: planner.role_run_id,
          plan: updated,
        },
      },
    ),
  );
  return { packet, plan: updated };
}
