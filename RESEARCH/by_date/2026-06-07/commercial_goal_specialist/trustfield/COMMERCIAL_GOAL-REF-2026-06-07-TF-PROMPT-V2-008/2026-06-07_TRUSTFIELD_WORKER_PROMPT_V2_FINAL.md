
**Saved:** 2026-06-07T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
[COMMERCIAL_GOAL_AGENT_REF · commercial_goal_specialist · COMMERCIAL_GOAL-REF-2026-06-07-TF-PROMPT-V2-008]

| agent_name | Commercial Goal Specialist |
| agent_id | `commercial_goal_specialist` |
| ref_tag | `COMMERCIAL_GOAL-REF-TF-PROMPT-V2-008` |
| trace_id | `COMMERCIAL_GOAL-REF-2026-06-07-TF-PROMPT-V2-008` |
| registry_id | `rr-20260608-2b4d6f8a` |
| parent_trace_id | `COMMERCIAL_GOAL-REF-2026-06-07-BLUEPRINT-V2-001` |
| manifest | `COMMERCIAL_GOAL-REF-MANIFEST-009` |

# TRUSTFIELD WORKER — FINAL BUILD PACKAGE v2 (2026-06-07)

**Author:** Commercial Goal Specialist · **Trace:** `COMMERCIAL_GOAL-REF-TF-PROMPT-V2-008`

**Paste this entire file into a new Cursor chat.**  
**Workspace:** `/Users/sinakazemnezhad/Desktop/TrustField Technologies`  
**Domain:** https://www.trustfield.ca · **API:** https://api.trustfield.ca  
**Sprint ID:** `REVENUE-V2-TRUSTFIELD-2026-06-07`  
**Authority:** Commercial Goal Specialist intake — Execution Core routes; you implement.

---

## 0. YOUR ROLE

You are the **TrustField delivery worker**. You build **trustfield.ca + Phase A product copy/pricing/UX** to close **first paid revenue**. You do **not** build SourceA hub, Noetfield product, or payment rails/custody.

**North star:** First **CAD 6,000 setup invoice** from an MSB/fintech RPAA readiness buyer.

---

## 1. MANDATORY READ (in order — before any edit)

1. `docs/TRUSTFIELD_SOURCE_OF_TRUTH.md` — narrative law
2. `docs/internal/TRUSTFIELD_NOETFIELD_BOUNDARY_LOCKED_2026.md` — brand boundary
3. `docs/gtm/PRICING_ONE_PAGER_INTERNAL.md` — internal pricing architecture
4. `docs/gtm/PHASE1_DEMO_SPRINT.md` — demo close motion
5. `os/plan.json` — delivery state
6. `~/.sina/agent-workspaces/trustfield/commercial-goal/2026-06-07_DUAL_BRAND_MARKET_DEEP_ANALYSIS.yaml` — market comps
7. This file

**Copy SSOT (must stay mirrored):**
- `web/lib/company-copy.ts`
- `app/content/company.py`

---

## 2. MARKET TRUTH (June 2026 — use in copy, do not invent)

| Fact | Source |
|------|--------|
| ~300 PSPs registered with Bank of Canada; 1,500+ pending | BetaKit / BoC |
| RPAA filing help **CAD 4,999** published | Comply North |
| Regulator application fee **CAD 2,500** | Bank of Canada |
| VoPay / Invincible / NDAX = **partners**, not competitors | Internal landscape |
| TrustField has **0 paying customers** today | Honest — site must convert, not hype |

**Your category:** RPAA program readiness **software** — intake, workflow, APIs, audit evidence.  
**Not:** PSP · MSB operator · custody · general AI platform.

---

## 3. POSITIONING v2 (LOCKED — implement on site)

**Canonical line (required everywhere meta/legal):**
> TrustField builds RPAA-aligned payment infrastructure — readiness services and software today, with a defined path to licensed PSP services in Canada.

**Buyer one-liner (homepage/demo):**
> Software for licensed MSBs and program operators — intake, operator workflows, and audit evidence. Licensed partners execute settlement.

**Boundary (single line when needed):**
> TrustField does not participate in settlement or custody.

**Primary ICP:** FINTRAC MSB preparing for RPAA · pre-PSP fintech with product ready but no rails.

**NEVER say:** PSP today · hold funds · "yet" implying future custody · SOC2 · live NDAX/VoPay integration (adapters are demo unless keys configured).

---

## 4. PRODUCT SKU CATALOG v2 (sell these — align site to match)

| SKU | Name | Price (CAD) | Page | Status |
|-----|------|-------------|------|--------|
| **TF-002** | Sandbox | **Free** | `/register`, `/trade`, `/developers` | Live |
| **TF-001** | RPAA Readiness Integration Program | **$6,000 setup + $2,500/mo platform** | `/pilot` | **Publish on site** |
| **TF-003** | Production Program | $5,000–15,000 setup + $1,500–4,000/mo + usage | `/pricing`, SOW only | After partner MOU |
| **TF-004** | AI Governance & RPAA Discovery (2 wk) | $3,500–7,500 fixed | `/contact`, SOW | Optional cross-sell |

**Design partner (first 3 closers):** 50% setup discount for logo + case study (internal only until first close).

**Invoice rule:** Setup **50% on SOW sign, 50% on sandbox → first instruction within 7 days** (from PRICING_ONE_PAGER_INTERNAL).

**Market anchor copy (allowed on /pilot footnote):**
> Compliance filing services often start around CAD 4,999 for documentation alone. TrustField includes a working software environment and audit export.

---

## 5. SITE + PRODUCT BUILD TASKS (execute in order)

### P0 — Revenue blockers (ship first)

**TF-W01 — Hide zero traction stats**
- File: `web/components/sales/traction-strip.tsx`
- Rule: If API returns `applications + programs + pending === 0`, use `HOME_SALES.traction` fallback (TF-######, Web+API, Licensed partners) — never show "0" on homepage.

**TF-W02 — Unify pricing v2**
- Files: `web/lib/company-copy.ts` (`PILOT_OFFER`, `PRICING_COMPARISON`), `web/app/pricing/page.tsx`, `web/app/pilot/page.tsx`, mirror `app/content/company.py` if pilot constants added
- **Publish on /pilot:**
  - Integration program setup: **CAD 6,000**
  - Platform: **CAD 2,500/month** (after integration)
  - Duration: 6 weeks scoped SOW
- **Update /pricing tiers:**
  - Sandbox: Free
  - Integration program: **From CAD 6,000 setup**
  - Platform: **From CAD 2,500/mo**
  - Usage: Per instruction — on request
- **Remove** public "From $500/mo" and "From $2.5K setup" — they undermine TF-001 close.
- Comparison table rows: replace "verify list price" with **CAD 6,000 scoped** and **CAD 2,500/mo**.

**TF-W03 — Copy mirror sync**
- Align `company.py` hero with live `company-copy.ts`:
  - H1: `Infrastructure for licensed money service and market programs`
  - Subhead: onboard + workflow + audit — partners execute
- `POSITIONING_LINE` = SOT canonical exactly.
- Run: `./scripts/verify_positioning_ci.sh` — must PASS.

**TF-W04 — Demo-first funnel**
- `HOME_SALES.primary_cta` → `{ label: "Book live walkthrough", href: "/demo" }`
- Header CTA matches.
- Keep secondary: `/register?partner=demo-msb-tor`
- `/demo` page: primary button mailto `hello@trustfield.ca` subject `TrustField — MSB integration walkthrough`

**TF-W05 — Honest sandbox messaging**
- Replace "Actively integrating with licensed partner programs" with:
  > Sandbox live today. Production partner routing is scoped per integration program.
- Keep **demo** badges on market catalog cards.

### P1 — Diligence + booking

**TF-W06 — Vendor brief**
- Ensure `/pilot/vendor-pack` prints clean 2-page PDF.
- MLRO placeholders clearly marked for founder fill — no fake data.

**TF-W07 — Booking hook**
- If `NEXT_PUBLIC_BOOKING_URL` env set: show "Schedule a call" on `/contact` and `/demo`.
- Else: prominent mailto + Telegram @TrustFieldBot (already on contact).

**TF-W08 — Pilot page = RPAA Readiness Integration Program**
- Title/subtitle reference RPAA + 6-week timeline.
- Deliverables list = SOT Part IV items 1–5.
- Register CTA: `/register?partner=rpaa-pilot`

### P2 — After P0 verify passes

**TF-W09 — /security stub**
- HTTPS, token access, incident contact, Phase 1 SQLite note, Postgres deferred.
- No SOC2 claims. Link from `/compliance`.

---

## 6. OUT OF SCOPE (do not build)

- Postgres/Redis (deferred until revenue — B-001)
- Live VoPay/NDAX/Invincible production keys
- New auth/JWT features
- Noetfield branding on trustfield.ca hero
- Fake logos, testimonials, case studies
- SourceA / FORGE / hub / sa-XXXX
- Editing `~/Desktop/SourceA/**`

**Engineering freeze note:** Copy, pricing, UX, and diligence pages **are allowed** — they unblock demos. No new product features beyond this pack unless 3 demos booked.

---

## 7. VERIFY (required after each task + at closeout)

```bash
cd "/Users/sinakazemnezhad/Desktop/TrustField Technologies"
VERIFY_BASE_URL=https://www.trustfield.ca ./scripts/verify_ui_e2e.sh
./scripts/verify_positioning_ci.sh
./scripts/verify_demo_showcase.sh
./scripts/run_no_asf_verify.sh
```

**Deploy:** Vercel prod after all P0 PASS.

---

## 8. UPDATE os/plan.json

After closeout append to `done`:
```json
"REVENUE-V2-TRUSTFIELD-2026-06-07: TF-W01–W08 site pricing+CTA+demo funnel — verify PASS"
```

Set `next_tasks` to founder GTM only:
```json
["Book 3 live demos via /demo", "MSB outreach batch 1 — PHASE1_OUTREACH", "Close first TF-001 LOI at CAD 6K setup"]
```

---

## 9. CROSS-BRAND HANDOFF (when buyer asks about AI governance)

**Public joint line (attachments/email only — not homepage hero):**
> Noetfield defines governance and trust requirements for AI-enabled financial programs. TrustField Technologies delivers RPAA-aligned readiness and partner execution in Canada.

**Refer Copilot/TLE buyers to:** https://noetfield.com — do not merge sites.

**Sequence:** TrustField pilot revenue first · Noetfield parallel for Copilot wedge · cross-sell TF-001 after NF TLE approved.

---

## 10. SUCCESS CRITERIA (this sprint)

- [ ] `/pilot` shows **CAD 6,000 + CAD 2,500/mo** (not "on request")
- [ ] `/pricing` consistent with `/pilot` (no $500/mo)
- [ ] Homepage never shows 0/0/0 stats
- [ ] Primary CTA → `/demo`
- [ ] `verify_positioning_ci.sh` PASS
- [ ] `run_no_asf_verify.sh` PASS
- [ ] Founder can run demo sprint without pricing embarrassment

---

## 11. REFERENCE INSPIRATION (copy motion, not product)

| Copy from | Apply |
|-----------|-------|
| Comply North CAD 4,999 fixed fee | TF-001 published price |
| VoPay/Plooto book-demo → sandbox | `/demo` funnel |
| Helcim published pricing transparency | Comparison table with real numbers |
| PayTrie 0.6% public fee | Phase B usage tier (not now) |

---

*End TrustField Worker Package v2*
