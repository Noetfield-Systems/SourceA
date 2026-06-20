# Competitor Analysis Format — Market Reality v1

**Version:** 1.0.0 · **Saved:** 2026-06-20T08:49:39Z · **Authority:** ASF save order
**Path:** `~/Desktop/SourceA/docs/COMPETITOR_ANALYSIS_FORMAT_MARKET_REALITY_v1.md`
**Purpose:** Mandatory format for competitor analysis when ASF asks for market examples, pricing, product proof, or "who does this in the real world?"

---

## 0. Why This Exists

This format prevents abstract agent answers.

ASF does not want renamed internal concepts, invented product categories, or "our system could..." theory when asking for competitors. The correct job is to find real companies, real products, real buyers, real pricing, and real operating mechanics.

Existing internal idea documents can still be useful later, but they are not a substitute for competitor analysis.

---

## 1. Mandatory Competitor Row Format

Every competitor example must include these fields:

| Field | Required answer |
|---|---|
| Company | Real company name |
| Product / service | Exact market product or feature name |
| What they sell | Their buyer-facing wording, not SourceA's invented wording |
| Who runs it | Vendor-managed, customer self-hosted, hybrid, marketplace, service team, etc. |
| How it runs | Trigger, workflow, job, trace, audit, ticket, event, pipeline, control, etc. |
| Who buys | Real buyer role and company type |
| Pricing / cost | Public price, usage unit, custom range, or "not public" with market-estimated range |
| Revenue model | Seat, usage, platform fee, annual contract, enterprise quote, services, add-ons |
| Why buyers pay | Concrete pain: debugging, compliance, reliability, support, audit, cost, proof, speed |
| How they reached market | PLG, enterprise sales, open source, compliance wedge, developer docs, integrations, agencies |
| Source links | Pricing, docs, product page, marketplace, review, or funding/customer proof |
| SourceA lesson | One practical lesson; no renaming, no abstraction |

---

## 2. Bad vs Good

### Bad

"Run receipt is useful because every company needs proof."

This is abstract and not market analysis.

### Good

**Temporal Cloud**

- Product / service: Managed durable execution platform.
- What they sell: Workflows, retries, schedules, event history, replay.
- Who runs it: Temporal runs the cloud service; customer runs workers with business logic.
- How it runs: Customer starts workflow; Temporal records event history and coordinates retries.
- Who buys: Platform engineering and backend teams.
- Pricing / cost: Essentials starts around $100/month; Business around $500/month; usage by Actions and Storage.
- Why buyers pay: They do not want to build durable workflow orchestration and replay themselves.
- SourceA lesson: If we discuss execution proof, we must show the concrete run page, retention, retry, and pricing model.

---

## 3. Required Scope For "100 Examples"

When ASF asks for 100 competitor examples, do not produce 100 abstract scenarios. Produce 100 competitor rows across real markets:

1. Durable execution and workflow platforms.
2. Background job and queue platforms.
3. CI/CD and deployment run history.
4. LLM tracing, eval, and observability tools.
5. Compliance evidence and GRC platforms.
6. Support ticket and AI support history tools.
7. Payment, billing, and commerce event logs.
8. Security, identity, and audit log platforms.
9. CRM, sales, and revenue activity timelines.
10. Data pipelines, reverse ETL, and operational sync tools.

---

## 4. Forbidden In Competitor Analysis

- Do not lead with SourceA internal words.
- Do not rename a market category before studying the existing one.
- Do not invent an "ICP example" when ASF asked for competitors.
- Do not say "we can use this for Noetfield/TrustField" until the competitor product is explained.
- Do not mix companies into a neat artificial separation.
- Do not turn mechanism into product. Internal mechanism is not market language.
- Do not give code unless ASF asks for implementation.

---

## 5. Required Answer Shape

When answering in chat before saving a full file:

1. State the corrected market question in one sentence.
2. Give 5-10 competitor rows with real product/pricing details.
3. Explain the market pattern in plain language.
4. Then say what SourceA can learn.
5. If more detail is needed, save the full competitor table.

---

## 6. Core Rule

**Do not invent first. Find who already sells the similar capability, learn exactly how they package it, who buys it, how it runs, how it is priced, and only then map a SourceA lesson.**

This is the opposite of abstraction. It is market-first reasoning.
