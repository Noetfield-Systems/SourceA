# Consideration — Entity money flow & safe revenue path (v1)

**Saved:** 2026-06-08T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
```yaml
trace_id: governance_goal_specialist-20260608-002
trace_family: governance_goal_specialist-20260608
trace_type: consideration
trace_author: governance_goal_specialist
trace_owner: governance_goal_specialist
trace_created: 2026-06-08
trace_pair: governance_goal_specialist-20260608-003
trace_vault: governance_goal_specialist-20260608-001
trace_registry: docs/TRACE_REGISTRY_GOVERNANCE_GOAL_20260608.md
```

**Status:** CONSIDERATION — not LOCKED law, not a Cursor rule, not execution authority  
**Date:** 2026-06-06  
**Source:** Governance Goal Specialist · Controlled Execution OS loop 1  
**Audience:** ASF, TrustField GTM, Noetfield spec lane, Execution Core reconciliation  
**Counsel:** Requires validation by BC corporate/commercial counsel before signing contracts  

**Supersedes:** Nothing — advisory only; LOCKED RPAA opinion and Trust Ledger positioning remain authoritative for regulatory posture.

**Related:**
- `docs/NOETFIELD_GOVERNANCE_PLANE_LOCKED_v1.md`
- `corpus/uploaded/2026-05-batch-013/noetfield-rpaa-legal-opinion-letter-v1.md`
- TrustField mirror: `TrustField Technologies/docs/considerations/CONSIDERATION_ENTITY_MONEY_FLOW_SAFE_REVENUE_v1.md`
- Vault: `~/.sina/agent-workspaces/noetfield_local/legal-goal/2026-06-06_MISSION_OUTPUT.yaml`

---

## Purpose

Capture founder-facing **considerations** (not mandates) for:

1. How customer money should flow between TrustField and Noetfield  
2. What to reject (Noetfield as payee / facilitator / grantor of funds)  
3. A practical 30-day safe revenue sequence  

If this consideration conflicts with LOCKED law or counsel advice, **LOCKED law and counsel win**.

---

## Consideration summary (one line)

**Customers pay TrustField only. TrustField delivers work. Trust Ledger is a deliverable artifact — not a bank account or payment rail.**

---

## Rejected structures (governance risk — not recommended)

The following were **considered and not recommended** pending counsel redesign:

| Structure | Why not recommended |
|-----------|---------------------|
| Noetfield receives customer payments (temporary or permanent) | Funds proximity; MSB/PSP optics; contradicts non-custodial RPAA opinion |
| Noetfield as “grantor” or “facilitator” of client money flow | Payment facilitation; unclear seller-of-record |
| Customer → Noetfield → TrustField passthrough | Escrow/trust-account optics; personal liability if entities not incorporated |
| Trust Ledger as financial ledger | LOCKED positioning: Trust Ledger = governance evidence (TLEs); payment rails out of scope |
| Pre-registration contracting without clear entity | Founder personal liability; procurement/grant disqualification risk |

---

## Recommended money flow (consideration)

```text
Customer  ──invoice──►  TrustField Technologies (sole seller-of-record)
TrustField  ──delivers──►  assessment + Trust Ledger Entry (TLE) evidence pack
(later, when Noetfield is incorporated + product exists)
TrustField  ──license fee──►  Noetfield   [intercompany only — never from customer]
```

### Entity roles (consideration)

| Entity | Revenue role today | Money handling |
|--------|-------------------|----------------|
| **TrustField Technologies** | Invoice, contract, deliver | Business bank account receives all client fees |
| **Noetfield** | Spec / methodology reference in SOW annex | No client deposits; no invoicing until incorporated + product |
| **SourceA** | Internal automation spine | Never customer-facing; never on invoice |

---

## Founder sequence (consideration — 30 days)

### Week 1 — Legal shell

1. Incorporate **TrustField Technologies** (BC CCPC considered appropriate for B.C. + PacifiCan lane) **before** first paid invoice.  
2. Open **business bank account** in TrustField legal name only.  
3. Bind **E&O + cyber liability** insurance in TrustField name.  
4. Start **CanadaBuys** supplier registration for TrustField (parallel).

### Week 2 — Offer + paper

5. **Single offer:** “AI Governance & RPAA Readiness Discovery” — fixed fee CAD 3,500–7,500, 2 weeks.  
6. **Deliverables:** control gap matrix, partner execution map, 60-min readout, one sample **TLE** (evidence file).  
7. Counsel to finalize: **MSA**, **Discovery SOW**, **DPA** schedule.  
8. TrustField one-pager — governance/readiness language only.

### Week 3 — Sell

9. Three conversations — fintech, credit union, or MSP adjacency first (not healthcare/legal without vertical addenda).  
10. Close path: NDA → MSA → DPA → SOW → invoice from TrustField account.

### Week 4 — Close

11. Target: **one paid signature** (not multiple free pilots).

---

## Noetfield lane (consideration — today)

| In scope now | Out of scope now |
|--------------|------------------|
| Spec corpus under `noetfield/` | Customer invoicing |
| TLE schema / sample board pack as **TrustField deliverable format** | Client-deposit bank account |
| Methodology cited in TrustField SOW annex | Customer MSAs signed as Noetfield |
| Handoff contract **draft** (docs) for future dual-entity deals | SaaS terms / product revenue |

**Defer until product:** Noetfield incorporation, standalone API, intercompany license fee from TrustField.

---

## Future money split (consideration — when Noetfield is a real company)

1. Incorporate Noetfield when standalone governance product + paying license exist.  
2. TrustField continues to collect **100%** from customers.  
3. TrustField pays Noetfield via **intercompany license / IP fee** (monthly or per engagement).  
4. Customers **never** pay Noetfield directly.

---

## Language considerations (sales + SOW)

**Favor:** governance, readiness, evidence pack, Trust Ledger Entry, advisory, licensed partners execute.

**Avoid (RPAA optics):** settlement, routing, quote engine, custody, facilitator of funds, MSB operator, PSP operator.

---

## Open questions for counsel

- Sole proprietorship interim trading-as vs incorporate-before-first-dollar  
- Exact limitation-of-liability cap for Discovery SOW  
- Whether assessment-only engagement is processor vs joint controller under PIPEDA  
- Timing of Noetfield incorporation relative to first governance-license SKU  

---

*End consideration v1 — advisory only*
