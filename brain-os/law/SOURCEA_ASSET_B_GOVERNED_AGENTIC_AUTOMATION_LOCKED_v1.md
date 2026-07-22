# Asset B — Governed Agentic Automation (DFY) — LOCKED v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-15  
**Authority:** ASF — **fastest cash lane** for SourceA pre-revenue  
**Law:** `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md` §2b · §10 · §16  
**Engine:** `scripts/governed_agentic_automation_offer_v1.py` · receipt `~/.sina/governed-agentic-automation-offer-v1.json`  
**Validator:** `scripts/validate-governed-agentic-automation-offer-v1.sh`  
**Demo:** `SOURCEA_AGENCY_PRODUCT_DEMO_SCRIPT_LOCKED_v1.md` (Buyer 1 proof) · `run_sourcea_agency_product_demo_v1.sh`

---

## 1. What Asset B is

**Asset B** is the **agentic orchestration capability itself** — the self-healing multi-agent system SourceA runs daily. Buyers pay for **done-for-you governed agentic automation**, not governance slides without execution.

| Asset | What it is | Speed to cash |
|-------|------------|---------------|
| **Asset A** | Noetfield governance pilots (Copilot · board receipts) | Medium — 1–3 months |
| **Asset B** | DFY governed agentic automation (outreach · ops · research loops) | **Fastest — weeks** |

**Law:** Pre-revenue, **cash now beats scalable-later.** Asset B is the default first-dollar motion unless NW1 closes first (§10 — whichever closes first).

---

## 2. Speed-to-cash ranking (LOCKED)

| Rank | Motion | Price band | Timeline | ROI note |
|------|--------|------------|----------|----------|
| **1** | **DFY governed agentic automation** | Project **$3–10K** · retainer **$2–5K/mo** | **Weeks** | Marginal delivery cost near-zero — reuse orchestration patterns; one retainer covers ~$200/mo run cost |
| **2** | Noetfield governance pilot (NW1) | CAD $2K shadow → annual | 1–3 months | Higher long-term value · **run in parallel** — do not wait for first dollar |
| **3** | **Combined motion** (recommended max ROI) | DFY project/retainer **+** governance instrumentation | Same engagement | One client: cash + live Noetfield deployment + case study |

**Combined motion law:** Build the client's agent loop **and** instrument it with signed receipts / export bundle. On the **same** engagement — separate vocabulary on compliance calls (§9 separation).

**Do not pitch on first touch:** Noetfield Copilot · TrustField MSB · board pack — unless buyer asks compliance after agent loop scope is agreed.

---

## 3. SKUs (client-facing)

Invoice names below — **no internal SKU codes** in outbound email.

| SKU | Client name | Price | Deliverable |
|-----|-------------|-------|-------------|
| **SKU-DFY-001** | **Agent Loop Build** | **$3,000–$10,000** project | One governed agent loop live in client workflow (outreach · ops · or research) · handoff doc · 30-day fix window |
| **SKU-RET-001** | **Agent Loop Retainer** | **$2,000–$5,000/mo** | Ongoing loop ops · weekly receipt export · approval-gated changes · self-healing monitor |
| **SKU-COMBO-001** | **Governed Automation + Receipts** | DFY/retainer **+** governance pack | SKU-DFY or SKU-RET **plus** signed receipt chain · tamper-checked export · replay demo in closeout |
| **SKU-OPS-002** | Ops Health Audit (lead-in) | **$750** | Mac Guard / SourceA spine audit — **feeder** to DFY (not hero SKU) |
| **SKU-OPS-001** | Mac Guard Agency | **$500** + **$299/mo** | White-label weekly proof — parallel Buyer 1 ladder |

**W3 economic signals (Asset B):**

- First **SKU-DFY-001** paid ≥ **$3,000**, **or**
- First **SKU-RET-001** month ≥ **$2,000**, **or**
- First **SKU-OPS-002** audit **$750** (feeder — counts but DFY is primary AB target)

Log: `governed_agentic_automation_offer_v1.py --log-w3 --json`

---

## 4. What you deliver (scopes)

Reuse SourceA factory patterns — **do not rebuild from scratch per client.**

| Loop type | Examples | Proof on closeout |
|-----------|----------|-------------------|
| **Outreach** | Research → draft → approval → send/book | Send receipts · approval gate log |
| **Ops** | Health monitor · cooldown · tier validators · weekly export | `tier0-pass` · weekly HTML/PDF |
| **Research** | Gather → merge → brief → disk write (SAVE path) | Attachment path · receipt JSON |
| **Client agent** | Cursor/Worker-style loop with policy at dispatch | Session gate PASS · `factory_now_line` pattern |

**Fixed run cost (founder):** ~**$200/mo** — orchestration is the **multiplier**: one founder delivers team-scale output at flat cost.

**Margin law:** Bill for outcome + receipts. Never bill hourly for glue wiring.

---

## 5. Combined motion playbook

One engagement · three outcomes:

1. **Cash** — project or retainer invoice paid  
2. **Live deployment** — governance instrumentation in a real workflow (de-risks Noetfield product)  
3. **Case study** — named reference + export bundle screenshot (with permission)

| Phase | Days | Action |
|-------|------|--------|
| **Discover** | 1 | Pick one loop (outreach / ops / research) · approval owner · success metric |
| **Build** | 3–10 | Deploy loop using SourceA patterns · policy at dispatch · disk receipts |
| **Instrument** | 2–5 | Export bundle · tamper check · replay walkthrough |
| **Handoff** | 1 | Runbook · retainer option · weekly proof cadence |

**Bridge line (after demo):**  
> We run this stack on our own factory every day. Your loop gets the same receipts — what ran, what was blocked, what policy applied.

---

## 6. Outreach (Asset B — AB1)

**From:** **hello@sourcea.app** only — `SOURCEA_COMMERCIAL_SENDER_LOCKED_v1.md`  
**Send:** `python3 scripts/send_ab1_single_v1.py --to recipient@company.com --name "First"`

**Subject:** Agent loops with receipts — live in 2–3 weeks

> Hi,
>
> Teams shipping Cursor agents for clients hit the same wall: the loop runs, but nobody can prove what executed, what was blocked, or whether it is safe to run again tomorrow.
>
> SourceA operates a self-healing multi-agent factory every day — outreach, ops, research — with policy before execution and signed receipts on disk. We deliver that as done-for-you work: **Agent Loop Build** ($3–10K) or **Retainer** ($2–5K/mo).
>
> No pitch deck — 15 minutes to screen-share today's factory receipts.
>
> — SourceA · hello@sourcea.app · https://sourcea.app

Templates on disk: `~/.sina/governed-agentic-automation-email-templates-v1.json`  
Refresh: `python3 scripts/governed_agentic_automation_offer_v1.py --pack --json`

---

## 7. Win codes (Asset B)

| Code | Condition | Status |
|------|-----------|--------|
| **AB1** | First SKU-DFY-001 ≥ $3K **or** SKU-RET-001 first month ≥ $2K | ❌ |
| **AB2** | Second paying DFY/retainer client | ❌ |
| **AB3** | Combined-motion case study published (with permission) | ❌ |

**Parallel:** AB1 does not cancel NW1 · SW2 · W3 — **whichever closes first** per portfolio SSOT §10.

---

## 8. Void on Asset B calls

| VOID | REPLACE WITH |
|------|--------------|
| "I'll build you some agents" (generic freelancer) | **Governed** agentic automation with signed receipts |
| Governance slides without running agents | We **run** this daily — here's today's factory receipt |
| Zapier/n8n glue as hero | Outcome + receipt bundle — orchestrator is implementation detail |
| Pitch Noetfield Copilot on first touch | Agent loop scope first · compliance face only if buyer asks |

---

## 9. Machine pointers

| Check | Command |
|-------|---------|
| Offer receipt | `python3 scripts/governed_agentic_automation_offer_v1.py --status --json` |
| Pack templates | `python3 scripts/governed_agentic_automation_offer_v1.py --pack --json` |
| Validator | `bash scripts/validate-governed-agentic-automation-offer-v1.sh` |
| Agency demo | `bash scripts/run_sourcea_agency_product_demo_v1.sh --prep-only` |
| Portfolio SSOT | `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md` §2c |

---

**End LOCKED v1**
