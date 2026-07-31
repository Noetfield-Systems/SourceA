# ENTERPRISE_BUYER_CAPABILITY_MATRIX_v1

**Purpose.** One row per enterprise buying category, with the claim SourceA/Noetfield is
permitted to make and the overclaim that is forbidden. Nothing here may be written into an
application, brief, one-pager or outreach email at a maturity higher than the label below.

**Method.** Every `PROVEN` label was verified live on 2026-07-31 by fetching the surface or
running the endpoint. Every `NO_EVIDENCE` label means a targeted code search of the SourceA
repo returned no implementation, only incidental mentions.

**Maturity labels.** `PROVEN` (live and externally verifiable) · `WORKING_INTERNAL` (runs, not
externally verifiable) · `PILOT_READY` · `IN_BUILD` · `ROADMAP` · `NO_EVIDENCE`.

> **Hard rule.** `ROADMAP`, `IN_BUILD` and `NO_EVIDENCE` capabilities must never be written as
> currently delivered. In partner applications they are either omitted or explicitly marked as
> roadmap.

---

## 1. Governed execution (primary differentiation)

| Field | Value |
|---|---|
| Buyer problem | Agents take real actions with no enforceable authority boundary |
| Budget owner | Chief AI Officer / VP AI Platform |
| Capability purchased | Policy and authority connected to actual runtime execution |
| Noetfield component | Executive Governor worker, Founder Gates worker, receipt chain |
| Canonical evidence | Governor `/health` 200 · Gates `/health` 200 · `sourcea.app/sourcea/proof/live` 200 · `receipts/` on disk |
| **Maturity** | **PROVEN** |
| Partner relevance | IBM (policy to runtime), Palantir (governed autonomy) |
| Commercial package | Enterprise AI Execution Control Plane |
| Permitted claim | "Policy and authority are enforced at execution time, and every run emits a verifiable receipt." |
| Prohibited overclaim | Any claim of a certified control framework, or of enforcement across third-party agent runtimes not integrated |

## 2. Evaluation before trust (PASS / BLOCK)

| Field | Value |
|---|---|
| Buyer problem | Model and agent behaviour is asserted, not measured |
| Budget owner | Model Risk & Validation / Responsible AI lead |
| Capability purchased | Deterministic pre-execution evaluation with a written verdict |
| Noetfield component | `sourcea-boot` (four checks), `BOOT_REPORT.json` |
| Canonical evidence | `sourcea.app/eval` 200 · published on PyPI · verdict written to disk |
| **Maturity** | **PROVEN** |
| Partner relevance | NVIDIA (evaluation), Microsoft (agent evaluations) |
| Commercial package | AI Safety and Security Assessment |
| Permitted claim | "A single command returns PASS or BLOCK and writes the report to disk, in about five minutes, with no sales call." |
| Prohibited overclaim | Do not present this as a full red-team suite, adversarial benchmark, or model-safety certification |

## 3. Execution containment / sandboxing

| Field | Value |
|---|---|
| Buyer problem | Agent code execution touching production systems |
| Budget owner | CISO / Head of AI Security |
| Capability purchased | Isolated execution with a hard boundary |
| Noetfield component | FBE sandbox executor (Railway), `/v1/executions` |
| Canonical evidence | FBE runner `/health` 200 · clone→execute→verify→commit E2E with push intentionally disabled |
| **Maturity** | **PROVEN** (execution) · push-to-remote deliberately disabled |
| Partner relevance | NVIDIA (secure deployment), Microsoft (governed actions) |
| Commercial package | Governed Agent Production Pilot |
| Permitted claim | "Agent work runs in an isolated executor; promotion beyond the sandbox is a separate gated step." |
| Prohibited overclaim | Do not claim hardened multi-tenant isolation, formal escape resistance, or a security-audited sandbox |

## 4. Halt, kill switch and human escalation

| Field | Value |
|---|---|
| Buyer problem | No way to stop autonomous work once it is running |
| Budget owner | CISO / GRC |
| Capability purchased | Enforced stop and human decision gate |
| Noetfield component | `EMERGENCY_STOP.app`, auto-run-disable flag, Founder Gates (ASK / RED / DEFER) |
| Canonical evidence | `EMERGENCY_STOP.app` present · kill flag currently **ON** (factory frozen) · Gates E2E `e2e_a78fc2bf` ACCEPTED |
| **Maturity** | **PROVEN** |
| Partner relevance | IBM, Palantir (authority boundaries) |
| Commercial package | Enterprise AI Execution Control Plane |
| Permitted claim | "Autonomous execution can be halted by an enforced kill flag, and risk decisions escalate to a human gate before proceeding." |
| Prohibited overclaim | Do not claim sub-second global revocation across external systems |

## 5. Evidence, receipts and audit trail

| Field | Value |
|---|---|
| Buyer problem | Cannot show an auditor what the AI actually did |
| Budget owner | GRC / Compliance |
| Capability purchased | Durable, self-hosted, exportable evidence |
| Noetfield component | Receipt chain, export bundles, procurement pack |
| Canonical evidence | `sourcea.app/sourcea/security` 200 · receipts on disk incl. cost fields · sample bundle published |
| **Maturity** | **PROVEN** |
| Partner relevance | IBM (audit-ready reporting) |
| Commercial package | Continuous Assurance and Managed Operations |
| Permitted claim | "Receipts are self-hosted on the customer's disk and exportable for counsel and audit." |
| Prohibited overclaim | **No SOC 2, ISO 27001, HIPAA or GDPR certification may be claimed.** The security page already states framework maps are educational, not certification. Keep that wording. |

## 6. Cost and run accounting

| Field | Value |
|---|---|
| Buyer problem | Agent spend is invisible until the invoice |
| Budget owner | CIO / business operations owner |
| Capability purchased | Per-run cost attribution |
| Noetfield component | Receipt cost fields, ROI allocation lock |
| Canonical evidence | Cost fields present in `receipts/` JSON |
| **Maturity** | **WORKING_INTERNAL** (not externally verifiable by a buyer today) |
| Partner relevance | Microsoft (cost visibility) |
| Commercial package | Continuous Assurance |
| Permitted claim | "Runs carry cost attribution in the receipt." |
| Prohibited overclaim | Do not claim a customer-facing cost dashboard or budget enforcement until one ships |

## 7. Model routing and selection

| Field | Value |
|---|---|
| Buyer problem | Locked to one model vendor; no controlled substitution |
| Budget owner | VP AI Platform |
| Capability purchased | Multi-model routing under policy |
| Noetfield component | Kernel model matrix, brain-chat model selection with fallback |
| Canonical evidence | Live brain worker reports `provider`, `default_model`, `model_fallback` behaviour |
| **Maturity** | **WORKING_INTERNAL** |
| Partner relevance | Microsoft (multi-model selection), NVIDIA (model hosting) |
| Commercial package | Enterprise AI Execution Control Plane |
| Permitted claim | "Requests route across multiple model providers with fallback." |
| Prohibited overclaim | Do not claim deterministic policy-driven routing with promotion/rollback lineage until proven |

## 8. Model adaptation and training lifecycle

| Field | Value |
|---|---|
| Buyer problem | Production experience never improves the model |
| Budget owner | VP AI Platform / ML Platform |
| Capability purchased | Fine-tuning, adapters, distillation, evaluation sets, promotion lineage |
| Noetfield component | **None found** |
| Canonical evidence | **NONE.** Targeted search found no fine-tuning, LoRA or adapter code. The `distill_*` scripts distil **documents into the chatbot's retrieval corpus**; this is knowledge-base construction, not model distillation. |
| **Maturity** | **NO_EVIDENCE** |
| Partner relevance | NVIDIA (this is the centre of their NeMo pitch) |
| Commercial package | Model and Agent Improvement Factory (**not sellable today**) |
| Permitted claim | Only: "governed model **evaluation** and routing", plus episode/receipt capture as the raw material a future improvement loop would consume. |
| Prohibited overclaim | **Do not claim SFT, LoRA, adapters, distillation, training data curation, or a data flywheel.** Do not cite the `distill_*` scripts as model distillation. This is the single highest-risk claim in the package. |

## 9. AI and agent cybersecurity

| Field | Value |
|---|---|
| Buyer problem | Prompt injection, tool abuse, credential leakage via agents |
| Budget owner | CISO / Head of AI Security |
| Capability purchased | Injection resistance, tool authorization, secret isolation, exfiltration prevention |
| Noetfield component | Partial: fail-closed dispatch, sandbox containment, secrets held as encrypted worker secrets |
| Canonical evidence | Fail-closed dispatch and containment are real (rows 1, 3). **Prompt-injection / jailbreak defence: no implementation found**, only two incidental mentions. |
| **Maturity** | Containment + fail-closed **PROVEN** · injection defence **NO_EVIDENCE** · exfiltration controls, connector authorization, supply-chain provenance **NO_EVIDENCE** |
| Partner relevance | NVIDIA (guardrails), Microsoft (identity/data controls) |
| Commercial package | AI Safety and Security Assessment (scoped to what is proven) |
| Permitted claim | "Execution is contained and fails closed; secrets are isolated from the executing surface." |
| Prohibited overclaim | **Do not claim prompt-injection defence, jailbreak resistance, data-exfiltration prevention, connector/MCP authorization, or supply-chain provenance.** Do not claim generic enterprise cybersecurity, SOC replacement, endpoint protection or offensive security. |

## 10. Observability, drift and forensic replay

| Field | Value |
|---|---|
| Buyer problem | No runtime visibility or post-incident reconstruction |
| Budget owner | CIO / Enterprise Architecture |
| Capability purchased | Traces, lineage, drift detection, forensic replay |
| Noetfield component | Receipts (strong), trace storage (partial) |
| Canonical evidence | Brain worker reports `trace_storage_ready: false`, `trace_storage: "console"`. Receipts are durable; full traces are not. |
| **Maturity** | Receipts **PROVEN** · full traces **IN_BUILD** · drift detection and forensic replay **NO_EVIDENCE** |
| Partner relevance | Microsoft (lifecycle monitoring), IBM (continuous controls monitoring) |
| Commercial package | Continuous Assurance |
| Permitted claim | "Every consequential run produces a durable receipt." |
| Prohibited overclaim | Do not claim full distributed tracing, drift detection, safety-regression monitoring or forensic replay |

## 11. Production deployment (cloud / on-prem / hybrid)

| Field | Value |
|---|---|
| Buyer problem | Must run inside the enterprise boundary |
| Budget owner | CIO / Enterprise Architecture |
| Capability purchased | On-prem and hybrid deployment |
| Noetfield component | Cloudflare Workers + Railway (vendor cloud only) |
| Canonical evidence | All live surfaces are vendor-hosted. **No on-prem or hybrid deployment path found.** Self-hosted **receipts** exist; the self-hosted **platform** does not. |
| **Maturity** | Cloud **PROVEN** · on-prem / hybrid **NO_EVIDENCE** |
| Partner relevance | IBM, Palantir (both expect on-prem) |
| Commercial package | Platform Integration / OEM Partnership |
| Permitted claim | "Receipts are self-hosted on the customer's side; the control plane runs on managed cloud today." |
| Prohibited overclaim | **Do not claim on-premise or hybrid deployment.** Distinguish self-hosted *receipts* from a self-hosted *platform*; conflating them is a material misrepresentation to IBM and Palantir. |

---

## Unresolved claim gaps (blocking)

These must be resolved before the rewritten applications can pass diligence:

1. **Model training lifecycle has no implementation.** This is the core of the NVIDIA pitch. Either build a real adaptation/evaluation loop, or apply to NVIDIA on evaluation, guardrails and governed execution only.
2. **Prompt-injection defence has no implementation** while being the first thing a CISO asks about.
3. **On-prem/hybrid does not exist**, and both IBM and Palantir assume it.
4. **Full traces are not durable** (`trace_storage: console`), so "complete traces and lineage" cannot be claimed.
5. **No third-party certification.** Any SOC 2 / ISO implication must stay out.

## PASS / FAIL recommendation per application

| Application | Recommendation | Reason |
|---|---|---|
| **IBM Partner Plus** | **PASS** | Strongest fit. Policy-to-runtime enforcement, receipts, audit evidence, halt/escalation are all PROVEN. Must not claim on-prem or certification. |
| **Microsoft for Startups** | **PASS** | Governed actions, multi-model routing with fallback, evaluation and cost attribution are defensible at WORKING_INTERNAL or better. Do not claim lifecycle monitoring or full traces. |
| **NVIDIA Inception** | **FAIL as currently framed** | NVIDIA's programme centres on the model lifecycle: data curation, post-training, distillation, continuous optimization. SourceA has **no evidence** for any of it. Reframe strictly to evaluation, guardrails, containment and governed execution around NVIDIA-hosted models, or the application invites a technical conversation that cannot be survived. |

## Homepage containment

The advisor's containment rule is preserved. The public homepage carries only four
evidence-backed pillars (Safety, Cybersecurity scoped to containment, Model **evaluation**,
Governed execution) plus the explicit no-certification note. The full capability story belongs
on the platform-partner page and in partner materials, not the homepage.
