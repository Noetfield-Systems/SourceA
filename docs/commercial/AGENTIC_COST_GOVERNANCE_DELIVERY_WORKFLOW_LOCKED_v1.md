# Agentic Cost Governance — Delivery workflow (LOCKED v1)

**Version:** 1.0.0 LOCKED  
**Saved at:** 2026-07-05T00:55:00Z  
**SourceA lane:** Audit kit execution + firewall pilot operation  
**Handoff points:** Noetfield (buyer framing) ↔ NOOS (status tracking) ↔ SG (policy canon)

---

## One sentence

> SourceA runs the 5-phase audit workflow (intake → inventory → analysis → policy → pilot); Noetfield frames it as commercial service; NOOS tracks status; SG records policy canon.

---

## 5-phase workflow

### PHASE 1: Intake (T+0 to T+1)

**What happens:**
1. Noetfield sends client to SourceA intake form (web link / email)
2. Client fills: company, team, AI tools, spend tracking, budget constraints
3. SourceA Worker receives intake → stores in `~/.sina/agentic-cost-governance-intake-[client_id]-v1.json`
4. SourceA Brain confirms receipt → email Noetfield + client

**Artifacts:**
- `agentic-cost-governance-intake-v1.json` (template + instance)
- Intake receipt email
- Audit scope document (generated)

**Timeline:** 24 hours  
**Owner:** SourceA Worker (intake form) · Noetfield (client outreach)  
**Blockers:** None at Phase 1

---

### PHASE 2: Audit (T+1 to T+5)

**What happens:**
1. SourceA sends client follow-up forms: tool inventory + API inventory + spend surface map
2. Client/team fills forms (async, 3–4 days typical)
3. SourceA Worker collects responses → processes inventories
4. SourceA Brain runs leakage checklist + escalation risk checklist
5. SourceA generates findings: identified_gaps[], spend leaks, risk matrix

**Artifacts:**
- `agentic-cost-governance-tool-inventory-[client_id]-v1.json`
- `agentic-cost-governance-api-inventory-[client_id]-v1.json`
- `agentic-cost-governance-spend-surface-map-[client_id]-v1.json`
- `agentic-cost-governance-leakage-checklist-[client_id]-v1.json` (results)
- `agentic-cost-governance-escalation-risk-[client_id]-v1.json` (results)
- Interim audit report (shared with Noetfield + client for review)

**Timeline:** 4 days  
**Owner:** SourceA Worker + Brain (analysis) · Client (inventory data)  
**Blockers:**
- Client slow to respond to inventory forms → 3-day grace, then SourceA estimates from available data

---

### PHASE 3: Policy design (T+5 to T+6)

**What happens:**
1. SourceA auditor customizes routing policy: tiers, triggers, escalation rules (based on findings)
2. SourceA generates budget caps per workflow + org total (based on leakage analysis + client budget)
3. Client + Noetfield review + approve policy (24h async review)
4. SourceA signs policy effective → generates receipt

**Artifacts:**
- `PREMIUM_MODEL_FIREWALL_ROUTING_POLICY-[client_id]-LOCKED-v1.md` (customized)
- `AGENTIC_BUDGET_CAP_POLICY-[client_id]-LOCKED-v1.md` (customized)
- Policy approval receipt (signed by client + Noetfield)

**Timeline:** 1 day (24h review window)  
**Owner:** SourceA Brain (design) · Noetfield (buyer framing) · Client (approval)  
**Blockers:**
- Client denies policy → SourceA + Noetfield discuss revisions (back to design, 2-day impact)

---

### PHASE 4: Firewall deployment (T+6 to T+7)

**What happens:**
1. SourceA Engineer wires firewall rules to client's API layer (or proxy layer)
2. 7-day test run: firewall active on **test workflows only** (no end-user impact)
3. SourceA logs all test calls, alerts, and approvals
4. Team reviews test results: false positives, approval latencies, spend accuracy
5. If SLAs pass → firewall goes live on all workflows (Day 1 of 30-day pilot)

**Artifacts:**
- Firewall deployment receipt (test run validation)
- Test run logs (all API calls, policy decisions)
- Pre-flight checklist (all items complete)

**Timeline:** 1 day  
**Owner:** SourceA Engineer + Brain  
**Blockers:**
- False positive rate > 5% → SourceA tunes policy rules, 2-day delay
- Approval workflow latency > 4h on Tier 3 → SourceA adds Slack/email retry, 1-day delay

---

### PHASE 5: Pilot execution & monitoring (T+7 to T+37, 30 days)

**What happens:**
1. Firewall rules live on all workflows
2. Every API call logged: model, cost, approval status, requester
3. Daily spend snapshot email sent to Finance + ops lead
4. Alerts triggered: 70% cap → warning · 90% cap → approval required · 100% cap → hard stop
5. SourceA monitors + adjusts policy (e.g., Tier 3 triggers too sensitive)
6. Client team reviews daily snapshots + approves escalations
7. SourceA logs everything in audit trail (immutable)

**Artifacts:**
- Daily spend snapshots (email + dashboard)
- Audit log (all API calls + policy decisions)
- Exception requests (customer emergency, batch jobs)
- Weekly summary (compliance %, cost trend)

**Timeline:** 30 days  
**Owner:** SourceA Brain (monitoring) · Client (approvals) · Finance (budget tracking)  
**Blockers:**
- Firewall breaks customer workflow → 15-min manual override + post-incident review
- Cost overages not explained → daily snapshot review with client ops

---

## Phase 6: Final report & handoff (T+37 to T+40)

**What happens:**
1. SourceA compiles final report: cost reduction %, compliance %, incidents
2. SourceA generates recommendations: policy hardening, tool consolidation, long-term governance
3. Noetfield presents report to client (customer-facing framing)
4. Decision: keep firewall + annual monitoring contract · OR sunset + manual controls

**Artifacts:**
- Final report (30-day metrics + recommendations)
- Audit trail export (immutable log)
- Policy amendment recommendations
- Monitoring contract (if client chooses to continue)

**Timeline:** 3 days  
**Owner:** SourceA Brain (report) · Noetfield (client presentation)

---

## Delivery boundaries

| Layer | Owns | Does NOT own |
|-------|------|-------------|
| **SourceA (factory)** | Audit kit · firewall logic · logging · policy enforcement | Buyer comms · contract negotiation · renewal · strategic positioning |
| **Noetfield (commercial)** | Client relationship · pricing · contract · "cost governance" framing | Policy design · firewall rules · audit analysis · implementation |
| **NOOS (status)** | Audit start/end dates · client name · phase status · spend metrics | Detailed audit data · policy rules · customer communications |
| **SG (canon)** | Policy snapshots (final version) · SLAs · team roles | Day-to-day operation · exceptions · test logs |

---

## Handoff protocols

### Noetfield → SourceA (intake start)

**Input:** Client contact + company + primary AI use case  
**Format:** Slack DM to `#sourcea-intake` or email to `sourcea-audits@sourcea.app`

**Example:**
```
Client: Acme Corp
Contact: jane@acme.com
Size: 50 people
Primary AI: customer support chatbot (ChatGPT)
Budget: $5K/month target
Constraint: CASL compliance (Canada)
Timeline: Audit by July 20
```

**SourceA response:** Within 4h, send intake link to Noetfield + client

---

### Audit phase → Noetfield (interim report)

**When:** End of Phase 2 (T+5)  
**Output:** Interim audit report (findings, gaps, spend leaks)  
**Format:** PDF + Slack summary

**Example:**
```
INTERIM AUDIT REPORT — Acme Corp

Findings:
  • ChatGPT usage: $2,500/mo (50% of budget)
  • GPT-4 used for simple classification (could be GPT-3.5): $400/mo leak
  • 3 orphaned API keys (2024) still active: $150/mo wasted
  • No spend visibility (currently estimated): risk = unknown $

Potential savings: $550/mo (11% reduction)
Estimated firewall ROI: 3.5 months

Policy recommendation: 3-tier routing · $300/mo per-workflow caps
```

**Noetfield action:** Review with client, discuss firewall interest

---

### Policy approved → SourceA (deployment ready)

**When:** End of Phase 3 (T+6)  
**Input:** Client + Noetfield approval signature  
**Format:** Email with signed policy + budget caps + deployment date

**SourceA action:** Wire firewall rules, start test run

---

### Pilot complete → Noetfield (final report)

**When:** End of Phase 5 + Phase 6 (T+40)  
**Output:** Final report + recommendations  
**Format:** Presentation deck + detailed metrics

**Example metrics:**
```
FINAL REPORT — Acme Corp

Cost reduction: 18% ($900/mo savings) ✓
Compliance: 98% of calls routed per policy ✓
Customer impact: 0 incidents ✓
Approval SLA: Avg 6h (Tier 2) · 2h (Tier 3) ✓

Recommendations:
  • Consolidate to 2 tools (remove Gemini trial)
  • Deploy Tier 2 approval workflow to Slack
  • Set annual budget resets (not monthly)
  • Assign AI spend owner (CFO or ops lead)

Next: Annual monitoring contract + quarterly policy reviews
```

**Noetfield action:** Present to client, discuss annual contract

---

## Data flow & receipts

```
Intake form
    ↓
~/.sina/agentic-cost-governance-intake-[client_id]-v1.json
    ↓
Inventory forms (tool + API + spend)
    ↓
~/.sina/agentic-cost-governance-[type]-[client_id]-v1.json (3 files)
    ↓
Leakage + escalation checklists (run by Brain)
    ↓
~/.sina/agentic-cost-governance-findings-[client_id]-v1.json
    ↓
Interim report (send to Noetfield + client)
    ↓
Policy customization + approval
    ↓
~/noetfield-secrets/agentic-firewall-policies/POLICY-[client_id]-LOCKED-v1.md
    ↓
Firewall deployment test run (7 days)
    ↓
~/.sina/agentic-cost-governance-firewall-testrun-[client_id]-v1.json
    ↓
Live pilot (30 days)
    ↓
~/.sina/agentic-cost-governance-audit-log-[client_id]-v1.json (immutable, append-only)
~/.sina/agentic-cost-governance-daily-snapshot-[client_id]-[date]-v1.json (daily)
    ↓
Final report + recommendations
    ↓
SG canon: policy snapshot + SLAs
NOOS: audit dates + client name + phase status
```

---

## Law

- **No claims** of "deployed firewall" until pilot is complete + receipted
- **All audit data immutable** — append-only JSON, never overwrite
- **Client approval required** at Phase 3 before firewall deployment
- **Firewall test run mandatory** — 7 days before go-live
- **Daily spend reporting** — no exceptions, automatic email
- **Budget caps hard stops** — 429 response on overages
- **Escalation automatic** — CFO alerted within 1h of cap breach

---

## Timeline summary

| Phase | Duration | Owner | Blocker risk |
|-------|----------|-------|--------------|
| 1. Intake | 1 day | Worker | Low |
| 2. Audit | 4 days | Worker + Brain | Low (client response time) |
| 3. Policy | 1 day | Brain + Noetfield | Medium (approval delay) |
| 4. Deploy | 1 day | Engineer + Brain | Low–Medium (false positives) |
| 5. Pilot | 30 days | Brain + Client | Low (ongoing monitoring) |
| 6. Report | 3 days | Brain + Noetfield | Low |
| **TOTAL** | **~40 days** | | |

---

## Next: Noetfield handoff document
