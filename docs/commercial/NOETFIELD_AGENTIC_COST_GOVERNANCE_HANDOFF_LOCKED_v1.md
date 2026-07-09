# Noetfield ← SourceA handoff: Agentic Cost Governance (LOCKED v1)

**Version:** 1.0.0 LOCKED  
**Saved at:** 2026-07-05T01:00:00Z  
**For:** Noetfield commercial team · Noetfield CTO · SG policy canon  
**From:** SourceA delivery factory

---

## What SourceA is delivering

SourceA has built a **turn-key audit kit + Premium Model Firewall pilot** for Noetfield to resell as a commercial service.

**Service name:** "Agentic Cost Governance" (or "AI Spend Leak Audit + Premium Model Firewall")

**Deliverables:**
1. **Audit kit** — 10 templates (intake, inventories, checklists, policies, reports)
2. **Firewall pilot** — cheap-first routing + escalation rules + budget caps
3. **Delivery workflow** — 5-phase audit + 30-day pilot + final reporting
4. **Execution authority** — SourceA runs audit + operates firewall for pilot period

---

## How to use this (Noetfield workflow)

### Step 1: Close the deal (Noetfield sales)

**Your pitch:**
- "AI Spend Leak Audit: we find leaks in your AI tool usage and deploy a firewall to enforce cost controls."
- "Investment: $2–5K (scope on discovery)"
- "Timeline: 5–7 day audit + 30-day pilot"
- "Outcome: 15%+ cost reduction · 95%+ policy compliance · zero incidents"

**Pricing notes:**
- Audit kit fixed cost (toolkit setup): $500
- Firewall pilot per-workflow: $100–500 per workflow (depends on integration complexity)
- Approval workflow setup: $200
- Daily monitoring + reporting: $100/month (optional yearly contract)

**Contract language (from SourceA):**
- Pilot is 30 days, after which client decides: keep + annual contract OR sunset
- Budget caps are hard stops — no exceptions except CFO approval
- SourceA provides audit logs immutable — compliance-ready

---

### Step 2: Intake (send to SourceA)

**When client signs:**

Send to SourceA Worker (Slack: `#sourcea-intake` or email: `sourcea-audits@sourcea.app`):
```
Client: [name]
Contact: [email]
Company: [industry]
Team size: [#]
Primary AI tools: [list]
Monthly AI spend (estimate): $[X]
Budget target: $[Y]
Constraints: [CASL, HIPAA, internal comms only, etc.]
Timeline: [prefer date range]
Your (Noetfield) contact: [your email for updates]
```

**SourceA response:** 4 hours, intake link sent to client

**Your next action:** Frame the intake to client as "SourceA will guide you through this."

---

### Step 3: Interim report (T+5)

**SourceA sends:** Interim audit report to you + client

**Your action:**
- Review findings (gaps + leakage)
- Share with client's finance/ops
- Discuss: "Ready to deploy a firewall? Let's see if this saves you money."

**If client is skeptical:**
- SourceA can estimate ROI (e.g., $400/mo GPT-4 leak could be $100 with routing policy)
- Low risk: 7-day test run before full deployment

---

### Step 4: Policy approval (T+6)

**SourceA sends:** Customized routing policy + budget caps

**Your action:**
- Review with client's CTO/CFO
- SourceA will include recommendation: "Start with conservative budgets, loosen after 2 weeks if all green"
- Get client signoff (email approval fine)
- Forward approval to SourceA

**If client requests changes:**
- Route to SourceA Brain (Slack: `#sourcea-audits`)
- Typical change: adjust Tier 2 triggers or per-workflow caps
- SourceA updates policy, resend for approval

---

### Step 5: Pilot launch (T+7)

**SourceA:** Deploys firewall, starts daily monitoring

**Your action:** Minimal
- Let client know: "Firewall is live. You'll get daily spend reports."
- If client has questions about daily snapshot email → forward to SourceA Brain

**If something breaks:**
- Client: "Firewall blocked our chatbot!"
- You: Notify SourceA immediately (Slack: `#sourcea-alerts`)
- SourceA: Manual override + post-incident review (typically 15 min fix)

---

### Step 6: Final report (T+40)

**SourceA sends:** Final report (cost %, compliance %, recommendations)

**Your action:**
- Present to client with Noetfield framing (e.g., "Here's how we reduced your AI costs by 18%")
- Discuss: "Ready for annual monitoring + policy reviews?"
- If yes → draft annual contract (Noetfield owns contract, SourceA operates firewall)

---

## What Noetfield owns

✅ **Client relationship** (Noetfield = primary contact)  
✅ **Contract + pricing** (You negotiate, sign)  
✅ **"Cost governance" brand** (Position as your service)  
✅ **Renewal / upsells** (Your sales process)  

---

## What SourceA owns

✅ **Audit kit templates** (in SourceA repo)  
✅ **Firewall logic + policies** (SourceA wires + operates)  
✅ **Audit logs + receipts** (SourceA maintains immutable trail)  
✅ **Daily monitoring** (SourceA sends snapshots)  
✅ **Approval workflows** (SourceA wires Slack/email integration)

---

## Key contact points

| Phase | SourceA contact | Noetfield action |
|-------|-----------------|-----------------|
| Intake | `sourcea-audits@sourcea.app` | Frame to client |
| Audit (T+1→T+5) | SourceA Brain monitors client response | Follow up on inventory forms |
| Interim report (T+5) | SourceA sends | Share with client finance |
| Policy review (T+6) | SourceA Brain customizes | Client approval + forward to SourceA |
| Firewall deploy (T+7) | SourceA Engineer wires | Notify client "live today" |
| Pilot (T+7→T+37) | SourceA Brain daily monitoring | Client questions → forward to SourceA |
| Final report (T+40) | SourceA sends | Present to client + discuss renewal |

---

## SG canon integration

**SourceA sends to SG (end of Phase 6):**
- Final customized policy (read-only reference)
- Audit timeline + SLAs met/not met
- Pilot success metrics (cost %, compliance %)
- Client confidentiality note: "Audit data is Noetfield/client property, not public"

**SG action:**
- Archive final policy snapshot
- Record: "Agentic Cost Governance v1 · Date range · Client · Metrics"
- Use as reference for next audit (patterns, leakage types, best practices)

---

## NOOS integration

**SourceA sends to NOOS (ongoing):**
- Intake start date
- Client name (for dashboard)
- Phase status updates (weekly)
- Pilot metrics (cost %, compliance %, incidents)
- Final completion + renewal decision

**NOOS dashboard shows:** "Acme Corp audit 60% complete (Phase 4 of 6)"

---

## Mistakes to avoid

❌ **"SourceA is building firewall" in sales deck** → Say "We're deploying a firewall YOU control"  
❌ **Promise firewall without pilot** → Always reference 30-day test  
❌ **Promise specific savings** → Say "15%+ typical, scope on audit"  
❌ **Approve policy without reviewing** → You own the client relationship  
❌ **Tell client SourceA is out of scope** → SourceA is your delivery partner, not invisible

✅ **"SourceA audits your AI spend, we present the results"** → Clear ownership  
✅ **"30-day pilot proves ROI before you commit"** → De-risks client  
✅ **"Your data stays your data"** → Compliance framing  
✅ **"If something breaks, SourceA fixes it immediately"** → SLA language  

---

## Sample sales email (Noetfield → Client)

```
Subject: AI Cost Control — Audit + Firewall pilot (30 days, low risk)

Hi [Client name],

We built something new: an AI Spend Leak Audit + cost control firewall.

Here's how it works:
1. 5-day audit — we inventory your AI tools, find where you're overspending
2. Custom firewall policy — route to cheaper models automatically, escalate premium only when needed
3. 30-day pilot — we enforce the policy, track results, no commitment
4. Final report — cost savings %, compliance metrics, then you decide

Investment: $2–5K (scope on audit). ROI typically 3–4 months.

Example: One client found $400/month in GPT-4 waste (simple tasks). Our firewall caught it automatically.

Timeline: We start intake this week, results in ~40 days.

Interest? I'll connect you with our audit team.

[Your name]
Noetfield
```

---

## Renewal & upsell

**After 30-day pilot:**

**If client loved it:**
- "Annual monitoring contract" — $1.2K/year (daily spend reports + quarterly policy reviews)
- "Tool consolidation project" — retire unused tools, SourceA helps migrate workflows
- "Team training" — how to request Tier 2/3 escalations, understand reports

**If client hesitated:**
- "Extend pilot 30 more days" — increase Tier 2 caps, loosen triggers, prove more ROI
- "Manual controls only" — SourceA exports audit log, client manages from there
- "Sunset gracefully" — SourceA turns off firewall, sends final recommendations

---

## Law (Noetfield-facing)

- **SourceA owns audit accuracy** — if findings are wrong, SourceA re-audits at no cost
- **SourceA owns firewall reliability** — 99.5% uptime SLA on pilot
- **You own client satisfaction** — if client is unhappy, escalate to SourceA Brain (not executive)
- **Renewal is Noetfield's call** — SourceA does not contact clients for upsells (you do)
- **Data privacy** — audit logs stay in SourceA repo until you request export (then deleted after 90 days)

---

## Next steps

1. **Review audit kit** (3 docs in SourceA `docs/commercial/`)
2. **Draft your sales deck** (use sample email above as base)
3. **Prep your first customer** (intake brief to SourceA when ready)
4. **Assign Noetfield point-of-contact** (your email for updates)

**SourceA team is ready** — Slack: `#sourcea-audits` or email: `sourcea-audits@sourcea.app`

---

## Contact

**SourceA audit delivery:**
- Intake/questions: `sourcea-audits@sourcea.app`
- Slack: `#sourcea-audits` (private channel)
- Emergency (firewall down): `#sourcea-alerts`

**SourceA Brain** (policy customization, client escalations):
- Slack: `@sourcea-brain` or `#sourcea-audits`

---

**Agentic Cost Governance is ready to ship. Let's acquire customers.**
