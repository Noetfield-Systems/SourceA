# SourceA Competitor Landscape — Research Report v1.2

**Saved:** 2026-06-16T04:33:35Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15  
**Track:** commercial · competitive intelligence  
**Authority (compare only):** `SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md` · `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md`  
**Threads:** STRATEGIC-SLICE · NW1 Noetfield · W3 revenue · pre-LLM gate (D15) · Asset B DFY  
**Intake merged:** `archive/attachments/commercial/SOURCEA_NOETFIELD_COMPETITOR_LANDSCAPE_2026-06-15_v1_3.md` (external-eye 30-company map · Jun 2026)  
**Supersedes intake:** v1_1 · **Report delta v1.2:** Asset B disk SKU bridge in revenue models

---

## Executive verdict

SourceA competes in **L6 governed execution** — not L0 models, not L7 chat UI, not L3 orchestration alone.

**Closest direct competitors (2025–2026):** Notenic, FuseGov, , ThinkNEO, AgentPEP, Predicate Authority, , WitnessAI, Credo AI GAIA, Securiti, Microsoft Authorization Fabric + Purview. *(Tier 1 below — tighter architectural fit than gateway/GRC names in the 30-map.)*

**Noetfield lane competitors:** Securiti Copilot Readiness,  (Copilot Studio), Microsoft Purview (native), Credo AI, IBM watsonx.governance, Vanta/Drata (evidence posture).

**SourceA differentiation (honest):** self-hosted law-first receipts + validators + re-brief on SSOT change + founder-owned factory — **weaker** on cloud scale, SIEM packs, and sales motion; **stronger** on tamper-evident disk proof and anti-staleness boot (`critic_boot`).

**White space (one sentence):** Per-action enforcement **at dispatch** + **signed, tamper-evident, replayable receipt** — spread across gateways, GRC, security, and observability, but **unified by none**. Live proof: BLOCK → ALLOW → tamper-FAIL → replay in **<5 min**.

---

## Market map — 30 competitors (external-eye · Jun 2026)

**Class:** EXTERNAL_CRITIC synthesis — pitch/raise/NW1 context only. **Scale/signal = public funding or acquisition status, not audited revenue.** Full tables: intake doc §1.

| Category | Count | Examples | SourceA gap vs category |
|----------|-------|----------|-------------------------|
| **A. LLM / AI gateways** | 7 | Portkey, LiteLLM, Kong, Cloudflare, Vercel, OpenRouter, Helicone | Content/PII guardrails · routing — not per-action signed receipts |
| **B. Agent GRC / management** | 13 | watsonx, ServiceNow, OneTrust, Credo AI, Kore.ai, Palantir AIP | Policy lifecycle · evidence via integration — not dispatch enforcement |
| **C. AI security / runtime** | 8 | Lakera, Cisco AI Defense, Straiker, , WitnessAI | Detection / prompt firewall — not signed replayable ledger |
| **D. Observability / replay** | 2 | AgentOps, Arize | Replay + HITL — observes/pauses, does not enforce at dispatch |

**Also adjacent (not in 30):** Galileo, Langfuse, Confident AI, Aporia; Noma, Mindgard, Lasso, Patronus, Prompt Security→SentinelOne.

**Tier 1 L6 names (Notenic, FuseGov, AgentPEP, Predicate)** remain **closer architectural rivals** than gateway incumbents — see § Tier 1 below.

---

## Consolidation signals (public · HYPOTHESIS — verify before pitch)

| Acquirer / signal | Target (public report) | Implication for SourceA |
|-------------------|------------------------|-------------------------|
| Palo Alto Networks | Portkey (2026) | Gateways + governance layer = strategic M&A |
| Check Point | Lakera | Prompt security → platform bundle |
| Cisco | Robust Intelligence → AI Defense | Runtime AI security consolidation |
| SentinelOne | Prompt Security | AI security roll-up |
| ServiceNow | Traceloop → AI Control Tower | Agent observability → enterprise control plane |

**Use in raise/deck:** enforcement-receipt layer has **strategic value** beyond near-term ARR. **Do not** quote competitor revenue. Label **HYPOTHESIS** in outbound.

---

## Revenue models (ILLUSTRATIVE — not guarantees)

| Motion | Model | Disk anchor |
|--------|-------|-------------|
| **Noetfield DP** | CAD $2K deposit → NF-RD $5–10K → annual CAD $15–30K ACV (illustrative) | `NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_LOCKED_v1.md` |
| **Scale path** | 10 DPs Yr1 → ~CAD $150–300K ARR; enterprise CAD $50–150K+ post-SOC2 | SSOT §10–11 · intake v1.3 §3 |
| **Services bridge** | $3–10K project or $2–5K/mo retainer *(illustrative)* | **Disk SKUs:** Asset B DFY `SOURCEA_ASSET_B_GOVERNED_AGENTIC_AUTOMATION_LOCKED_v1.md` · agency $750/$299 `SOURCEA_AGENCY_PRODUCT_DEMO_SCRIPT_LOCKED_v1.md` · Buyer 1 $200–$2K/mo — SSOT §10 |
| **Exit lens** | Acquisition by governance/security incumbent | Consolidation table above · intake v1.3 §2 |

**Law:** Illustrative models ≠ roadmap · ≠ factory queue · confirm on buyer calls.

---

## Layer map — who competes where

| Layer | Job | Key competitors | SourceA / portfolio |
|-------|-----|-----------------|---------------------|
| **L0 Models** | Reasoning | OpenAI, Anthropic, Google Gemini | Commodity inside gate |
| **L3 Durable orchestration** | Crash-proof workflows | [Temporal](https://temporal.io/), [Inngest](https://www.inngest.com/), [Kestra](https://kestra.io/) | Partial — factory spine, not Temporal Cloud |
| **L4 Agent runtime** | Graphs, tools, memory | [LangGraph](https://www.langchain.com/langgraph), Microsoft Agent Framework, Devin | Cursor + Council — not product |
| **L5 Enterprise execution** | Approve → run → audit | [Hubler](https://www.hubler.ai/), OpenAI Frontier, PLATEER XGEN | Order Guardian + task orders |
| **L6 Governance PEP/PDP** | Block before action | Notenic, FuseGov, , AgentPEP, Predicate, ThinkNEO, Microsoft Auth Fabric | **Wedge** — ENFORCE, critic_boot, trust ledger |
| **L6 Compliance GRC** | Policy lifecycle, board packs | Credo AI, IBM watsonx, OneTrust, Holistic AI, Monitaur | **Noetfield** face |
| **L6 Copilot-specific** | M365 agent governance | Securiti, , Purview, WitnessAI | **Noetfield NF-RD** |
| **L1 Observe + economics** | Health, margin | Datadog, Paid.ai, Arthur, Fiddler | Growing — hub health, execution_truth |
| **L7 Surface** | Human orientation | Linear, Stripe Docs | Hub quarantined · standalone apps |

---

## Tier 1 — Direct L6 runtime governance (closest to SourceA engine)

| Company | URL | What they sell | Overlap | SourceA gap vs them | SourceA edge vs them |
|---------|-----|----------------|---------|---------------------|----------------------|
| **Notenic** | https://notenic.ai/ | State-Transition Authority — GRE between inference and systems of record | **Highest** — pre-execution admissibility | Cloud enterprise sales · launch partner program | Disk law + LOCKED SSOT + self-hosted founder stack |
| **FuseGov** | https://www.fusegov.com/ | 3-layer agent governance — registry, boundary enforcement, evidence packs | High — gateway/sidecar + audit evidence | Patent AU filing · critical-infra positioning | Essay discourse fleet moat · factory receipts culture |
| **** | https://.ai/ | Full agent management — identity, lifecycle, governance, orchestration | High — 20-dim eval before every action | Fleet dashboard · OSS SDK tier | Narrower wedge — compliance latency + re-brief |
| **ThinkNEO** | https://thinkneo.ai/ | Enterprise AI control plane — guardrails, FinOps, gateway | Medium-high — OpenAI-compatible gateway + audit logs | Unified control plane maturity | Pre-LLM packet gate · not just API gateway |
| **AgentPEP** | https://github.com/Shivapas/AgentPEP | Open-source PEP — OPA/Rego, intercept every tool call | High on PEP pattern | SOC2 narrative · 14.8K dec/s benchmarks | Integrated briefing + SSOT fingerprint |
| **Predicate Authority** | https://github.com/PredicateSystems/predicate-authority-sidecar | Rust sidecar — sub-ms ALLOW/DENY, cryptographic proof ledger | High on sidecar speed | Zero-trust execute proxy | Governance critic fixtures + fake-green detection |
| **Microsoft Authorization Fabric** | https://techcommunity.microsoft.com/blog/microsoft-security-blog/authorization-and-governance-for-ai-agents-runtime-authorization-beyond-identity/4509161 | Entra-protected PEP+PDP — ALLOW/DENY/REQUIRE_APPROVAL before tools | High for Copilot/Foundry buyers | Azure-native · Entra lock-in | Multi-lane portfolio · not Azure-only |
| **ThinkFleet Shield** | https://www.thinkfleet.ai/products/shield | Proxy governance — shadow AI, SIEM, evidence | Medium — tone + ops console reference on disk | Product maturity | Anti-staleness latches · maintainer audit |

---

## Tier 2 — Copilot / compliance buyers (Noetfield lane)

| Company | URL | Offer | Price signal | Noetfield counter-position |
|---------|-----|-------|--------------|---------------------------|
| **Securiti** | https://securiti.ai/copilot-readiness-assessment/ | Copilot Readiness Assessment · data-centric AI governance · complements Purview | Enterprise SaaS | **Board-grade signed TLE + re-brief on policy change** — not data labeling alone |
| **** | https://.io/ | AISPM + AIDR — Copilot Studio, Bedrock, Vertex agent discovery | Gartner Cool Vendor TRiSM 2025 | Build-time + runtime agent security — we sell **governance latency** + evidence export |
| **Credo AI** | https://www.credo.ai/ | GAIA agentic oversight — inventory, tool permissioning, traces | Mid-market to six-figure | Policy packs — we sell **mechanical boot BLOCK** before agent acts |
| **IBM watsonx.governance** | https://www.ibm.com/watsonx/governance | ML lifecycle · model cards · enterprise GRC | Six-figure | Faster pilot · CAD $2K deposit · 4–6 week NF-RD |
| **Microsoft Purview** | https://learn.microsoft.com/en-us/purview/ | Native audit · eDiscovery · retention for Copilot | M365 E5 compliance tier | Purview logs metadata not full prompts in audit log — **cryptographic receipt + tamper FAIL** |
| **WitnessAI** | https://witness.ai/ | Network-layer AI traffic capture · shadow AI · intent ML | $58M raise Jan 2026 | Network observe — we enforce **pre-execution on disk state** |
| **Vanta / Drata** | https://www.vanta.com/ | SOC2 evidence automation | ~$10–14K/yr startup | Copilot-specific governance brief — not generic SOC2 |

**Noetfield SKU anchors (disk):** NF-QS $2–3.5K · NF-RD $5–10K · NF-TB $10K USD — see research SKU matrix 2026-06-08.

---

## Tier 3 — Durable orchestration (partners or wrong comparison)

| Company | URL | Funding / signal | vs SourceA |
|---------|-----|------------------|------------|
| **Temporal** | https://temporal.io/ | Series D $300M · $5B val (Feb 2026) | **Partner pattern** — outer durability; SourceA is governance not workflow engine |
| **Inngest** | https://www.inngest.com/ | $21M Series A · AgentKit | Faster TS agent ship — different buyer |
| **LangGraph** | https://www.langchain.com/langgraph | LangSmith ecosystem | Inner agent graph — use alongside, not replace |

**Production pattern 2026:** Temporal (outer) + LangGraph (inner). SourceA should **not** pitch as Temporal competitor — pitch as **policy layer above any orchestrator**.

---

## Tier 4 — Wrong comparisons (do not sell against)

| Label | Examples | Why wrong |
|-------|----------|-----------|
| Consumer AI coworkers | Vybe, ChatGPT Enterprise chat | Wrong tone — enterprise ops only |
| Autonomous SWE | Devin, Cursor alone | Tool not governance platform |
| BI / planning | Anaplan, Tableau | No execution admissibility |
| Issue tracker | Linear as category | Activity slice only |

---

## Competitive matrix — feature level

| Capability | Notenic |  | Securiti | Credo AI | Microsoft | **SourceA** |
|------------|---------|--------|----------|----------|-----------|-------------|
| Pre-execution BLOCK | ✔️ core | partial runtime | partial | partial | ✔️ Auth Fabric | ✔️ critic_boot |
| SSOT re-brief on change | — | — | — | — | — | ✔️ briefing fingerprint |
| Signed receipt / tamper detect | attestation | evidence packs | audit | traces | audit log | ✔️ validators |
| Copilot-specific | — | ✔️ Studio | ✔️ readiness | ✔️ GAIA | ✔️ Purview | ✔️ Noetfield |
| Self-hosted / law-first | — | SaaS | SaaS | SaaS | cloud | ✔️ |
| SIEM export | — | ✔️ | ✔️ | ✔️ | ✔️ | partial |
| Enterprise sales machine | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | **weak** |

---

## Strategic implications

### For SourceA (engine)
- **Do not** compete on orchestration vs Temporal/Inngest.
- **Do** compete on **pre-LLM admissibility** vs Notenic, AgentPEP, Predicate, FuseGov.
- **Middleware pitch:** "Mount your LangGraph/Temporal agents on our boot gate."

### For Noetfield (NW1)
- **Primary rivals in room:** Securiti +  + Microsoft "good enough" Purview story.
- **Win line:** "Purview tells you something happened. Noetfield proves what was **permitted**, under which **policy version**, with **tamper-evident** export for the board."
- **Lose if:** buyer wants full SaaS SIEM + data discovery — send to partner or bundle later.

### For TrustField (backup)
- Comply North / Comply+ / FINTRAC tooling — regulated intake, not Copilot.

### For Mac Guard / agency (parallel)
-  fleet management · ThinkNEO gateway — agency ops, not compliance board.

---

## Evidence URLs (primary)

| Ref | URL |
|-----|-----|
| Notenic architecture | https://notenic.ai/ |
| FuseGov platform | https://www.fusegov.com/ |
|  | https://.ai/ |
| ThinkNEO | https://thinkneo.ai/ |
| AgentPEP | https://github.com/Shivapas/AgentPEP |
| Predicate Authority | https://github.com/PredicateSystems/predicate-authority-sidecar |
| Microsoft Authorization Fabric | https://techcommunity.microsoft.com/blog/microsoft-security-blog/authorization-and-governance-for-ai-agents-runtime-authorization-beyond-identity/4509161 |
|  platform | https://.io/platform |
| WitnessAI | https://witness.ai/ |
| Securiti Copilot Readiness | https://securiti.ai/copilot-readiness-assessment/ |
| Credo AI (Domo comparison) | https://www.domo.com/learn/article/ai-governance-tools |
| Temporal vs LangGraph | https://www.langchain.com/resources/langgraph-vs-temporal |
| Temporal vs Inngest 2026 | https://wetheflywheel.com/en/comparisons/temporal-vs-inngest/ |
| Canada agentic AI guide | https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/guide-use-agentic-artificial-antelligence.html |
| On-disk constellation | `SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md` |

---

## Next 3 moves (convinced)

1. ~~**NW1 battle card**~~ — `NOETFIELD_NW1_BATTLE_CARD_LOCKED_v1.md`
2. ~~**Pitch stats (external critic)**~~ — `archive/attachments/commercial/EXTERNAL_CRITIC_PITCH_STATS_BULLETS_2026-06-15_v1.md`
3. **W1 demo film** — other repo (not SourceA)
4. ~~**Integration story**~~ — `SOURCEA_ORCHESTRATOR_PARTNER_INTEGRATION_LOCKED_v1.md`
5. ~~**30-company market map + consolidation**~~ — intake `SOURCEA_NOETFIELD_COMPETITOR_LANDSCAPE_2026-06-15_v1_3.md` merged v1.2

## Attachments index:** intake v1.3 · strategy pack · one-pager MERGED EXTERNAL · merge checklist · `validate-competitor-landscape-v1_3.sh` · **UI benchmark** `_2026-06-15_v1.md` · HTML `generate_commercial_onepager_html_v1.py`
