# SourceA Live Upgrade Cycle Plan (sourcea.app / sourcea.ca / sourcea.uk)

Date: 2026-07-21  
Scope: All three SourceA sites + shared landing/interaction surfaces  
Status: Finalized for execution in current cycle

## A) Market + Client Truth (Real Market Pressure)

### 1) Top 3 client problems causing delay or abandonment right now

1. **No proof-first first touch on key landing CTAs**
   - Evidence: multiple tracked paths still had mailto/cal routes in-source before patch; we replaced all three regional contract pages and CTAs that were previously call-first.
   - Claim type: verified in repo edits (now switched to `/start?...` intake routes).

2. **Offer clarity gap between lanes at decision point**
   - Evidence: current lane-to-offer progression is present but inconsistent across pages, causing longer time-to-intent and repeated qualification loops.
   - Claim type: user-provided market/goal constraint plus observed page spread (startup vs operator vs enterprise CTAs).

3. **Trust continuity still not globally forced at escalation edges**
   - Evidence: several files still anchored to proof artifacts only indirectly (e.g., proof/live) rather than explicit handoff requirements.
   - Claim type: hypothesis with 48h instrumentation test planned below.

### 2) Jobs they are paying for but not seeing

- Predictable path from first visit to verifiable proof artifact.
- Lane-specific pricing and next action in less than 30 seconds.
- Procurement-safe enterprise bridge that includes receipt, policy, and replay evidence before proposal.

### 3) Promise vs need gap

- **SourceA promise:** proof, receipts, replay, policy-at-dispatch.  
- **Prospect need:** direct path from intent to proof artifact and then to decision.
- **Gap:** proof is available but not enforced as the first action in every lane surface and CTA surface.

### 4) Evidence support

- `SourceA-landing/green-unified/data/sourcea-landing-cta-v1.json` and `sourcea-site-interact-v1.json` now route escalation to `/start?...` and no longer expose cal-only path.
- `SourceA-landing/green-unified/sourcea-site-interact-v1.js` now defaults to non-overlay routing.
- `sourcea-chatbot` escalation chips now route to intake-first path.

## B) Sales & Revenue Upgrade (Highest Immediate Lift)

### Startup lane (48h proof start)
- **Pricing/funnel adjustment:** primary CTA now maps to `/start?source=...` intake, then gated progression into `/start` flow and package path.
- **Lane decision copy (20–30s):**
  - Hero: `Start with a 48h proof-safe startup build path.`
  - Subhead: `Pick your lane, get audit evidence, then choose build scope.`
- **Lead magnet:** `48-hour Ops Health Audit checklist + intake scorecard` (live form entry fields).
- **Proof artifact:** `Startup Proof Packet` (receipt + audit tag + replay link + decision log ID).
- **Risk-reduction offer:** `If first packet is incomplete, we re-run proof diagnostics at no cost within 48 hours.`
- **Next-step CTA:** `Get 48h proof intake` → `/start?source=startup` then `/sourcea/proof/live` reference.

### Operator lane (evaluate/proof)
- **Pricing/funnel adjustment:** make `Proof Sprint` path the first qualified option; enterprise-style conversion after packet.
- **Lane decision copy (20–30s):**
  - Hero: `No black-box automation. Start with PASS/BLOCK evidence.`
  - Subhead: `Run one proof sprint, review decision log, then scale with confidence.`
- **Lead magnet:** `Operator Proof Sprint scorecard` with pass/fail template.
- **Proof artifact:** `Operator Proof Bundle` (receipt + audit trail + replay + decision log).
- **Risk-reduction offer:** `Replay correction on missing evidence for the first sprint only.`
- **Next-step CTA:** `Open operator proof sprint` → `/sourcea/48h-mvp.html` (or `/start?source=operator`) then proof artifact.

### Enterprise lane (Forge / platform)
- **Pricing/funnel adjustment:** all enterprise probes require procurement packet + proof checkpoint before retainer/quote handoff.
- **Lane decision copy (20–30s):**
  - Hero: `Enterprise AI control and governance begins with policy proof, not promises.`
  - Subhead: `Pilot-safe path: audit intent, proof packet, then scope + pricing.`
- **Lead magnet:** `Enterprise governance intake pack (control objectives + risk matrix).`
- **Proof artifact:** `Enterprise Evidence Packet` (policy version, audit tag, replay, decision log, procurement references).
- **Risk-reduction offer:** `If replay or policy evidence is missing, proposal is paused and escalated with explicit correction plan.`
- **Next-step CTA:** `Open enterprise pilot intake` → `/start?source=enterprise` then `/sourcea/proof/live`.

## C) Product Strategy Upgrade (Delivery + Trust)

### One core feature set upgrade
- Add one mandatory **Proof Packet Handoff Rule** across all three lane starts:
  - Intake issue ticket.
  - Proof packet id returned.
  - Receipt pointer.
  - Audit tag attached.
  - Replay artifact generated.
  - Decision log available for each lane.

### High-friction workflow before/after

- **Before:** landing CTA -> browse -> manual contact -> delayed proof visibility.
- **After:** landing CTA -> proof-bound `/start` intake -> packet seed -> policy-at-dispatch -> proof surface -> CRM/offer handoff using proof token.

### Trust mechanism in each step
- **Receipt:** shown before proposal.
- **Audit tag:** attached at policy execution boundary.
- **Decision log:** available before scope commit.
- **Replay link:** available before paid handoff.

## D) UI/UX Pro Upgrade (High Grade)

### 1) Landing
- **Objective:** force lane selection + proof expectation in first 20–30 seconds.
- **Current issue:** several paths still read like support-first actions.
- **Before-state issue:** escalation CTA implies human-first response.
- **After-state design:** proof-first CTA trio with secondary proof anchors.
- **Success KPI:** `Landing CTR → qualified intent >= 22%` in 7 days.
- **Copy:**
  - Hero: `Build with proof, not promises.`
  - Subhead: `Startup, operator, enterprise: one proof-bound intake path each.`
  - Trust proof: `Receipt + audit tag + replay link are issued before a qualified offer.`
  - CTA: `Get proof-led intake`

### 2) Pricing/funnel
- **Objective:** one clear commercial ladder per lane.
- **Current issue:** package understanding still requires extra navigation.
- **Before-state issue:** offer blocks don't enforce proof completion.
- **After-state design:** lane cards with entry band (`48h proof packet`) + proposal gate.
- **Success KPI:** `funnel-to-demo >= 12%` with conversion ambiguity down from baseline.
- **Copy:**
  - Hero: `Proof-first pricing across startup, operator, enterprise.`
  - Subhead: `Every option starts with a verifiable execution artifact.`
  - Trust proof: `Each package includes a signed proof packet and decision log.`
  - CTA: `Choose lane and start proof`

### 3) Execution/forge entry
- **Objective:** prevent handoff before proof readiness.
- **Current issue:** no enforced proof seed in initial handoff UI on every path.
- **Before-state issue:** inconsistent escalation text and fallback behavior.
- **After-state design:** proof seed prompt, hard failure reason, re-route button.
- **Success KPI:** `time-to-first proof artifact <= 6 minutes.` 
- **Copy:**
  - Hero: `No run, no proof, no gate-through.`
  - Subhead: `Policy check → receipt → replay is the default path.`
  - Trust proof: `You always get a linked decision artifact.`
  - CTA: `Start governed run`

## E) Proof-backed Delivery Plan (7-day sprint)

1. **Proof packet handoff gate across `/start` and /sourcea surfaces**  
   - Owner: Product Lead  
   - Action: enforce proof-first intake handoff for all `intent_id` routes and CTA surfaces  
   - Time: 1 day  
   - Dependencies: existing JSON SSOT wiring + positioning/config checks  
   - Acceptance: >95% of CTA clicks produce `trace_id + proof_state=seeded`  
   - Launch gate: no packetless handoff on tracked proof paths

2. **Update shared landing CTA SSOT to proof-first**  
   - Owner: Product/Commercial  
   - Action: keep `/start` intake as primary escalation across `sourcea-landing-cta-v1`, `sourcea-site-interact-v1`, `sourcea-site-pulse-config-v1`, `sourcea-positioning-v1`  
   - Time: 0.5 day  
   - Dependencies: config publish + cache refresh  
   - Acceptance: 100% configured CTAs point to `/start?...` except explicit proof routes  
   - Launch gate: config fetch pass in sourcea pages

3. **Harden interaction script behavior for non-overlay escalation**  
   - Owner: Frontend  
   - Action: disable cal overlay flow and route `Talk to a human` copies to intake proof path in JS defaults  
   - Time: 0.5 day  
   - Dependencies: script load order in `green-unified` pages  
   - Acceptance: no cal overlay attempts on `/sourcea/*` pages after load  
   - Launch gate: interaction smoke test on 3 pages

4. **Rewrite chatbot and secondary CTA language**  
   - Owner: UX + Product  
   - Action: align `sourcea-chatbot` chip labels and fallback copy to proof-led escalation wording  
   - Time: 0.5 day  
   - Dependencies: no behavior change in chat toolchain  
   - Acceptance: 0 broken CTA labels and no `/sourcea` external escalation links in top chip copy  
   - Launch gate: manual chat flow check

5. **Weekly KPI instrumentation and go/no-go gate**  
   - Owner: Growth Ops  
   - Action: track A→B conversion and proof packet timing from `/start` and pricing pages  
   - Time: 1 day  
  - Dependencies: analytics event sink  
   - Acceptance: event stream has all five KPIs with baseline + daily trend  
   - Launch gate: at least 3 KPIs in pass range before full promotion

## F) Risk & Failure Plan

- **Biggest risk:** proof-first wiring is technically present but low intent-to-proof uptake persists due to copy misunderstanding.
- **Invalidation condition:** within 7 days, if qualified-intent CTR remains below 16% and demo-to-paid is below 5%, freeze all secondary experiments and revert to one-lane copy.
- **Backup for week 2:** single-path hard funnel: all lanes enter through one guarded `/start?source=single-path` route with explicit proof artifact preview before any proposal branch.

## G) KPI Dashboard for next check-in

| KPI | Target (Pass) | Watch | Fail/Stop | Stop rule |
|---|---|---|---|---|
| Landing CTR to qualified intent | `>= 22%` | `16% - 21%` | `< 16%` | Hold promo tests and rewrite top 3 hero labels |
| Funnel-to-demo conversion | `>= 12%` | `8% - 11%` | `< 8%` | Remove extra proof branching and simplify lane path |
| Trial/demo-to-paid conversion | `>= 9%` | `5% - 8%` | `< 5%` | Add direct packet handoff proof in offer email + pricing page |
| Time to first proof artifact | `<= 6 min` | `6 - 10 min` | `> 10 min` | Shorten required intake fields by 30% |
| Weekly revenue in-scope (startup/operator/enterprise) | startup `>= $7,500`, operator `>= $6,000`, enterprise `>= $10,000` | startup `4k-7.5k`, operator `3.5k-6k`, enterprise `6k-10k` | any below watch band for 2 consecutive weeks | pause scaling and run one-path rescue funnel |

## Upgrade-cycle execution output

1. What was upgraded this cycle: `sourcea.app`, `sourcea.ca`, and `sourcea.uk` landing-entry and escalation paths now default to proof-led `/start` intake plus explicit proof packet framing.  
2. Why this is highest priority: conversion friction is currently at the first touch; proof-first routing removes the highest-leak step and aligns directly with Product Value + proof commitments.  
3. What changed in messaging, pricing, UX, and trust: offer CTA copy now routes to `/start` intake, lane choices keep proof at the center, and escalation messaging is no longer calendar-first.  
4. Exact measurable outcome: pass thresholds above in section G must be achieved before widening rollout.  
5. What to run next and why: complete 7-day instrumentation cycle, then run Fallback A/B on lane copy only if 3+ KPIs remain in pass range.
