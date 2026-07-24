# SourceA Executive Control Plane v0

Deterministic, memory-bearing **Executive Office** kernel.

> Same State + Same Event + Same Policy Version = Same Decision

This is **not** an agent framework. There is no LLM on the decision path, no network, no Cloudflare Durable Object in v0.

Authority: `NF-EXECUTIVE-CONTROL-PLANE-V0` (SG lock).

## Architecture

```text
Event → reconcile → Goal / Commitment / Drift
  → PolicyEngine (known class) or RED/AMBER
  → ConflictResolver
  → ExecutiveGovernor (one DecisionResult)
  → NextActionCompiler → WorkPacket
  → Executor (untrusted, outside this package)
  → EvidenceVerifier → close Commitment or Incident
```

| Module | Role |
|--------|------|
| ExecutiveGovernor | Applies policy; never executes |
| GoalController | Active / frozen / achieved goals |
| CommitmentController | OPEN commitments require evidence to close |
| ConflictResolver | Fixed precedence; Founder Decision Packet when unresolvable |
| DriftMonitor | GOAL / SCOPE / AUTHORITY / BUDGET / EVIDENCE / FOUNDER_INTENT |
| NextActionCompiler | Approved DecisionRecord → typed WorkPacket |
| EvidenceVerifier | Mechanical DONE; agent-says-done is invalid |
| IncidentMotor | Repeated failure, zero progress, Human Tax, out-of-scope, … |

## Decision zones

- **GREEN** — known reversible policy; Governor may finalize.
- **AMBER** — needs plan + critic evidence before finalize.
- **RED** — irreversible / governance / unknown class → `RED_ZONE_REQUIRED` + Founder Decision Packet.

## Invariants

1. No `ACTIVE_FOREVER` work.
2. Executors cannot mutate canonical state.
3. Plan proposals are stored as `untrusted: true` only.
4. `max_fanout: 0` forbids `spawn:subagents`.
5. Live Decision Capacity policies for `WEBPAGE_CHANGE` / `WEBPAGE_REPAIR` seed GREEN fixtures.

## Example state (minimal)

```ts
import { createInitialState, addGoal, ingestEvent, compileNextAction } from "./src/index.ts";

let s = createInitialState();
s = addGoal(s, {
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
  budgets: { max_attempts: 2, max_minutes: 30, max_cost_usd: 1.5, max_fanout: 0, max_human_tax_units: 5 },
});
s = ingestEvent(s, {
  type: "TASK_REQUEST",
  goal_id: "goal_18",
  decision_class: "WEBPAGE_REPAIR",
  intent: "repair page",
  reversible: true,
});
const { packet } = compileNextAction(s, s.last_decision_result!.decision!);
```

## Example WorkPacket fields

- `executor_class`, `allowed_capabilities`, `forbidden_capabilities`
- `acceptance_predicates`, `evidence_required`
- `budget.max_attempts|max_minutes|max_cost_usd|max_fanout`
- `on_failure`, `rollback_policy`

## How a future Advisor submits an untrusted proposal

```ts
ingestEvent(state, {
  type: "PLAN_PROPOSAL",
  plan: {
    plan_id: "plan_204",
    goal_id: "goal_18",
    assumptions: ["..."],
    candidate_actions: ["..."],
    risks: [],
    success_predicates: [],
    founder_decisions_required: [],
    source_decision_ids: [],
  },
});
```

The plan is appended to `state.plans` with `untrusted: true`. Goals, policies, and decisions are **not** mutated by this event. Only the Governor (policy / Founder decision path) may approve work.

## Test

```bash
cd packages/executive-control-plane-v0
npm install
npm test
```

## Known limitations (v0)

- In-memory only (no DB).
- No Cloudflare / pulse motor.
- No Runway GoalDO import.
- Planner/Critic are input events only; no model calls.
