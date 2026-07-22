# SOURCE-A — Master Blueprint v1 (Zero → Enterprise)

**Built on:** LLM Agent Operating Law SSOT v3 · Cloud Kernel v1.3 · the live Mac L0 Workbench + Chat Unify cycle.
**Grounded in:** the AI founder/startup market as of **June 2026**.
**Purpose:** one executable path from where SourceA is today to an enterprise-grade, fundable, revenue-generating company — driven through `sourcea.app`.

> Governing creed (SSOT v3): *Fundable systems are proven by receipts, not diagrams. Contracts run the system. Nothing becomes an order until it's bound to disk and clears the gate.*

---

## 0. Executive thesis (read once)

SourceA is a **deterministic, receipt-proven AI factory**: a controlled runtime where an LLM only *proposes* a plan, a contract *gates* it, the work executes, a validator *verifies* it, and every run commits an **auditable, replayable receipt** (artifact · evidence · decision).

The wedge, in one line:

> **"Not another AI tool that lies to you — a factory that proves every job with a receipt."**

This is not a slogan; it is the exact thing the June-2026 market is converging on (audit trails, governance-as-code, replayable execution) and the exact thing 88% of incident-hit enterprises lack. SourceA sells this as a **vertical AI agent service** to founders/agencies, **top-down** (done-for-you run → early-access seat → self-serve SaaS), and proves it with receipts instead of decks.

---

## 1. Market basis — why now (June 2026)

Synthesized from current market data; treat as positioning input, re-check quarterly.

- **Vertical AI agents are the main investable surface** (~55% of agentic-AI capital). Generalists lose; "industry-embedded" wins. Play: one vertical, one workflow, ship in ~90 days.
- **Agent execution infrastructure** (runtimes, control layers, observability, recovery) is the fast-rising second category — investors now fund whether agents can be *monitored, governed, secured, recovered*, not just what they can do.
- **Governance is table stakes AND a sales advantage.** EU AI Act (Art. 12: immutable logs, SHA-256 hash-chaining, ≥6-month retention), NIST AI RMF 1.1 (Mar 2026), NIST AI Agent Standards Initiative (Feb 2026), COSO gen-AI guidance. Regulators now require the *reasoning trace*, not just the action log.
- **The pain is acute:** ~88% of enterprises reported AI-agent security incidents in the past year. The market's named failure modes — **"Paper Governance"** (policy in a doc, disconnected from the running system) and **"Retrofitted Evidence"** (compliance reconstructed after the fact) — are *exactly* what SourceA's design prevents.
- **Funding reality:** median round ~$19M (down from ~$25M), fewer-but-bigger checks, ~65% follow-ons, but first financings still win big when mapped to an *urgent bottleneck* (security, orchestration, control). Founder-market fit matters.
- **Wrapper risk is real:** "what if the LLM provider adds your feature?" Defensibility must come from moats, not model access.
- **Pricing that works in 2026:** hybrid = base subscription + per-outcome fee above a threshold.

**Positioning conclusion:** SourceA is simultaneously (a) a **vertical AI agent** (pick ONE vertical to start) and (b) an embodiment of the **execution-infrastructure + governance layer** the market now demands. The receipt is the moat: it is the audit trail, the deliverable, the demo, and the compliance artifact — one object, four buyers.

---

## 2. Honest current state (Reality vs Target — no Paper Governance)

| Layer | Reality today (on disk / live) | Target |
| :-- | :-- | :-- |
| L0 control plane | Mac Workbench (Hub :13020, AG Routing :8782, Mac Law :8781), SCAN→SHIP belt, `~/.sina` receipts — **live** | unchanged |
| Cloud motor | Railway FBE, always-on, contract-gated — **live** | hardened, autoscale |
| Orchestration | Chat Unify (Founder loop, ORD loop + Truth gate, Official Form, API Station, Hub Pro) + n8n cron — **live** | + Prompt Forge + Proof Pack machines |
| State / DB | Supabase tiers — **live** | Neon migration *only after ASF approval* |
| Proof | Green factory receipt (forge drain, approved) + built video ad — **live** | audit-grade hash-chained receipts |
| Storefront | `sourcea.app` live (200/TLS via Worker proxy) | offer + proof on page |
| Observability | JSON receipts + Hub logs | OpenTelemetry (later) |

**Rule:** every claim in a sale, a deck, or an agent reply must be **disk-bound** (SSOT v3 §B). If it isn't on disk, it's draft.

---

## 3. Positioning & ICP

- **ICP (start):** founders & agencies who already sell AI output (content/ads/automation) and are burned by unreliable "agent soup."
- **Wedge vertical (founder decision — recommended default):** **AI ad/content production** — you already have `video-ad-factory` and a green run. One vertical, one workflow, shippable now. (Alternatives only if you have a warmer buyer elsewhere.)
- **Core promise:** verifiable, gated, receipt-proven execution. Every deliverable ships with a replayable proof.
- **Anti-positioning:** we are not a chatbot, not a prompt wrapper, not "trust the AI." We are a *controlled runtime machine*.

---

## 4. Offer ladder & pricing (sell top-down)

| Tier | What it is | Build cost | Pricing (2026 hybrid) | When |
| :-- | :-- | :-- | :-- | :-- |
| **T1 · Done-for-you run** | Client brings a need; you run the factory; deliver output **+ Proof Pack** | ~zero new code | per-run fee or small retainer (e.g. base + per-run) | **now** |
| **T2 · Early-access seat** | Client triggers runs via a thin interface you operate | thin UI | base subscription + per-outcome above threshold | next |
| **T3 · Self-serve SaaS** | Signup, billing, multi-tenant | real build | tiered base + usage; enterprise = +compliance | after T1/T2 prove demand |

Top-down because **T1 needs nothing you don't have**, and its revenue + feedback funds T3. Never build self-serve before T1/T2 prove people pay.

---

## 5. Architecture blueprint (zero → end)

The system is three stacked planes; the **receipt** is the universal unit that crosses all of them.

```
FOUNDER (observer / gate)
  │  direction + approve
  ▼
L0  Mac Workbench  ── control plane (SCAN→SAY→PICK→PROVE→SHIP), receipts to ~/.sina
  │  SHIP triggers (cloud only, after PROVE)
  ▼
L1–L8 Cloud Kernel ── motor: Plan→Control→Execute→Verify→Commit (Execution Contract = brain)
  │  every Run → Task → {Artifact · Evidence · Decision}
  ▼
RECEIPT  ── the product unit: deliverable + audit trail + demo + compliance artifact
```

The orchestration cycle (Chat Unify, SSOT v3 §E):

```
founder language → [Prompt Forge] → Cursor → reply → [ORD + Truth gate] → [Founder loop] → bounded order
                                                                    │ green run
                                                                    ▼
                                                            [Proof Pack machine]  ← NEW (this blueprint)
                                                                    │
                                                            client deliverable / investor demo / audit pack
```

**Receipt schema = the asset.** `artifact` (the output), `evidence` (the reasoning/verification trail), `decision` (approved/rejected + rationale). Make it **append-only + SHA-256 hash-chained + retained ≥6 months** → this single upgrade turns a receipt into a *compliance-grade* artifact (EU AI Act Art. 12), which is a paid enterprise feature later.

---

## 6. Execution roadmap (receipt-gated phases)

Each phase ships only when its **proof receipt** exists. No phase is "done" by self-report.

**Phase 0 — Sell Now (0–2 weeks).** Put the offer + the green receipt + the video-ad sample on `sourcea.app`; one CTA (book a run). Land **1 paying done-for-you client**.
→ *Proof:* a signed T1 client + a delivered Proof Pack receipt on disk.

**Phase 1 — Productize one workflow (2–6 weeks).** Harden the one vertical factory; build the **Proof Pack machine** (below) so every run auto-produces the buyer/audit artifact.
→ *Proof:* 5 consecutive green runs, each with a Proof Pack, delivered to ≥2 clients.

**Phase 2 — Early-access seats (6–12 weeks).** Thin operate-it-for-them interface; hybrid pricing live; 3–5 design partners.
→ *Proof:* 3 paying seats + NRR signal + the truth-gate pass-rate metric.

**Phase 3 — Self-serve + enterprise (3–6 months).** Multi-tenant, RBAC/RLS, audit-grade receipts, compliance mapping → enterprise unlock and/or fundraise.
→ *Proof:* self-serve signups converting + an audit pack a regulated buyer accepts.

---

## 7. The next machine to build: **Proof Pack** (Chat Unify machine #6)

**Why this one:** it monetizes the exact thing the 2026 market rewards, and one object serves four buyers — the **client** (deliverable), the **investor** (demo), the **regulator/enterprise** (audit pack), and **you** (truth-for-yourself). It is the bridge from "green run" to "money."

**Input:** a green run / approved receipt (from `~/.sina/...` — disk-bound).
**Stages (proposed):**
1. **Collect** — pull the run's artifact + evidence + decision + execution trace from disk.
2. **Verify** — re-run it through the ORD truth gate; only PASS proceeds (SSOT v3 §B).
3. **Seal** — hash-chain the receipt (SHA-256), stamp version + timestamp + owner (defeats Paper Governance / Retrofitted Evidence).
4. **Package** — render three views from the same sealed object: client deliverable, one-screen investor demo, compliance/audit pack.
5. **Emit** — write to `~/.sina/chat-unify/proof-packs/` + a shareable export; log a Proof Pack receipt.

**Output:** a sealed, replayable Proof Pack (deliverable + demo + audit pack) and its own receipt.
**Done = disk-checkable:** a sample green run produces a sealed Proof Pack on disk that re-verifies green and renders all three views.

*(The exact build prompt for Cursor follows this document.)*

---

## 8. KPIs (enterprise-grade, funding-relevant)

- **Run success rate** (green / total runs)
- **Truth-gate pass rate** (ORD PASS % on first attempt) — your reliability headline
- **Time-to-receipt** (intake → sealed Proof Pack)
- **Cost per run** (token + infra) and **gross margin per run** (vs price)
- **Activation** (client → first delivered Proof Pack), **retention / NRR**
- **Logos / design partners / paying seats**, then **ARR**

These map 1:1 to what 2026 investors underwrite: a specific buyer, budget, outcome, and *production-grade reliability* you can show.

---

## 9. Risk register & mitigations

| Risk | Mitigation (mostly already in the architecture) |
| :-- | :-- |
| **Wrapper risk** (LLM provider adds your feature) | Moat = receipts + vertical depth + compliance-grade audit + workflow embedding — not model access |
| **Blueprint Explosion** (10→5000) | Blueprint Registry (versions/dependencies/tests/status) — Kernel v1.3 §7 |
| **Concurrent queue race** | CAS / single-writer head guard — *found & fixed this week* |
| **Infra availability** (Mac-tied loop) | Always-on Railway + cloud cron; Mac → observer |
| **Single-founder bandwidth** | The machines do the work; ramp gated by greens (10 before throttle up) |
| **The inevitable 2026 agent incident** | Gates + immutable audit trail are both the defense *and* the product |
| **Paper Governance accusation** | Every control has a location in code + an on-disk artifact + an owner (SSOT v3) |

---

## 10. Future upgrades (enterprise / high-grade)

1. **Audit-grade receipts** — append-only, SHA-256 hash-chained, ≥6-month retention → sell "compliance-ready execution" (EU AI Act / NIST / COSO).
2. **Multi-tenant + RBAC + RLS** — the T3 self-serve foundation.
3. **SOC 2 + NIST AI RMF mapping** — enterprise procurement unlock; each control tied to a receipt.
4. **Replayable Run Viewer** — a UI that replays any run step-by-step from its receipt: simultaneously the sales demo, the debug tool, and the auditor's view.
5. **Blueprint Marketplace** — published, versioned, tested blueprints → network-effect moat.
6. **MCP-native Tool Registry** — align with the converging agent-interop standard.
7. **Per-outcome billing engine** — meter the hybrid pricing automatically off receipts.
8. **SLA tiers + circuit-breaker dashboards** — reliability as a sellable tier.
9. **Regulatory sandbox mode** — supervised test runs against golden datasets with pass/fail before production (matches EU sandbox expectations).

---

## 11. Governing principles (anchors — SSOT v3)

- Direction, not force. Mission, not micro-steps. One bounded action out.
- Disk-bound or it's draft. Truth from receipts, never self-report.
- Contracts run the system; the LLM only proposes plans.
- Green and serving the need beats ideal — log the debt, move on.
- Prefer the next mission closest to a **demoable receipt or a paying outcome**.

> **The receipt is the product, the proof, the moat, and the audit trail — all at once. Build everything to produce a better receipt.**

---

*Master Blueprint v1 · Source-A · keep at `brain-os/roadmap/` · supersede with a versioned v2. Market basis re-validate quarterly.*
