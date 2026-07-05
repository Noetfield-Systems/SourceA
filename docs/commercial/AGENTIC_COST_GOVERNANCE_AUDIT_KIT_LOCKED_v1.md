# Agentic Cost Governance — Audit Kit (LOCKED v1)

**Version:** 1.0.0 LOCKED  
**Saved at:** 2026-07-05T00:45:00Z  
**Authority:** SourceA delivery factory  
**Service:** AI Spend Leak Audit + Premium Model Firewall pilot  
**Delivery lane:** Noetfield commercial (buyer-facing) ↔ SourceA (audit/firewall factory) ↔ NOOS (status) ↔ SG (canon)  

---

## One sentence

> Audit an org's AI tool usage, model costs, and routing to find spend leaks, then deploy a Premium Model Firewall to enforce cheap-first + escalation rules with budget caps and approval workflows.

---

## Service definition

| Element | Lock |
|---------|------|
| **Deliverable** | Audit report + firewall policy + 30-day monitoring receipt |
| **Duration** | 5–7 day audit · 30-day pilot · final report |
| **Cost** | $2–5K (scope on discovery) |
| **Success criteria** | Identify ≥2 spend leaks · policy enforcement ≥95% · zero production incidents |
| **Buyer outcome** | Model routing governance · cost visibility · predictable AI spend |

---

## 10-artifact audit kit

### 1. Client intake checklist

**File:** `data/agentic-cost-governance-intake-v1.json`

**Captures:**
- Client name · org size · primary AI use cases
- Current AI tools (ChatGPT, Claude, Gemini, etc.) · licenses/keys
- Spend tracking method (or none)
- Budget constraints · cost sensitivity
- Approval chains for premium models
- Compliance/policy requirements
- Integration points (SaaS · API · internal tools)

**Output:** Intake receipt with client_id + audit_scope

---

### 2. AI tool inventory template

**File:** `data/agentic-cost-governance-tool-inventory-v1.json`

**Columns:**
- Tool name (ChatGPT, Claude, Gemini, Llama, etc.)
- Current license tier
- Monthly cost (actual or estimate)
- Users/seats
- Primary workflows (content, code, analysis, etc.)
- Model version (GPT-4, Claude 3.5, etc.)
- Usage pattern (ad-hoc / batch / scheduled)
- Integration (UI / API / plugin)

**Audit rule:** Cross-reference against spend receipts + team interviews

---

### 3. API key/workflow inventory

**File:** `data/agentic-cost-governance-api-inventory-v1.json`

**Captures:**
- API key location (dev machine / server / env var / secret manager)
- Associated tool + tier
- Usage scope (development / QA / production)
- Rotation age (last rotated)
- Access control (who has key)
- Rate limits (if any)
- Spend tracking enabled? (Y/N)

**Audit rule:** Find orphaned keys, untracked APIs, shared credentials

---

### 4. Automation spend surface map

**File:** `data/agentic-cost-governance-spend-surface-map-v1.json`

**Maps:**
- Each integration point → connected AI tool
- Monthly API calls / tokens per integration
- Cost per call · monthly projection
- Frequency (how often runs)
- Owner/team responsible
- Alert threshold (spend cap per workflow)

**Example:**
```
{
  "integration": "customer-support-chatbot",
  "tool": "gpt-4-turbo",
  "calls_monthly": 5000,
  "cost_per_1k_tokens": 0.03,
  "projected_monthly": 150,
  "frequency": "continuous",
  "owner": "support-team",
  "alert_cap": 200
}
```

---

### 5. Premium model leakage checklist

**File:** `data/agentic-cost-governance-leakage-checklist-v1.json`

**Audit questions:**
- [ ] Are premium models (GPT-4, Claude Opus) used for low-complexity tasks (e.g., classify email subject)?
- [ ] Are batch jobs using real-time API instead of batch endpoints?
- [ ] Do workflows have fallback to cheaper models?
- [ ] Are prompts optimized for token count (or verbose)?
- [ ] Is context caching enabled where applicable?
- [ ] Are high-cost models used in development/testing?
- [ ] Do multiple teams pay for overlapping tool licenses?
- [ ] Is there unused/trial tool access still active?

**Output:** Leakage_score (0–100) · identified_gaps[] · estimated_savings

---

### 6. Fallback/escalation risk checklist

**File:** `data/agentic-cost-governance-escalation-risk-v1.json`

**Audit questions:**
- [ ] If cheap model (GPT-3.5) fails, does workflow error or escalate silently to expensive model?
- [ ] Are there retry loops without backoff that multiply API costs?
- [ ] Do workflows degrade gracefully on high latency?
- [ ] Is there manual override allowing bypass of cost controls?
- [ ] Are there unmonitored escalation paths (e.g., ops engineer can use any model)?
- [ ] What happens if approval workflow times out?

**Output:** Risk_matrix[] · incident_scenarios[] · mitigation_plan[]

---

### 7. Model routing policy template

**File:** `docs/commercial/PREMIUM_MODEL_FIREWALL_ROUTING_POLICY_LOCKED_v1.md`

**Structure:**
```
# Routing Policy (default cheap → escalate on signal)

## Layer 1 (Default)
Model: gpt-3.5-turbo (or org cheap tier)
Usage: standard tasks · high volume · testing
Cost cap: $0.003 per 1K tokens
No approval needed

## Layer 2 (Escalation signal)
Model: gpt-4 / claude-3-sonnet
Trigger: task_type = "analysis" OR tokens_projected > 2000
Cost cap: $0.03 per 1K tokens
Manager approval: required
Reason field: mandatory

## Layer 3 (Premium/urgent)
Model: gpt-4-turbo / claude-3-opus
Trigger: task_type = "strategic" OR customer-facing OR time_critical
Cost cap: $0.15 per 1K tokens
VP approval: required
Business case field: mandatory
```

**Policy enforcement:** Check task metadata before API call · log all escalations · track approval chain

---

### 8. Budget cap policy template

**File:** `docs/commercial/AGENTIC_BUDGET_CAP_POLICY_LOCKED_v1.md`

**Defines:**
- Org-wide monthly AI spend cap
- Per-workflow caps
- Per-team caps
- Per-tool caps
- Grace period before hard stop (alert → 24h warning → block)
- Escalation workflow (team → manager → CFO if exceeded)
- Reporting cadence (daily spend snapshot)

**Example:**
```
Org cap: $5K/month
Support team: $800/month
Dev team: $2K/month
Each API call checks: (total_spend + projected_call_cost) < cap
If over: return 429 Too Many Requests + alert + escalate
```

---

### 9. Receipt/audit log template

**File:** `data/agentic-cost-governance-audit-log-v1.json`

**Logs every:**
- API call (timestamp, tool, model, tokens, cost, requester)
- Policy check (model, decision: allowed/escalated/blocked, reason)
- Approval event (approval_id, requester, approver, decision, business_case)
- Spend alert (threshold_exceeded, cap, current_spend, action_taken)
- Firewall rule update (policy_id, change, effective_date)

**Output:** Immutable audit trail for compliance + invoice reconciliation

---

### 10. Final report template

**File:** `docs/commercial/AGENTIC_AUDIT_FINAL_REPORT_TEMPLATE_LOCKED_v1.md`

**Sections:**
1. Executive summary (spend trend, leaks found, savings potential)
2. Current state (tools, costs, usage patterns)
3. Leakage analysis (5 gaps found, $XXK/month savings)
4. Firewall policy (routing rules deployed, approval flow)
5. 30-day pilot results (cost reduction %, compliance %, incidents)
6. Recommendations (long-term governance, tool consolidation)
7. Next steps (policy hardening, team training, monitoring)

---

## Delivery packet registry

| Artifact | Path | Format | Status |
|----------|------|--------|--------|
| Intake checklist | `data/agentic-cost-governance-intake-v1.json` | JSON | **TEMPLATE** |
| Tool inventory | `data/agentic-cost-governance-tool-inventory-v1.json` | JSON | **TEMPLATE** |
| API inventory | `data/agentic-cost-governance-api-inventory-v1.json` | JSON | **TEMPLATE** |
| Spend surface map | `data/agentic-cost-governance-spend-surface-map-v1.json` | JSON | **TEMPLATE** |
| Leakage checklist | `data/agentic-cost-governance-leakage-checklist-v1.json` | JSON | **TEMPLATE** |
| Escalation risk | `data/agentic-cost-governance-escalation-risk-v1.json` | JSON | **TEMPLATE** |
| Routing policy | `docs/commercial/PREMIUM_MODEL_FIREWALL_ROUTING_POLICY_LOCKED_v1.md` | MD | **TEMPLATE** |
| Budget policy | `docs/commercial/AGENTIC_BUDGET_CAP_POLICY_LOCKED_v1.md` | MD | **TEMPLATE** |
| Audit log | `data/agentic-cost-governance-audit-log-v1.json` | JSON | **TEMPLATE** |
| Final report | `docs/commercial/AGENTIC_AUDIT_FINAL_REPORT_TEMPLATE_LOCKED_v1.md` | MD | **TEMPLATE** |

---

## Workflow (SourceA factory)

**Phase 1: Intake (T+0 → T+1)**
1. Client fills intake checklist
2. SourceA Worker loads intake receipt → `agentic-cost-governance-intake-v1.json`
3. Generates audit_scope + client_id

**Phase 2: Audit (T+1 → T+5)**
1. Client/team completes tool inventory, API inventory, spend surface map
2. SourceA auditor runs leakage + escalation checklist
3. Generates findings report + identified_gaps[]

**Phase 3: Firewall policy (T+5 → T+6)**
1. SourceA generates routing policy + budget caps (customized per client)
2. Client approves policy (async, Noetfield handles buyer communication)
3. Policy signed into effect

**Phase 4: 30-day pilot (T+7 → T+37)**
1. SourceA deploys firewall rules to client's workflow layer
2. Audit log collects all model calls + policy decisions
3. Daily spend snapshots
4. Alert + escalation on budget overages

**Phase 5: Final report (T+37 → T+40)**
1. SourceA generates final report (cost reduction %, compliance %, incidents)
2. Policy effectiveness analysis
3. Recommendations for long-term governance

---

## Law

- **No production firewall** until tested in pilot and receipted
- **Client approval required** before policy enforcement (Noetfield handles buyer framing)
- **All audit logs immutable** — append-only JSON, never edit
- **Escalation alerts go to CFO/finance** — not buried in logs
- **Budget cap hard stops** — exceeded → 429 response + escalate
- **Monthly report sent to client** + SG for canon + NOOS for tracking

---

## Next: Premium Model Firewall pilot definition (see PREMIUM_MODEL_FIREWALL_PILOT_SCOPE_LOCKED_v1.md)
