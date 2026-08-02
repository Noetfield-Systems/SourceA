/** Executive Mesh v1 — domain types */

export type DeliberationLevel = "L0" | "L1" | "L2" | "L3" | "L4";
export type RoleId = "SG" | "MEMORY_STEWARD" | "STRATEGIC_PLANNER" | "CRITIC";
export type RoleConclusion =
  | "RECOMMEND"
  | "OPPOSE"
  | "VETO"
  | "REQUEST_EVIDENCE"
  | "DECLARE_CONFLICT"
  | "NO_ACTION_REQUIRED"
  | "PASS";

export type RunStatus =
  | "RECEIVED"
  | "SNAPSHOT_LOCKED"
  | "CONTEXT_READY"
  | "ROLE_DELIBERATION"
  | "COUNCIL_REVIEW"
  | "GOVERNOR_DECIDED"
  | "ACTION_COMPILED"
  | "EXECUTING"
  | "VERIFYING"
  | "ACCEPTED"
  | "INCIDENT"
  | "DEFERRED_BY_POLICY"
  | "FOUNDER_DECISION_REQUIRED"
  | "BOUNDED_FAILURE";

export type Terminal =
  | "ACCEPTED"
  | "BOUNDED_FAILURE"
  | "INCIDENT"
  | "DEFERRED_BY_POLICY"
  | "FOUNDER_DECISION_REQUIRED";

export interface EventEnvelope {
  event_id: string;
  event_type: string;
  schema_version: string;
  organization_id: string;
  correlation_id: string;
  causation_id: string | null;
  idempotency_key: string;
  canonical_state_version: number;
  producer: string;
  produced_at: string;
  payload: Record<string, unknown>;
  payload_hash: string;
}

export interface RoleDecisionPacket {
  role: RoleId;
  role_run_id: string;
  parent_run_id: string;
  snapshot_version: number;
  blueprint_version: string;
  model_route_version: string;
  decision_question: string;
  conclusion: RoleConclusion;
  recommended_action: string;
  confidence: number;
  assumptions: string[];
  evidence_refs: string[];
  policy_refs: string[];
  objections: string[];
  unresolved_uncertainties: string[];
  hard_vetoes: string[];
  dissent: string[];
  artifact_refs: string[];
  packet_hash: string;
  body?: Record<string, unknown>;
}

export interface ContextPack {
  snapshot_version: number;
  role: RoleId;
  founder_charter_slice: string[];
  active_goal_contracts: Record<string, unknown>[];
  applicable_policies: Record<string, unknown>[];
  open_decisions: Record<string, unknown>[];
  open_commitments: Record<string, unknown>[];
  recent_incidents: Record<string, unknown>[];
  graph_neighborhood: Record<string, unknown>[];
  retrieved_evidence: Record<string, unknown>[];
  contradictions: string[];
  excluded_material: string[];
  provenance_manifest: string[];
  context_hash: string;
}

export interface PlanGraphPacket {
  packet_type: "PlanGraphPacket";
  target_outcome: string;
  milestones: string[];
  dependencies: string[];
  parallel_groups: string[][];
  acceptance_predicates: string[];
  rollback_points: string[];
  assumptions: string[];
  risks: string[];
  founder_decisions_required: string[];
  recommended_runway: string;
  critic_status: "PENDING" | "PASSED" | "FAILED";
}

export interface WorkPacketMesh {
  action_id: string;
  goal_id: string;
  decision_id: string;
  commitment_id: string;
  why_now: string;
  executor_class: "RUNWAY_GOAL_KERNEL" | "FBE_RAILWAY" | "CF_LIGHT";
  inputs: Record<string, unknown>;
  allowed_capabilities: string[];
  forbidden_capabilities: string[];
  acceptance_predicates: string[];
  evidence_required: string[];
  budget: {
    max_attempts: number;
    max_minutes: number;
    max_cost_usd: number;
    max_fanout: number;
  };
  rollback_policy: string;
  failure_policy: string;
  execution_idempotency_key: string;
}

export interface ExecutiveRun {
  run_id: string;
  status: RunStatus;
  terminal: Terminal | null;
  snapshot_version: number;
  correlation_id: string;
  idempotency_key: string;
  event: EventEnvelope;
  context_pack: ContextPack | null;
  role_packets: RoleDecisionPacket[];
  plan: PlanGraphPacket | null;
  decision_id: string | null;
  decision_hash: string | null;
  work_packet: WorkPacketMesh | null;
  evidence: { evidence_id: string; kind: string; valid: boolean; detail: string }[];
  commitment_id: string | null;
  commitment_status: "OPEN" | "CLOSED" | null;
  digest: Record<string, unknown> | null;
  audit: { at: string; kind: string; detail: Record<string, unknown> }[];
  stale_rejected: boolean;
}

export const WEBPAGE_REPAIR_POLICY = {
  decision_class: "WEBPAGE_REPAIR",
  policy_version: "webpage_repair.v1.live.185ec3865a14",
  body: {
    when: { task_type: "webpage_repair", risk: "low_or_medium" },
    select: {
      workflow: "deterministic_web_repair_v1",
      executor: "cheapest_passing_executor",
    },
    limits: { max_files: 5, max_attempts: 2, max_fanout: 0 },
    verify: [
      "build_passes",
      "visual_diff_present",
      "target_issue_absent",
      "unrelated_pages_unchanged",
    ],
    escalate_when: [
      "positioning_change_detected",
      "protected_file_required",
      "two_distinct_plans_failed",
    ],
  },
};
