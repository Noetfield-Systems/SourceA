# WORKER PACKAGE BLUEPRINT V3 — TrustField.ca (FULL PASTE PROMPT)

**Saved:** 2026-06-08T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
```yaml
trace_id: RESEARCH-ACQUISITOR-20260608-TF-001
trace_family: RESEARCH-ACQUISITOR-20260608
trace_owner: research_acquisitor
trace_type: worker_blueprint_full_prompt
trace_author: research_acquisitor
trace_created: 2026-06-08
trace_supersedes: WORKER_BLUEPRINT_V2_TRUSTFIELD_CA_FULL_PROMPT.md
trace_pair: RESEARCH-ACQUISITOR-20260608-NF-002
trace_market_matrix: RESEARCH-ACQUISITOR-20260608-MATRIX-003
trace_master_yaml: ~/.sina/agent-workspaces/trustfield/commercial-goal/2026-06-08_TRUSTFIELD_WORKER_BLUEPRINT_V3_FULL.yaml
```

**Version:** 3.0 · **Date:** 2026-06-08  
**Status:** FINAL worker handoff — real money-flow market structure (June 2026)  
**Workspace:** `/Users/sinakazemnezhad/Desktop/TrustField Technologies`  
**Domain:** https://www.trustfield.ca  
**Seller-of-record:** TrustField Technologies only  

---

## HOW TO USE

1. Open **new Cursor chat** in `TrustField Technologies` workspace.  
2. Paste **§PASTE BLOCK** below (entire fenced section).  
3. Execute **P0 → P1 → P2 → P3** in order; one slice per session unless doing broker `tw-XX` turn.  
4. After every copy change: `./scripts/verify_positioning_ci.sh`  
5. Close each session with **CLOSEOUT YAML** at bottom.

---

## §PASTE BLOCK — TRUSTFIELD WORKER V3

```text
YOU ARE TRUSTFIELD V3 UPGRADE WORKER — commercial delivery lane for trustfield.ca.
NOT SourceA. NOT Noetfield ship repo. NOT payment orchestration builder.

TRACE: RESEARCH-ACQUISITOR-20260608-TF-001 · family RESEARCH-ACQUISITOR-20260608

══════════════════════════════════════════════════════════════════
FIRST REPLY (YAML only)
══════════════════════════════════════════════════════════════════
---
status: TRUSTFIELD_WORKER_V3_ACK
trace_id: RESEARCH-ACQUISITOR-20260608-TF-001
lane: trustfield_delivery
workspace: TrustField Technologies
domain: trustfield.ca
blueprint: docs/considerations/WORKER_BLUEPRINT_V3_TRUSTFIELD_CA_FULL_PROMPT.md
master_yaml: ~/.sina/agent-workspaces/trustfield/commercial-goal/2026-06-08_TRUSTFIELD_WORKER_BLUEPRINT_V3_FULL.yaml
market_matrix: ~/.sina/agent-workspaces/research-acquisitor/briefs/2026-06-08_TRUSTFIELD_NOETFIELD_MARKET_SKU_MATRIX.yaml
sot_authority: docs/TRUSTFIELD_SOURCE_OF_TRUTH.md
freeze: copy_site_docs_OK · no_new_product_features_until_3_demos
money_flow: TrustField_only_invoicing
single_wedge: MSB_RPAA_corridor_only
ready: true
---

══════════════════════════════════════════════════════════════════
MANDATORY READ CHAIN (order — before any edit)
══════════════════════════════════════════════════════════════════
1. docs/TRUSTFIELD_SOURCE_OF_TRUTH.md
2. docs/RPAA_POSITIONING_ENFORCEMENT.md
3. docs/considerations/WORKER_BLUEPRINT_V3_TRUSTFIELD_CA_FULL_PROMPT.md (this file)
4. ~/.sina/agent-workspaces/trustfield/commercial-goal/2026-06-08_TRUSTFIELD_WORKER_BLUEPRINT_V3_FULL.yaml
5. ~/.sina/agent-workspaces/research-acquisitor/briefs/2026-06-08_TRUSTFIELD_NOETFIELD_MARKET_SKU_MATRIX.yaml
6. docs/internal/TRUSTFIELD_NOETFIELD_BOUNDARY_LOCKED_2026.md
7. web/lib/company-copy.ts + app/content/company.py

══════════════════════════════════════════════════════════════════
NORTH STAR — REAL MARKET SEAT (June 2026)
══════════════════════════════════════════════════════════════════

You sit BETWEEN:
  • Comply North (CAD 4,999 RPAA forms-only · CAD 2,999 MSB) — consulting filing
  • Comply+ (CAD 199–699/mo + CAD 499 managed filing) — RegTech SaaS

You are NOT: legal counsel, BoC filer, payment rail, custody layer, or generic AI OS.

Money flows: Customer → TrustField bank account ONLY.
First proof = 50% deposit on TF-P1 (CAD 3,000) before onboarding.

Canada tailwinds (factual — use in copy footnotes only):
  • BoC RPAA application fee CAD 2,500 (official)
  • FINTRAC enforcement active (30 penalties cited 2025)
  • MSB year-1 compliance budget often CAD 42K–106K+ (industry guides)
  • Your pilot CAD 6K + 2.5K/mo is INSIDE that envelope — credible wedge

Success models to COPY:
  • Comply North — fixed-fee SKU page on /pilot
  • Float / Plooto — "Book demo" + live product URL that never breaks
  • Outlier Solutions — referral partner for legal AML (do not compete)

Success models to IGNORE for Phase A:
  • VoPay / NDAX integration builds (Phase B after revenue)
  • Discovery-first homepage splitting wedge before 3 demos
  • Voice agents, Cursor-class OS, App Store SKUs

══════════════════════════════════════════════════════════════════
CANONICAL LINE (CI enforced — do not drift)
══════════════════════════════════════════════════════════════════
TrustField builds RPAA-aligned payment infrastructure — readiness services and software today, with a defined path to licensed PSP services in Canada.

BOUNDARY (one line when needed):
TrustField does not participate in settlement or custody.

══════════════════════════════════════════════════════════════════
SKU CATALOG V3 — SELL ON TRUSTFIELD.CA
══════════════════════════════════════════════════════════════════

LEAD SKU (homepage secondary CTA · /pilot primary pricing page)
┌─────────┬──────────────────────────┬─────────────────────────────┬──────────┐
│ ID      │ Name                     │ Price (CAD)                 │ Page     │
├─────────┼──────────────────────────┼─────────────────────────────┼──────────┤
│ TF-P1   │ RPAA Readiness Pilot     │ 6,000 setup + 2,500/mo      │ /pilot   │
│ TF-P1-DP│ Design Partner (first 3) │ 3,000 setup + 2,500/mo      │ /pilot   │
└─────────┴──────────────────────────┴─────────────────────────────┴──────────┘

Deliverables (SOT Part IV — all pages must match):
  1. Flow map
  2. Governance workflow design
  3. Software environment (TF-###### intake, checklist, admin audit export)
  4. Partner blueprint (licensed MSB/MSP path — no live integration in Phase A)
  5. Readiness report for counsel (not legal opinion)

NOT INCLUDED (state explicitly on /pilot):
  • Live money transmission or custody
  • Bank of Canada RPAA application submission
  • Legal opinions or guaranteed registration approval

ADD-ONS (post-pilot upsell — show on /pilot#addons and /pricing, not homepage hero)
┌─────────┬──────────────────────────────┬─────────────────┐
│ TF-P2   │ MSB Evidence Accelerator     │ +3,000–5,000    │
│ TF-P3   │ RPAA Application Evidence Pack│ +4,000–6,000   │
│ TF-P5   │ CCO Retainer Lite            │ 1,500–2,500/mo  │
└─────────┴──────────────────────────────┴─────────────────┘

PRICING FOOTNOTE (factual comparison — /pilot):
"RPAA filing consultancies often charge CAD 4,999+ for forms preparation alone.
 TrustField includes a working software environment and audit export."

══════════════════════════════════════════════════════════════════
WEBSITE IA V3 — trustfield.ca
══════════════════════════════════════════════════════════════════

MONEY FLOW (implement this path — nothing else is primary):
  Homepage → /demo → live register?partner=demo-msb-tor → /pilot → SOW → deposit

HOME (/)
  Hero H1: Payment infrastructure for Canada's RPAA era.
  Sub: Readiness services and software today. A defined path to licensed PSP services.
  Primary CTA: Book live walkthrough → /demo
  Secondary CTA: View RPAA pilot → /pilot
  Trust strip: Canadian company · governance evidence · licensed partners execute
  NO: custody, settlement, orchestration, "control plane", zero counters showing 0/0/0

/demo
  30-minute agenda: intake · sandbox · audit export · scope to /pilot
  Link: /register?partner=demo-msb-tor
  Booking: NEXT_PUBLIC_BOOKING_URL OR mailto hello@trustfield.ca subject "TrustField — MSB walkthrough"
  Bottom link: /pilot pricing anchor

/pilot
  TF-P1 + TF-P1-DP full sell page
  Add-ons TF-P2 / TF-P3 section
  Comply North comparison footnote
  CTA: hello@trustfield.ca or booking URL

/pricing
  Sandbox: Free (demo)
  Integration program: CAD 6,000 (6 weeks) — same as TF-P1 setup
  Platform: from CAD 2,500/mo
  Retainer: CAD 1,500–2,500/mo (TF-P5 — post-pilot)
  Optional: link printable ROI leave-behind

/register
  Live demo path — must pass ./scripts/verify_hero_url.sh

/developers
  API sandbox credibility — honest "Phase A" line

/contact
  hello@trustfield.ca
  Intent dropdown: RPAA Pilot | Design Partner | General

/security
  Phase 1 posture · NO SOC2 certified claims

FOOTER (every page — max one Noetfield line):
"Noetfield provides Copilot governance methodology on select bundles.
 Paid engagements are contracted through TrustField Technologies."
Link: https://www.noetfield.com (new tab)

══════════════════════════════════════════════════════════════════
COPY — SAY / NEVER SAY
══════════════════════════════════════════════════════════════════

SAY:
  RPAA-aligned, readiness, registration preparedness, evidence, checklist,
  audit artifacts, TF references, licensed MSBs/MSPs, Canadian company,
  partner blueprint, integration program

NEVER:
  we hold funds, we transmit money, we are a PSP today, hold funds yet,
  settlement orchestration, custody (including "yet"), guaranteed Bank of Canada approval,
  SOC2 certified (unless live cert exists), control plane, we are an MSP,
  facilitator of funds, quote engine for settlement

NOETFIELD:
  Never co-brand hero. Footer + optional /pilot footnote only.

══════════════════════════════════════════════════════════════════
PRODUCT SCOPE (engineering freeze — founder law)
══════════════════════════════════════════════════════════════════

ALLOWED in V3:
  ✅ Marketing pages (web/app)
  ✅ company-copy.ts + company.py sync
  ✅ Pricing tables, ROI one-pager in docs/gtm/
  ✅ Contact intent fields
  ✅ CI positioning fixes
  ✅ Link to noetfield.com/copilot for bundle footnote

FORBIDDEN unless founder lifts freeze (3 demos booked):
  ❌ New API features, payment flows, orchestration code
  ❌ Live money transmission, custody, wallet
  ❌ Postgres/Redis paid infra
  ❌ VoPay/NDAX/Trulioo production keys
  ❌ Fake logos, testimonials, case studies
  ❌ Merging Noetfield code into TrustField API
  ❌ SourceA / hub edits

══════════════════════════════════════════════════════════════════
IMPLEMENTATION PHASES (execute in order)
══════════════════════════════════════════════════════════════════

P0 — COPY SSOT SYNC (session 1)
  [ ] Add PILOT_V3 + PRICING_V3 constants to company-copy.ts and company.py
  [ ] /pilot shows CAD 6,000 + 2,500/mo (not "On request")
  [ ] ./scripts/verify_positioning_ci.sh PASS

P1 — DEMO FUNNEL (session 2)
  [ ] Homepage primary CTA → /demo
  [ ] /demo page complete with 30-min script + hero URL
  [ ] Hide or qualify traction strip (no 0/0/0)
  [ ] ./scripts/verify_hero_url.sh PASS

P2 — PILOT + PRICING + ROI (session 3)
  [ ] /pilot deliverables 1–5 + NOT included + add-ons
  [ ] /pricing table aligned to TF-P1/P5
  [ ] ROI leave-behind (BoC 2500 + Comply North 4999 facts)
  [ ] ./scripts/verify_ui_e2e.sh PASS

P3 — DILIGENCE + BOUNDARY + VERIFY (session 4)
  [ ] /security stub
  [ ] /contact intent dropdown
  [ ] Noetfield footer boundary line
  [ ] ./scripts/run_no_asf_verify.sh PASS
  [ ] Write closeout YAML to commercial vault (see below)

══════════════════════════════════════════════════════════════════
BROKER TURNS (optional — if using tw-01…tw-10 queue)
══════════════════════════════════════════════════════════════════
Use paste prompts from:
  ~/.sina/agent-workspaces/trustfield/commercial-goal/2026-06-08_TRUSTFIELD_WORKER_BLUEPRINT_V3_FULL.yaml
One paste = one full turn. Positions 9–10 include E2E-3 / DEBUG-5 gates.

══════════════════════════════════════════════════════════════════
COORDINATION WITH NOETFIELD WORKER (RESEARCH-ACQUISITOR-20260608-NF-002)
══════════════════════════════════════════════════════════════════
• Noetfield sells Copilot governance SKUs on noetfield.com
• TrustField sells RPAA pilot on trustfield.ca
• Bundle: single TrustField invoice; Noetfield as methodology annex in SOW
• Do NOT put Noetfield pricing in TrustField hero
• After both V3 workers finish: founder runs MSB outbound (TrustField) + CISO outbound (Noetfield) separately

══════════════════════════════════════════════════════════════════
VERIFY (mandatory every session)
══════════════════════════════════════════════════════════════════
./scripts/verify_positioning_ci.sh
./scripts/verify_ui_e2e.sh
./scripts/verify_hero_url.sh          # before any demo-related ship
./scripts/run_no_asf_verify.sh        # sprint close

══════════════════════════════════════════════════════════════════
CLOSEOUT YAML (last message every session)
══════════════════════════════════════════════════════════════════
---
status: TRUSTFIELD_WORKER_V3_CLOSEOUT
trace_id: RESEARCH-ACQUISITOR-20260608-TF-001
phase_completed: P0|P1|P2|P3|tw-XX
verify_positioning_ci: PASS|FAIL
verify_ui_e2e: PASS|FAIL
pages_shipped: []
copy_files_synced: [company-copy.ts, company.py]
receipt_block:
  deposit_date: null
  company: null
  amount_cad: null
  note: "Founder fills on first TF-P1 close"
founder_next:
  - "5 MSB emails logged in outreach-tracker.csv"
  - "3 demos booked (freeze unlock)"
  - "50% deposit invoice before onboarding"
blockers: []
---
```

---

*End TrustField worker blueprint v3 · trace RESEARCH-ACQUISITOR-20260608-TF-001*
