# AI Infrastructure Partnership Proposals — v3 (verified + refined)

**Saved:** 2026-06-10T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**trace_id:** `RESEARCH-ACQUISITOR-20260610-PARTNER-012`  
**version:** v3 · **date:** 2026-06-10  
**refined_by:** Commercial Goal Specialist + Research Acquisitor synthesis  
**parent_judges:** `COMMERCIAL_GOAL-REF-1000PACK-AUDIT-018` · `PREMORTEM-JUDGE-017` · `MARKET-ARCHITECTURE-PAY-019` (pending)  
**execution_authority:** false  
**Disclaimer:** Draft frameworks only — not legal contracts. Verify each program URL before submit. Brain/legal review before send.

---

## Positioning (market + disk — one paragraph)

Fast AI builders (Lovable, Bolt, Replit) optimize **speed without proof**. Regulated and enterprise buyers ask: *What did the AI do, when, and how do we know it was right?* You already emit **machine-verified closeouts** locally (`receipts/sa-*-receipt.json`, `VALIDATOR_PASS` → `TASK_CLOSED` → `BROKER_ACK`, `closeout_gate_v1.py`). That is the **sellable kernel** — not the 1000-pack grid.

**Partner pitch (external):**  
> We are the **controlled audit layer** for multi-agent execution. You supply models, cloud, and credits; we supply **receipt-proof consumption**, Canadian regulated buyer paths (RPAA MSB readiness · M365 Copilot governance), and reference architecture for enterprise AI ops.

**Honest limit:** Credits reduce burn and unlock eval/semantic paths — they **do not replace** first TF/NF invoice, outreach, or sustained AUTO-RUN (Kill #6).

---

## Chain seats (June 2026)

| Seat | You give partners | You get | Confidence |
|------|-------------------|---------|------------|
| **Consumption** | Metered API routing (Haiku/Sonnet/embeddings) | Credits, rate limits | High |
| **Reference / ISV** | Case study + marketplace listing | Co-sell, Azure leads | Med (post-pilot) |
| **Startup hub** | Logo, profile, usage growth | Stacked perks (NVIDIA → AWS) | High (membership); Med ($ amount) |
| **Semantic layer** | Governance doc RAG (Noetfield + SourceA) | Voyage tokens + optional Atlas | High (200M tier) |
| **Volume inference** | CHECK/scout roles | Groq free tier + conditional grant | High (free); Med ($10K) |
| **OSS governance** | AGT adapter / co-blog | Credibility, Azure co-sell path | Med (post-pilot) |

**Invoice surfaces (revenue):** TrustField TF-001 · Noetfield NF-001 — separate from partner credits.

---

## Partner matrix v3 (10 proposals)

| # | Partner | Role in stack | Realistic ask (2026) | Evidence grade | Apply when |
|---|---------|---------------|----------------------|--------------|------------|
| **P05** | Voyage / MongoDB | L8 semantic (`voyage-4-lite`) | API key + **200M org free tokens** (one-time); MongoDB Startups **$5K+ Atlas + extra Voyage** if qualified | **A** — MongoDB docs | **Now** (config) |
| **P03** | NVIDIA Inception | Credit hub (AWS/GCP paths) | Free membership, **no equity**; partner cloud **$25K–$100K AWS** if qualified (not guaranteed) | **A** program · **B** $ tier | **Week 1** |
| **P06** | Groq | CHECK/scout volume inference | Free tier always; **~$10K** startup grant if eligible | **A** free · **C** grant | Free now; form when ready |
| **P02** | OpenAI | Embed fallback + planner smoke | **$2.5K via Ramp** (needs Ramp account); VC/referral tiers later | **A** Ramp path | Week 1–2 if Ramp wanted |
| **P04** | Microsoft | Noetfield Copilot + Azure OpenAI | Founders Hub **Azure credits**; ISV/marketplace **after NF-001 pays** | **A** Hub · **B** ISV | Hub now; ISV defer |
| **P09** | OpenRouter | Brain/eval routing (402 blocker) | **$500–$5K** credit line — **confirm program** | **D** — unverified | After eval path defined |
| **P01** | Anthropic | Primary ACT (CLI + API logged) | **$25K–$100K** with VC/referral; else office hours + limits | **B** | After demo + receipt deck |
| **P07** | Google Cloud | Hub monitor deploy (phase 2) | Up to **$350K** AI path via Inception/Google — qualified | **C** | After local AUTO-RUN proof |
| **P10** | AWS Activate | GPU/staging via Inception | **$25K–$100K** via Inception/AWS stack | **B** | Stack with P03 |
| **P08** | Microsoft AGT | OSS governance reference | Adapter POC, co-blog, Azure co-sell intro | **B** | After Kill #6 + one pilot |

**Evidence grades:** A = primary vendor/docs · B = multiple secondary sources · C = qualified/conditional · D = negotiate/verify before pitch

---

## Verified program facts (web + disk — Jun 2026)

### P05 Voyage (grade A)
- MongoDB docs: **200M free tokens** for `voyage-4-lite` and most models; **org-level one-time allocation**, shared across projects; **does not refresh**.
- Pricing after free tier: ~**$0.02 / 1M tokens** for voyage-4-lite.
- MongoDB for Startups: **$5K+ Atlas** + additional Voyage tokens; review ~3–10 days; bootstrapped eligible.
- **Disk action:** `VOYAGE_API_KEY` (Tier 3) → re-index → `provider_payload()["semantic"] == true`.

### P03 NVIDIA Inception (grade A program / B credits)
- **Free**, no equity, no application fee (NVIDIA FAQ).
- Requires: incorporated, website, ≥1 developer, <10 years, AI-focused.
- Cloud credits via **partners** (e.g. AWS Activate path); **$25K–$100K not automatic** — partner eligibility applies.
- **Do not pitch:** “Guaranteed $350K GCP” — use “qualified path via Inception portal.”

### P02 OpenAI via Ramp (grade A with caveat)
- **$2,500 OpenAI API credits** via Ramp Rewards marketplace — **requires Ramp corporate card account**.
- Some aggregators cite **$5K** Founder Stack variant — verify at claim time.
- Direct **$100K OpenAI** tiers typically **VC referral**, not bootstrap.

### P04 Microsoft (grade A Hub / B ISV)
- Founders Hub: **Azure credits** for Azure OpenAI — not a substitute for direct OpenAI credits.
- ISV / Copilot marketplace: **after NF-001 design partner deposit** — strengthens Copilot governance pack pitch.
- AGT (Apr 2026) = **credibility alignment**, not cash — ties to P08.

### P06 Groq (grade A free / C grant)
- Free tier usable immediately; **$10K startup credits** — eligibility (stage/accelerator) **not guaranteed**.

### P09 OpenRouter (grade D until verified)
- 402 blocker on eval is **real logged**; credit line amounts **unverified** — contact enterprise before relying in financial plan.

---

## Bootstrap apply sequence (gated — v3)

### Phase A — This week (no VC, no architecture change)

| Day | Action | Partner | Proof artifact |
|-----|--------|---------|----------------|
| 1 | Set `VOYAGE_API_KEY` + re-index vectors | P05 | `semantic: true` + retrieval validator PASS |
| 1–2 | Apply NVIDIA Inception (portal) | P03 | Acceptance email + portal access |
| 2 | Groq console free tier + startup form if eligible | P06 | API key live on CHECK role |
| 3–5 | Ramp signup → redeem OpenAI $2.5K (optional) | P02 | Credit visible in OpenAI billing |
| 3–5 | Microsoft Founders Hub apply | P04 | Azure credits activated |
| 5–7 | MongoDB for Startups (parallel to P05) | P05 | Application submitted |

### Phase B — After proof artifacts logged

| Gate | Then apply |
|------|------------|
| Receipt deck + cost/sa + 154 receipts | P01 Anthropic startup |
| Eval path documented | P09 OpenRouter (verify program first) |
| Kill #6 sustained pack + NF-001 or TF-001 invoice | P08 AGT + P04 ISV conversation |
| AUTO-RUN sustained locally | P07 GCP · P10 AWS Activate bundles via Inception |

### Phase C — Defer

- Full cloud worker deploy until first invoice optional
- ISV marketplace listing until paying pilot
- Any exclusivity clause with any vendor (**multi-engine is core**)

---

## Standard application block v3 (buyer-facing — paste into forms)

```text
COMPANY: TrustField Technologies Inc. (Canada)
BRANDS: trustfield.ca (RPAA readiness) · noetfield.com (Copilot governance)
CATEGORY: Controlled multi-agent execution · compliance evidence · audit receipts

PROBLEM WE SOLVE: Enterprises cannot use fast AI builders without answering
"What did the AI do, when, and how do we know it was right?"

PROOF (summary — attach 1-page PDF, not raw repo paths):
  · Machine-verified task closeouts with validator PASS receipts
  · Append-only event governance chain per task
  · Fake-completion gate blocks batch stamp fraud
  · 150+ receipt-backed factory tasks in repository (Jun 2026)

BUYERS: Canadian MSBs / RPAA program operators · M365 Copilot adopters (CISO, compliance)

STACK: Multi-engine — Claude API (ACT), OpenRouter (Brain/eval), Voyage (embeddings)
       No single-vendor exclusivity.

WE OFFER PARTNERS: Reference customer · logged usage growth · regulated vertical GTM
                   · optional co-authored governance brief

WE ASK: [credits / startup tier / ISV conversation — per proposal row]
```

**Attach (1 page):** architecture diagram + **one redacted receipt JSON** + buyer SKU one-liner (TF-001 / NF-001).

---

## Tie to dual P0 + commercial SKUs

| Goal | Partnership helps | Does NOT replace |
|------|-------------------|------------------|
| Factory Kill #6 (sustained drain) | P05/P06/P02 cut $/task | AUTO-RUN proof |
| Semantic memory P1 | P05 Voyage | Embedding code rewrite (done) |
| First invoice TF/NF | P04 ISV strengthens Noetfield; proof story helps TrustField diligence | Outreach · demos · SOW |
| Eval spine unblock | P09 OpenRouter + P02 embed fallback | OpenRouter credits alone |
| Proof-layer narrative | P08 AGT validates audit-trail category | Building FORGE SKU |
| Credits ≠ revenue | All P01–P10 | **CAD 6K TF / CAD 2K–10K NF deposit** |

---

## Success falsifiers (binary — per partner)

| Partner | PASS when |
|---------|-----------|
| P05 | `provider_payload()["semantic"] == true` + `validate-vector-retrieval-v1.sh` PASS |
| P03 | Inception portal access + partner credit offer visible (any amount) |
| P06 | Groq API on CHECK role with documented RPM/cost |
| P02 | OpenAI billing shows Ramp/grant credit |
| P04 | Founders Hub Azure credits active |
| P09 | `eval_1b_gate_ok: true` OR sustained eval without HTTP 402 |
| P01 | Anthropic credit code or confirmed startup tier |
| P07/P10 | Cloud credits issued in console |
| P08 | AGT maintainer call scheduled OR adapter POC merged |

---

## What NOT to promise (keep in every pitch)

- Fortune 500 deployments · SOC2 certified today · fully autonomous L3
- TrustField processes payments or holds funds
- Exclusivity to one model vendor
- “10 FORGE beta users” if emails are placeholders
- Guaranteed dollar amounts for NVIDIA/AWS/GCP/OpenRouter without qualification language

---

## What changed v2 → v3

1. **Web-verified** NVIDIA / Voyage / Ramp program facts with evidence grades  
2. **Voyage clarified:** 200M = org one-time, non-refreshing (MongoDB docs)  
3. **Ramp caveat:** requires Ramp account; verify $2.5K vs $5K at claim  
4. **OpenRouter downgraded** to grade D until program confirmed  
5. **Buyer-facing application block** — less internal path noise  
6. **Linked** to proof-layer product narrative (receipts = enterprise wedge)  
7. **Dual P0** explicit: credits parallel factory + first invoice  
8. **Day-by-day** Phase A apply sequence with proof artifacts  

---

## One-line gold (v3)

**Join the chain as the controlled receipt layer:** apply **Voyage + Inception + Groq free tier** this week; add **Ramp OpenAI + Microsoft Founders Hub** for cash-flow relief; pitch **Anthropic + Microsoft ISV + AGT** only when you can show **receipts, sustained AUTO-RUN, and a paying Copilot or RPAA pilot** — your wedge is **compliance proof**, not another app builder.

---

## Next actions (founder vs executor)

| Who | Action |
|-----|--------|
| **ASF** | Hub START AUTO RUN (factory) · approve which Phase A apps to submit |
| **Executor** | P05 key + re-index · P03/P04/P06 forms · optional Ramp |
| **Brain** | Receipt deck PDF for P01 · ISV path after NF-001 |
| **Commercial Goal** | Parallel TF/NF outreach — credits do not substitute |

**execution_authority:** false
