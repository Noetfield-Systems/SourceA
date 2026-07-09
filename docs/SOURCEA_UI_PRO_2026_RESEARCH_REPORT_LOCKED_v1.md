# SourceA UI Pro Research Report (LOCKED v1)

**Saved:** 2026-07-06T13:56:00Z  
**Authority:** July 2026 B2B AI/devtools benchmark + SourceA live audit  
**Plan:** `docs/SOURCEA_UI_PRO_444_UPGRADE_PLAN_LOCKED_v1.md`  
**SSOT:** `data/sourcea-ui-pro-444-upgrade-plan-v1.json`

---

## Executive summary

SourceA has the **agentic stack** (Brain, Tools dock, Site Pulse, Forge Terminal, live receipts) but not the **2026 interaction model**: product-as-hero, inline demo, bento proof grid, scroll story, command palette.

**Gap:** Hero looks high-tech but is mostly decorative. Brain/Tools live in FABs. Trust stats can show `—` before JS. SKU pages lack contact surfaces.

**Fix:** Wave 1 (UP-UI-001–108) — live console, Forge embed, SSR trust, Brain prompt bar, home unify.

---

## July 2026 benchmark patterns

| Pattern | Who | Lift (industry) | SourceA mapping |
|---------|-----|-----------------|-----------------|
| Product-is-the-hero | Linear, Notion | Kinetic UI demo in hero | `#sa-biz-command` → live receipt + Forge |
| Inline interactive preview | Vercel, Clerk, Neon | +20–60% signups | Terminal `embed=1` in hero |
| Bento grid (real screenshots) | Linear, Raycast | +47% dwell | 6-tile proof grid WS-10 |
| Scroll-driven story | Linear, Supabase | Guided tour without video | Plan→Commit pin WS-11 |
| Command palette | Raycast | Power-user entry | `sourcea-cmdk-v1.js` WS-13 |
| Agentic demo | Walnut, Karumi 2026 | Responds to questions | Brain + live tools WS-32 |
| Self-serve before demo call | Navattic 2026 | +63% demo engagement | Already law — enforce WS-09 |
| Personalization | HubSpot-class | +202% CTA | `?seg=` hero WS-14 |
| LCP &lt; 2.5s | All top sites | ~7%/sec conversion | WS-27 |

**References:** [SaaSHero 2026](https://www.saashero.net/design/landing-page-design-inspiration-2026/) · [SplitSense 2026](https://splitsense.ai/blog/guides/saas-landing-page-best-practices-14-proven-tips-2026/) · [Pravin Kumar 2026](https://www.pravinkumar.co/blog/saas-landing-page-conversion-strategies-2026) · [Walnut agentic demos](https://www.walnut.io/blog/product-demos/blog-product-demos-what-are-agentic-demos/) · [Social Animal teardowns](https://socialanimal.dev/blog/saas-website-examples-2026-design-pattern-teardowns/)

---

## Current SourceA inventory

| Layer | Status | Pro gap |
|-------|--------|---------|
| Visual polish (`founder-home.html`) | Aurora, parallax, cinematic | Decorative > functional |
| Brain | Live v5 retrieval | FAB-only, not hero |
| Tools dock | Segments + guided modal | Corner, not centerpiece |
| Site Pulse | KV + feedback | No public stats strip |
| Forge Terminal | Real product | Outbound link only |
| Trust bar | JS hydrators | RI-2 em-dash placeholders |
| Engine chips | Static spans | Not interactive tabs |
| `/` vs `/sourcea/` | Split experience | Nav/content drift |

---

## Recommended waves (maps to 444 plan)

### Wave 1 — P0 (week 1)
- Hero live console (WS-03)
- Forge hero embed (WS-04)
- Trust SSR (WS-05)
- Engine chips (WS-06)
- Brain hero prompt (WS-07)
- Home unify + CTA law (WS-08, WS-09)

### Wave 2 — P1 (weeks 2–3)
- Bento grid, scroll story, pulse strip, cmdk, persona hero, SKU landers

### Wave 3 — P2 (weeks 4–6)
- Video-on-hover, OG cards, agentic demo, founder analytics

---

## What NOT to build

- Autoplay hero video (LCP harm)
- Navattic-style third-party demo (Forge + Brain **are** the demo)
- Book-demo primary CTA
- Fake metrics / certifications
- Full SPA rewrite

---

## 2026 homepage formula (SourceA)

1. Outcome H1 + proof subcopy  
2. Hero right: Forge embed OR live receipt console  
3. Hero left: Brain prompt + 2 CTAs (Terminal · Start 48h)  
4. Trust strip with **real numbers in HTML**  
5. Bento: 6 clickable proof tiles  
6. Scroll story: Plan→Commit  
7. Pricing link above fold  
8. FAQ (AI-search)  
9. Pulse activity strip  
10. Footer ecosystem map  

---

*Research locked — implementation in 444-step plan.*
