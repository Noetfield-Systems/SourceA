# Portfolio 100 Comparables — Market Reality v1

**Version:** 1.0.0 · **Saved:** 2026-06-20T09:21:59Z · **Authority:** ASF SAVE TO + UPGRADE
**Path:** `~/Desktop/SourceA/docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`
**Format:** `docs/_ANALYSIS_FORMAT_MARKET_REALITY_v1.md` — all fields per row
**Stacks:** SourceA (20) · WitnessBC (20) · Noetfield (20) · TrustField (20) · VIRLUX agentic factory (20)

---

## 0. How to use

Each row is a **real vendor** with links and pricing evidence. Portfolio companies may copy any row — no forced separation. Implementation extraction:

`Vendor feature → what buyer sees → what we implement`

**VIRLUX policy (ASF 2026-06-20):** FINTRAC/cross-border payments **out of VIRLUX**. Payment/MSB comparables belong under **TrustField** or a future company — not VIRLUX catalog.

---

## 1. SourceA — governed agent orchestration + run history (rows 1–20)

### 1. Trigger.dev

**Stack:** SourceA · **Product / service:** Durable background jobs & AI workflows

| Field | Answer |
|-------|--------|
| What they sell | Open-source AI agent and workflow platform — run long tasks with retries and a visual run dashboard |
| Who runs it | Vendor-managed cloud; optional self-host MIT |
| How it runs | Developer writes tasks in TypeScript; platform executes, logs steps, retries failures |
| Who buys | Backend and platform engineers at SaaS startups |
| Pricing / cost | Free $0 + Hobby $10/mo + Pro $50/mo; $0.25 per 10,000 run invocations + compute seconds — https://trigger.dev/pricing |
| Revenue model | Usage-based SaaS + self-host OSS |
| Why buyers pay | They need durable jobs without building Redis/BullMQ observability themselves |
| How they reached market | Open source → dev community → PLG cloud tiers |
| Source links | https://trigger.dev · https://trigger.dev/pricing |
| Portfolio lesson | Run detail page with pass/fail, steps, logs, retry — copy for Worker Hub job dashboard |

### 2. Inngest

**Stack:** SourceA · **Product / service:** Durable serverless functions

| Field | Answer |
|-------|--------|
| What they sell | Reliable workflows with invisible infra — step functions for serverless apps |
| Who runs it | Vendor-managed cloud; OSS self-host |
| How it runs | Event triggers functions; each step durable with trace retention |
| Who buys | Serverless product teams on Vercel/Netlify |
| Pricing / cost | Hobby $0 (50k executions); Pro $75/mo — https://www.inngest.com/pricing |
| Revenue model | Tiered SaaS by executions + events |
| Why buyers pay | Serverless timeout limits break AI workflows; Inngest removes that pain |
| How they reached market | Dev-first docs, framework integrations, free tier |
| Source links | https://www.inngest.com · https://www.inngest.com/pricing |
| Portfolio lesson | Step timeline + trace retention tiers on every factory job |

### 3. Hatchet

**Stack:** SourceA · **Product / service:** Task orchestration for AI pipelines

| Field | Answer |
|-------|--------|
| What they sell | Low-latency orchestration for agentic AI workflows with automatic retries |
| Who runs it | Vendor cloud + open-source self-host |
| How it runs | Postgres-backed task DAG; workers execute with priority lanes |
| Who buys | AI pipeline and data engineering teams |
| Pricing / cost | Free tier; Starter ~$180/mo; Production ~$425/mo (market reviews) |
| Revenue model | Usage-based cloud + OSS |
| Why buyers pay | BullMQ/Redis ops burden; Hatchet gives DAG + streaming for AI |
| How they reached market | Open source 2023; AI pipeline wedge |
| Source links | https://hatchet.run |
| Portfolio lesson | Priority lanes + durable steps for agent orchestration |

### 4. Upstash QStash

**Stack:** SourceA · **Product / service:** HTTP message queue & scheduler

| Field | Answer |
|-------|--------|
| What they sell | Serverless message queue — schedule and retry HTTP calls without infra |
| Who runs it | Fully managed Upstash cloud |
| How it runs | Publish HTTP message; QStash delivers with retries and DLQ |
| Who buys | Serverless developers |
| Pricing / cost | ~$1 per 100k messages pay-as-you-go; tiers from ~$180/mo |
| Revenue model | Message-volume SaaS |
| Why buyers pay | Simple cron/webhook delivery without running Redis |
| How they reached market | Developer PLG via Upstash ecosystem |
| Source links | https://upstash.com/qstash · https://upstash.com/pricing |
| Portfolio lesson | Lightweight dispatch layer for hub Actions → cloud workers |

### 5. Langfuse

**Stack:** SourceA · **Product / service:** LLM engineering platform

| Field | Answer |
|-------|--------|
| What they sell | Observability, prompts, evals, and analytics for LLM apps and agents |
| Who runs it | Cloud SaaS or MIT self-host |
| How it runs | SDK captures traces; dashboard filters by user, session, cost, latency |
| Who buys | AI engineering teams |
| Pricing / cost | Free 50k obs/mo; Core ~$29/mo; Pro ~$199/mo — https://langfuse.com/pricing |
| Revenue model | Usage tiers + self-host |
| Why buyers pay | Black-box LLM failures; teams need traces before users complain |
| How they reached market | Open-source MIT → 2300+ companies → cloud upsell |
| Source links | https://langfuse.com · https://langfuse.com/docs |
| Portfolio lesson | Hierarchical trace viewer per agent turn with cost/latency |

### 6. Helicone

**Stack:** SourceA · **Product / service:** LLM gateway & observability

| Field | Answer |
|-------|--------|
| What they sell | Proxy layer for LLM requests — caching, analytics, monitoring |
| Who runs it | Managed cloud; OSS gateway option |
| How it runs | One-line proxy integration; logs every request |
| Who buys | LLM app developers |
| Pricing / cost | Free hobby ~10k req; Pro from ~$79/mo (market) |
| Revenue model | Request-volume SaaS |
| Why buyers pay | Hidden LLM spend and latency; need request-level log |
| How they reached market | Open-source gateway → dev adoption |
| Source links | https://helicone.ai |
| Portfolio lesson | Per-model cost and latency dashboard on dispatch |

### 7. AgentOps

**Stack:** SourceA · **Product / service:** Agent observability

| Field | Answer |
|-------|--------|
| What they sell | Session replay and monitoring for autonomous AI agents |
| Who runs it | Managed cloud (SDK OSS MIT) |
| How it runs | SDK records agent steps, tools, costs; time-travel debugging UI |
| Who buys | Agent builders and AI startups |
| Pricing / cost | Free tier ~5k events; Pro ~$40/mo (market) |
| Revenue model | Event-volume SaaS |
| Why buyers pay | Agents loop unpredictably; need replay not just logs |
| How they reached market | Agent-specific niche vs generic APM |
| Source links | https://www.agentops.ai |
| Portfolio lesson | Time-travel replay for worker/agent debugging |

### 8. Braintrust

**Stack:** SourceA · **Product / service:** Eval + logging platform

| Field | Answer |
|-------|--------|
| What they sell | Experiment tracking, eval scores, and production logs for AI products |
| Who runs it | Managed cloud |
| How it runs | Log spans; run eval suites; compare prompt versions |
| Who buys | AI product and eng teams |
| Pricing / cost | From ~$249/mo (market); free tier for evals |
| Revenue model | Platform fee + usage |
| Why buyers pay | Ship AI without knowing if quality regressed |
| How they reached market | Eval-first wedge for AI product teams |
| Source links | https://www.braintrust.dev |
| Portfolio lesson | PASS/FAIL eval score on shipped agent runs |

### 9. Promptfoo

**Stack:** SourceA · **Product / service:** LLM eval & red-team CLI

| Field | Answer |
|-------|--------|
| What they sell | Test prompts, agents, RAG — red teaming for jailbreaks and PII leaks |
| Who runs it | OSS free; Enterprise custom (acquired OpenAI Mar 2026) |
| How it runs | CLI/CI runs matrix evals locally or in cloud |
| Who buys | Developers and security teams |
| Pricing / cost | Community free 10k probes/mo; enterprise contact sales |
| Revenue model | OSS + enterprise SaaS |
| Why buyers pay | Production AI security failures; CI gate before deploy |
| How they reached market | Open source → Fortune 500 adoption → enterprise |
| Source links | https://www.promptfoo.dev |
| Portfolio lesson | Pre-ship eval gate on worker output |

### 10. Giskard

**Stack:** SourceA · **Product / service:** LLM agent testing library

| Field | Answer |
|-------|--------|
| What they sell | Open-source evaluation and testing for LLM agents before production |
| Who runs it | OSS library + Giskard Hub enterprise |
| How it runs | Run test suites on agents; Hub adds collaboration and continuous red-team |
| Who buys | ML/AI QA teams |
| Pricing / cost | OSS free; Hub subscription contact sales |
| Revenue model | OSS + enterprise Hub |
| Why buyers pay | Agent failures in prod are expensive; test before ship |
| How they reached market | Paris OSS 2021 → enterprise Hub |
| Source links | https://www.giskard.ai |
| Portfolio lesson | Pre-prod agent regression test library |

### 11. Mastra

**Stack:** SourceA · **Product / service:** TypeScript agent framework

| Field | Answer |
|-------|--------|
| What they sell | Agent framework with built-in observability and workflow primitives |
| Who runs it | OSS + Mastra Cloud |
| How it runs | Define agents in TS; deploy with tracing hooks |
| Who buys | TypeScript agent developers |
| Pricing / cost | OSS free; cloud tiers (market) |
| Revenue model | OSS + cloud hosting |
| Why buyers pay | Need agent harness without building from scratch |
| How they reached market | Dev framework PLG |
| Source links | https://mastra.ai |
| Portfolio lesson | Standard agent harness hooks in SourceA motor |

### 12. Restate

**Stack:** SourceA · **Product / service:** Durable execution engine

| Field | Answer |
|-------|--------|
| What they sell | Durable async/await for long-running backend workflows |
| Who runs it | OSS + Restate Cloud |
| How it runs | Developer writes durable functions; engine persists state |
| Who buys | Backend platform teams |
| Pricing / cost | OSS free; cloud usage-based |
| Revenue model | OSS + cloud |
| Why buyers pay | Workflow state loss on crashes; need durable execution |
| How they reached market | Infrastructure OSS → cloud |
| Source links | https://restate.dev |
| Portfolio lesson | Long-running worker without orchestrator ghost state |

### 13. Windmill

**Stack:** SourceA · **Product / service:** Developer workflow platform

| Field | Answer |
|-------|--------|
| What they sell | Scripts, flows, schedules with run history and permissions |
| Who runs it | OSS + Windmill Cloud |
| How it runs | Write scripts/flows; schedule; audit run log |
| Who buys | Ops and platform teams |
| Pricing / cost | OSS free; cloud team tiers |
| Revenue model | OSS + seat/usage cloud |
| Why buyers pay | Internal ops automations need audit trail |
| How they reached market | Open-source automation platform |
| Source links | https://windmill.dev |
| Portfolio lesson | Internal ops job dashboard with run history |

### 14. Pipedream

**Stack:** SourceA · **Product / service:** Integration workflows

| Field | Answer |
|-------|--------|
| What they sell | Connect APIs and run code workflows with event triggers |
| Who runs it | Managed cloud |
| How it runs | Visual + code workflows; each run logged |
| Who buys | Developers and ops |
| Pricing / cost | Free tier + usage paid plans |
| Revenue model | Usage + seat SaaS |
| Why buyers pay | Glue between SaaS tools without maintaining cron servers |
| How they reached market | Developer integrations marketplace |
| Source links | https://pipedream.com |
| Portfolio lesson | Connector-based automation run log pattern |

### 15. Activepieces

**Stack:** SourceA · **Product / service:** Open-source automation

| Field | Answer |
|-------|--------|
| What they sell | Self-hostable Zapier alternative with flow builder |
| Who runs it | OSS + Activepieces Cloud |
| How it runs | Build flows; trigger on events; view run history |
| Who buys | SMB and developers |
| Pricing / cost | OSS free; cloud paid tiers |
| Revenue model | OSS + cloud SaaS |
| Why buyers pay | Want automation without vendor lock-in |
| How they reached market | Open-source community → cloud |
| Source links | https://www.activepieces.com |
| Portfolio lesson | Self-hostable workflow runs for portfolio factories |

### 16. Relay.app

**Stack:** SourceA · **Product / service:** Human-in-the-Auto Runtimemation

| Field | Answer |
|-------|--------|
| What they sell | Collaborative automations with approval steps |
| Who runs it | Vendor SaaS |
| How it runs | Workflow pauses for human approval; then continues |
| Who buys | Ops and rev teams |
| Pricing / cost | From ~$19/mo (market) |
| Revenue model | Seat + workflow SaaS |
| Why buyers pay | Full auto is risky; need founder approval gates |
| How they reached market | SMB ops PLG |
| Source links | https://www.relay.app |
| Portfolio lesson | Approval step before ACT/implement in worker loop |

### 17. Vellum

**Stack:** SourceA · **Product / service:** LLM ops platform

| Field | Answer |
|-------|--------|
| What they sell | Prompt deployment, eval, and monitoring for production LLM apps |
| Who runs it | Managed SaaS |
| How it runs | Version prompts; run evals; monitor production |
| Who buys | LLM product teams |
| Pricing / cost | Team/enterprise custom tiers |
| Revenue model | Seat + usage enterprise |
| Why buyers pay | Prompt chaos in production; need versioned deploy |
| How they reached market | Product-led for AI teams |
| Source links | https://www.vellum.ai |
| Portfolio lesson | Versioned prompt + eval on every dispatch |

### 18. Portkey

**Stack:** SourceA · **Product / service:** AI gateway

| Field | Answer |
|-------|--------|
| What they sell | LLM gateway with routing, caching, observability, governance |
| Who runs it | Managed cloud |
| How it runs | Proxy all LLM calls; log, route, cache |
| Who buys | Platform engineering |
| Pricing / cost | Usage-tier SaaS |
| Revenue model | Usage + platform fee |
| Why buyers pay | Multi-model routing and cost control |
| How they reached market | Gateway wedge in crowded LLM ops |
| Source links | https://portkey.ai |
| Portfolio lesson | Route models + log every call at dispatch |

### 19. Literal AI

**Stack:** SourceA · **Product / service:** Agent trace platform

| Field | Answer |
|-------|--------|
| What they sell | Tracing and eval UI for LLM apps and agents |
| Who runs it | Managed cloud |
| How it runs | Instrument app; view conversation traces and evals |
| Who buys | Agent startups |
| Pricing / cost | Startup-friendly tiers |
| Revenue model | Usage SaaS |
| Why buyers pay | Need lightweight trace without LangSmith lock-in |
| How they reached market | YC-style agent observability |
| Source links | https://www.literalai.com |
| Portfolio lesson | Conversation/run logging for agent sessions |

### 20. Hamming AI

**Stack:** SourceA · **Product / service:** Voice/agent QA

| Field | Answer |
|-------|--------|
| What they sell | Scenario test suites for voice and conversational agents |
| Who runs it | Managed SaaS custom |
| How it runs | Define scenarios; run regression; score outcomes |
| Who buys | Voice AI and agent QA teams |
| Pricing / cost | Custom (young startup) |
| Revenue model | Enterprise contracts |
| Why buyers pay | Agent quality before release in regulated CX |
| How they reached market | Voice agent QA niche |
| Source links | https://www.hamming.ai |
| Portfolio lesson | Regression scenario suite before agent release |

## 2. WitnessBC — AI policy packs + agentic install + replay proof (rows 21–40)

### 21. LowerPlane

**Stack:** WitnessBC · **Product / service:** Compliance automation

| Field | Answer |
|-------|--------|
| What they sell | AI-powered SOC 2, ISO 27001, HIPAA compliance with public pricing |
| Who runs it | Vendor-managed SaaS |
| How it runs | Integrations collect evidence; advisor helps pass audit |
| Who buys | Startups needing first SOC 2 |
| Pricing / cost | From $4,995/yr SOC2; bundles up to $15,995 — https://lowerplane.com/pricing |
| Revenue model | Annual subscription transparent tiers |
| Why buyers pay | Consultants charge $18k+ with opaque pricing |
| How they reached market | Public price cards vs Delve sales-led |
| Source links | https://lowerplane.com · https://lowerplane.com/pricing |
| Portfolio lesson | Public pricing ladder like WitnessBC toolkits → install tiers |

### 22. Delve

**Stack:** WitnessBC · **Product / service:** AI compliance automation

| Field | Answer |
|-------|--------|
| What they sell | AI agents auto-collect evidence for SOC 2, HIPAA, GDPR, ISO |
| Who runs it | Vendor SaaS + expert Slack support |
| How it runs | AI agents integrate tools; collect screenshots and logs |
| Who buys | AI startups needing fast SOC 2 |
| Pricing / cost | ~$18,000–30,000+/yr (market); contact sales — note Mar 2026 audit controversy |
| Revenue model | High-touch annual SaaS |
| Why buyers pay | 200–400 hours manual compliance → promised 50–100 hours |
| How they reached market | YC 2023 → $32M Series A 2025 |
| Source links | https://delve.co |
| Portfolio lesson | Fast install motion — always verify independent auditor (lesson from 2026 controversy) |

### 23. Sprinto

**Stack:** WitnessBC · **Product / service:** Continuous compliance

| Field | Answer |
|-------|--------|
| What they sell | Automate SOC 2, ISO, GDPR evidence collection and monitoring |
| Who runs it | Vendor SaaS |
| How it runs | Connect infra; continuous control monitoring; audit export |
| Who buys | SaaS startups |
| Pricing / cost | From ~$6,000/yr (market); custom enterprise |
| Revenue model | Annual SaaS by framework |
| Why buyers pay | Manual spreadsheet evidence doesn't scale |
| How they reached market | Compliance wedge for SaaS PLG |
| Source links | https://sprinto.com |
| Portfolio lesson | Policy pack → control checklist → export bundle |

### 24. Scrut Automation

**Stack:** WitnessBC · **Product / service:** GRC automation

| Field | Answer |
|-------|--------|
| What they sell | Compliance automation for SOC 2, ISO, and risk management |
| Who runs it | Vendor SaaS |
| How it runs | Control monitoring; evidence vault; audit readiness |
| Who buys | Mid-market compliance leads |
| Pricing / cost | Custom mid-market pricing |
| Revenue model | Annual enterprise SaaS |
| Why buyers pay | GRC spreadsheets fail audits |
| How they reached market | Mid-market compliance sales |
| Source links | https://scrut.io |
| Portfolio lesson | Shadow-mode parallel install narrative for Witness AI Flow |

### 25. Comp AI

**Stack:** WitnessBC · **Product / service:** SOC 2 in a box

| Field | Answer |
|-------|--------|
| What they sell | Get SOC 2 compliant quickly with AI-assisted automation |
| Who runs it | Vendor SaaS |
| How it runs | Guided setup; automated evidence; auditor handoff |
| Who buys | Early-stage SaaS |
| Pricing / cost | Startup tiers (market) |
| Revenue model | Annual SaaS |
| Why buyers pay | Need SOC 2 to close enterprise deals fast |
| How they reached market | Startup compliance PLG |
| Source links | https://comp.ai |
| Portfolio lesson | ≤30-day install promise on Witness AI Flow SOW |

### 26. Oneleet

**Stack:** WitnessBC · **Product / service:** Security + compliance

| Field | Answer |
|-------|--------|
| What they sell | Security monitoring and compliance for startups |
| Who runs it | Vendor SaaS |
| How it runs | Security controls + compliance evidence in one platform |
| Who buys | Startups |
| Pricing / cost | Custom pricing |
| Revenue model | Annual SaaS + services |
| Why buyers pay | Separate security and compliance tools are expensive |
| How they reached market | Startup security/compliance bundle |
| Source links | https://oneleet.com |
| Portfolio lesson | Proof call + deposit SOW before signature |

### 27. Secureframe

**Stack:** WitnessBC · **Product / service:** Automated compliance

| Field | Answer |
|-------|--------|
| What they sell | Automate evidence for SOC 2, ISO 27001, and more |
| Who runs it | Vendor SaaS |
| How it runs | Integrations → continuous monitoring → audit export |
| Who buys | Mid-market SaaS |
| Pricing / cost | Custom; typically $10k+ (market) |
| Revenue model | Annual SaaS |
| Why buyers pay | Audit prep without full-time compliance hire |
| How they reached market | Enterprise-leaning startup compliance |
| Source links | https://secureframe.com |
| Portfolio lesson | Export bundle buyer can hand to auditor |

### 28. Vanta

**Stack:** WitnessBC · **Product / service:** Trust management

| Field | Answer |
|-------|--------|
| What they sell | Automate compliance for SOC 2, ISO 27001, HIPAA, and more |
| Who runs it | Vendor SaaS (pattern reference) |
| How it runs | Connect stack; continuous monitoring; trust center |
| Who buys | Startups to mid-market |
| Pricing / cost | Custom; often $10k–50k/yr (market) |
| Revenue model | Annual SaaS + add-ons |
| Why buyers pay | Buyers require SOC 2 proof before contract |
| How they reached market | Category leader PLG → enterprise |
| Source links | https://www.vanta.com |
| Portfolio lesson | Control → linked proof artifact (pattern only) |

### 29. Drata

**Stack:** WitnessBC · **Product / service:** Compliance automation

| Field | Answer |
|-------|--------|
| What they sell | Continuous compliance monitoring and audit readiness |
| Who runs it | Vendor SaaS (pattern reference) |
| How it runs | Automated evidence; policy templates; auditor portal |
| Who buys | SaaS companies |
| Pricing / cost | Custom annual contracts |
| Revenue model | Annual SaaS |
| Why buyers pay | Pass audits without compliance team explosion |
| How they reached market | Vanta ; strong PLG |
| Source links | https://drata.com |
| Portfolio lesson | Live control status page pattern |

### 30. Gumloop

**Stack:** WitnessBC · **Product / service:** No-code AI automation

| Field | Answer |
|-------|--------|
| What they sell | Build AI workflows with guardrails, MCP hosting, team analytics |
| Who runs it | Vendor SaaS |
| How it runs | Visual canvas; agent interactions; policy guardrails |
| Who buys | Business and ops teams |
| Pricing / cost | Free 5k credits/mo; Pro $37/mo — https://www.gumloop.com/pricing |
| Revenue model | Credit-based subscription |
| Why buyers pay | Non-dev teams need governed AI automation |
| How they reached market | PLG free tier → Pro $37 |
| Source links | https://www.gumloop.com/pricing |
| Portfolio lesson | App policies + guardrails UI on agent dispatch |

### 31. Stack AI

**Stack:** WitnessBC · **Product / service:** Enterprise AI agents

| Field | Answer |
|-------|--------|
| What they sell | No-code enterprise AI agents with SOC2/HIPAA compliance |
| Who runs it | Vendor SaaS |
| How it runs | Build agent workflows; deploy with access control |
| Who buys | Regulated enterprise IT |
| Pricing / cost | Free 500 runs/mo; enterprise custom |
| Revenue model | Enterprise annual contracts |
| Why buyers pay | Need governed internal AI without dev team |
| How they reached market | Enterprise compliance positioning |
| Source links | https://www.stack-ai.com |
| Portfolio lesson | SOC2/HIPAA lane packaging for Witness AI Ops retainer |

### 32. Relevance AI

**Stack:** WitnessBC · **Product / service:** AI workforce platform

| Field | Answer |
|-------|--------|
| What they sell | Build and deploy AI agents for GTM and operations |
| Who runs it | Vendor SaaS |
| How it runs | Agent builder; actions + vendor credits; workforce dashboard |
| Who buys | GTM and ops teams |
| Pricing / cost | Pro $19/mo; Team $234/mo — https://relevanceai.com/docs/get-started/pricing |
| Revenue model | Actions + credits SaaS |
| Why buyers pay | Replace repetitive GTM work with agents |
| How they reached market | Agent workforce PLG |
| Source links | https://relevanceai.com/docs/get-started/pricing |
| Portfolio lesson | Packaged agent install SKUs like Witness AI Flow |

### 33. Lakera Guard

**Stack:** WitnessBC · **Product / service:** GenAI security

| Field | Answer |
|-------|--------|
| What they sell | Runtime guardrails for LLM apps — block injections and policy violations |
| Who runs it | Vendor SaaS enterprise |
| How it runs | API middleware scans prompts/responses; logs decisions |
| Who buys | AppSec and platform teams |
| Pricing / cost | Enterprise custom |
| Revenue model | API usage + enterprise |
| Why buyers pay | Prompt injection and data leakage in production |
| How they reached market | Security wedge for GenAI |
| Source links | https://www.lakera.ai |
| Portfolio lesson | Policy at dispatch allow/block log |

### 34. Holistic AI

**Stack:** WitnessBC · **Product / service:** AI risk management

| Field | Answer |
|-------|--------|
| What they sell | AI governance and risk dashboard for enterprise |
| Who runs it | Vendor SaaS |
| How it runs | Inventory AI systems; assess risk; monitor |
| Who buys | Risk officers and compliance |
| Pricing / cost | Enterprise custom |
| Revenue model | Annual enterprise |
| Why buyers pay | Board asks what AI is running and its risk |
| How they reached market | Enterprise AI governance sales |
| Source links | https://www.holisticai.com |
| Portfolio lesson | Risk score on each agent action for ops retainer |

### 35. Arthur AI

**Stack:** WitnessBC · **Product / service:** Model monitoring

| Field | Answer |
|-------|--------|
| What they sell | Monitor ML and LLM performance, drift, and quality |
| Who runs it | Vendor SaaS |
| How it runs | Ingest predictions; detect drift; alert |
| Who buys | ML platform owners |
| Pricing / cost | Enterprise custom |
| Revenue model | Annual enterprise |
| Why buyers pay | Model quality degrades silently in production |
| How they reached market | ML monitoring incumbents extend to LLM |
| Source links | https://www.arthur.ai |
| Portfolio lesson | Drift/quality alerts on Witness AI Ops |

### 36. Monitaur

**Stack:** WitnessBC · **Product / service:** ML governance lifecycle

| Field | Answer |
|-------|--------|
| What they sell | Governance for ML models from development to production |
| Who runs it | Vendor SaaS |
| How it runs | Policy workflows; model documentation; audit trail |
| Who buys | Regulated ML teams |
| Pricing / cost | Enterprise custom |
| Revenue model | Annual enterprise |
| Why buyers pay | Regulators require model lifecycle proof |
| How they reached market | Regulated industry ML governance |
| Source links | https://www.monitaur.ai |
| Portfolio lesson | Model/agent inventory for policy packs |

### 37. Lasso Security

**Stack:** WitnessBC · **Product / service:** GenAI security platform

| Field | Answer |
|-------|--------|
| What they sell | Discover shadow AI; protect GenAI apps |
| Who runs it | Vendor SaaS |
| How it runs | Scan for shadow AI; enforce policies |
| Who buys | CISO teams |
| Pricing / cost | Startup and enterprise tiers |
| Revenue model | Annual SaaS |
| Why buyers pay | Employees use ungoverned AI tools |
| How they reached market | GenAI security startup wedge |
| Source links | https://www.lasso.security |
| Portfolio lesson | Shadow AI discovery in policy starter kits |

### 38. Dust.tt

**Stack:** WitnessBC · **Product / service:** Enterprise AI assistants

| Field | Answer |
|-------|--------|
| What they sell | Build internal AI assistants connected to company data |
| Who runs it | Vendor SaaS |
| How it runs | Template assistants; team workspaces; usage controls |
| Who buys | Enterprise ops teams |
| Pricing / cost | Team tiers custom |
| Revenue model | Seat + usage SaaS |
| Why buyers pay | ChatGPT doesn't know company context safely |
| How they reached market | Enterprise assistant PLG |
| Source links | https://dust.tt |
| Portfolio lesson | Packaged team templates for first install |

### 39. Voiceflow

**Stack:** WitnessBC · **Product / service:** Conversation agent builder

| Field | Answer |
|-------|--------|
| What they sell | Build chat and voice agents with logs and analytics |
| Who runs it | Vendor SaaS |
| How it runs | Visual builder; deploy channels; conversation logs |
| Who buys | CX and product teams |
| Pricing / cost | Free + paid team tiers — https://www.voiceflow.com/pricing |
| Revenue model | Seat + usage SaaS |
| Why buyers pay | Need CX agents without custom dev |
| How they reached market | Conversation design community → SaaS |
| Source links | https://www.voiceflow.com |
| Portfolio lesson | Conversation run history on agent loops |

### 40. Maven AGI

**Stack:** WitnessBC · **Product / service:** Enterprise support agents

| Field | Answer |
|-------|--------|
| What they sell | AI agents for customer support with escalation workflows |
| Who runs it | Vendor SaaS enterprise |
| How it runs | Agent resolves tickets; logs actions; escalates |
| Who buys | Support leaders at mid-market+ |
| Pricing / cost | Enterprise custom |
| Revenue model | Annual enterprise + usage |
| Why buyers pay | Support volume exceeds headcount |
| How they reached market | Support AI enterprise sales |
| Source links | https://www.mavenagi.com |
| Portfolio lesson | Escalation + action log per ticket pattern |

## 3. Noetfield — AI governance + Copilot/board evidence (rows 41–60)

### 41. VerifyWise

**Stack:** Noetfield · **Product / service:** AI governance platform

| Field | Answer |
|-------|--------|
| What they sell | Register, assess, govern, and monitor AI systems — EU AI Act, ISO 42001, NIST |
| Who runs it | Self-hosted or managed cloud; source-available |
| How it runs | Registry → risk assessment → policy enforcement → audit export |
| Who buys | SMB to enterprise compliance teams |
| Pricing / cost | Free start; Enterprise Plus custom — https://verifywise.ai/pricing |
| Revenue model | No per-seat; enterprise deployment |
| Why buyers pay | Six-figure Credo contracts exclude startups |
| How they reached market | Open source → free tier → enterprise |
| Source links | https://verifywise.ai · https://verifywise.ai/pricing |
| Portfolio lesson | AI system inventory + one-click board export for Copilot programs |

### 42. FairNow

**Stack:** Noetfield · **Product / service:** AI governance & compliance

| Field | Answer |
|-------|--------|
| What they sell | Centralize AI inventory, automate risk assessments and compliance workflows |
| Who runs it | Vendor SaaS (acquired AuditBoard 2025) |
| How it runs | AI registry; automated bias tests; evidence collection |
| Who buys | Enterprise compliance in financial services and HR |
| Pricing / cost | Contact sales; no public pricing |
| Revenue model | Enterprise annual SaaS |
| Why buyers pay | Manual GRC can't keep up with AI regulation |
| How they reached market | Seed 2023 → AuditBoard acquisition |
| Source links | https://www.fairnow.ai |
| Portfolio lesson | Automated evidence collection for board packs |

### 43. Credo AI

**Stack:** Noetfield · **Product / service:** AI governance platform

| Field | Answer |
|-------|--------|
| What they sell | Discover, assess, and govern every AI agent, model, and application continuously |
| Who runs it | Enterprise SaaS |
| How it runs | AI Registry + Policy Engine + Risk Intelligence |
| Who buys | Fortune 500 and regulated enterprises |
| Pricing / cost | Contact sales; six-figure contracts typical (market) |
| Revenue model | Enterprise annual platform fee |
| Why buyers pay | Regulators demand continuous AI governance not quarterly audits |
| How they reached market | Forrester Wave Leader; policy pack co-authoring |
| Source links | https://www.credo.ai |
| Portfolio lesson | Board-ready audit pack pattern for NW1 Copilot wedge |

### 44. Giskard

**Stack:** Noetfield · **Product / service:** LLM agent testing

| Field | Answer |
|-------|--------|
| What they sell | Test AI agents to catch issues before production |
| Who runs it | OSS + Hub enterprise |
| How it runs | Test library in CI; Hub for continuous red-team |
| Who buys | ML and AI QA engineers |
| Pricing / cost | OSS free; Hub contact sales |
| Revenue model | OSS + enterprise Hub |
| Why buyers pay | Copilot plugins fail silently without pre-prod tests |
| How they reached market | OSS Paris 2021 |
| Source links | https://www.giskard.ai |
| Portfolio lesson | Pre-prod Copilot/agent regression tests |

### 45. Promptfoo

**Stack:** Noetfield · **Product / service:** LLM security eval

| Field | Answer |
|-------|--------|
| What they sell | Red-team and eval prompts, agents, RAG in CI |
| Who runs it | OSS + enterprise |
| How it runs | CLI matrix evals; 50+ attack plugins |
| Who buys | DevSec and platform teams |
| Pricing / cost | Community free; enterprise custom |
| Revenue model | OSS + enterprise |
| Why buyers pay | AI security vulnerabilities before production |
| How they reached market | OSS → OpenAI acquisition 2026 |
| Source links | https://www.promptfoo.dev |
| Portfolio lesson | Microsoft Copilot plugin eval gate in CI |

### 46. Holistic AI

**Stack:** Noetfield · **Product / service:** AI risk platform

| Field | Answer |
|-------|--------|
| What they sell | Enterprise AI risk scoring and governance dashboard |
| Who runs it | Vendor SaaS |
| How it runs | Inventory; risk score; monitor drift |
| Who buys | Chief Risk Officers |
| Pricing / cost | Enterprise custom |
| Revenue model | Annual enterprise |
| Why buyers pay | EU AI Act and board scrutiny on AI |
| How they reached market | Enterprise sales |
| Source links | https://www.holisticai.com |
| Portfolio lesson | Copilot use-case risk register |

### 47. Monitaur

**Stack:** Noetfield · **Product / service:** ML governance

| Field | Answer |
|-------|--------|
| What they sell | End-to-end ML governance lifecycle |
| Who runs it | Vendor SaaS |
| How it runs | Document models; approval workflows; audit logs |
| Who buys | Regulated industries |
| Pricing / cost | Enterprise custom |
| Revenue model | Annual enterprise |
| Why buyers pay | Model approval trails required by regulators |
| How they reached market | Regulated ML focus |
| Source links | https://www.monitaur.ai |
| Portfolio lesson | Approval workflow per AI system |

### 48. Arthur AI

**Stack:** Noetfield · **Product / service:** AI performance monitoring

| Field | Answer |
|-------|--------|
| What they sell | Monitor model and LLM quality, bias, drift |
| Who runs it | Vendor SaaS |
| How it runs | Ingest outputs; dashboards; alerts |
| Who buys | Model owners |
| Pricing / cost | Enterprise custom |
| Revenue model | Annual enterprise |
| Why buyers pay | Copilot answers degrade over time unnoticed |
| How they reached market | ML monitoring brand |
| Source links | https://www.arthur.ai |
| Portfolio lesson | Drift alerts on Copilot outputs |

### 49. Fiddler AI

**Stack:** Noetfield · **Product / service:** Model performance management

| Field | Answer |
|-------|--------|
| What they sell | Explainability and monitoring for ML models |
| Who runs it | Vendor SaaS |
| How it runs | Explain predictions; monitor drift; report |
| Who buys | ML platform teams |
| Pricing / cost | Enterprise custom |
| Revenue model | Annual enterprise |
| Why buyers pay | Explain high-risk AI decisions to auditors |
| How they reached market | Explainability wedge |
| Source links | https://www.fiddler.ai |
| Portfolio lesson | Explainability on high-risk Copilot answers |

### 50. Lakera

**Stack:** Noetfield · **Product / service:** LLM firewall

| Field | Answer |
|-------|--------|
| What they sell | Runtime security for GenAI applications |
| Who runs it | Vendor SaaS |
| How it runs | API guard scans prompts; block/allow log |
| Who buys | AppSec teams |
| Pricing / cost | Enterprise custom |
| Revenue model | API + enterprise |
| Why buyers pay | Prompt injection on enterprise Copilot |
| How they reached market | GenAI security |
| Source links | https://www.lakera.ai |
| Portfolio lesson | Block/allow log per prompt at dispatch |

### 51. Lasso Security

**Stack:** Noetfield · **Product / service:** GenAI security

| Field | Answer |
|-------|--------|
| What they sell | Shadow AI discovery and GenAI app protection |
| Who runs it | Vendor SaaS |
| How it runs | Scan enterprise; policy enforcement |
| Who buys | CISO |
| Pricing / cost | Custom tiers |
| Revenue model | Annual SaaS |
| Why buyers pay | Shadow Copilot and ChatGPT use |
| How they reached market | GenAI security startup |
| Source links | https://www.lasso.security |
| Portfolio lesson | Shadow Copilot discovery for NW1 |

### 52. Cranium

**Stack:** Noetfield · **Product / service:** AI security platform

| Field | Answer |
|-------|--------|
| What they sell | AI asset visibility and third-party AI risk |
| Who runs it | Vendor SaaS |
| How it runs | Discover AI assets; assess vendor AI risk |
| Who buys | Security teams |
| Pricing / cost | Enterprise custom |
| Revenue model | Annual enterprise |
| Why buyers pay | Third-party AI in supply chain is invisible |
| How they reached market | AI security startup |
| Source links | https://cranium.ai |
| Portfolio lesson | Third-party AI inventory |

### 53. HiddenLayer

**Stack:** Noetfield · **Product / service:** ML security

| Field | Answer |
|-------|--------|
| What they sell | Model security and threat detection for AI |
| Who runs it | Vendor SaaS |
| How it runs | Monitor models; detect adversarial attacks |
| Who buys | Security operations |
| Pricing / cost | Enterprise custom |
| Revenue model | Annual enterprise |
| Why buyers pay | AI models are attack surface |
| How they reached market | ML security specialist |
| Source links | https://hiddenlayer.com |
| Portfolio lesson | Threat detection on AI apps |

### 54. Enkrypt AI

**Stack:** Noetfield · **Product / service:** LLM firewall

| Field | Answer |
|-------|--------|
| What they sell | Secure gateway for LLM applications |
| Who runs it | Vendor SaaS |
| How it runs | Proxy LLM calls; policy enforcement log |
| Who buys | Security teams |
| Pricing / cost | Startup tiers |
| Revenue model | Usage + enterprise |
| Why buyers pay | Data leakage via LLM prompts |
| How they reached market | LLM firewall startup |
| Source links | https://www.enkryptai.com |
| Portfolio lesson | Policy enforcement log per call |

### 55. ModelOp

**Stack:** Noetfield · **Product / service:** Model governance

| Field | Answer |
|-------|--------|
| What they sell | Enterprise AI governance for banks and insurance |
| Who runs it | Vendor SaaS |
| How it runs | Model inventory; governance workflows; reporting |
| Who buys | Bank/insurance compliance |
| Pricing / cost | Enterprise custom |
| Revenue model | Annual enterprise |
| Why buyers pay | Regulators require model inventory |
| How they reached market | Financial services ML governance |
| Source links | https://www.modelop.com |
| Portfolio lesson | Enterprise AI registry pattern |

### 56. Langfuse

**Stack:** Noetfield · **Product / service:** LLM observability

| Field | Answer |
|-------|--------|
| What they sell | Traces, evals, prompts for LLM applications |
| Who runs it | Cloud or self-host MIT |
| How it runs | OpenTelemetry traces; session tracking; cost dashboard |
| Who buys | AI engineering |
| Pricing / cost | Free 50k obs; Core $29/mo — https://langfuse.com/pricing |
| Revenue model | Usage SaaS + OSS |
| Why buyers pay | Can't audit Copilot without per-action trail |
| How they reached market | OSS → cloud |
| Source links | https://langfuse.com/pricing |
| Portfolio lesson | Per-action audit trail for Copilot runs |

### 57. Braintrust

**Stack:** Noetfield · **Product / service:** Eval platform

| Field | Answer |
|-------|--------|
| What they sell | Evals and logging for AI products in production |
| Who runs it | Managed cloud |
| How it runs | Log production; run eval suites; compare versions |
| Who buys | AI product teams |
| Pricing / cost | From ~$249/mo |
| Revenue model | Platform + usage |
| Why buyers pay | Board wants pass-rate trend not anecdotes |
| How they reached market | Eval-first for AI products |
| Source links | https://www.braintrust.dev |
| Portfolio lesson | Board metric: pass rate trend over time |

### 58. Collibra

**Stack:** Noetfield · **Product / service:** Data + AI governance

| Field | Answer |
|-------|--------|
| What they sell | Data governance extended to AI assets |
| Who runs it | Enterprise SaaS (pattern reference) |
| How it runs | Catalog data and AI; lineage; policy |
| Who buys | Data governance teams |
| Pricing / cost | Enterprise custom |
| Revenue model | Annual enterprise |
| Why buyers pay | AI outputs need data lineage |
| How they reached market | Incumbent data gov extends to AI |
| Source links | https://www.collibra.com |
| Portfolio lesson | Data lineage on AI outputs (pattern) |

### 59. OneTrust

**Stack:** Noetfield · **Product / service:** Privacy + AI governance

| Field | Answer |
|-------|--------|
| What they sell | Privacy, GRC, and AI governance modules |
| Who runs it | Enterprise SaaS (pattern reference) |
| How it runs | DPIA; AI use register; policy workflows |
| Who buys | Privacy and GRC leaders |
| Pricing / cost | Enterprise custom |
| Revenue model | Annual enterprise |
| Why buyers pay | Privacy and AI regulations overlap |
| How they reached market | Privacy platform adds AI module |
| Source links | https://www.onetrust.com |
| Portfolio lesson | DPIA + AI use register (pattern) |

### 60. IBM watsonx.governance

**Stack:** Noetfield · **Product / service:** AI governance suite

| Field | Answer |
|-------|--------|
| What they sell | Govern, monitor, and manage AI models enterprise-wide |
| Who runs it | IBM enterprise SaaS (pattern reference) |
| How it runs | Model inventory; bias detection; lifecycle governance |
| Who buys | Large enterprise |
| Pricing / cost | Enterprise custom |
| Revenue model | Annual enterprise license |
| Why buyers pay | Executive dashboard for AI risk |
| How they reached market | IBM enterprise sales |
| Source links | https://www.ibm.com/watsonx |
| Portfolio lesson | Executive dashboard pattern only — not primary comparable |

## 4. TrustField — Canadian MSB / FINTRAC program infra (rows 61–80)

### 61. Comply North

**Stack:** TrustField · **Product / service:** Canadian MSB compliance consulting

| Field | Answer |
|-------|--------|
| What they sell | FINTRAC MSB registration, bank onboarding, CCO packages for Canadian MSBs |
| Who runs it | Consulting firm + policy tools |
| How it runs | Fixed-scope packages; consultant handles FINTRAC communication |
| Who buys | Canadian MSB founders and fintechs |
| Pricing / cost | MSB registration $2,999 CAD; AML policies $999; CCO $1,999–3,999 — https://complynorth.com/pricing |
| Revenue model | Fixed-scope service packages |
| Why buyers pay | Consultants charge 40–50% markup; need transparent CAD pricing |
| How they reached market | Fixed-price packages + FINTRAC expertise |
| Source links | https://complynorth.com · https://complynorth.com/pricing |
| Portfolio lesson | Fixed CAD SKU cards on TrustField product page |

### 62. ComplyNorth Policies

**Stack:** TrustField · **Product / service:** AML policy generator

| Field | Answer |
|-------|--------|
| What they sell | FINTRAC-ready AML policies in minutes — instant download |
| Who runs it | Self-serve SaaS tool |
| How it runs | Answer questionnaire; pay once; download 5 policies |
| Who buys | New Canadian MSBs |
| Pricing / cost | From $99.99 CAD one-time — https://policies.complynorth.com |
| Revenue model | One-time purchase |
| Why buyers pay | Consultants take 2–4 weeks and charge $3,000+ |
| How they reached market | Self-serve policy generator PLG |
| Source links | https://policies.complynorth.com |
| Portfolio lesson | Instant policy download SKU for MSB onboarding |

### 63. BriteBase

**Stack:** TrustField · **Product / service:** Compliance-as-a-Service Canada

| Field | Answer |
|-------|--------|
| What they sell | AML operating platform + fractional CAMLO for Canadian MSBs |
| Who runs it | CaaS vendor + practitioner bench |
| How it runs | Platform + named fractional compliance officer owns five pillars |
| Who buys | Lean Canadian MSB/PSP |
| Pricing / cost | Managed AML tiers (contact); predictable annual vs hiring CCO $230k+ |
| Revenue model | Annual CaaS retainer |
| Why buyers pay | Full CCO hire is category mismatch for lean MSB |
| How they reached market | Canadian MSB CaaS wedge |
| Source links | https://britebase.ca |
| Portfolio lesson | Platform + fractional CAMLO bundle — TrustField operating model |

### 64. Outlier Solutions

**Stack:** TrustField · **Product / service:** Canadian compliance consulting

| Field | Answer |
|-------|--------|
| What they sell | Compliance solutions for MSBs, fintechs, and reporting entities |
| Who runs it | Consulting firm |
| How it runs | Advisory; program build; examination prep |
| Who buys | Canadian reporting entities |
| Pricing / cost | Custom consulting fees |
| Revenue model | Project + retainer services |
| Why buyers pay | FINTRAC examinations require expert guidance |
| How they reached market | Canadian compliance consultancy |
| Source links | https://www.outliercanada.com |
| Portfolio lesson | FINTRAC examination prep service line |

### 65. Sumsub

**Stack:** TrustField · **Product / service:** KYC/KYB verification

| Field | Answer |
|-------|--------|
| What they sell | Identity verification and AML screening API |
| Who runs it | Vendor SaaS API |
| How it runs | API verification; ongoing monitoring; case management |
| Who buys | Fintechs and marketplaces |
| Pricing / cost | From ~$1.35/verification public tier — https://sumsub.com/pricing |
| Revenue model | Per-verification usage |
| Why buyers pay | Build vs buy on KYC is obvious at scale |
| How they reached market | API-first PLG for fintech |
| Source links | https://sumsub.com/pricing |
| Portfolio lesson | Customer onboarding check API for MSB intake |

### 66. Persona

**Stack:** TrustField · **Product / service:** Identity verification

| Field | Answer |
|-------|--------|
| What they sell | Verify customers with configurable identity flows |
| Who runs it | Vendor SaaS API |
| How it runs | Hosted verification flows; case review dashboard |
| Who buys | Fintech product teams |
| Pricing / cost | Usage/custom pricing |
| Revenue model | Per-verification + platform |
| Why buyers pay | KYC UX and compliance in one API |
| How they reached market | Developer-first identity |
| Source links | https://withpersona.com |
| Portfolio lesson | KYC case file per customer in TrustField sandbox |

### 67. Middesk

**Stack:** TrustField · **Product / service:** KYB automation

| Field | Answer |
|-------|--------|
| What they sell | Automate business verification for B2B onboarding |
| Who runs it | Vendor SaaS |
| How it runs | API + dashboard for business entity verification |
| Who buys | B2B fintech and platforms |
| Pricing / cost | Custom pricing |
| Revenue model | Annual + usage |
| Why buyers pay | Manual KYB on business customers is slow |
| How they reached market | KYB API wedge |
| Source links | https://www.middesk.com |
| Portfolio lesson | Business verification workflow in MSB program |

### 68. Flagright

**Stack:** TrustField · **Product / service:** AML for fintech

| Field | Answer |
|-------|--------|
| What they sell | AML monitoring and case management for neobanks |
| Who runs it | Vendor SaaS |
| How it runs | Transaction monitoring; alert queue; case manager |
| Who buys | Neobanks and fintechs |
| Pricing / cost | Startup-friendly custom |
| Revenue model | Usage + platform annual |
| Why buyers pay | AML build in-house takes years |
| How they reached market | Fintech AML startup |
| Source links | https://www.flagright.com |
| Portfolio lesson | Transaction alert queue for MSB monitoring |

### 69. Salv

**Stack:** TrustField · **Product / service:** AML intelligence network

| Field | Answer |
|-------|--------|
| What they sell | AML and fraud with shared intelligence network |
| Who runs it | Vendor SaaS |
| How it runs | Screening + network alerts + case tools |
| Who buys | EU fintechs |
| Pricing / cost | Custom pricing |
| Revenue model | Annual platform |
| Why buyers pay | Isolated AML misses network fraud patterns |
| How they reached market | Consortium AML startup |
| Source links | https://www.salv.com |
| Portfolio lesson | Shared intelligence alerts pattern |

### 70. Hummingbird

**Stack:** TrustField · **Product / service:** AML case management

| Field | Answer |
|-------|--------|
| What they sell | Case management for financial crime investigations |
| Who runs it | Vendor SaaS |
| How it runs | Alert triage; investigation narrative; SAR prep assist |
| Who buys | Compliance operations teams |
| Pricing / cost | Custom enterprise |
| Revenue model | Annual enterprise |
| Why buyers pay | Investigators drown in alerts without case UX |
| How they reached market | Compliance ops case management |
| Source links | https://www.hummingbird.co |
| Portfolio lesson | Investigator case timeline export |

### 71. Notabene

**Stack:** TrustField · **Product / service:** Travel Rule compliance

| Field | Answer |
|-------|--------|
| What they sell | Travel Rule messaging for crypto VASPs |
| Who runs it | Vendor SaaS network |
| How it runs | VASP-to-VASP Travel Rule protocol |
| Who buys | Crypto exchanges and VASPs |
| Pricing / cost | Custom pricing |
| Revenue model | Network + usage |
| Why buyers pay | Travel Rule is mandatory for crypto transfers |
| How they reached market | Crypto compliance network |
| Source links | https://www.notabene.id |
| Portfolio lesson | Cross-border crypto compliance — TrustField lane not VIRLUX |

### 72. Sygna

**Stack:** TrustField · **Product / service:** Travel Rule network

| Field | Answer |
|-------|--------|
| What they sell | Travel Rule and AML for virtual asset service providers |
| Who runs it | Vendor SaaS |
| How it runs | Bridge messaging; compliance dashboard |
| Who buys | VASPs globally |
| Pricing / cost | Custom pricing |
| Revenue model | Network SaaS |
| Why buyers pay | Regulatory Travel Rule compliance |
| How they reached market | Asia-origin Travel Rule leader |
| Source links | https://www.sygna.io |
| Portfolio lesson | VASP messaging — defer to TrustField/future crypto MSB |

### 73. Crystal Intelligence

**Stack:** TrustField · **Product / service:** Blockchain analytics

| Field | Answer |
|-------|--------|
| What they sell | Crypto transaction monitoring and investigation |
| Who runs it | Vendor SaaS |
| How it runs | Wallet screening; risk scoring; case export |
| Who buys | Crypto firms mid-market |
| Pricing / cost | ~$25,000–60,000/yr small firm (market est.) |
| Revenue model | Annual by volume/modules |
| Why buyers pay | Crypto MSBs need chain analytics |
| How they reached market | Mid-market crypto compliance |
| Source links | https://crystalintelligence.com |
| Portfolio lesson | Wallet screening if TrustField serves crypto MSB |

### 74. TRM Labs

**Stack:** TrustField · **Product / service:** Blockchain intelligence

| Field | Answer |
|-------|--------|
| What they sell | Crypto compliance and forensics platform |
| Who runs it | Vendor SaaS |
| How it runs | KYT screening; investigations; FedRAMP for gov |
| Who buys | Crypto exchanges and banks |
| Pricing / cost | ~$40,000–90,000/yr small (market); startup programs available |
| Revenue model | Annual enterprise |
| Why buyers pay | Regulators expect blockchain analytics on crypto |
| How they reached market | Startup programs for young crypto firms |
| Source links | https://www.trmlabs.com |
| Portfolio lesson | Risk scoring on transfers — TrustField not VIRLUX |

### 75. Elliptic

**Stack:** TrustField · **Product / service:** Crypto compliance

| Field | Answer |
|-------|--------|
| What they sell | Blockchain analytics for compliance and investigations |
| Who runs it | Vendor SaaS |
| How it runs | Screening; wallet attribution; case building |
| Who buys | Crypto and fintech |
| Pricing / cost | ~$40,000–80,000/yr small (market) |
| Revenue model | Annual enterprise |
| Why buyers pay | Crypto AML requires proven analytics vendor |
| How they reached market | European crypto compliance leader |
| Source links | https://www.elliptic.co |
| Portfolio lesson | Compliance case export for crypto MSB |

### 76. PassFort

**Stack:** TrustField · **Product / service:** KYC orchestration

| Field | Answer |
|-------|--------|
| What they sell | Orchestrate KYC/KYB workflows with policy engine |
| Who runs it | Vendor SaaS |
| How it runs | Policy-driven onboarding; vendor orchestration |
| Who buys | Banks and fintech |
| Pricing / cost | Custom enterprise |
| Revenue model | Annual platform |
| Why buyers pay | KYC vendor fragmentation needs orchestration |
| How they reached market | KYC orchestration mid-market |
| Source links | https://www.passfort.com |
| Portfolio lesson | Policy-driven onboarding orchestration |

### 77. ComplyAdvantage

**Stack:** TrustField · **Product / service:** Sanctions screening

| Field | Answer |
|-------|--------|
| What they sell | AI-driven sanctions and PEP screening |
| Who runs it | Vendor SaaS API |
| How it runs | Real-time screening; ongoing monitoring; case manager |
| Who buys | AML teams globally |
| Pricing / cost | Custom by volume |
| Revenue model | Usage + platform annual |
| Why buyers pay | Sanctions lists change daily; manual screening fails |
| How they reached market | API-first AML data |
| Source links | https://complyadvantage.com |
| Portfolio lesson | Ongoing sanctions rescreen workflow |

### 78. Hawk AI

**Stack:** TrustField · **Product / service:** AML and fraud

| Field | Answer |
|-------|--------|
| What they sell | AI-powered AML and fraud detection for banks |
| Who runs it | Vendor SaaS |
| How it runs | Transaction monitoring; alert scoring; investigator UI |
| Who buys | Banks and payment firms |
| Pricing / cost | Custom enterprise |
| Revenue model | Annual enterprise |
| Why buyers pay | False positive overload without AI triage |
| How they reached market | Bank AML AI |
| Source links | https://www.hawk.ai |
| Portfolio lesson | Alert triage dashboard for MSB ops |

### 79. Lucinity

**Stack:** TrustField · **Product / service:** AML investigation

| Field | Answer |
|-------|--------|
| What they sell | Case manager with AI-assisted investigation narratives |
| Who runs it | Vendor SaaS |
| How it runs | Case workflow; AI narrative; SAR support |
| Who buys | AML investigators |
| Pricing / cost | Custom enterprise |
| Revenue model | Annual enterprise |
| Why buyers pay | Investigation write-ups take hours per alert |
| How they reached market | Investigator UX startup |
| Source links | https://lucinity.com |
| Portfolio lesson | Investigation narrative export for FINTRAC STR prep |

### 80. RationalGo

**Stack:** TrustField · **Product / service:** FINTRAC reporting tools

| Field | Answer |
|-------|--------|
| What they sell | Lower-barrier tools for Canadian FINTRAC reporting workflows |
| Who runs it | Vendor SaaS (verify live site) |
| How it runs | Assist STR/LCTR workflow and reporting |
| Who buys | Small Canadian MSBs |
| Pricing / cost | Low-barrier pricing (verify on site) |
| Revenue model | Subscription or per-report |
| Why buyers pay | Manual FINTRAC reporting is error-prone |
| How they reached market | Canadian MSB niche tools |
| Source links | Search RationalGo FINTRAC — verify live pricing |
| Portfolio lesson | STR/LCTR workflow assist for lean MSB |

## 5. VIRLUX — agentic factory building SaaS (rows 81–100)

### 81. Nagent

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** Agent marketplace & builder

| Field | Answer |
|-------|--------|
| What they sell | Discover, build, publish, and monetize AI agents — no-code platform |
| Who runs it | Vendor SaaS marketplace |
| How it runs | Browse marketplace; run agents; builders publish with 15% commission |
| Who buys | Agent builders and business users |
| Pricing / cost | $49 / $199 / $9,999/mo — https://nagent.ai/pricing |
| Revenue model | Subscription + marketplace commission |
| Why buyers pay | Need agents without building from scratch |
| How they reached market | Marketplace + builder PLG 2024 |
| Source links | https://nagent.ai · https://nagent.ai/pricing |
| Portfolio lesson | Factory catalog + monetization — core VIRLUX UX to copy |

### 82. FlowHunt

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** No-code AI agent builder

| Field | Answer |
|-------|--------|
| What they sell | Build AI workflows for marketing, SEO, sales — credit-based runs |
| Who runs it | Vendor SaaS |
| How it runs | Visual editor; template catalog; credit consumption per run |
| Who buys | Marketing and ops teams |
| Pricing / cost | €50–500/mo — https://www.flowhunt.io |
| Revenue model | Credit subscription |
| Why buyers pay | Non-dev teams need daily AI automation |
| How they reached market | EU PLG free trial → paid credits |
| Source links | https://www.flowhunt.io |
| Portfolio lesson | Template catalog + run credits for sandbox bay |

### 83. Gumloop

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** AI workflow automation

| Field | Answer |
|-------|--------|
| What they sell | No-code AI workflows with guardrails and MCP hosting |
| Who runs it | Vendor SaaS |
| How it runs | Canvas builder; concurrent agent runs; MCP server hosting |
| Who buys | Business teams |
| Pricing / cost | Free 5k credits; Pro $37/mo — https://www.gumloop.com/pricing |
| Revenue model | Credit SaaS |
| Why buyers pay | Governed automation without engineering |
| How they reached market | PLG $37/mo wedge |
| Source links | https://www.gumloop.com/pricing |
| Portfolio lesson | Guardrails + MCP hosting on factory runs |

### 84. Relevance AI

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** AI workforce

| Field | Answer |
|-------|--------|
| What they sell | Build agent workforce for GTM and operations tasks |
| Who runs it | Vendor SaaS |
| How it runs | Agent templates; actions metered; team workspaces |
| Who buys | GTM teams |
| Pricing / cost | Pro $19/mo; Team $234/mo |
| Revenue model | Actions + vendor credits |
| Why buyers pay | Delegate repetitive work to agents |
| How they reached market | Workforce positioning PLG |
| Source links | https://relevanceai.com/docs/get-started/pricing |
| Portfolio lesson | Prebuilt agent SKUs in factory catalog |

### 85. Stack AI

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** Enterprise agent builder

| Field | Answer |
|-------|--------|
| What they sell | No-code enterprise AI agents with compliance wrappers |
| Who runs it | Vendor SaaS |
| How it runs | Visual agent builder; deploy with SSO/RBAC |
| Who buys | Enterprise IT in regulated industries |
| Pricing / cost | Free 500 runs; enterprise custom |
| Revenue model | Enterprise annual |
| Why buyers pay | Need governed agents without custom dev |
| How they reached market | Enterprise compliance GTM |
| Source links | https://www.stack-ai.com |
| Portfolio lesson | Compliance wrapper tier on premium factories |

### 86. AgenticFlow

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** No-code AI automation

| Field | Answer |
|-------|--------|
| What they sell | AI automation for marketing and business workflows |
| Who runs it | Vendor SaaS |
| How it runs | Visual flows; multi-agent; templates |
| Who buys | SMB automation buyers |
| Pricing / cost | From ~$19/mo (market, launched 2024) |
| Revenue model | Freemium subscription |
| Why buyers pay | Marketing teams want AI without code |
| How they reached market | 2024 launch freemium |
| Source links | https://www.agenticflow.ai |
| Portfolio lesson | Marketing workflow templates in catalog |

### 87. Dify

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** LLM app/agent builder

| Field | Answer |
|-------|--------|
| What they sell | Open-source platform to build and deploy LLM apps and agents |
| Who runs it | OSS + Dify Cloud |
| How it runs | Visual workflow; RAG; agent tools; self-host option |
| Who buys | Developers and teams |
| Pricing / cost | OSS free; cloud tiers |
| Revenue model | OSS + cloud SaaS |
| Why buyers pay | Want agent builder without lock-in |
| How they reached market | OSS community → cloud |
| Source links | https://dify.ai |
| Portfolio lesson | Self-host factory studio option |

### 88. Langflow

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** Visual agent builder

| Field | Answer |
|-------|--------|
| What they sell | Open-source visual framework for building LangChain agents |
| Who runs it | OSS + DataStax cloud |
| How it runs | Drag-drop agent graph; fork templates |
| Who buys | Python/LLM developers |
| Pricing / cost | OSS free; cloud paid |
| Revenue model | OSS + enterprise cloud |
| Why buyers pay | Visual agent composition speeds prototyping |
| How they reached market | OSS → DataStax backing |
| Source links | https://www.langflow.org |
| Portfolio lesson | Forkable factory specs in Studio tab |

### 89. Voiceflow

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** Conversation agent platform

| Field | Answer |
|-------|--------|
| What they sell | Build and deploy chat/voice agents with analytics |
| Who runs it | Vendor SaaS |
| How it runs | Design conversations; deploy channels; log runs |
| Who buys | CX builders |
| Pricing / cost | Free + team paid tiers |
| Revenue model | Seat + usage SaaS |
| Why buyers pay | CX agents need logs and iteration |
| How they reached market | Conversation design community |
| Source links | https://www.voiceflow.com |
| Portfolio lesson | Template marketplace pattern for catalog |

### 90. Beam.ai

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** Enterprise agent automation

| Field | Answer |
|-------|--------|
| What they sell | AI agents for enterprise process automation |
| Who runs it | Vendor SaaS |
| How it runs | Prebuilt agents; supervisor/worker model; integrations |
| Who buys | Enterprise ops |
| Pricing / cost | Custom/team pricing |
| Revenue model | Enterprise annual |
| Why buyers pay | Enterprise wants agent teams not chatbots |
| How they reached market | Enterprise agent automation sales |
| Source links | https://beam.ai |
| Portfolio lesson | Specialist agent teams tab — hire crew pattern |

### 91. MindStudio

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** AI app builder

| Field | Answer |
|-------|--------|
| What they sell | Build and publish AI apps without code |
| Who runs it | Vendor SaaS |
| How it runs | Visual builder; publish to store; usage metering |
| Who buys | Prosumer and builder segment |
| Pricing / cost | Usage tiers |
| Revenue model | Usage + subscription |
| Why buyers pay | Publish agents as products quickly |
| How they reached market | App store for AI apps |
| Source links | https://www.mindstudio.ai |
| Portfolio lesson | Publish factory template to catalog store |

### 92. Wordware

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** Natural-language AI apps

| Field | Answer |
|-------|--------|
| What they sell | Build AI apps from natural language specifications |
| Who runs it | Vendor SaaS beta |
| How it runs | Describe app in language; deploy agent |
| Who buys | Prompt engineers and founders |
| Pricing / cost | Beta/custom |
| Revenue model | Subscription |
| Why buyers pay | Natural-language lowers builder barrier |
| How they reached market | Prompt-native builder hype 2024–25 |
| Source links | https://www.wordware.ai |
| Portfolio lesson | Prompt-led factory compose in Studio |

### 93. Lindy

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** Natural-language agents

| Field | Answer |
|-------|--------|
| What they sell | Build AI agents by describing tasks in plain language |
| Who runs it | Vendor SaaS |
| How it runs | Natural language agent config; integrations |
| Who buys | SMB operators |
| Pricing / cost | From ~$49/mo (market) |
| Revenue model | Seat + usage SaaS |
| Why buyers pay | Non-dev founders need agents fast |
| How they reached market | Natural language agent PLG |
| Source links | https://www.lindy.ai |
| Portfolio lesson | Natural-language factory fork in Studio |

### 94. Relay.app

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** Human-in-the-Auto Runtimemation

| Field | Answer |
|-------|--------|
| What they sell | Automations with human approval checkpoints |
| Who runs it | Vendor SaaS |
| How it runs | Workflow with pause for approval |
| Who buys | Ops teams |
| Pricing / cost | From ~$19/mo |
| Revenue model | Seat SaaS |
| Why buyers pay | Agents need founder approval before irreversible acts |
| How they reached market | SMB ops PLG |
| Source links | https://www.relay.app |
| Portfolio lesson | Founder approval gate before live bay upgrade |

### 95. Activepieces

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** Open automation platform

| Field | Answer |
|-------|--------|
| What they sell | Self-hostable automation with pieces (modules) |
| Who runs it | OSS + cloud |
| How it runs | Compose flows from pieces; run history |
| Who buys | Developers |
| Pricing / cost | OSS free; cloud paid |
| Revenue model | OSS + cloud |
| Why buyers pay | Factory modules as composable pieces |
| How they reached market | OSS automation |
| Source links | https://www.activepieces.com |
| Portfolio lesson | Piece = factory module in catalog |

### 96. Pipedream

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** Code-first workflows

| Field | Answer |
|-------|--------|
| What they sell | Integrate APIs with code workflows and event triggers |
| Who runs it | Vendor SaaS |
| How it runs | Code steps; connectors; run log |
| Who buys | Developers |
| Pricing / cost | Free + usage tiers |
| Revenue model | Usage SaaS |
| Why buyers pay | Connectors accelerate factory tool wiring |
| How they reached market | Developer integration PLG |
| Source links | https://pipedream.com |
| Portfolio lesson | Connectors as factory tool integrations |

### 97. Trigger.dev

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** Background job platform

| Field | Answer |
|-------|--------|
| What they sell | Durable TypeScript jobs with run dashboard |
| Who runs it | Cloud + OSS self-host |
| How it runs | Task execution with retries and observability UI |
| Who buys | Dev teams |
| Pricing / cost | Free + $10 + $50/mo — https://trigger.dev/pricing |
| Revenue model | Usage SaaS |
| Why buyers pay | Live factory runs need durable backend |
| How they reached market | Dev PLG |
| Source links | https://trigger.dev/pricing |
| Portfolio lesson | Run detail page backend for live bay executions |

### 98. Inngest

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** Durable serverless workflows

| Field | Answer |
|-------|--------|
| What they sell | Step functions for long-running serverless work |
| Who runs it | Cloud + OSS |
| How it runs | Event-driven durable steps with traces |
| Who buys | Product engineers |
| Pricing / cost | Free; Pro $75/mo |
| Revenue model | Execution-tier SaaS |
| Why buyers pay | Multi-step factory orchestration |
| How they reached market | Serverless ecosystem integrations |
| Source links | https://www.inngest.com/pricing |
| Portfolio lesson | Orchestrate multi-step factory runs in live bay |

### 99. Runlayer

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** MCP governance

| Field | Answer |
|-------|--------|
| What they sell | Govern MCP servers and agent tool access |
| Who runs it | Vendor SaaS |
| How it runs | Policy on MCP tools; audit agent tool calls |
| Who buys | Platform security teams |
| Pricing / cost | Custom enterprise |
| Revenue model | Enterprise annual |
| Why buyers pay | MCP sprawl needs governance not just hosting |
| How they reached market | MCP governance wedge 2025–26 |
| Source links | https://www.runlayer.com |
| Portfolio lesson | Integrate MCP governance — do not compete (VIRLUX vision) |

### 100. Subtext

**Stack:** VIRLUX (agentic factory SaaS) · **Product / service:** UI proof for agents

| Field | Answer |
|-------|--------|
| What they sell | Prove agent UI actions with verifiable proof layer |
| Who runs it | Young startup (verify site) |
| How it runs | Capture UI proof of agent actions for buyers |
| Who buys | Builder tools ecosystem |
| Pricing / cost | Verify on site |
| Revenue model | SaaS/API |
| Why buyers pay | Buyers don't trust agent demos without UI proof |
| How they reached market | Agent proof ecosystem |
| Source links | Search subtext UI proof agents |
| Portfolio lesson | Pair UI proof with verify receipt — VIRLUX marketplace field |


---

## 6. Cross-stack implementation patterns (ASF agreed)

| Pattern | Vendor example | Buyer sees | Implement anywhere |
|---------|----------------|------------|-------------------|
| Run detail page | Trigger.dev | Pass/fail, steps, logs, retry | Worker Hub job dashboard |
| Agent trace | Langfuse | Turn timeline + cost | Trace on every dispatch |
| Policy at dispatch | Lakera / Gumloop | Allow/block + reason | Pre-LLM policy gate |
| Evidence export | VerifyWise / LowerPlane | Downloadable audit bundle | One-click compliance pack |
| Fixed-scope MSB SKU | Comply North | $2,999 CAD registration | TrustField product page |
| Factory catalog | Nagent | Browse → run → receipt | VIRLUX `/dashboard/factory` |
| Honest tier ladder | VIRLUX internal | mock_only → freemium_cap → production | Label on every run surface |

---

## 7. VIRLUX north star (post-pivot)

Sandbox → freemium cap → paid bay + **run detail page** + **MCP verify receipt**. No payment rails on VIRLUX.

*Locked ASF 2026-06-20 · 100 comparable rows · market-first reasoning.*
