# Canada ICP — Grant & Angel/VC Evidence Requirements (Q3 2026)

**Saved:** 2026-07-01T10:20:15Z  
**Version:** 1.1 — LOCKED  
**route_id:** `locked_product_spec_doc`  
**sequence_id:** SA-2026-07-01-CANADA-ICP-GRANT-VC-EVIDENCE-DB  
**Class:** Investor planning database — market reality + evidence SSOT for grants, angels, seed VC  
**Authority:** Inform planning and outreach — subordinate to `ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md` · `TRUSTFIELD_VC_TRUST_LEGAL_ANTI_MORTEM_v1.md`

**Companion artifacts (same database — 5 files):**
- Entity matrix: `docs/ENTITY_EVIDENCE_MATRIX_SOURCEA_TRUSTFIELD_NOETFIELD_CANADA_GRANT_ANGEL_V_LOCKED_v1.md`
- IRAP narrative: `docs/IRAP_TECHNICAL_NARRATIVE_ENFORCEMENT_KERNEL_UNCERTAINTY_DRAFT_LOCKED_v1.md`
- Real market analysis: `docs/REAL_MARKET_ANALYSIS_JULY_2026_ENGLISH_INVESTOR_PLANNING_LOCKED_v1.md`
- Trading lane alignment: `docs/TRADING_LANE_TRUSTFIELD_NOETFIELD_BOUNDED_AUTONOMY_MARKET_ALIGNMENT_ANAL_LOCKED_v1.md`

---

## Database index (master — 5 locked docs)

| # | Doc | Purpose | When to use |
|---|-----|---------|-------------|
| 1 | **This file** | Grant/angel/VC evidence requirements + sequencing | Funding lane planning |
| 2 | **Entity matrix** | Per-entity checklist · disk paths · status columns | Weekly ops tick-box |
| 3 | **IRAP narrative** | ITA one-pager + SR&ED uncertainty spine | NRC intake 1-877-994-4727 |
| 4 | **Real market analysis** | July 2026 market reality — traders, VC, enterprise | Strategy · brainstorm |
| 5 | **Trading lane analysis** | TrustField/Noetfield vs bounded-autonomy market | Wedge · outbound routing |
| 6 | **555 upgrade inbox** | Immediate next 5 plans + execution queue | Worker RUN · one plan/turn |

---

## Readiness dashboard (disk-verified 2026-07-01)

| Tier | Score | Status | Blocker |
|------|-------|--------|---------|
| **T0 Legal/entity** | 1/10 | 🔴 Not fundable | CCPC · IP assignment · bank — COUNSEL |
| **T1 Grants (SR&ED/IRAP)** | 4/12 | 🟡 Narrative ready · records thin | Experiment log · timesheets · ITA call |
| **T2 Angel** | 6/23 | 🟡 Tech proof on disk · no W3 | Film W1 · paid pilot · LinkedIn anchor |
| **T3 Seed VC** | 0/8 | 🔴 Do not raise | W1+W3 + MRR path |
| **W1/W2/W3 (ENFORCEMENT)** | W2 ✅ · W1 ⏳ · W3 ⏳ | 🟡 Kernel yes · economic no | Film demo · close TF pilot |

**Disk proof (run before any investor call):**

```bash
bash scripts/validate-demo-enforcement-v1.sh
bash scripts/validate-demo-enforcement-v1.sh --tamper-test
bash scripts/validate-demo-write-path-v1.sh
bash scripts/validate-enforcement-kernel-v1.sh
```

**Commercial signal on disk:** Ocree Capital (TrustField T-P6/TF-001) and Fundmore.ai (Noetfield NF-RD) **approved to send** per `os/commercial/SOURCEA_ECOSYSTEM_FAST_BUSINESS_MODEL_LOCKED_v2.md` — champion + send still pending.

---

## Upgrade changelog (v1.0 → v1.1)

| Change | Reason |
|--------|--------|
| Added 5-doc master index | Single entry point for planning database |
| Added readiness dashboard | Quantified gap vs fundable |
| Linked real market + trading lane docs | Complete database set |
| Disk-verified validator commands | Replace assumed paths with PASS proof |
| Ocree/Fundmore approval status | Sync with business model SSOT |

---

## Executive summary

**Lens:** What a real IRAP advisor, CRA reviewer, angel syndicate, or seed associate will ask for — not what a pitch deck claims.

**Market context (July 2026):** Canadian seed is a **proof-of-efficiency round**. Deal counts are down; diligence is longer; US co-invest participation has fallen. Capital concentrates in companies with **revenue, pilots, or strategic regulatory relevance**. Non-dilutive grants (SR&ED, IRAP) are used deliberately to extend runway before equity.

**Portfolio framing (frozen):**

> One decision control plane (SourceA) · two regulated wedges (TrustField · Noetfield) · one primary SKU (FORGE) · shared enforcement kernel.

**Category sentence (frozen):**

> *We make AI execution impossible to bypass governance.*

**One-line positioning (investor):**

> **Prove every agent action — before the model runs, after it ships.**

---

## 1. Three funding lanes — different evidence, same spine

| Lane | Who decides | What they actually fund | Primary evidence type |
|------|-------------|-------------------------|------------------------|
| **Grants / tax credits** | CRA, NRC IRAP ITA, provincial programs | R&D with **technological uncertainty** | Contemporaneous technical records |
| **Angels** | Networks, syndicates, BC/Ontario tax-credit programs | Team + early de-risking + relationship | Entity clean + pilot signal + founder credibility |
| **Seed VC** | Institutional funds, lead + syndicate | Repeatable traction + defensibility | Revenue/LOI + data room + live technical proof |

**Critical insight:** Grants want **R&D narrative + lab notebooks**. Angels want **founder + first dollar**. VCs want **diligence packets that survive an 11pm associate review** without a phone call.

All three reward the same underlying asset in 2026: **verifiable execution evidence** — not chat memory, not hub screenshots, not projection-as-law.

---

## 2. Grant evidence — CRA and IRAP

### 2A. SR&ED (federal + provincial stack)

**What it is:** Refundable R&D tax credit. For a CCPC, up to **35% federal** on first $4.5M qualifying spend, plus provincial stacks (e.g. **8% OITC** in Ontario up to $240K/year; **10% BC SR&ED** refundable, permanent per Budget 2026).

**Evidence CRA accepts (and audits):**

| Category | Examples | Portfolio analog |
|----------|----------|------------------|
| Uncertainty documentation | Why existing methods fail; literature review | Why chat-as-memory fails; why observability alone doesn't enforce at execution |
| Hypothesis + experiment log | Design of experiments, test protocols, results | Eval-1b runs, tamper-FAIL tests, gate BLOCK/ALLOW |
| Architecture + code | Diagrams, source, commit history | `scripts/commit_intent_v1.py`, validators, receipt schema |
| Time + cost records | Timesheets, payroll, invoices | R&D hours on enforcement kernel vs commercial |
| Progress artifacts | Meeting minutes, dated signed docs | LOCKED governance docs, dated receipts |

**Form T661 must answer:**
1. Scientific/technological **uncertainty**?
2. **Hypotheses** to reduce it?
3. **Systematic investigation**?
4. **Advancement** (failed experiments count)?
5. **Contemporaneous records**?

**What kills SR&ED for AI/agent startups:**
- "Building a product" without naming uncertainty
- Routine API integration / wrapper work claimed as R&D
- Retroactive documentation at claim time
- Commercial activity mixed with R&D without allocation

**Minimum Q3 2026 SR&ED package:** See entity matrix § SR&ED rows.

**Realistic refund band (early software CCPC):** $40K–$600K depending on qualifying payroll.

---

### 2B. NRC IRAP

**Typical award:** $75K–$200K per project; 60–80% of technical labour. **Relationship-driven** — ITA first, not cold portal.

**Hard eligibility:**
- Incorporated for-profit Canadian SME, ≤500 FTE
- Genuine **technological uncertainty** (not routine engineering)
- **Co-funding capacity** (pay salaries first; IRAP reimburses)
- Work **not started before approval**

**ITA assesses:** (1) technical merit (2) business capacity (3) likelihood of results (4) commercialization (5) Canada economic benefit

**What kills IRAP:**
- "AI platform" without unsolved technical problems
- No internal technical team
- Work started pre-approval
- Market research as R&D
- No commercial path

**Full draft narrative:** `docs/IRAP_TECHNICAL_NARRATIVE_ENFORCEMENT_KERNEL_UNCERTAINTY_DRAFT_LOCKED_v1.md`

**Process:** ITA (~2 weeks) → assessment → co-developed proposal → **3–6 months** to decision. Start Q3; cash likely Q4+.

---

### 2C. Provincial / angel-side tax credits

| Program | Founder must have ready |
|---------|-------------------------|
| BC Venture Capital Tax Credit (EBC) | Pre-approved authorization; eTCA; central securities register; bank deposit proof |
| Ontario OITC | Stacks on SR&ED — same T661 evidence |
| BC SR&ED (T666) | Same SR&ED technical package |

---

## 3. Angel evidence — Q3 2026 Canada bar

| Signal | Weight | Evidence artifact |
|--------|--------|-------------------|
| Founder credibility | High | LinkedIn anchor 20–40s; domain depth — human 10–20% for Canada ICP |
| Live technical proof | High | 90s demo: BLOCK → ALLOW → receipt → tamper FAIL |
| First economic signal | Very high | Paid pilot $2–6K CAD, signed SOW, bank deposit |
| Clean entity | Table stakes | CCPC cert, minute book, IP assignment |
| Honest risk disclosure | Medium-high | Written "not MSB-licensed" / "no custody" |
| Cap table clarity | Table stakes | No entity blur on invoices |

**Check sizes (Canada 2026):**

| Stage | Typical check | Yes threshold |
|-------|---------------|---------------|
| Friends & family | $25K–$100K | Founder + vision + entity |
| Angel network | $100K–$300K | Demo + LOI/pilot + clean legal |
| Pre-seed syndicate | $250K–$750K | Above + 2 design partners + use of funds |

**Angel data room (Phase 6 — after W3 signal):** See `investor/TRUSTFIELD_VC_TRUST_LEGAL_ANTI_MORTEM_v1.md` Part 5.

**Fatal anti-patterns:** Entity blur · revenue fiction · metric theater · MSB overclaim · empty IP chain.

---

## 4. Seed VC evidence — Q3 2026 

| Metric | 2026 expectation |
|--------|------------------|
| SaaS MRR | $25K–$50K with ~15% MoM — or equivalent |
| Enterprise AI | 2+ design partners, pilot-to-paid path, workflow lock-in |
| AI infra/governance | Higher bar: audit trail, switching costs — wrappers discounted |
| Deal size | ~$3M average seed |
| Valuation | $4M–$7M post (AI/ML technical team premium) |
| Process | 3–6 months; 20–40 meetings; US syndicate ~27% (down) |

**VC evidence ranked (agentic infra):**

| Rank | Evidence | Portfolio deliverable |
|------|----------|----------------------|
| 1 | Production proof / paid pilot | W3: TrustField discovery SOW $3–7.5K CAD |
| 2 | Technical credibility | W1: 5-min enforcement demo filmed |
| 3 | Lead VC validation | Target Q4 2026 / Q1 2027 |
| 4 | Founder signal | LinkedIn anchor + Canada regulatory fluency |
| 5 | PR + landing | Amplifier only — after #1 and #2 |

**ENFORCEMENT-6MO win condition:**

| # | Deliverable | Proof |
|---|-------------|-------|
| W1 | Live 5-min demo | BLOCK · ALLOW · receipt · tamper FAIL |
| W2 | Minimal kernel | Single commit path · receipt per action |
| W3 | Economic signal | Pilot · LOI · paid design partner |

**Without W1+W3, do not run institutional seed in Q3.**

---

## 5. Canada regulatory wedge (Q3 2026)

| Moment | Why it matters | Evidence to show |
|--------|----------------|------------------|
| CSA Project Tokenization | Issuers need examinable evidence | TrustField: receipt chain, replay, tamper-FAIL |
| Bill C-15 (Royal Assent Mar 26, 2026) | Stablecoin registry ~2027 | Shadow evidence pack for MSB-adjacent ops |
| FINTRAC agentic AML | Dealers examined on evidence chain | Policy at dispatch → signed receipt (15-min demo) |
| CIRO 2026 unified rules | Dealer surveillance + AI governance | Govern-before-execution positioning |

**Grant angle:** *How do you enforce policy on autonomous agent actions in regulated financial workflows when observability only logs after the fact?*

**VC angle:** *Regulated Canadian fintech needs evidence examiners can replay — receipt layer, not another tokenization platform.*

---

## 6. Master evidence tiers

### Tier 0 — Table stakes (all lanes)

- CCPC incorporated · minute book · IP assignment · business bank · intercompany firewall · NUANS clear · entity email domain

### Tier 1 — Grant-ready (SR&ED + IRAP)

- R&D uncertainties · experiment log · architecture + commits · timesheets · financials · business plan · team CVs · ITA one-pager

### Tier 2 — Angel-ready

- Tier 0–1 + LinkedIn anchor + 90s demo + paid pilot/LOI + contract kit + redacted receipt JSON + 3-slide deck + cap table + EBC pre-approval (if BC)

### Tier 3 — Seed VC-ready (Q4 2026 target)

- Tier 2 + $25K+ MRR equivalent · 8–10 slide deck · full data room · reference customer · security one-pager · SR&ED/IRAP in process

**Full per-entity checklist:** entity matrix doc.

---

## 7. Q3 2026 sequencing

```text
July–August 2026
├── Organize SR&ED contemporaneous records (ongoing)
├── NRC IRAP intake — 1-877-994-4727 (entity per counsel)
├── Ship W1 demo + film
├── Close 1 paid TrustField discovery pilot (W3)
└── FORBIDDEN: ecosystem PR, whitepaper-first, holding sprint

September 2026
├── IRAP proposal with ITA (if invited)
├── Angel conversations (2–3 networks)
├── VC Trust Center data room v1
└── SR&ED claim prep for fiscal year end

October–December 2026
├── File SR&ED with T2
├── Extend to 8–10 slide seed deck
├── Seed process only if W1+W3 shipped
└── Milestone tranches tied to W1/W2/W3 KPIs
```

---

## 8. Entity strategy for Canada funding

| Funding | Entity | Rule |
|---------|--------|------|
| Grants (SR&ED/IRAP) | Entity performing R&D | Counsel decides — SourceA spine vs TrustField commercial R&D |
| Angels/VC commercial | One clean front door | TrustField for regulated wedge; holdingco after 2 revenue wedges |
| Investor hero | TrustField commercial face | SourceA = engine relationship in DD appendix only |

**Do not pitch five entities on slide one.**

---

## 9. Say vs show (2026)

| Say (weak) | Show (strong) |
|------------|---------------|
| "AI governance platform" | 90s tamper-FAIL demo |
| "Enterprise interest" | Redacted SOW + bank deposit |
| "Novel architecture" | Validator stdout + receipt JSON |
| "Canada regulatory expertise" | Named CSA/Bill C-15 thread |
| "SR&ED eligible" | Dated experiment log |
| "Strong founder" | LinkedIn anchor + 3 shipped artifacts |

---

## 10. Bottom line by funding type (Q3 2026)

| Funding | Credible in Q3? | Minimum evidence |
|---------|-----------------|------------------|
| SR&ED | Yes — if records exist | CCPC + R&D narrative + contemporaneous logs |
| IRAP | Start Q3; cash Q4+ | ITA + technical uncertainty + team |
| Angels ($100–300K) | Yes — if W1+W3 ship | Demo + pilot + clean entity + founder video |
| Seed VC ($1–3M) | Not yet — Q4/Q1 | W1+W3 + 2nd pilot + path to $25K MRR |

**Single unlock for all three lanes:**

> Paid Canadian fintech pilot with replayable receipt chain — policy at dispatch → signed receipt → tamper-FAIL — on camera in under five minutes.

---

## Related disk SSOT

| Path | Role |
|------|------|
| `docs/REAL_MARKET_ANALYSIS_JULY_2026_ENGLISH_INVESTOR_PLANNING_LOCKED_v1.md` | Full July 2026 market reality analysis (English) |
| `docs/TRADING_LANE_TRUSTFIELD_NOETFIELD_BOUNDED_AUTONOMY_MARKET_ALIGNMENT_ANAL_LOCKED_v1.md` | Trading lane wedge alignment deep dive |
| `brain-os/law/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md` | W1/W2/W3 win condition |
| `investor/TRUSTFIELD_VC_TRUST_LEGAL_ANTI_MORTEM_v1.md` | VC trust center · pre-mortem |
| `investor/AGENTIC_INFRA_FUNDRAISE_PORTFOLIO_STRATEGY_v1.md` | Fundraise sequencing |
| `os/commercial/CANADA_RWA_STRATEGY_DEEP_RESEARCH_UPGRADE_LOCKED_v2.md` | Canada regulatory map |
| `os/commercial/CANADA_PRIORITY_A_SEND_READY_EMAILS_LOCKED_v1.md` | Priority A outreach |
| `investor/ENFORCEMENT_3SLIDE_DECK_v1.md` | Angel first meeting |
| `docs/research-vault/GOLDEN_REPORT_SOURCEA_SITE_POSITIONING_v1.md` | Positioning SSOT |
| `docs/555_PLANS_NEXT_UPGRADES_INVESTOR_PLANNING_INBOX_LOCKED_v1.md` | 555 immediate upgrade queue |
| `data/investor-planning-555-inbox-v1.json` | Machine inbox · queue_head |
| `receipts/investor-planning-proof-bundle-2026-07-01/` | 555-01 proof bundle (DONE) |

---

*Locked for investor planning database v1.1. Bump `Saved:` UTC on material edits.*

**Upgrade v1.1:** 5-doc master index · readiness dashboard · disk-verified validators · Ocree/Fundmore approval sync.
