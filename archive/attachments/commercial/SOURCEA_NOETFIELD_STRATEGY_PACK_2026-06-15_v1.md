# SourceA / Noetfield — Commercial Strategy Pack

**Saved:** 2026-06-15T09:16:46Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** v1 · **Date:** 2026-06-15 · **Status:** External-eye draft

> **Reconciliation note.** This is an outside-eye consolidation built from the council discussion and current 2026 market context. Your disk already holds locked equivalents — `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md`, `NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_LOCKED_v1.md`, `SOURCEA_ICP_MARKET_IDENTITY_LOCKED_v1.md`. Treat this as something to **compare and merge against locked law**, not replace it. Where this conflicts with a LOCKED doc, the locked doc wins.

---

## 1. Big Picture

**Category.** SourceA is **Runtime Governance Infrastructure** — pre-LLM governed execution. Every agent action is gated by policy *at dispatch*, written to a signed, replayable ledger, and protected by tamper detection — **before** the model acts, not after the fact.

**Two layers, separate buyers and revenue.**
- **Infrastructure layer** — the SourceA engine: policy-at-dispatch, receipt ledger, replay, tamper-evidence, signed audit chain.
- **Application layer** — **Noetfield** (compliance/governance buyer surface, *primary*), with TrustField, Forge, and AgentField as adjacent surfaces. Each layer carries its own buyer and its own revenue line.

**The wedge — why now.** Enterprises put agents into production faster than they built controls. A majority now run agents; most lack formal governance; a large share of agentic projects are projected to fail on weak risk controls and unclear value. The incumbent model — static policy enforced at session start — is now treated as insufficient: governance has to run at the **request level, on every action**. That is exactly SourceA's posture. The market has written the pitch; we supply the proof.

**The differentiator — provable enforcement.** Competitors *describe* static policy. SourceA *shows* the entire chain running live: **cold start → request → policy evaluation → decision → enforcement → signed receipt → replay → tamper-FAIL → signed audit chain — visible in under five minutes.** Proof density, not prose, is the moat. A prospect who watches that chain in five minutes is worth more than any slide or statistic.

**Operating focus.** One engine. Noetfield primary; TrustField parallel (not a P0 build). Buyer-1 GTM runs in parallel with the engine, never sequenced behind it.

**The motion.** Agents open conversations; recorded proof closes them; the founder approves only irreversible steps (send, book, spend, sign). Pre-revenue, the asset that substitutes for revenue is **an active design partner running the system in a real workflow** — that is the fundable signal and the spine of the next raise.

**Buyer sequencing (law).** Platform engineering **NOW** → Embed (orchestrator / partner integration) → Enterprise (procurement, SOC 2). Do **not** fight enterprise procurement pre-revenue; you will die in the security questionnaire.

---

## 2. Roadmap

Framed by the only currency that matters pre-revenue: **proof + the first paid design partner.** Revenue gates map to the funding ladder — design-partner *active usage* is the accepted pre-seed/seed validation in 2026; roughly $1–3M ARR is the Series A repeatability bar. You are optimizing for the first signal, not the second yet.

### Phase 0 — Unblock (this week)
Three artifacts still gate everything. All currently open.
1. **Send** one NW1 outreach email — battle card body + one-pager attached + a named live-demo date.
2. **Record** the W1 proof demo — <5 min, full chain, cold start. (Script `demo-enforcement-5min-v1.sh` already runs clean; no new engineering required.)
3. **Ship** one runnable SW1 repo/demo link — runs in <5 min.

**Milestone:** deal motion live.
**Guard:** do not build automation to send one already-drafted email.

### Phase 1 — First paid design partner (0–60 days)
Run one **CAD $2K shadow-mode pilot**: 30–60 days, one workflow / one agent fleet, one success metric, conversion clause to annual, refund if you don't deliver. Hit the metric → convert → **capture exactly what in the message and the demo made them say yes** → produce a case study + named reference.

**Milestone:** 1 paid design partner + 1 reference logo.

### Phase 2 — Templatize, don't scale blind (60–120 days)
Turn the *proven* outreach into a small repeatable loop — still approval-gated. Target **3 design partners + a technical-adoption signal** (SW1 repo usage / demo runs). Wire the Mac automation **one lane at a time** (commercial first, factory second). Never automate a motion you haven't proven by hand.

**Milestone:** 3 DPs, a repeatable motion, the beginnings of a raise narrative.

### Phase 3 — Embed + widen (120 days+)
Orchestrator / partner integration (Embed buyer). Open-core the enforcement core as a demand-gen feeder — **only post-Eval-1, once the core is stable.** Begin enterprise-readiness (SOC 2 path) **only when pulled by real enterprise demand.**

**Milestone:** embed design partner(s) + inbound from open-core adoption.

### Standing guardrails (all phases)
- **Frozen zone:** no new architecture layers before outreach is sent.
- **Proof-density bar:** every demo / pilot / deck shows the full chain in <5 min, cold start.
- **Separation law:** Noetfield speaks compliance/board; SourceA speaks infrastructure. Don't blur them.
- **No blind scaling:** validate the motion by hand-approval before automating it.
- **CASL-safe outreach:** identified sender, consent/relationship basis, unsubscribe path; one quality message over a volume blast.
- **Human approval on every irreversible action;** never skip permissions on send / book / spend paths.

---

## 3. ICP List — Buyer 1 (Platform / AI-Infra Engineering)

**One-liner:** Teams that *already run AI agents in production* and *lack provable, per-action governance* — small enough that one technical champion can approve a CAD $2K pilot without procurement, exposed enough that an unauthorized agent action is a real liability.

### Firmographic profile
- **Stage/size:** Seed–Series C startups, or a single business unit / platform team inside a larger company. ~50–2,000 employees, or one autonomous team within a bigger org.
- **AI maturity:** agents already in production or in serious pilot — not "exploring AI." No agents = no pain = not your ICP yet.
- **Budget:** a technical champion with discretionary spend up to a few thousand for a pilot. Avoid anything that routes through formal procurement at first touch.
- **Regulatory exposure:** handles regulated or sensitive data, or sells into regulated buyers — so governance is a board/compliance concern, not a nice-to-have.

### Priority segments (ranked by pain × reachability)
1. **AI-native / agent-platform startups** — companies whose product *is* agents (agent builders, autonomous workflow tools, vertical AI agents). Acute pain, fast technical buyers, no procurement. *Archetypes: agent-orchestration startups, vertical "AI employee" companies, autonomous SDR/ops tooling.*
2. **Fintech & financial-services platform teams** — agents touching money movement, underwriting, or customer data; every action is auditable by regulators. *Archetypes: payments infra, lending/underwriting platforms, treasury/ops automation.*
3. **Healthtech & insurance** — PHI/claims exposure; HIPAA-class liability on any agent action. *Archetypes: claims automation, clinical-ops copilots, prior-auth agents.*
4. **Legal / compliance tech** — agents drafting or filing where a wrong action is malpractice-grade. *Archetypes: contract-review, e-discovery, regulatory-filing agents.*
5. **Dev-tools & data-platform companies shipping agentic features** — already on agent frameworks, already feeling the governance gap internally. *Archetypes: code-gen platforms, data-pipeline copilots, internal-tooling agents.*

### Champion persona (who signs)
- **Primary:** Head of Platform Engineering · Head of AI Infrastructure · Head of ML Platform · Staff+ platform engineer · founder/CTO at agent-native startups.
- **Influencers (later, not first touch):** Head of Compliance / Risk, CISO — these belong to the *Enterprise* phase, not Buyer 1.
- **Anti-persona:** procurement, generic IT, "innovation lab" with no production system. Selling to these first is the enterprise-procurement trap.

### Trigger / qualifying signals (a lead is "hot" if ≥2 hit)
- Recently shipped or announced an agentic feature.
- Public mention of an agent incident, a near-miss, or governance concern.
- Hiring for AI safety / governance / platform / ML-platform roles.
- Built on agent frameworks (LangGraph, CrewAI, AutoGen, MCP-based stacks).
- Under SOC 2 / regulatory pressure or selling into regulated buyers.
- Recently raised to scale AI (budget + urgency).

### Disqualifiers (skip or defer)
- No agents in production yet (no pain).
- Pure prompt-wrapper apps with no execution/action risk.
- Locked into a single vendor's orchestration that already bundles governance.
- Large enterprise that forces 9-month procurement at first contact → defer to Phase 3.

### Fit scorecard (score each account 0–2; pursue ≥7/12)
| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Agents in production | none | piloting | live in prod |
| Governance gap | solved | partial | none / acute |
| Regulatory exposure | low | medium | high |
| Champion access | procurement-only | influencer | platform owner w/ budget |
| Trigger signals | 0 | 1 | ≥2 |
| Deal velocity | procurement | committee | single-signer pilot |

### Sourcing the named-account list (do this against the rubric)
Pull candidates from: agent-framework GitHub orgs and dependents, AI-engineering communities/Slacks, recent agentic-product launches and funding announcements, and (Phase 3) the SI channel. **Build the actual named list from your own research/CRM against the scorecard above** — I've deliberately given you segments, personas, and qualifying criteria rather than a fabricated list of specific people to email, because (a) specific current contacts can't be verified reliably and (b) CASL means each first message should be researched, identified, and relationship/consent-based, not a scraped blast.

---

*End of pack. Companion buyer-facing doc: `NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_2026-06-15_v1.md`.*
