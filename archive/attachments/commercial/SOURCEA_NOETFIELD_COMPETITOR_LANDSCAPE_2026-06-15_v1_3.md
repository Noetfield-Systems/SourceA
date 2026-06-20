# SourceA / Noetfield — Competitor Landscape & Revenue View

**Saved:** 2026-06-16T04:33:35Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** v1.3 · **Date:** 2026-06-15 · **Status:** External-eye intake (merged into research report v1.2)

> **Reconcile** against `archive/attachments/commercial/SOURCEA_COMPETITOR_LANDSCAPE_RESEARCH_REPORT_v1.md`. Competitor "scale/signal" is **public funding/acquisition status, not audited revenue** — private-company revenue isn't reliably knowable, so don't quote these as facts. Revenue *figures* in §3 are illustrative models of **your** potential, not guarantees.

## How to read this — SourceA's position
SourceA = **pre-LLM governed execution**: per-action policy enforcement *at dispatch* + a **signed, tamper-evident, replayable receipt chain**. Almost everyone below does *one* adjacent thing — gateways enforce content/PII guardrails (not per-action agent authorization with signed receipts), GRC platforms map policy and produce audit evidence via integrations (not in-line runtime enforcement), security tools detect threats and red-team (not provable enforcement receipts), and observability tools *see* actions but don't *enforce* them. Your white space is the **provable-enforcement receipt** as the artifact, shown live in <5 min.

## 1. The 30 (grouped by category)

### A. LLM / AI gateways — policy at dispatch (closest architecturally)
| # | Company | What it does | Where SourceA differs | Scale / signal |
|---|---|---|---|---|
| 1 | **Portkey** | Control-plane gateway: routing, caching, guardrails (PII/content), audit trails | Guardrails on prompt content, not per-action agent authorization w/ signed tamper-evident receipts | Acquired by Palo Alto Networks (2026); OSS Apache-2.0 + managed |
| 2 | **LiteLLM** | OSS self-hosted gateway, 100+ providers, virtual-key budgets | No built-in guardrails or enforcement; routing/cost layer only | Open source, widely adopted |
| 3 | **Kong AI Gateway** | Enterprise gateway, plugin ecosystem, policy enforcement, HIPAA | API-traffic policy, not agent-action receipts/replay | Established infra vendor |
| 4 | **Cloudflare AI Gateway** | Edge gateway across global DCs, caching, DLP, real-time guardrails | Edge content controls; no signed replayable action ledger | Public incumbent |
| 5 | **Vercel AI Gateway** | Unified model access for Vercel-native apps, ZDR routing | Access layer, not governance/enforcement | VC-backed platform |
| 6 | **OpenRouter** | Aggregator, 300+ models, fallback routing | Pure routing/marketplace; no enforcement or audit chain | High-volume aggregator |
| 7 | **Helicone** | Drop-in analytics/observability gateway | Observes spend/latency; no enforcement | OSS + managed startup |

### B. Agent governance / management & GRC
| # | Company | What it does | Where SourceA differs | Scale / signal |
|---|---|---|---|---|
| 8 | **IBM watsonx.governance** | "Enterprise AI assurance layer" — governance + traditional GRC | Lifecycle/MRM governance, audit via integration; not in-line per-action enforcement | Public incumbent |
| 9 | **ServiceNow AI Control Tower** | Discover/govern/observe/secure all agents; runtime observability (Traceloop) | Control-tower oversight, not dispatch-level signed enforcement | Public incumbent (acq. Traceloop) |
| 10 | **OneTrust AI Governance** | Extends privacy/trust platform to AI: intake, inventory, policy, monitoring | GRC + monitoring; enforcement is policy-driven guardrails, not action receipts | Established trust-platform vendor |
| 11 | **Collibra AI Governance** | Data + AI governance catalog/lineage | Catalog/lineage layer, not runtime enforcement | Established data-gov vendor |
| 12 | **Credo AI** | Policy/registry/workflow; translates regs → controls, audit-ready evidence | Enforcement leans on CI/CD/CASB/gateway integrations, not in-line agent guardrails | VC-funded AIGP leader |
| 13 | **Holistic AI** | AI risk mgmt, bias/fairness, lifecycle governance | Risk/compliance layer, not per-action runtime receipts | VC-funded startup |
| 14 | **Modulos** | Dedicated AI governance platform, EU AI Act mapping | Compliance mapping/assurance, not dispatch enforcement | VC-funded startup |
| 15 | **Trustible** | AI governance, policy-to-control mapping | Policy/evidence layer | VC-funded startup |
| 16 | **Deeploy** | Lifecycle governance: control frameworks, approval workflows, monitoring | Governance officer workflows + monitoring, not signed action chain | Niche vendor |
| 17 | **Kore.ai** | Agent management/orchestration platform | Builds & runs agents; governance is a feature, not provable enforcement infra | Established agent-platform vendor |
| 18 | **Clarista** | Enterprise agent orchestration + governance, BYO-LLM, deploy-to-cloud | Orchestration-first; governance bundled, not standalone signed receipts | Positioned enterprise startup |
| 19 | **Palantir AIP** | Gov/defense-grade agent platform with controls | Full platform/lock-in; not a vendor-neutral enforcement layer | Public incumbent |
| 20 | **Atlan** | Context + governance + audit trails for agents | Data-context + governance; not dispatch-level enforcement receipts | VC-funded data startup |

### C. AI security / agentic runtime protection
| # | Company | What it does | Where SourceA differs | Scale / signal |
|---|---|---|---|---|
| 21 | **Lakera (Lakera Guard)** | Prompt firewall: injection/jailbreak detection at model interface | "Governs the prompt, not the agent" — no action enforcement/receipts | Acquired by Check Point |
| 22 | **Protect AI** | ML/AI supply-chain + model security, scanning | Security scanning, not runtime action governance | Acquired/scaled security vendor |
| 23 | **HiddenLayer** | AI/model detection & response, security | Threat detection, not enforcement receipts | VC-funded security startup |
| 24 | **Cisco AI Defense** | AI Firewall + red-teaming (ex-Robust Intelligence) | Runtime input/output protection, not signed action ledger | Public incumbent (acq. Robust Intelligence) |
| 25 | **Straiker** | Agent visibility + MCP scanning + runtime enforcement | Security-framed enforcement/detection; not a signed replayable governance receipt | VC-funded startup |
| 26 | **General Analysis** | Agentic red-teaming + runtime controls + governance evidence + release gates | Testing/red-team-first; enforcement evidence, not the live receipt-chain wedge | VC-funded startup |
| 27 | **WitnessAI** | Network-routed AI traffic governance/enforcement | Network-layer control, not per-action signed receipts | VC-funded startup |
| 28 | **[external-design-benchmark]** | Governance for Copilot Studio / low-code agent sprawl | Targets low-code/copilot surface, not infra-level enforcement | VC-funded startup |

### D. AI observability / replay / evals (adjacent)
| # | Company | What it does | Where SourceA differs | Scale / signal |
|---|---|---|---|---|
| 29 | **AgentOps** | Session replay ("time-travel"), HITL approval gates, audit trails, loop detection | Closest on replay + approval gates — but observes/pauses, doesn't *enforce* policy at dispatch with tamper-evident receipts | VC-funded startup |
| 30 | **Arize (AX / Phoenix)** | Agent evals + OTEL tracing/observability | Sees & scores traces; no enforcement or signed chain | Well-funded observability leader |

*Also adjacent (not tabled): Galileo, Langfuse, Confident AI, Aporia (observability/evals); Noma, Mindgard, Lasso, Patronus, Prompt Security→SentinelOne (AI security).*

## 2. What the map tells you
- **Nobody owns your exact wedge.** Per-action enforcement *at dispatch* + a **cryptographically signed, tamper-evident, replayable receipt** is the one capability spread thin across three categories but unified by none. Gateways stop at content guardrails; GRC stops at evidence-via-integration; security stops at detection; observability stops at seeing.
- **The market is consolidating by acquisition** (Portkey→Palo Alto, Lakera→Check Point, Robust Intelligence→Cisco, Prompt Security→SentinelOne, Traceloop→ServiceNow). That is a strong signal of value **and a realistic exit path** — security/governance incumbents are buying exactly this layer.
- **Your live demo is the differentiator** the table can't show: most of these *describe* governance; few can run BLOCK → ALLOW → tamper-FAIL → signed replay in five minutes.

## 3. Potential revenue (illustrative — your numbers, not promises)

**Bottom-up, design-partner phase (Noetfield):**
- Pilot: CAD $2K deposit → annual conversion. Assume design-partner ACV **CAD $15–30K/yr**.
- 10 design partners Yr 1 → **~CAD $150–300K ARR**. 25–40 by Yr 2 → **~CAD $0.5–1M ARR** (the Series-A repeatability zone).
- Enterprise phase ACV (post SOC 2 / procurement): **CAD $50–150K+** per account — a handful materially changes the ARR curve.

**Services bridge (capability, not product) — fastest cash:**
- Agentic-automation-with-governance engagements at **$3–10K/project or $2–5K/mo retainer**. 2–3 concurrent retainers ≈ **$6–15K/mo** while funding the product motion, at a near-fixed ~$200/mo run cost.
- **Disk SKUs (agency lane):** `SOURCEA_AGENCY_PRODUCT_DEMO_SCRIPT_LOCKED_v1.md` — $750 ops audit · $299/mo agency · Buyer 1 $200–$2K/mo (SSOT §10).
- **Disk SKUs (Asset B DFY):** `SOURCEA_ASSET_B_GOVERNED_AGENTIC_AUTOMATION_LOCKED_v1.md` — $3–10K project · $2–5K/mo retainer · AB1 fastest cash.

**Strategic / exit lens:**
- Given the consolidation pattern, a credible enforcement-receipt layer with live design partners is an acquisition target for the same incumbents buying the rest of this list. The revenue case isn't only ARR — it's **strategic value to a buyer who needs your layer and can't build the trust artifact**.

*Sources: vendor/category guides and analyst coverage gathered June 2026; acquisition/funding statuses are public signals to verify before relying on them. Confirm all pricing/ACV against your own buyer calls.*

**Supersedes:** `SOURCEA_NOETFIELD_COMPETITOR_LANDSCAPE_2026-06-15_v1_1.md` (intake tables unchanged · disk SKU rows added v1.3)
