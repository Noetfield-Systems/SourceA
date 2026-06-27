#!/usr/bin/env python3
"""Generate 444 Pure Flow upgrade plans from Vancouver  intelligence SSOT."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEL = ROOT / "docs/pure-flow--intelligence-vancouver-v1.md"
OUT_BATCH = ROOT / "data/pureflow-upgrade-queue-444-locked-v1.json"
OUT_ACTIVE = ROOT / "data/pureflow-upgrade-queue-active-v1.json"
OUT_INDEX = ROOT / "labs/pure-flow-pool-landing/WORKER_QUEUE_444_INDEX_v1.md"

WORK_ROOT = "labs/pure-flow-pool-landing"
SITE_URL = "https://pureflow.sourcea.app"

S_T1 = [
    ("Puddle Pool Services", "digital E-Report + book online + no contract"),
    ("Lions Gate Pool & Spa", "published spa pricing + strata depth"),
    ("West Coast Pool & Spa", "same tech same time + 24hr emergency"),
    ("Imperial Paddock Pools", "commercial strata + retail water test"),
    ("C-Blu Service & Supplies", "10yr loyalty trust + repair depth"),
    ("Pond's Pool & Spa", "green pool recovery + communication"),
    ("Pacific Pools", "strata technical appointment tone"),
    ("Pools Plus Vancouver", "RED SEAL plumber + warranty tech"),
    ("Pool Compass Inc.", "eco chemicals + e-commerce"),
]

S_T2 = [
    ("Mint Pool & Spa", "founder-led North Shore trust"),
    ("Bright Pools", "commercial strata cleaning"),
    ("Priority Pool Maintenance", "since 1978 LM coverage"),
    ("Waterworx Pools", "Fraser Health certified"),
    ("Crystalview Pool Spa & Patio", "book a service call retail"),
    ("Splash Hot Tubs & Pools", "weekly spa packages Sea to Sky"),
    ("All Star Spa Services", "hot tub delivery + service"),
    ("Hot Tubs Galore", "parts house calls"),
    ("Mobile Pool & Spa Service", "Langley mobile since 1999"),
    ("Poolside Spa Sales & Service", "Whistler/Squamish"),
    ("Stevens Pools Ltd.", "BBB service"),
    ("Brian's Pool & Spa", "BBB service"),
    ("Payton Pools", "Mission/Fraser since 1974"),
    ("Pleasure Pools Plus", "BBB LM"),
    ("Pacific West Spa & Pool", "BBB LM"),
    ("Valley Grove Pools", "Fraser construction"),
    ("JC Fireplaces & Spas", "spa/fireplace crossover"),
    ("Classic Leisure Lifestyles", "BBB"),
]

NEIGHBORHOODS = [
    "Kitsilano", "Kerrisdale", "Dunbar", "Point Grey", "Shaughnessy", "West Point Grey",
    "Arbutus", "Cambie", "Marpole", "Oakridge", "South Granville", "Fairview",
    "Mount Pleasant", "West End", "Yaletown", "Renfrew", "Kensington", "Fraserview",
    "Lower Lonsdale", "Lynn Valley", "Edgemont", "Deep Cove", "Ambleside", "Dundarave",
    "British Properties", "Caulfeild", "Hollyburn", "Westmount", "Burnaby Heights",
    "Brentwood", "Metrotown", "New Westminster", "Richmond Steveston", "Surrey South",
    "White Rock", "Coquitlam Burke Mtn", "Port Moody", "Langley Walnut Grove",
]

UPGRADE_PILLARS = [
    ("booking", "Booking & schedule UX", [
        "Add preferred-day/time slot UI pattern inspired by {}",
        "Embed Calendly/Jobber booking step after form — beat {} friction",
        "SMS confirm within 4hrs copy on booking success — match {} reliability promise",
        "Mobile sticky Book CTA hides on #book in view — test vs {} mobile",
        "Spa-only fast path on homepage — learn from {}",
        "One-time service path without audit language — counter {} tone",
        "Spring opening booking banner Mar–Apr — seasonal spike like {}",
        "Fall closing booking banner Sep–Oct — seasonal spike like {}",
        "Green pool emergency book-now card — Pond's-style urgency",
        "Add evening/weekend preferred time options — homeowner convenience",
    ]),
    ("pricing", "Pricing transparency", [
        "Show weekly pool anchor $449/mo on pricing card — Lions Gate parity",
        "Show spa weekly from $129/mo — undercut Lions Gate $159 anchor",
        "Open/close package $350–$550 range on seasonal cards",
        "Green recovery flat from $295 on hero float — Pond's ",
        "Chemicals-included fair-use footnote on all plans — Puddle pattern",
        "No contract month-to-month badge on pricing — Puddle differentiator",
        "Combo pool+spa save $59/mo callout — bundle math visible",
        "Bi-weekly $279 anchor for lighter-use pools",
        "FAQ: what affects price (size, salt, travel) — Puddle honesty",
        "Compare table row: hidden fees vs Pure Flow upfront pricing",
    ]),
    ("report", "PureFlow Report proof", [
        "Post-visit email report template HTML — copy Puddle E-Report structure",
        "Report section: sample PDF download mock — trust artifact",
        "Hero report card: real pool photo + chemistry — done, polish caption",
        "Phone mockup report: add timestamp + tech name field",
        "FAQ: what is in every PureFlow Report — educate like {}",
        "Automate report email from Worker after visit (future) — document API",
        "Add checklist icons on report features list — scanability",
        "Video loop: 15s report walkthrough on #report section",
        "Customer quote about reports in reviews section — social proof",
        "Report archive login placeholder (phase 2) — stickiness",
    ]),
    ("seo", "Hyperlocal SEO", [
        "Neighborhood landing page: {hood} pool & spa service",
        "Meta title/description for {hood} — local search intent",
        "JSON-LD LocalBusiness areaServed include {hood}",
        "Internal link from homepage neighborhood strip → {hood} page",
        "Blog stub: pool care in {hood} rain dilution tips",
        "FAQ schema for {hood} service area page",
        "Open Graph image per neighborhood (template)",
        "Sitemap.xml include all neighborhood routes",
        "robots.txt + canonical for {hood} page",
        " counter-copy: why Pure Flow vs service in {hood}",
    ]),
    ("trust", "Trust & credentials", [
        "Trust strip: Insured · Locally owned · Vancouver BC",
        "CPO-certified path badge (when certified) — Puddle parity",
        "RED SEAL / gas ticket mention if hired — Pools Plus pattern",
        "Same technician every week promise — West Coast/Mint",
        "We answer the phone — real {phone} not placeholder",
        "Google Business Profile link in footer",
        "BBB-ready business block (when listed)",
        "Privacy policy page for booking form",
        "Service area map SVG Zone 1 Vancouver West",
        "Founder story soften to neighbor service — not audit brand",
    ]),
    ("spa", "Spa & hot tub lane", [
        "Spa weekly plan card primary on mobile — year-round revenue",
        "Hot tub brands we service list — Crystalview breadth",
        "Inflatable spa FAQ — Puddle niche",
        "Spa chemistry winter care tip — Lions Gate season",
        "Bi-weekly spa $89  anchor mention in compare",
        "Spa+pool combo upsell on spa-only bookings",
        "Cover cleaning included copy on spa plans",
        "Error code / weak jets repair CTA — repair upsell",
        "Sea to Sky spa note: defer or partner link Splash",
        "Spa testimonial slot in reviews",
    ]),
    ("convert", "Conversion & compare", [
        "Compare: Pure Flow vs usual pool guy — 5 rows",
        "Compare: vs {} — one honest row each",
        "Stats bar: 100% visits documented",
        "Stats bar: confirm within 4 business hours",
        "Availability strip Mon–Sat morning/afternoon",
        "How-it-works 4 steps booking not assessment",
        "Exit-intent book CTA (light, no dark patterns)",
        "Referral field on booking form analytics",
        "UTM capture on booking API KV",
        "A/B headline test copy variant in config.js",
    ]),
    ("ops", "Ops & backend", [
        "Booking API: store preferred_date/time in KV email",
        "Twilio SMS confirm hook (phase 2) document in README",
        "Cloudflare Email enable hello@pureflow.sourcea.app",
        "Register pureflowpools.ca domain + route Worker",
        "Google Analytics 4 events on book submit",
        "Meta Pixel placeholder gated by config",
        "Jobber/Zapier webhook on new lead",
        "Admin KV export script for leads",
        "Rate limit / honeypot on booking form",
        "E2E smoke: booking + photo + domain checks in publish script",
    ]),
    ("reviews", "Reviews & social", [
        "Google Reviews embed when 5+ reviews live",
        "HomeStars profile link (when claimed)",
        "Review ask email template post-visit",
        "Screenshot testimonial cards with Vancouver names",
        "Neighborhood-specific review quote for {hood}",
        "Star rating aggregate in JSON-LD",
        "Instagram gallery strip (phase 2)",
        "Before/after green pool recovery gallery",
        "Video testimonial placeholder",
        "Respond-to-negative review playbook doc",
    ]),
    ("content", "Content & education", [
        "FAQ: soft Capilano water chemistry",
        "FAQ: rain dilution Vancouver pools",
        "FAQ: salt cell winter care",
        "FAQ: how often weekly vs biweekly",
        "FAQ: chemicals included limits",
        "FAQ: residential only not strata",
        "Blog: spring opening checklist Vancouver",
        "Blog: when to close pool Vancouver",
        "Blog: hot tub year-round vs pool seasonal",
        "Glossary: pH chlorine alkalinity plain English",
    ]),
    ("tech", "Technical & perf", [
        "Lighthouse mobile perf pass 90+",
        "Image WebP for visit-report-pool",
        "Preload hero fonts subset",
        "lazy load below-fold images",
        "CSP headers on Worker",
        "404 page on-brand",
        "site.webmanifest icons complete",
        "favicon apple-touch-icon",
        "hreflang en-CA",
        "structured data Service schema",
    ]),
    ("growth", "Growth & partnerships", [
        "Realtor partner landing stub",
        "Property manager referral program copy",
        "Airbnb host pool/spa plan mention",
        "Neighbourhood Facebook group outreach script",
        "Nextdoor business post template",
        "Spring postcard mailer copy Zone 1",
        "Referral $50 credit program terms",
        "Partner with local pool store chemical pickup",
        "Trade show booth one-pager PDF",
        "LinkedIn company page checklist",
    ]),
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _prompt(plan: dict) -> str:
    return f"""WORK: {plan['id']} — Pure Flow Pool & Spa upgrade (Sunflow Worker lane)
BOUND: {WORK_ROOT}/ only — do not edit brain-os or unrelated apps
SITE: {SITE_URL}
INTEL: docs/pure-flow--intelligence-vancouver-v1.md

## Mission
{plan['title']}

##  signal
**{plan.get('', 'Market')}** — {plan.get('_edge', 'Vancouver pool/spa ')}

## Pillar
{plan['pillar']} · Level {plan['level']}

## Acceptance
- Implement or document the upgrade in bounded paths
- Deploy only if founder ship window; else leave ready on disk
- Verify: `python3 scripts/publish_pureflow_landing_v1.py` smoke OR light grep proof
- One turn · WORKER_ROUND_REPORT · STOP

## Forbidden
- Strata/commercial compliance scope (residential Zone 1 only)
- Assessment/audit tone on customer-facing copy
- Personal founder name on public URLs or contact lines
"""


def generate() -> dict:
    plans: list[dict] = []
    n = 0
    all_s = S_T1 + S_T2
    comp_i = 0
    hood_i = 0

    for level, (pillar_key, pillar_name, templates) in enumerate(UPGRADE_PILLARS, 1):
        for tmpl in templates:
            if n >= 444:
                break
            comp_name, comp_edge = all_s[comp_i % len(all_s)]
            hood = NEIGHBORHOODS[hood_i % len(NEIGHBORHOODS)]
            comp_i += 1
            hood_i += 1
            title = tmpl.format(=comp_name, hood=hood, phone="(604) real-line")
            n += 1
            pid = f"pf-upg-{n:03d}"
            row = {
                "n": n,
                "id": pid,
                "sa_id": pid,
                "stack": "pureflow",
                "worker_lane": "sunflow_worker",
                "plane": "product",
                "queue_role": "act",
                "pillar": pillar_key,
                "pillar_name": pillar_name,
                "level": level,
                "": comp_name,
                "_edge": comp_edge,
                "neighborhood": hood if "{hood}" in tmpl else None,
                "title": title,
                "work_root": WORK_ROOT,
                "status": "queued",
                "maps_intel": "docs/pure-flow--intelligence-vancouver-v1.md",
            }
            row["prompt"] = _prompt(row)
            plans.append(row)
        if n >= 444:
            break

    # Pad to exactly 444 with -specific counter-moves
    while n < 444:
        comp_name, comp_edge = all_s[comp_i % len(all_s)]
        hood = NEIGHBORHOODS[hood_i % len(NEIGHBORHOODS)]
        comp_i += 1
        hood_i += 1
        n += 1
        pid = f"pf-upg-{n:03d}"
        title = f"Counter-move: adopt best booking/proof tactic from {comp_name} for {hood} homeowners"
        row = {
            "n": n,
            "id": pid,
            "sa_id": pid,
            "stack": "pureflow",
            "worker_lane": "sunflow_worker",
            "plane": "product",
            "queue_role": "act",
            "pillar": "counter",
            "pillar_name": " counter-move",
            "level": 13,
            "": comp_name,
            "_edge": comp_edge,
            "neighborhood": hood,
            "title": title,
            "work_root": WORK_ROOT,
            "status": "queued",
            "maps_intel": "docs/pure-flow--intelligence-vancouver-v1.md",
        }
        row["prompt"] = _prompt(row)
        plans.append(row)

    return {
        "schema": "pureflow-upgrade-queue-v1",
        "version": "1.0.0",
        "count": 444,
        "locked": True,
        "saved_at": _now(),
        "authority": "docs/pure-flow--intelligence-vancouver-v1.md",
        "one_law": "444 product upgrades for Pure Flow — Sunflow Worker executes one pf-upg per INBOX turn",
        "work_root": WORK_ROOT,
        "site_url": SITE_URL,
        "worker_lane": "sunflow_worker",
        "summary": {
            "pillars": len(UPGRADE_PILLARS),
            "s_t1": len(S_T1),
            "s_t2": len(S_T2),
            "neighborhoods": len(NEIGHBORHOODS),
            "id_range": "pf-upg-001..pf-upg-444",
        },
        "plans": plans,
    }


def write_index(batch: dict) -> None:
    lines = [
        "# Pure Flow Worker — 444 upgrade queue index",
        "",
        f"**Saved:** {_now()}",
        f"**Batch:** `data/pureflow-upgrade-queue-444-locked-v1.json`",
        f"**Active:** `data/pureflow-upgrade-queue-active-v1.json`",
        f"**Site:** {SITE_URL}",
        "",
        "## Run",
        "",
        "```bash",
        "cd ~/Desktop/SourceA",
        "python3 scripts/pureflow_worker_inbox_seed_v1.py --next",
        "# Worker chat: RUN INBOX",
        "```",
        "",
        "## Pillars",
        "",
    ]
    for level, (_, name, _) in enumerate(UPGRADE_PILLARS, 1):
        lines.append(f"- L{level}: {name}")
    lines.append("")
    lines.append("## Head (first 25)")
    lines.append("")
    for p in batch["plans"][:25]:
        lines.append(f"- `{p['id']}` — {p['title'][:90]}")
    lines.append("")
    lines.append(f"*… {batch['count'] - 25} more in batch JSON*")
    OUT_INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    batch = generate()
    assert len(batch["plans"]) == 444, len(batch["plans"])
    OUT_BATCH.write_text(json.dumps(batch, indent=2) + "\n", encoding="utf-8")
    active = {
        "schema": "pureflow-upgrade-queue-active-v1",
        "version": "1.0.0",
        "saved_at": _now(),
        "queue_path": "data/pureflow-upgrade-queue-444-locked-v1.json",
        "head_id": "pf-upg-001",
        "head_n": 1,
        "count": 444,
        "completed": [],
        "worker_lane": "sunflow_worker",
        "site_url": SITE_URL,
    }
    OUT_ACTIVE.write_text(json.dumps(active, indent=2) + "\n", encoding="utf-8")
    write_index(batch)
    print(json.dumps({"ok": True, "count": 444, "batch": str(OUT_BATCH), "active": str(OUT_ACTIVE)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
