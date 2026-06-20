
**Saved:** 2026-06-07T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
[COMMERCIAL_GOAL_AGENT_REF · commercial_goal_specialist · COMMERCIAL_GOAL-REF-2026-06-07-NF-PROMPT-V2-010]

| agent_name | Commercial Goal Specialist |
| agent_id | `commercial_goal_specialist` |
| ref_tag | `COMMERCIAL_GOAL-REF-NF-PROMPT-V2-010` |
| trace_id | `COMMERCIAL_GOAL-REF-2026-06-07-NF-PROMPT-V2-010` |
| registry_id | `rr-20260608-1a2b3c4d` |
| parent_trace_id | `COMMERCIAL_GOAL-REF-2026-06-07-DUAL-ANALYSIS-007` |
| manifest | `COMMERCIAL_GOAL-REF-MANIFEST-009` |

# NOETFIELD WORKER — FINAL BUILD PACKAGE v2 (2026-06-07)

**Author:** Commercial Goal Specialist · **Trace:** `COMMERCIAL_GOAL-REF-NF-PROMPT-V2-010`

**Paste this entire file into a new Cursor chat.**  
**Canonical ship repo:** `/Users/sinakazemnezhad/Desktop/Noetfield-All-Documents/Noetfield`  
**Domain:** https://noetfield.com  
**Sprint ID:** `REVENUE-V2-NOETFIELD-2026-06-07`  
**Authority:** Commercial Goal Specialist intake — you implement product + public site for **first design partner revenue**.

---

## 0. YOUR ROLE

You are the **Noetfield delivery worker**. You upgrade **noetfield.com + Copilot governance product** to close **first design partner at CAD 2,000–10,000**. You do **not** build TrustField payment rails, SourceA hub, or `:8000` mono spine routes.

**North star:** One org pays pilot fee, generates **signed TLE v1**, exports **board PDF**, uses it in a real governance meeting.

---

## 1. MANDATORY READ (in order)

1. `docs/strategy/NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md`
2. `docs/strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md`
3. `docs/copilot/DESIGN_PARTNER_SOW_OUTLINE.md`
4. `docs/CONSIDERATION_ENTITY_MONEY_FLOW_SAFE_REVENUE_v1.md` (or MonoRepo mirror)
5. `os/plan.json`
6. `docs/ops/NOETFIELD_CANONICAL_SHIP_REPO_LOCKED_v1.md`
7. `~/.sina/agent-workspaces/trustfield/commercial-goal/2026-06-07_DUAL_BRAND_MARKET_DEEP_ANALYSIS.yaml`
8. This file

**Note:** Spec-only copies may exist under `SinaaiMonoRepo/SinaaiDataBase/noetfield/` — **ship from `Noetfield-All-Documents/Noetfield` only.**

---

## 2. MARKET TRUTH (June 2026 — use in copy)

| Fact | Implication |
|------|-------------|
| Enterprise AI governance **USD 30K–500K/yr** (Credo, OneTrust, Saidot class) | You win at **CAD 2K–10K pilot wedge**, not platform rebuild |
| Saidot: AI register, library, Azure/Bedrock integrations, custom enterprise pricing | You: **Copilot + M365 + TLE + board PDF** — narrower, faster |
| Microsoft Purview is incumbent | **Integrate metadata, don't replace** |
| Noetfield homepage already shows **$2k–10k** and **$10k/6wk** | Product + price exist — **GTM is bottleneck (4/10)** |

**Your category:** AI Governance & Evidence layer for **Microsoft 365 Copilot adoption** — not generic GRC, not payments.

---

## 3. POSITIONING v2 (LOCKED)

**Primary buyer line:**
> We produce the audit trail your Copilot deployment will be asked for later.

**One-line category:**
> AI Governance & Evidence layer for Copilot adoption — structured assessments today, Trust Ledger system evolving.

**What Noetfield is:**
- Pre-execution governance evaluation (allow/deny/review)
- Trust Ledger Entry (TLE v1) with confidence score
- Evidence Index (metadata-only M365: Purview, Entra, Audit, SharePoint)
- Board-ready PDF + procurement ZIP export

**What Noetfield is NOT:**
- Payment initiation, custody, settlement, FX, money transmission
- TrustField delivery site · VIRLUX · member portal execution
- Generic USD 100K GRC platform pitch

**Public joint line (procurement attachments only):**
> Noetfield defines governance and trust requirements for AI-enabled financial programs. TrustField Technologies delivers RPAA-aligned readiness and partner execution in Canada.

---

## 4. PRODUCT SKU CATALOG v2 (sell these — align site + SOW)

| SKU | Name | Price (CAD) | Where | Proof |
|-----|------|-------------|-------|-------|
| **NF-001** | Copilot Design Partner Pilot | **$2,000–10,000** | Homepage, `/copilot/pilot` | Live on noetfield.com |
| **NF-002** | Six-Week Governance Audit | **$10,000 · 6 weeks** | Homepage "Three offerings" | Live on noetfield.com |
| **NF-003** | Enterprise Copilot Compliance Validation | Contact sales | Homepage | Listed |
| **NF-004** | Trust Ledger platform (evolving SaaS) | Future subscription | `/workspace`, API | Product on disk |

**NF-001 deliverables (SOW):**
- Governance evaluate (allow/deny/review + RID)
- Evidence index (metadata-only M365 connectors)
- Signed TLE v1 + confidence score
- Board pack PDF + procurement ZIP
- Audit export bundle

**Success signal (GTM locked):** Partner uses **board PDF in governance meeting**.

**Money rule:** Customer pays **Noetfield** for NF-001/NF-002. **Never** hold client funds. **Never** invoice as payment facilitator.

**Cross-sell (after TLE approved for fintech):** Refer RPAA program delivery to **trustfield.ca** — TrustField invoices separately.

---

## 5. SITE + PRODUCT BUILD TASKS (Tier A — before customer #2)

Per `NOETFIELD_GTM_60_DAY_LOCKED_v1.md` Tier A:

### P0 — GTM unlock (70% founder time is outreach — you enable it)

**NF-W01 — Pricing consistency audit**
- Ensure homepage, `/copilot/pilot`, `DESIGN_PARTNER_SOW_OUTLINE.md`, and procurement one-pager all say **CAD 2,000–10,000** (same currency, same band).
- NF-002 = **CAD 10,000 · 6 weeks** everywhere.
- Add footnote: "Pilot fees are fixed-scope — not per-seat enterprise GRC pricing."

**NF-W02 — 5-minute demo path (locked script)**
- `/copilot/demo/` — optimize flow for script:
  1. Hook: board-ready decision record
  2. Evaluate intent → RID
  3. Connect M365 evidence (or stub)
  4. Draft TLE → **show confidence score**
  5. Approve chain
  6. Export PDF board pack
- Entry CTAs from homepage → `/copilot/demo/` and `/copilot/pilot/`
- Run: `make verify-gtm` — must PASS

**NF-W03 — Public demo URL confidence**
- `scripts/print-demo-url.sh` + staging/tunnel docs working
- Homepage: "Book design partner" CTA → `/copilot/pilot/` with clear next step (email or form)

**NF-W04 — Procurement one-click**
- Verify `scripts/procurement-pack-e2e.sh` PASS
- `/copilot/procurement/` — one-click ZIP export messaging on homepage hero strip

**NF-W05 — Confidence score visibility**
- Board PDF cover + workspace UI must show **confidence score** prominently (GTM priority #3)
- Sample TLE at `/trust-ledger/sample-report/` linked from homepage

### P1 — Buyer diligence

**NF-W06 — Design partner page upgrade**
- `/copilot/pilot/index.html` — attach SOW outline summary, success signals, 4–6 week timeline, metadata-only data boundary
- Link: `docs/copilot/PROCUREMENT_ONE_PAGER.md`

**NF-W07 — TrustField boundary on site**
- Footer or `/copilot/procurement/` add one line boundary — **no TrustField RPAA/product merge on homepage hero**
- Optional link: "Need Canadian RPAA program delivery?" → `https://www.trustfield.ca/pilot` (referral only)

**NF-W08 — Homepage v2 structure (match positioning v1.2)**
- Hero: buyer line + TLE/Evidence/Board pack bullets (already close — tighten copy)
- Remove any payment/PSP language if present
- "Read-only simulation only" badge stays (accurate — no execution authority)

### P2 — Do NOT start until first customer

- Tier B: Real M365 OAuth (partially done — don't expand scope)
- Tier C: SSO, multi-tenant enterprise — **blocked until 3+ customers**
- New repos, RunReceipt, MergePack, member portal

---

## 6. OUT OF SCOPE

- TrustField codebase edits
- SourceA hub / sa-XXXX
- Payment rails, custody, settlement claims
- Fabricating customer logos or testimonials
- Building Saidot-scale USD 100K platform before first **CAD 2K** close
- More than **3 tasks** in `os/plan.json next_tasks` at once (GTM locked rule)

---

## 7. VERIFY (required at closeout)

```bash
cd "/Users/sinakazemnezhad/Desktop/Noetfield-All-Documents/Noetfield"
make verify-gtm
make tle-smoke
./scripts/copilot-pilot-e2e.sh
./scripts/procurement-pack-e2e.sh
./scripts/verify-ui-e2e.sh
```

Write results to `reports/cursor-reply-latest.txt` per ship rule.

---

## 8. UPDATE os/plan.json

Set `next_tasks` (max 3):
```json
[
  "NF-W02: 5-min demo script + /copilot/demo polish",
  "NF-W06: Design partner page + SOW attach",
  "Founder: 3 Copilot design partner outreach conversations"
]
```

Append to `done`:
```json
"REVENUE-V2-NOETFIELD-2026-06-07: Tier A GTM site+demo+procurement — verify-gtm PASS"
```

---

## 9. 5-MINUTE DEMO SCRIPT (implement in UI copy)

1. **Hook:** "Copilot adoption needs a board-ready decision record, not another chatbot."
2. **Evaluate** → show RID in governance console
3. **Connect** M365 metadata → Evidence Index
4. **Draft TLE** → highlight **confidence score**
5. **Approve** sequential chain (CIO → Legal → Security)
6. **Export PDF** + mention audit JSON for diligence

**URLs:** `/copilot/pilot/` · `/workspace` · `/trust-ledger/sample-report/`

---

## 10. REFERENCE INSPIRATION (copy patterns)

| Company | Product | Price signal | Copy |
|---------|---------|--------------|------|
| **Saidot** | AI governance SaaS | Enterprise custom; 14-day trial | Library + register + export |
| **Credo AI** | Policy packs | USD 30K–150K/yr reported | Don't compete — wedge at CAD 2K–10K |
| **OneTrust** | GRC + AI | USD 100K+ | Board PDF + procurement pack analog |
| **Comply North** | RPAA filing | CAD 4,999 | Fixed fee transparency — you have this on homepage |

---

## 11. SUCCESS CRITERIA (this sprint)

- [ ] Homepage + pilot + SOW = consistent **CAD 2K–10K** / **CAD 10K/6wk**
- [ ] `make verify-gtm` PASS
- [ ] 5-min demo path works without founder improvisation
- [ ] Confidence score visible in demo + PDF
- [ ] Procurement ZIP one-click works
- [ ] No TrustField brand merge on hero
- [ ] Founder can start design partner outreach immediately

---

## 12. PARALLEL WITH TRUSTFIELD (do not block on each other)

| Week | Noetfield | TrustField |
|------|-----------|------------|
| 1–2 | Demo polish + 3 Copilot outreach | Site pricing v2 + /demo CTA |
| 3–4 | Close NF-001 design partner | 3 MSB live demos |
| 5+ | Case study from board PDF | TF-001 RPAA integration cross-sell |

**Fastest combined cash:** NF-001 close (Copilot buyer, price public) **parallel** TrustField MSB track.

---

*End Noetfield Worker Package v2*
