/** Domain objects — SourceA Executive Control Plane v0 */

export type DecisionZone = "GREEN" | "AMBER" | "RED";
export type GoalStatus =
  | "ACTIVE"
  | "BLOCKED"
  | "ACHIEVED"
  | "ABANDONED"
  | "SUPERSEDED"
  | "FROZEN";
export type CommitmentStatus = "OPEN" | "BLOCKED" | "STALLED" | "CLOSED" | "OVERDUE";
export type DriftKind =
  | "GOAL_DRIFT"
  | "SCOPE_DRIFT"
  | "AUTHORITY_DRIFT"
  | "BUDGET_DRIFT"
  | "EVIDENCE_DRIFT"
  | "FOUNDER_INTENT_DRIFT"
  | "ARCHITECTURE_DRIFT";

export interface FounderCharter {
  schema: "noetfield.executive.founder_charter.v0";
  charter_id: string;
  version: string;
  non_negotiables: string[];
  red_zone_classes: string[];
  delegation_envelope: {
    max_cost_usd: number;
    allow_irreversible: boolean;
    allow_external_commitment: boolean;
    allow_governance_change: boolean;
  };
  created_at: string;
  updated_at: string;
}

export interface GoalContract {
  schema: "noetfield.executive.goal_contract.v0";
  goal_id: string;
  version: string;
  authority_hash: string;
  intent: string;
  decision_class: string;
  status: GoalStatus;
  scope_allowlist: string[];
  forbidden_effects: string[];
  acceptance_predicates: string[];
  evidence_required: string[];
  budgets: {
    max_attempts: number;
    max_minutes: number;
    max_cost_usd: number;
    max_fanout: number;
    max_human_tax_units: number;
  };
  created_at: string;
  updated_at: string;
  source_decision_ids: string[];
}

export interface DecisionPolicy {
  schema: "noetfield.executive.decision_policy.v0";
  policy_id: string;
  version: string;
  decision_class: string;
  policy_version: string;
  zone: DecisionZone;
  reversible: boolean;
  body: {
    when: Record<string, string>;
    select: Record<string, string>;
    limits: Record<string, number>;
    verify: string[];
    escalate_when: string[];
  };
  created_at: string;
  updated_at: string;
}

export interface DecisionRecord {
  schema: "noetfield.executive.decision_record.v0";
  decision_id: string;
  version: string;
  zone: DecisionZone;
  goal_id: string;
  decision_class: string;
  policy_version: string;
  status: "APPROVED" | "RED_ZONE_REQUIRED" | "REJECTED";
  action_summary: string;
  created_at: string;
  updated_at: string;
  source_decision_ids: string[];
  founder_decision?: boolean;
}

export interface PlanRecord {
  schema: "noetfield.executive.plan_record.v0";
  plan_id: string;
  version: string;
  goal_id: string;
  untrusted: true;
  assumptions: string[];
  candidate_actions: string[];
  risks: string[];
  success_predicates: string[];
  founder_decisions_required: string[];
  created_at: string;
  updated_at: string;
  source_decision_ids: string[];
}

export interface Commitment {
  schema: "noetfield.executive.commitment.v0";
  commitment_id: string;
  version: string;
  decision_id: string;
  goal_id: string;
  owner: string;
  due_at: string | null;
  required_artifact: string;
  status: CommitmentStatus;
  dependencies: string[];
  max_silence_minutes: number;
  created_at: string;
  updated_at: string;
  source_decision_ids: string[];
}

export interface ConflictRecord {
  schema: "noetfield.executive.conflict_record.v0";
  conflict_id: string;
  version: string;
  kind: string;
  left_ref: string;
  right_ref: string;
  resolved: boolean;
  resolution: string | null;
  created_at: string;
  updated_at: string;
  source_decision_ids: string[];
}

export interface CapabilityGrant {
  schema: "noetfield.executive.capability_grant.v0";
  grant_id: string;
  version: string;
  allowed: string[];
  forbidden: string[];
  created_at: string;
  updated_at: string;
  source_decision_ids: string[];
}

export interface WorkPacket {
  schema: "noetfield.executive.work_packet.v0";
  action_id: string;
  version: string;
  goal_id: string;
  decision_id: string;
  plan_step_id: string | null;
  why_now: string;
  executor_class: string;
  inputs: Record<string, unknown>[];
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
  on_failure: string;
  rollback_policy: string;
  status: "OPEN" | "STOPPED" | "ACCEPTED" | "FAILED" | "FROZEN";
  zero_progress_cycles: number;
  created_at: string;
  updated_at: string;
  source_decision_ids: string[];
}

export interface EvidenceReceipt {
  schema: "noetfield.executive.evidence_receipt.v0";
  evidence_id: string;
  version: string;
  work_packet_id: string;
  kind: string;
  valid: boolean;
  detail: string;
  created_at: string;
  updated_at: string;
  source_decision_ids: string[];
}

export interface DriftFinding {
  schema: "noetfield.executive.drift_finding.v0";
  finding_id: string;
  version: string;
  drift_kind: DriftKind;
  goal_id: string | null;
  detail: string;
  created_at: string;
  updated_at: string;
  source_decision_ids: string[];
}

export interface IncidentRecord {
  schema: "noetfield.executive.incident_record.v0";
  incident_id: string;
  version: string;
  reason:
    | "REPEATED_FAILURE"
    | "ZERO_PROGRESS"
    | "HUMAN_TAX_BREACH"
    | "UNAUTHORIZED_CAPABILITY"
    | "FALSE_COMPLETION"
    | "UNRESOLVED_CONFLICT"
    | "OUT_OF_SCOPE"
    | "NO_ACTIVE_GOAL"
    | "REJECTED_TASK";
  goal_id: string | null;
  work_packet_id: string | null;
  detail: string;
  created_at: string;
  updated_at: string;
  source_decision_ids: string[];
}

export interface AuditEvent {
  schema: "noetfield.executive.audit_event.v0";
  audit_id: string;
  at: string;
  kind: string;
  detail: Record<string, unknown>;
}

export interface DecisionResult {
  schema: "noetfield.executive.decision_result.v0";
  result_id: string;
  zone: DecisionZone;
  status: "APPROVED" | "RED_ZONE_REQUIRED" | "REJECTED" | "FROZEN";
  decision_hash: string;
  policy_version: string;
  rationale: string;
  decision: DecisionRecord | null;
  founder_packet_id: string | null;
  created_at: string;
}

export interface FounderDecisionPacket {
  schema: "noetfield.executive.founder_decision_packet.v0";
  packet_id: string;
  version: string;
  topic: string;
  what_changed: string;
  options: { id: string; label: string; risk: string }[];
  sg_recommendation: string;
  critic_view: string;
  risk_if_delayed: string;
  safest_interim_action: string;
  created_at: string;
  updated_at: string;
  source_decision_ids: string[];
}

export interface CanonicalState {
  schema: "noetfield.executive.canonical_state.v0";
  state_id: string;
  version: string;
  policy_bundle_version: string;
  created_at: string;
  updated_at: string;
  charter: FounderCharter;
  goals: GoalContract[];
  policies: DecisionPolicy[];
  decisions: DecisionRecord[];
  plans: PlanRecord[];
  commitments: Commitment[];
  conflicts: ConflictRecord[];
  work_packets: WorkPacket[];
  evidence: EvidenceReceipt[];
  drifts: DriftFinding[];
  incidents: IncidentRecord[];
  founder_packets: FounderDecisionPacket[];
  human_tax_units: number;
  failure_signatures: Record<string, number>;
  audit: AuditEvent[];
  last_decision_result: DecisionResult | null;
}

export type ExecutiveEvent =
  | { type: "TASK_REQUEST"; goal_id?: string; decision_class: string; intent: string; reversible?: boolean; irreversible?: boolean; governance_change?: boolean; scope_paths?: string[] }
  | { type: "FOUNDER_DECISION"; decision: Omit<DecisionRecord, "schema" | "created_at" | "updated_at" | "version"> & { version?: string } }
  | { type: "PLAN_PROPOSAL"; plan: Omit<PlanRecord, "schema" | "untrusted" | "created_at" | "updated_at" | "version"> & { version?: string } }
  | { type: "EXECUTOR_CLAIM_DONE"; work_packet_id: string; claim_only?: boolean }
  | { type: "EVIDENCE_SUBMITTED"; evidence: Omit<EvidenceReceipt, "schema" | "created_at" | "updated_at" | "version"> & { version?: string } }
  | { type: "FAILURE_OBSERVED"; work_packet_id: string; signature: string }
  | { type: "PROGRESS_CHECK"; work_packet_id: string; verified_progress: boolean }
  | { type: "HUMAN_TAX"; units: number; goal_id?: string }
  | { type: "OUT_OF_SCOPE_MUTATION"; goal_id: string; path: string }
  | { type: "SPAWN_SUBAGENTS_ATTEMPT"; work_packet_id: string }
  | { type: "CONFLICT_RAISED"; kind: string; left_ref: string; right_ref: string };
