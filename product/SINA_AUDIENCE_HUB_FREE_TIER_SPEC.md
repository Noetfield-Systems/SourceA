# Sina Audience Hub — free tier product spec

**Version:** 1.0  
**Date:** 2026-06-04  
**Status:** Product definition (from investor OS narrative → customer product)  
**Owner:** ASF

---

## What you asked for (one sentence)

Turn the **story and capability** in our investor docs into a **public web + mobile experience** — a **free tier** that introduces audiences to **Noetfield**, **TrustField**, and a **new umbrella brand**, then upgrades them into each product’s paid offering.

**This is not** DevBridge RUN SYSTEM, wire proof, or internal dispatch — those stay **private**.

---

## Product name (pick one — default below)

| Option | Role |
|--------|------|
| **Sina Hub** (recommended) | Umbrella free portal — “one door, three products” |
| Noetfield.com / TrustField.com | Each keeps its own site; Hub links in |
| New IP name (TBD) | If you register a new trademark, Hub becomes that brand |

**Default IP for this spec:** **Sina Hub** — tagline: *Understand our systems. Start free. Grow into the product you need.*

---

## Audience vs investor docs

| Investor docs | Customer free tier |
|---------------|-------------------|
| Portfolio OS, remote ops, G1/G2 | **Outcome stories** per product |
| “We proved Tailscale” | **Try a demo / sandbox / read-only** |
| Five repos internal | **Three customer front doors** |
| Ask for capital | **Sign up free → upgrade** |

Same **truth**, different **skin**: investors see HoldCo; customers see **value per brand**.

---

## Free tier — what users get (concrete)

### Layer A — Marketing (all visitors, no login)

- **One homepage** (web + responsive mobile web): who we are, three products, trust, legal.
- **Investor-quality clarity** simplified: problem → solution → “what you can do today.”
- **No** internal logs, smoke tests, or orchestrator language.

### Layer B — Free account (email / OAuth)

| Feature | Noetfield track | TrustField track | Hub-wide |
|---------|-----------------|------------------|----------|
| **Read** | Public spec summaries, glossary, 1–2 L2 articles | Trust/compliance explainer, sample checklist | Portfolio timeline / roadmap **public** milestones only |
| **Try** | Sandbox: schema viewer, sample audit event JSON | Sample trust report PDF / demo workflow (read-only) | Save preferences, bookmark docs |
| **Connect** | “Request enterprise pilot” form | “Book demo” / pilot waitlist | Newsletter, product updates |
| **Upgrade path** | Paid tenant + full platform | Paid B2B platform | N/A |

### Layer C — Paid (existing products — out of scope for free build)

- Full Noetfield platform (`apps/platform`, governance console).
- Full TrustField production (`web` deploy).
- VIRLUX / 777 / internal OS — **not** in v1 Hub unless you add later.

---

## Mobile application

**Phase 1 (ship fast):** **PWA** — same Next.js Hub, “Add to Home Screen,” push optional later.  
**Phase 2:** Native shell (Expo) only if metrics justify — reuse patterns from Cursor OS Pro lane, **different SKU**.

| PWA free tier | Native later |
|---------------|--------------|
| Browse products, account, notifications | Biometrics, offline packs |
| Open TrustField / Noetfield deep links | App Store presence for Hub brand |

---

## Architecture (executive)

```text
                    ┌─────────────────────┐
                    │  hub.sina.* (web)   │
                    │  Next.js · PWA      │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                   ▼
    noetfield.com        trustfield.com      (future IP)
    apps/web :13001      web :3000           landing
           │                   │
           └─────────┬─────────┘
                     ▼
              Shared (optional)
              - auth (Supabase/Clerk free tier)
              - analytics (Plausible free)
              - CMS for public copy (markdown from SourceA/investor)
```

**Content SSOT for Hub copy:** adapt from `SourceA/investor/` (ONE_PAGER, SYSTEM_OVERVIEW) — **customer-facing rewrite**, not PDF dump.

**Auth:** one Hub account → optional “link” to Noetfield tenant or TrustField org when they upgrade (Phase 2).

---

## Tier table (pricing narrative — you set numbers)

| Tier | Price | Hub | Noetfield | TrustField |
|------|-------|-----|-----------|------------|
| **Free** | $0 | Browse + account + samples | Read-only docs + sample schemas | Sample reports + waitlist |
| **Pro / Pilot** | Custom | — | Tenant + audit MVP | Staging / pilot |
| **Enterprise** | Contract | — | Full bank spec build | Production + compliance |

---

## What NOT to put in customer app

- RUN SYSTEM, DevBridge desk, SinaPromptOS dispatch
- `ready_to_paste`, ingest YAML, wire proof
- Tailscale instructions for founders
- Internal GLOBAL_PRIORITY / architect raw files

---

## Build phases (90 days)

| Phase | Deliverable | Show customer |
|-------|-------------|---------------|
| **P0 (2 weeks)** | `hub` Next.js site: homepage + 3 product pages + FAQ from investor FAQ (rewritten) | URL live on free host |
| **P1 (4 weeks)** | Free signup, email verify, gated PDF/samples | “Create free account” |
| **P2 (4 weeks)** | Noetfield sample viewer + TrustField demo pack embedded or linked | “Try” button works |
| **P3 (optional)** | PWA manifest + mobile polish | Add to Home Screen |
| **P4** | Paid upgrade CTAs → real Noetfield / TrustField onboarding | Revenue |

**Repos:**

| Piece | Where to build |
|-------|----------------|
| Hub web | **New:** `~/Desktop/SinaHub` or `SinaaiMonoRepo/apps/hub` |
| Noetfield free content | `Noetfield/apps/web` — extend |
| TrustField free content | `TrustField Technologies/web` — extend |

---

## New IP option

If **new IP** = new registered brand (e.g. “Sina Systems” / “Field & Note”):

1. Domain + logo + Hub only on new domain.
2. Noetfield + TrustField as **“powered by”** or product tabs.
3. Investor deck stays **portfolio**; consumer deck is **new IP only**.

Decide before P0 design — affects URL and trademark.

---

## Success metrics (customer, not wire)

| Metric | Target |
|--------|--------|
| Free signups / month | ↑ |
| Demo requests (TrustField) | ↑ |
| Pilot inquiries (Noetfield) | ↑ |
| Free → paid conversion | Track per product |
| Time on “what customers pay for” pages | ↑ |

---

## Next action for ASF (choose one)

1. **Approve name** — Sina Hub vs new IP.  
2. **Approve P0** — scaffold `SinaHub` Next.js on Desktop.  
3. **Point Hub content** — which investor PDF sections become public (ONE_PAGER + SYSTEM_OVERVIEW recommended).

---

*Internal ops remain on Mac + phone desk. This product is what **clients and audience** touch.*
