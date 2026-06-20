# Witness AI — 30-Point UI Upgrade Plan (Competitor-Informed)

**Saved:** 2026-06-15T21:32:28Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15  
**Lane:** Commercial design · witnessbc.com + portfolio send surfaces  
**Authority:** `COMPETITOR_SITES_UI_BENCHMARK_2026-06-15_v1.md` · `SOURCEA_COMPETITOR_LANDSCAPE_RESEARCH_REPORT_v1.md`  
**Scope:** UI/UX only — layout, motion, IA, trust chrome, proof surfaces — not business model or pricing strategy  
**Brand law:** **Witness AI** (`witnessbc.com`) ≠ **WitnessAI** (`witness.ai`) — never conflate in UI copy or meta

---

## Executive summary

1. **Top UI peers:** Nomotic (88), Zenity / Notenic (86) — we score ~88 on structure but **Trust = 5/10** vs Credo (10) and Zenity (9); that is the largest honest gap.
2. **Steal pattern mix:** Zenity dual-CTA + stat strip · Nomotic pricing grid + fleet mock · Notenic typography + category headline · Credo regulatory trust row · FuseGov 3-step onboarding strip.
3. **Our edge to preserve:** Proof chain terminal, lifecycle stepper, crosswalk table, control-plane hero — already A-grade; upgrade around them, do not replace.
4. **IA next:** Multi-page split (platform · proof · pricing · sources) — matches Nomotic/Notenic scannable depth without 700-line scroll fatigue.
5. **Target:** Lift Trust 5→8, CTA 9→9 (maintain), overall **88→92** on witnessbc.com deploy bundle.

---

## Competitor UI scorecard (top 8)

| Rank | Site | Overall | Hero | Visual | Trust | CTA | Pricing | IA | Proof | Steal for Witness AI |
|------|------|---------|------|--------|-------|-----|---------|----|----|----------------------|
| 1 | **Nomotic** | 88 | 9 | 9 | 8 | 8 | **9** | 9 | 9 | 4-tier grid · “Most Popular” · fleet dashboard density |
| 2 | **Zenity** | 86 | 9 | 9 | 9 | **9** | 7 | 8 | 8 | Dual CTA · stat-led urgency · tri-column platform |
| 2 | **Notenic** | 86 | **9** | **10** | 8 | 8 | 7 | 9 | 9 | Category-defining headline · long-scroll enterprise type |
| 4 | **WitnessAI** | 81 | 8 | 9 | 9 | 9 | 6 | 8 | 7 | Observe / Protect / Control pillar IA — **layout only, not brand** |
| 4 | **Credo AI** | 81 | 8 | 9 | **10** | 8 | 6 | 7 | 7 | Framework badge row · Fortune/analyst trust strip |
| 7 | **FuseGov** | 79 | 8 | 8 | 7 | 8 | 8 | 8 | 7 | Register → govern → protect 3-step visual |
| — | **Witness AI site** *(ours)* | ~88 | 9 | 9 | **5** | 9 | 9 | 9 | 9 | Proof terminal · crosswalk · control plane — **keep** |
| 9 | **Noetfield live** | 74 | 7 | 7 | 7 | 7 | 9 | 5 | 8 | Regulatory map · deposit visible — compress hero |

**Scoring method:** Same 8 dimensions as benchmark doc · 1–10 each · overall = average × 10.

---

## Current Witness AI UI gaps (honest)

| Dimension | Score | Gap vs leader | Fix theme |
|-----------|-------|---------------|-----------|
| Trust | 5 | −5 vs Credo | No logo strip · no analyst badge row · no customer proof numbers |
| Hero copy | 9 | −0 vs Notenic | Strong — tighten category line to one trademark-style phrase |
| Visual | 9 | −1 vs Notenic | Motion added v3.1 — needs subtle scroll-linked parallax restraint |
| Pricing UX | 9 | Tied Nomotic | Add deposit/refund micro-copy on Flow tier (borrow Noetfield HTML) |
| IA | 9 | Tied Nomotic | Sub-pages started — finish assemble + nav active states |
| Proof | 9 | Tied Nomotic | Add 15s autoplay “film strip” mode for demo-first visitors |
| CTA | 9 | Tied Zenity | Sticky CTA exists — add secondary “Assess governance” persistence on mobile |
| Buyer fit | 9 | Strong | Add CISO/GRC buyer line chip row under hero institutional line |

---

## 30-point UI upgrade plan

Each item: **# · Title · Inspo · Action · Surface · Priority · Effort**

### Hero & above-fold (1–5)

**1. Category-defining headline line**  
- **Inspo:** Notenic — “State-Transition Authority™”  
- **Action:** Add one locked subhead under H1: *Runtime governance infrastructure* or *AI policy at dispatch* as the repeatable category phrase; never “WitnessAI” styling.  
- **Surface:** `witnessbc-site/` home hero  
- **P0 · S**

**2. Dual primary CTA row**  
- **Inspo:** Zenity — Assess risk + Get demo  
- **Action:** Hero keeps “Assess agent governance” (ghost) + “Book proof demo” (primary); equal visual weight, 48px min touch targets.  
- **Surface:** Home hero · sticky CTA  
- **P0 · S**

**3. Stat strip with citation anchors**  
- **Inspo:** Zenity stat band · Nomotic metrics  
- **Action:** Keep 3 stats max; add superscript cite links to `#ref-N` or `sources.html#ref-N`; animate count-up on first viewport entry (respect `prefers-reduced-motion`).  
- **Surface:** Home hero stats-strip  
- **P0 · M**

**4. Buyer persona chip row**  
- **Inspo:** Credo AI enterprise buyer lines  
- **Action:** Row under institutional line: `CISO · GRC · Platform eng · AI policy ops · Internal audit` — pill chips, no logos.  
- **Surface:** Home hero  
- **P1 · S**

**5. Hero split balance on mobile**  
- **Inspo:** Notenic mobile stack  
- **Action:** Control-plane panel collapses to compact card below copy; proof CTA visible without scroll on 390px viewport.  
- **Surface:** `styles.css` hero-grid breakpoints  
- **P1 · M**

### Trust & credibility (6–10)

**6. Regulatory framework trust strip**  
- **Inspo:** Credo AI badge row  
- **Action:** Horizontal scrollable badge row: NIST AI RMF · ISO 42001 · EU AI Act · OWASP LLM · MITRE ATLAS — subtitle “Alignment maps only · not certification”.  
- **Surface:** Home `#trust` + `sources.html`  
- **P0 · M**

**7. Analyst citation callout card**  
- **Inspo:** Zenity · Credo — Gartner / Forrester blocks  
- **Action:** Keep Gartner quote block; add small “Primary source ↗” badge styling consistent with evidence cards.  
- **Surface:** Trust section  
- **P1 · S**

**8. Shadow-mode + metadata-only trust pills**  
- **Inspo:** Noetfield HTML · FuseGov evidence posture  
- **Action:** Three trust pills above fold or in trust grid: `Shadow mode · Metadata-only export · Fail-closed BLOCK` — icon + one line each.  
- **Surface:** Trust section · pricing footnotes  
- **P0 · S**

**9. Logo / cohort strip (text-only until customers)**  
- **Inspo:** Credo Fortune row · Nomotic “teams like”  
- **Action:** Text strip: “Built for teams governing agent workflows” + role labels (no fake logos). Replace with customer logos only when approved.  
- **Surface:** Trust section  
- **P1 · S**

**10. Crosswalk table print + expand UX**  
- **Inspo:** Credo regulatory tables  
- **Action:** Default collapsed; on `sources.html` show expanded; zebra rows · sticky header on desktop; `@media print` single-column.  
- **Surface:** Trust · sources page  
- **P1 · M**

### Visual system & motion (11–15)

**11. Typography scale audit**  
- **Inspo:** Notenic long-scroll rhythm  
- **Action:** Lock type scale: H1 2.5–3rem · section H2 1.75rem · lead 1.125rem · mono for receipt codes only.  
- **Surface:** `tokens.css`  
- **P1 · M**

**12. Motion budget law**  
- **Inspo:** Zenity subtle · Notenic minimal  
- **Action:** Document in `motion.css`: one hero entrance · one hover per card type · no infinite loops except control-plane glow; honor `prefers-reduced-motion: reduce`.  
- **Surface:** `motion.css` + README  
- **P1 · S**

**13. SVG icon system completion**  
- **Inspo:** Nomotic consistent icon grid  
- **Action:** Replace any remaining emoji/unicode in nav/UI with `icons.svg` sprite references; 24px grid, 1.75 stroke.  
- **Surface:** All pages  
- **P2 · M**

**14. Dark theme contrast pass**  
- **Inspo:** Nomotic dark fleet panel  
- **Action:** WCAG AA on proof terminal · matrix cells · crosswalk links in dark mode; fix any `#94a3b8` on `#060a0f` failures.  
- **Surface:** `tokens.css` dark vars  
- **P0 · M**

**15. OG / social preview card refresh**  
- **Inspo:** Zenity share cards  
- **Action:** Update `og-card.svg` with category line + witnessbc.com; validate Twitter/LinkedIn crop at 1200×630.  
- **Surface:** `assets/og-card.svg` · head partial  
- **P2 · S**

### Information architecture (16–20)

**16. Finish multi-page assemble pipeline**  
- **Inspo:** Nomotic · Notenic multi-route nav  
- **Action:** Complete `assemble_pages.py` + `content/*.html` → 9 pages; nav `.is-active` on current route.  
- **Surface:** `witnessbc-site/`  
- **P0 · L**

**17. Home page compression (≤10 sections)**  
- **Inspo:** Zenity home vs deep product pages  
- **Action:** Home = hero · trust · why · explore hub grid linking to sub-pages; move platform/proof/pricing to dedicated routes.  
- **Surface:** `content/index.html`  
- **P0 · M**

**18. Explore hub card grid**  
- **Inspo:** Nomotic pillar cards  
- **Action:** 2×3 grid: Platform · Loop · Proof · Compare · Policy · Pricing — each card: icon · one line · “Explore →”.  
- **Surface:** Home  
- **P1 · M**

**19. Breadcrumb + page-hero on sub-pages**  
- **Inspo:** Notenic section heroes  
- **Action:** `.page-hero` block on every sub-page: eyebrow · H1 · lead · optional secondary CTA.  
- **Surface:** All sub-pages  
- **P1 · M**

**20. Footer IA cleanup**  
- **Inspo:** Zenity footer columns  
- **Action:** Footer links → `.html` routes; full ref list only on `sources.html`; home footer links “References → sources.html”.  
- **Surface:** `partials/footer.html`  
- **P0 · S**

### Proof & product demo UI (21–25)

**21. Proof chain “film strip” autoplay**  
- **Inspo:** Noetfield HTML proof beats  
- **Action:** Optional 15s autoplay cycling request→…→tamper-FAIL with pause control; default off if reduced-motion.  
- **Surface:** `proof.html` · `proof-demo.js`  
- **P1 · M**

**22. Scenario pills visual upgrade**  
- **Inspo:** Nomotic eval dimensions  
- **Action:** Pills as segmented control with active underline; sync terminal + inline chain highlight (existing) + aria-live region for verdict.  
- **Surface:** Proof section  
- **P1 · S**

**23. Control plane hero density toggle**  
- **Inspo:** Nomotic fleet dashboard  
- **Action:** “Compact / Detailed” toggle on hero panel; detailed shows receipt codes per agent row.  
- **Surface:** Home hero · `control-plane.js`  
- **P2 · M**

**24. Lifecycle stepper mobile scroll-snap**  
- **Inspo:** FuseGov step flow  
- **Action:** Horizontal scroll-snap on mobile for 6 loop steps; active step detail sticky below.  
- **Surface:** `lifecycle.html`  
- **P1 · M**

**25. Compare matrix responsive mode**  
- **Inspo:** Nomotic comparison table  
- **Action:** Below 768px: card stack per row with checkmarks; keep Witness AI row highlighted.  
- **Surface:** `compare.html`  
- **P1 · M**

### CTA, pricing UI & conversion chrome (26–28)

**26. Pricing tier “Most Popular” badge polish**  
- **Inspo:** Nomotic featured tier  
- **Action:** Flow card: elevated shadow · teal border · badge animation once on scroll-into-view; deposit/refund one-liner under CTA (Noetfield pattern, educational).  
- **Surface:** `pricing.html`  
- **P1 · S**

**27. Sticky mobile CTA bar**  
- **Inspo:** Zenity persistent demo  
- **Action:** After 400px scroll on mobile: bottom bar “Book proof · Assess” — dismissible per session.  
- **Surface:** `site.js`  
- **P1 · M**

**28. FAQ accordion + demo anchor block**  
- **Inspo:** FuseGov FAQ · Zenity bottom CTA  
- **Action:** `#demo` banner with contrasting background; FAQ items use consistent chevron + focus ring; print hides accordion chrome.  
- **Surface:** `faq.html`  
- **P1 · S**

### Deploy, perf & send surfaces (29–30)

**29. Single-file bundle parity check**  
- **Inspo:** Noetfield HTML send attach  
- **Action:** `build.py` bundles `index.html` with inlined CSS/JS; add optional `--page proof` bundle for email attach; validate brand gate on bundle.  
- **Surface:** `scripts/build.py` · `dist/`  
- **P1 · M**

**30. Validate.sh UI regression gate extensions**  
- **Inspo:** Internal factory pattern  
- **Action:** Assert: all 9 HTML files exist · trust strip present · dual CTA · sub-page page-hero · proof only on proof.html · ≤10 sections on index.  
- **Surface:** `scripts/validate.sh`  
- **P0 · M**

---

## Phased rollout

### 90 days (P0 — ship deploy-ready witnessbc.com)

| Week | Items | Outcome |
|------|-------|---------|
| 1–2 | #16 #17 #20 #30 | Multi-page site live · validate PASS |
| 3–4 | #1 #2 #3 #6 #8 #14 | Trust strip + hero polish + a11y dark |
| 5–8 | #18 #19 #24 #25 | Sub-page UX complete |
| 9–12 | #29 deploy + founder review | Bundle to `~/.sina` + archive |

### 6 months (P1 — match Zenity/Notenic polish)

Items #4 #5 #7 #9 #10 #11 #12 #18 #21 #22 #26 #27 #28 — motion budget, proof film strip, mobile CTA, pricing micro-copy.

### 12 months (P2 — differentiation)

Items #13 #15 #23 — icon system, OG refresh, control-plane density toggle.

---

## Portfolio surfaces (beyond witnessbc-site)

| Surface | Current | Target | Top 3 UI steals |
|---------|---------|--------|-----------------|
| **witnessbc.com** | ~88 A | 92 A | Credo trust · Zenity CTA · Nomotic pricing |
| **Noetfield live** | 74 B | 82 A− | Zenity hero · HTML proof strip · compress IA |
| **Noetfield HTML attach** | 81 A− | 85 A | Credo badge row · FuseGov 3-step |
| **SourceA Nomotic HTML** | ~86 A | 88 A | Logo row when approved · deploy path |

---

## UI metrics (track pre/post)

1. **Trust dimension score** (internal 1–10 rubric) — target ≥8  
2. **Lighthouse Performance + Accessibility** — both ≥90 on home  
3. **Time-to-proof-demo** — visitor reaches interactive terminal in ≤2 clicks / ≤8s  
4. **Mobile hero CTA visibility** — primary CTA in viewport without scroll (390px)  
5. **Validate PASS** — `bash witnessbc-site/scripts/run-recipe.sh` green on every ship

---

## Void list (do NOT copy into UI)

- **WitnessAI brand** — no witness.ai colors, logos, or “Observe/Protect/Control” as our trademark  
- **Fake customer logos** — text cohort strip until written approval  
- **Certification badges** — no “ISO certified” · “EU AI Act compliant” chips  
- **Competitor names** on customer-facing pages (benchmark law)  
- **Securiti-style blog layout** — no SEO article masquerading as product page  
- **Infinite scroll motion** — causes a11y and perf regressions  
- **Funding/revenue stats** on UI as fact — market stats must cite `#ref-N` only

---

## Commands

```bash
bash ~/Desktop/SourceA/witnessbc-site/scripts/run-recipe.sh --open
bash ~/Desktop/SourceA/witnessbc-site/scripts/validate.sh
```

**Companion docs:** `COMPETITOR_SITES_UI_BENCHMARK_2026-06-15_v1.md` · `WITNESSBC_AI_BATTLE_CARD_NOTENIC_ZENITY_2026-06-15_v1.md`

---

*Witness AI · witnessbc.com · UI plan only · educational framework mapping · not legal advice.*
