# SourceA Reference Architecture Constellation (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-11-REF-CONSTELLATION  
**Authority:** ASF · subordinate to `SINA_OS_SSOT_LOCKED.md` · `STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md`  
**Router:** `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md`  
**Buyer · portfolio identity (wins on conflict):** `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md`  
**Companion:** `SOURCEA_RESULT_DRIVEN_DISCUSSION_POLICY_LOCKED_v1.md` · `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md` · `HUB_SOURCE_UI_ALIGNMENT_PROCEDURE_LOCKED_v1.md`

---

## 0. Purpose

One **locked map** of the external agentic-AI market — every reference ASF named — so agents, advisors, and UI work share the same mental model.

**Use this doc when:**

- Designing public site, hub panels, or docs zone (what category to resemble)
- Evaluating build vs buy vs partner
- Answering “where does SourceA sit vs Temporal / Frontier / ThinkFleet?”
- Avoiding wrong metaphors (consumer AI chat, Linear backlog as primary hero)

**Rule:** External products inform **tone and layer** — they do **not** override LOCKED SourceA law or `system_roadmap.py`.

---

## 1. Big picture — four eras of enterprise software

| Era | Question answered | Examples | Limit |
|-----|-------------------|----------|-------|
| **1990s ERP** | What happened? | SAP, Oracle, Dynamics | Backward-looking records |
| **2000s BI** | Why did it happen? | Tableau, Power BI, Salesforce analytics | Descriptive dashboards |
| **2010s AI planning** | What will happen? | Anaplan, IBP, predictive AI | Plans don’t execute |
| **2020s agentic execution** | **How do we make agents actually work — safely?** | Temporal, Frontier, Hubler, ThinkFleet, SourceA | Needs governance + proof |

**2026 market thesis:** Intelligence without execution is a recommendation nobody acts on. The winning layer is **governed execution** — not another chat UI.

**Sprawl warning (Tech in Asia / enterprise surveys):** ~94% of enterprises flag **agent sprawl** — many agents, no control tower. SourceA’s anti-fragmentation laws exist because this is the default failure mode.

---

## 2. Layer model — where every reference sits

```text
┌─────────────────────────────────────────────────────────────────┐
│ L7 SURFACE — what humans see (issues, docs, activity)          │
│   Linear · LinearB · Stripe Docs pattern · Sierra CX UI        │
├─────────────────────────────────────────────────────────────────┤
│ L6 GOVERNANCE — policy at execution path (PEP/PDP)             │
│   Notenic · ThinkFleet Shield · Canada bounded autonomy        │
│   SourceA: ENFORCE · trust ledger · council laws · READ_CHAIN    │
├─────────────────────────────────────────────────────────────────┤
│ L5 ENTERPRISE EXECUTION — approve → orchestrate → audit         │
│   Hubler · OpenAI Frontier · PLATEER XGEN · Botpress enterprise│
├─────────────────────────────────────────────────────────────────┤
│ L4 AGENT RUNTIME — graphs, tools, sandboxes, identity          │
│   LangGraph · Prajvis · Vybe · Jetty · Cognition/Devin         │
├─────────────────────────────────────────────────────────────────┤
│ L3 DURABLE ORCHESTRATION — workflows survive failure           │
│   Temporal · Jetty DAGs · Kestra YAML flows                    │
├─────────────────────────────────────────────────────────────────┤
│ L2 INFRA / DEPLOY — where compute runs                         │
│   Kubernetes · Fly.io Machines/sandboxes                       │
├─────────────────────────────────────────────────────────────────┤
│ L1 OBSERVABILITY + ECONOMICS — prove it ran · know margin      │
│   Datadog · Paid.ai · AgentMarketCap (benchmark map)           │
├─────────────────────────────────────────────────────────────────┤
│ L0 MODELS — reasoning engines (commodity inside layers above)  │
│   Claude Opus 4.6/4.7 · GPT-5.x · Gemini · Qwen                │
└─────────────────────────────────────────────────────────────────┘
```

**Golden rule:** Models are **L0**. SourceA product identity lives at **L3–L7**, not “we use Claude.”

---

## 3. Full reference catalog (all ASF sources)

### 3.1 L3 — Durable orchestration

| Ref | URL | One-line role | SourceA analog |
|-----|-----|---------------|----------------|
| **Temporal** | https://temporal.io/ | Durable workflows + activities; agent loops survive crash | Factory spine, broker receipts, long-running Worker rounds |
| **Kestra** | https://kestra.io/ | Declarative YAML orchestration; data/infra/AI pipelines; 1400+ plugins | n8n glue + hub Actions — **not** primary agent brain |
| **Jetty** | https://jetty.io/ · https://docs.jetty.io/ | OpenAI-compatible API + runbooks + sandboxes + trajectories | Dev/agent eval lane; runbook pattern for Worker evidence |

### 3.2 L4 — Agent runtime & graphs

| Ref | URL | One-line role | SourceA analog |
|-----|-----|---------------|----------------|
| **LangGraph** | https://www.langchain.com/langgraph | Stateful multi-agent graphs, HITL, memory, streaming | Inside Cursor chats + Council — not hub SSOT |
| **Prajvis** | https://prajvis.com/ | Identity, MCP tools, sandbox computers, multi-agent, schedules | Private agent workspaces + vault middle layer |
| **Vybe** | https://vybe.build/ | “AI coworkers” — Slack/email, 3000+ integrations, SMB tone | **Wrong public tone** — too consumer; useful for integration breadth ideas only |
| **Cognition / Devin** | https://cognition.ai/ | Autonomous SWE — plan, code, test, ship in repo | Worker lane when scoped to one sa-XXXX — under factory gate law |
| **OpenClaw / LangChain** | (via AgentMarketCap) | Open autonomous frameworks | Research only — no production north star |

### 3.3 L5 — Enterprise execution platforms

| Ref | URL | One-line role | SourceA analog |
|-----|-----|---------------|----------------|
| **Hubler** | https://www.hubler.ai/ | System of **Execution** — govern → approve → orchestrate → execute → audit | Order Guardian + task orders + hub Actions |
| **OpenAI Frontier** | https://openai.com/business/frontier/ | AI coworkers — business context, agent IAM, eval loops, auditable actions | External benchmark for “agent as employee” — SourceA is self-hosted + law-first |
| **PLATEER XGEN** | https://www.plateer.com/en | Enterprise agentic AI (APAC) — RAG, visual builder, hybrid governance | Commerce/enterprise deploy pattern — not SourceA stack |
| **Palantir AIP** | https://palantir.com/docs/foundry/aip/overview/ | Ontology + operational AI for regulated enterprise | **plantier** disambiguation — ontology-heavy; SourceA uses WTM + authority index instead |
| **Sierra** | https://sierra.ai/ | Agent OS for customer experience — build, optimize, outcome pricing | TrustField commercial lane — not factory spine |
| **Botpress** | https://www.botpress.com/ | Enterprise support agents — escalate rules, helpdesk-native | Support automation reference — not core identity |

### 3.4 L6 — Governance & compliance

| Ref | URL | One-line role | SourceA analog |
|-----|-----|---------------|----------------|
| **Notenic** | https://notenic.ai/architecture.html | PEP/PDP at tool-call layer — certify, intervene, hard-stop, revoke | ENFORCE bypass map · Eval-1 · gate receipts · trust ledger |
| **ThinkFleet** | https://www.thinkfleet.ai/ | Enterprise AI ops — agents/crews/flows + Shield (“Datadog for AI”) | **Tone anchor** — enterprise ops console, not consumer AI |
| **ThinkFleet Shield** | https://www.thinkfleet.ai/products/shield | Proxy governance — shadow AI, SIEM, compliance evidence packs | Drift engine + maintainer audit + anti-staleness latches |
| **Canada — Agentic AI Guide** | https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/guide-use-agentic-artificial-antelligence.html | **Bounded autonomy** + **recoverability**; FASTER; oversight/auditability | Maps 1:1 to founder laws + ENFORCE + result-driven closeout |

### 3.5 L2 — Infrastructure

| Ref | URL | One-line role | SourceA analog |
|-----|-----|---------------|----------------|
| **Kubernetes** | https://kubernetes.io/ | Container fleet — scale, secrets, self-heal | Noetfield cloud / future production fleet |
| **Fly.io** | https://fly.io/ | Fast Machines, global regions, agent sandboxes | Demos, edge agents, quarantine site (13060) |

### 3.6 L1 — Observability & economics

| Ref | URL | One-line role | SourceA analog |
|-----|-----|---------------|----------------|
| **Datadog** | https://www.datadoghq.com/ | Unified metrics, traces, logs, APM, security | External mature form of execution_truth + hub health |
| **Datadog × Temporal** | https://www.datadoghq.com/dg/monitor/temporal | Prebuilt Temporal dashboards + recommended monitors | Pattern for factory/broker panel monitors |
| **Paid.ai** | https://paid.ai/ | Agent-native billing — cost per action, margins, value receipts | Commercial lane economics — outcome + cost proof for TrustField |
| **AgentMarketCap** | https://agentmarketcap.ai/ | Market map — 716 agents scored (reasoning, coding, autonomy) | Model/tool picker reference — not architecture law |

### 3.7 L7 — Product surface & SDLC analytics

| Ref | URL | One-line role | SourceA analog |
|-----|-----|---------------|----------------|
| **Linear** | https://linear.app/ | Product dev system — issues, cycles, human+agent workflows, MCP | **Activity/triage slice only** — dark hero feed, not primary category |
| **LinearB** | https://linearb.io/ | Engineering productivity — AI code volume vs merge velocity | Scoreboard + factory metrics (Valid YES, dual_proof) |

### 3.8 L0 — Frontier models

| Ref | URL | One-line role | SourceA use |
|-----|-----|---------------|-------------|
| **Claude Opus 4.6** | https://www.anthropic.com/news/claude-opus-4-6 | Long-running agents, 1M context (beta), adaptive thinking, compaction | Brain/Worker when ASF names — under edit lock + gates |
| **Claude Opus 4.7** | https://www.anthropic.com/news/claude-opus-4-7 | Successor — stronger SWE, instruction following | Same — model inside governed runtime |
| **OpenAI Frontier models** | (via Frontier platform) | GPT-5.x family for enterprise agent execution | External critic / compare only unless ASF adopts |

### 3.9 Market signal sources (watch — not products)

| Ref | URL | What to extract |
|-----|-----|-----------------|
| **Martech360** | https://martech360.com/ | 2026 = agentic enterprise, control towers, agent mesh, governance as board priority |
| **Tech in Asia** | https://www.techinasia.com/ | APAC deploy-at-scale; agent sprawl risk; enterprise-first AI conference signal |
| **VC Tavern** | https://vctavern.com/ | Funding heat: computer-use agents, compliance agents, web infra for agents (Parallel, Simular, etc.) |
| **Presenc AI** | https://presenc.ai/ | AI brand visibility / citation tracking (GEO) — commercial GTM signal for TrustField, not ops spine |

---

## 4. Category matrix — quick lookup

| Category | Members | Job to be done |
|----------|---------|----------------|
| **Durable spine** | Temporal, Jetty workflows, Kestra | Work survives failure; schedulable pipelines |
| **Agent brain** | LangGraph, Devin, Cursor-class tools | Reason, plan, use tools in session |
| **Enterprise execution** | Hubler, Frontier, XGEN, Botpress | Turn plans into governed business outcomes |
| **Governance PEP** | Notenic, ThinkFleet Shield, Canada guide | Stop bad actions **before** systems of record |
| **Agent platform** | Prajvis, Vybe, Jetty sandboxes | Identity + tools + sandbox + schedules |
| **Infra** | K8s, Fly | Where binaries run |
| **Observe + bill** | Datadog, Paid.ai | Prove health; prove margin |
| **UX surface** | Linear, Stripe Docs pattern | Human orientation — not execution engine |
| **SDLC analytics** | LinearB | Throughput truth — not issue tracking |
| **Model commodity** | Opus 4.6/4.7, GPT-5.x, Gemini | Swap without replatforming |
| **Market intel** | AgentMarketCap, Martech360, TIA, VC Tavern, Presenc | Category drift + GTM + funding |

---

## 5. SourceA — our place in the market (honest status)

### 5.1 What we are

**SourceA is a self-hosted, law-first governed execution OS** for ASF’s mono factory — not a generic agent SaaS.

| Layer | SourceA today | Maturity |
|-------|---------------|----------|
| **L7 Surface** | Sina Command hub (13020) · quarantined public site experiment (13060) | Hub strong · public site ~82% fidelity — not production spine |
| **L6 Governance** | LOCKED laws, council_governance, ENFORCE, trust ledger, result-driven policy | **Strong on disk** · daily map fixed (sa-0790) |
| **L5 Execution** | Factory INBOX, Worker one-sa, Order Guardian, task orders | **Active** · FREEZE/conduct incidents show control-plane gaps |
| **L4 Agent runtime** | 8 private agents, Cursor chats, workspace vault | **Designed** · needs consistent vault deposit discipline |
| **L3 Durable orchestration** | Broker, factory gate, validators — Temporal-**like** patterns, not Temporal Cloud | **Partial** — receipts law improving |
| **L2 Infra** | Local Mac + Noetfield lane + Fly-class sandboxes (future) | **Split** — founder no-Terminal |
| **L1 Observe** | Hub built_at, drift sensors, execution_truth | **Growing** · not full Datadog tier |
| **L0 Models** | Claude/Cursor per ASF order | **Commodity** — gated |

### 5.2 Positioning sentence

> **Temporal-grade durability intent + Stripe-grade docs clarity + ThinkFleet-grade governance tone + Canada-grade bounded autonomy — on ASF-owned infrastructure, with Linear only for activity — not as the category label.**

### 5.3 What we are NOT (avoid wrong comparisons)

| Wrong label | Why |
|-------------|-----|
| “SourceA is like Linear” | Linear is L7 product management — we are L3–L6 execution + law |
| “SourceA is like ChatGPT” | Consumer chat — we are result-on-disk factory |
| “SourceA is like Devin alone” | Devin is L4 builder — we are whole OS + founder hub |
| “SourceA is Palantir” | Ontology sales motion + $M contracts — we are founder mono with WTM |
| “SourceA is Vybe” | SMB coworker sparkle — we need enterprise ops sobriety |

### 5.4 Competitive moat (real, not marketing)

1. **Law density** — 100+ LOCKED docs, authority index, unification engine  
2. **Founder-sovereign** — no Terminal, no founder email/call, hub-only ops  
3. **Factory honesty** — receipt = done; anti-fake-progress incidents  
4. **Canada-aligned governance** — bounded autonomy + recoverability by design  
5. **Mono integration** — Brain/Worker/8 agents/Noetfield/TrustField lanes one map  

---

## 6. Golden insights (consolidated)

### 6.1 Architecture

1. **Separate layers, never collapse.** LangGraph thinking inside Temporal-shaped durability inside Notenic-style gates inside Linear-shaped activity UI.  
2. **Governance at execution path wins.** Post-hoc log review is too late — ENFORCE + gate receipts are the moat.  
3. **One SSOT or sprawl.** Market is proving 94% sprawl fear — `GOVERNANCE_UNIFICATION_ENGINE` + authority index are survival tools.  
4. **Docs zone = Stripe structural mirror.** API reference white zone builds trust; dark hero = ops trace, not issue backlog.  
5. **n8n stays glue.** Kestra-class orchestration for batch; not the agent brain.

### 6.2 Founder & business

1. **Result table every session** — market sells “agents”; ASF needs **disk proof** (`SOURCEA_RESULT_DRIVEN_DISCUSSION_POLICY`).  
2. **Read-only by default** (Canada) — expand permissions only with oversight maturity.  
3. **Outcome receipts for commercial** — Paid.ai / Sierra pattern for TrustField when live: show value, not just invoice.  
4. **Founder never dials** — agentic commercial is infrastructure, not hero copy.  
5. **Honest progress** — AgentMarketCap scores mean nothing if Valid YES / dual_proof lie.

### 6.3 Build vs buy vs partner

| Need | Recommendation |
|------|----------------|
| Durable workflow engine at scale | **Study Temporal** · adopt patterns first · managed service only if Noetfield cloud matures |
| Enterprise agent IAM | **Study Frontier** · implement agent identity in hub — don’t buy lock-in yet |
| AI proxy governance | **Study ThinkFleet Shield** · extend drift engine + SIEM export pattern |
| Tool-call PEP | **Study Notenic** · strengthen ENFORCE + bypass map |
| Public docs UX | **Stripe Docs mirror** (quarantine site) · promote when fidelity ≥95% |
| CX agents | **Sierra/Botpress** patterns for TrustField lane only |
| Billing/margins | **Paid.ai** when commercial agents bill customers |
| Full observability | **Datadog** when multi-service cloud — until then hub execution_truth |
| APAC enterprise RAG | **PLATEER XGEN** as market comp — not fork |

### 6.4 UI / tone (ThinkFleet-class)

| Do | Don’t |
|----|-------|
| Show execution state, gates, receipts | “Magic AI” gradients and chat bubbles as hero |
| Ops vocabulary: workflow, gate, receipt, drift | Consumer “ask anything” as primary CTA |
| Prove audit trail | Vague “enterprise-grade” without panels |
| Dark zone = live trace / broker | Dark zone = issue tracker clone |

---

## 7. Public site & hub — reference-driven design target

| Zone | Primary reference | Secondary | Avoid |
|------|-------------------|-----------|-------|
| Dark hero | Temporal ops console · ThinkFleet dashboard | Linear activity feed | Linear backlog as main metaphor |
| Docs / API | Stripe Documentation structure | OpenAI API reference patterns | Invented component tree |
| Auth | Stripe-class clarity | — | Playful consumer onboarding |
| Hub Command | Hubler execution loop | ThinkFleet governance panels | Vybe coworker whimsy |
| Factory panel | LinearB throughput metrics | Datadog health | Vanity “AI score” |

---

## 8. 90-day priority stack (golden suggestion)

| Priority | Action | Reference inspiration |
|----------|--------|----------------------|
| **P0** | Keep governance daily map green (READ_CHAIN + council_governance + result-driven) | ThinkFleet governance-first |
| **P0** | Factory control plane owns execution (conduct incidents close) | Temporal durability truth |
| **P1** | Hub gate receipts panel = mini Notenic certify/intervene UX | Notenic |
| **P1** | Stripe docs zone ≥95% structural fidelity before spine merge | Stripe |
| **P1** | TrustField lane: Sierra-style outcome proof + Paid-style margin | Sierra · Paid.ai |
| **P2** | Optional Datadog when Noetfield multi-service | Datadog × Temporal |
| **P2** | Agent sprawl audit — one registry row per agent surface | Tech in Asia sprawl signal |

---

## 9. Advisor intake line (paste for external critics)

```text
Read SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md.
Classify: EXTERNAL_CRITIC — compare only.
SourceA = L3–L6 self-hosted governed execution OS (not Linear, not Vybe, not Palantir).
Tone = ThinkFleet-class enterprise ops. Proof = disk + validators + gate receipts.
Forbidden: replatform to Frontier/Temporal Cloud as P0 · consumer AI hero · chat-only advice.
```

---

## 10. Maintenance

| Event | Action |
|-------|--------|
| New major external platform | Add row §3 + category §4 — run `GOVERNANCE_UNIFICATION_ENGINE` on batch |
| SourceA status shift | Update §5.1 maturity table + §8 priorities |
| Site promoted from quarantine | Update §7 + `sourcea-site-v1-QUARANTINE.md` pointer |

**Rebuild after index edit:** `cd SourceA/scripts && python3 build-sina-command-panel.py`

---

*End SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1*
