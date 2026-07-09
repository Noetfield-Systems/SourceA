# Premium Model Firewall — Pilot scope (LOCKED v1)

**Version:** 1.0.0 LOCKED  
**Saved at:** 2026-07-05T00:50:00Z  
**Authority:** SourceA delivery factory  
**Parent:** `docs/commercial/AGENTIC_COST_GOVERNANCE_AUDIT_KIT_LOCKED_v1.md`  
**Status:** Design phase · not production yet (will be receipted after 30-day audit pilot)

---

## Pricing disclaimer

> Model names and per-token rates in this document are **examples only**. Routing uses **model class** (`tier1_cheap`, `tier2_standard`, `tier3_premium`) with `pricing_source: audit_time_live_lookup`. Replace `[audit_time_rate]` at discovery. No guaranteed savings. No production firewall without signed pilot scope.

---

## One sentence

> Cheap-first model routing: default to cheapest capable model, escalate to premium only when task signals require it, with manager approval and budget enforcement.

---

## 4-tier routing model

### Tier 1: Default (tier1_cheap)

**Model class:** `tier1_cheap`  
**Example model:** [client-defined cheap tier — not vendor-locked]

**Triggers:** Standard tasks, no special requirements

**Rules:**
```
IF task_type IN [classification, summarization, standard_chat]:
  ROUTE TO: model_class=tier1_cheap
COST: [audit_time_rate] USD per 1K tokens
APPROVAL: None required
BUDGET_CAP: Per-workflow limit (set at discovery)
LOG: {timestamp, task_id, model_class, tokens, cost, decision: "tier1_default"}
```

---

### Tier 2: Escalation signal (tier2_standard)

**Model class:** `tier2_standard`  
**Example model:** [client-defined standard premium — not vendor-locked]

**Triggers:**
- Task type = "analysis" OR "code_generation" OR "complex_reasoning"
- Projected token count > 2000
- Customer-facing output
- Business impact = "medium"
- Explicit user request (when dropdown available)

**Rules:**
```
IF (task_type IN [analysis, code, reasoning]) OR (tokens > 2000) OR (customer_facing=true):
  ROUTE TO: model_class=tier2_standard
COST: [audit_time_rate] USD per 1K tokens (relative to tier1 at audit)
APPROVAL: Required — async, manager approves within 24h
REASON_FIELD: Mandatory (why premium needed)
BUDGET_CAP: Per-workflow limit (e.g., $200/day)
LOG: {timestamp, task_id, model, tokens, cost, requester, reason, approval_status}
IF no_approval_after_24h: revert to Tier 1, notify requester
```

**Approval workflow:**
```
Manager (email/Slack): "Task ID X pending: reason=[user input]. Approve? Y/N"
If approved: run on gpt-4 + log approval_id + approver
If denied: revert to tier 1 + log denial reason
```

---

### Tier 3: Premium/urgent (tier3_premium)

**Model class:** `tier3_premium`  
**Example model:** [client-defined high-capability model — not vendor-locked]

**Triggers:**
- Task type = "strategic" OR "high_impact"
- Customer-critical OR time_sensitive
- Security/compliance decision required
- Business impact = "high" or "critical"

**Rules:**
```
IF (task_type IN [strategic, critical]) OR (impact=high):
  ROUTE TO: model_class=tier3_premium
COST: [audit_time_rate] USD per 1K tokens (relative to tier1 at audit)
APPROVAL: Required — VP or department head
BUSINESS_CASE_FIELD: Mandatory (detailed ROI/reason)
BUDGET_CAP: Per-project limit (e.g., $5K/month)
LOG: {timestamp, task_id, model, tokens, cost, requester, business_case, approver}
IF no_approval_within_4h: escalate to CFO, do not run
```

**Approval workflow:**
```
VP/Head (Slack): Task ID X urgent: [user business case]. Approve budget? Y/N
If approved: run on gpt-4-turbo + log + spend from project budget
If denied: fail task + escalate to CFO for review
```

---

### Tier 4: Blocked (cost control)

**Triggers:**
- Monthly spend cap exceeded
- Quota/per-workflow limit reached
- Policy violation (e.g., Tier 3 without approval attempt)
- Rate limit hit

**Rules:**
```
IF spend_total >= monthly_cap OR workflow_spend >= workflow_cap:
  RESPONSE: 429 Too Many Requests
NOTIFICATION: {spend_alert, current_spend, cap, next_reset}
ESCALATION: Alert CFO + Finance immediately
RECOVERY: Manual CFO approval to increase cap or reallocate budget
LOG: {timestamp, task_id, reason: "budget_exceeded", current_spend, cap, escalated_to}
```

---

## Spend receipt tracking

**Every API call logs:**
```json
{
  "call_id": "uuid",
  "timestamp": "2026-07-05T12:34:56Z",
  "task_id": "task-123",
  "requester": "alice@client.com",
  "model": "gpt-4",
  "tier": 2,
  "tokens_input": 1500,
  "tokens_output": 500,
  "cost_usd": 0.045,
  "decision": "tier2_approved",
  "approval_id": "appr-456",
  "approver": "manager@client.com",
  "reason": "complex data analysis required",
  "workflow": "customer-analytics",
  "monthly_cumulative": 543.21,
  "monthly_cap": 5000,
  "status": "completed"
}
```

---

## Workflow-level budget cap

**Each workflow gets a monthly ceiling:**

| Workflow | Monthly cap | Tier 1 cap | Tier 2 cap | Tier 3 cap |
|----------|-------------|-----------|-----------|-----------|
| Support chatbot | $300/mo | $250 | $50 | $0 (blocked) |
| Code generation | $800/mo | $400 | $350 | $50 |
| Strategic analysis | $2000/mo | $500 | $1000 | $500 |
| Customer reports | $500/mo | $300 | $150 | $50 |

**Rule:** Per-call check: `current_workflow_spend + projected_cost <= cap`

---

## Alert & exception policy

### Daily spend snapshot (automated email)

```
Subject: AI Spend Snapshot — [Client name] — [Date]

Org total: $123.45 (cap: $5000/mo)
  Tier 1: $50.00 (40%)
  Tier 2: $60.00 (49%)
  Tier 3: $13.45 (11%)

Top workflows:
  support-chatbot: $45.00
  code-gen: $38.00
  analytics: $18.50

Alerts:
  ⚠️ support-chatbot near cap ($245/$250)
  ✅ All other workflows normal

Next approval pending:
  → code-gen task #789 (12h) — $25 estimated
```

---

### Alert thresholds

| Condition | Action | Timeline |
|-----------|--------|----------|
| Workflow 70% of cap | Email to team lead | Immediate |
| Workflow 90% of cap | Email + manager approval required | 24h approval window |
| Workflow cap exceeded | 429 error + escalate to CFO | Immediate hard stop |
| Monthly org cap 80% | Finance/CFO notified | Daily report includes |
| Monthly org cap 95% | All Tier 2/3 require urgent CFO approval | Hard stop on new Tier 3 |

---

## Escalation/exception handling

**Legitimate overages (handle case-by-case):**

1. **Customer emergency** (e.g., security incident requiring urgent analysis)
   - Requester files exception request in Slack
   - Manager approves immediately + estimates cost
   - CFO gets alert within 1h
   - Retroactive budget adjustment after incident closes

2. **Batch job spike** (e.g., monthly reporting day)
   - Pre-approved recurring job
   - Budget automatically allocated for that day
   - Alert if actual > projected by >20%

3. **Policy change** (new task type discovered post-launch)
   - SourceA + Client agree on new tier routing
   - Policy update + new budget allocated
   - Effective immediately with CFO sign-off

---

## Pilot success criteria

| Metric | Target |
|--------|--------|
| Spend reduction (vs baseline) | ≥15% |
| Policy compliance rate | ≥95% |
| False positive blocks | <2% of attempted calls |
| Approval SLA (Tier 2) | <24h |
| Approval SLA (Tier 3) | <4h |
| Production incidents from firewall | 0 |
| Cost visibility accuracy | ≥99% |

---

## Implementation checklist (pilot)

- [ ] Intake complete + audit kit populated
- [ ] Leakage analysis done + gaps identified
- [ ] Routing policy approved by client + Noetfield
- [ ] Budget caps set per workflow + org total
- [ ] Approval workflow wired (Slack/email integration)
- [ ] Spend logging backend live
- [ ] Daily snapshot emails scheduled
- [ ] Alert system tested (no false positives)
- [ ] Exception handling documented
- [ ] Rollback procedure documented
- [ ] Firewall rules deployed to 1–2 test workflows
- [ ] 7-day test run (no end-users, SourceA + client ops only)
- [ ] Test results validated + SLAs confirmed
- [ ] Firewall rolled to all workflows (day 1 of 30-day pilot)

---

## Law

- **No production firewall claims** until this pilot is receipted
- **Cheap-first default** — no workflow routes to premium by default
- **Approval required for Tier 2+** — async, but enforced
- **Budget caps hard stops** — no soft warnings, 429 response
- **Immutable audit log** — every call logged, never edited
- **Daily financial reporting** — transparent spend tracking
- **CFO escalation automatic** — no buried exceptions

---

## Pilot duration

**Start:** After audit kit Phase 1 intake complete (T+1)  
**Duration:** 30 days of actual policy enforcement  
**End:** Final report generated, metrics validated, decision made (keep / harden / sunset)

---

## Next: SourceA delivery workflow (see AGENTIC_COST_GOVERNANCE_DELIVERY_WORKFLOW_LOCKED_v1.md)
