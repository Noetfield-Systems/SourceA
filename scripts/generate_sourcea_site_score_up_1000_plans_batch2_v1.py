#!/usr/bin/env python3
"""Generate batch-2 SourceA site score-up plans — grade-A+ · 93+ target · zero batch-1 dupes.

SSOT: docs/SOURCEA_SITE_SCORE_UP_1000_BATCH2_LOCKED_v1.md
Prerequisite pack: brain-os/plan-registry/sourcea-site-score-up-1000/
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCEA_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_VERSION = 2
PACK_BASE = SOURCEA_ROOT / "brain-os" / "plan-registry" / "sourcea-site-score-up-1000-batch2"
BATCH1_REG = SOURCEA_ROOT / "brain-os" / "plan-registry" / "sourcea-site-score-up-1000" / "REGISTRY.json"
PREFIX = "sa-score2"

# Advanced lanes — no overlap with batch-1 theme IDs (t01–t10)
THEMES = [
    ("t11-proof-cryptography", "Proof integrity & cryptography", 58, 96, "Sigstore / GitHub attestations"),
    ("t12-conversion-science", "Conversion funnel science", 62, 94, "Amplitude / Mixpanel"),
    ("t13-enterprise-procurement", "Enterprise buyer readiness", 48, 93, "Vanta / SafeBase"),
    ("t14-instant-first-win", "Instant first-win onboarding", 55, 94, "Loom / Replit Agent"),
    ("t15-distribution-seo", "Distribution & SEO surface", 50, 92, "Ahrefs / programmatic SEO"),
    ("t16-social-trust", "Social proof & trust signals", 52, 93, "G2 / testimonial.to"),
    ("t17-plg-virality", "Product-led growth loops", 45, 91, "Cal.com referral / Notion templates"),
    ("t18-developer-platform", "Developer & partner API", 40, 90, "Stripe API / Twilio webhooks"),
    ("t19-reliability-sla", "Reliability & public SLA", 60, 95, "statuspage.io / Better Stack"),
    ("t20-competitive-moat", "Competitive differentiation", 55, 94, "category design / Superhuman"),
]

WORKSTREAMS = [
    ("w11-architect", "Architect"),
    ("w12-harden", "Harden"),
    ("w13-measure", "Measure"),
    ("w14-automate", "Automate"),
    ("w15-integrate", "Integrate"),
    ("w16-optimize", "Optimize"),
    ("w17-comply", "Comply"),
    ("w18-scale", "Scale"),
    ("w19-monetize", "Monetize"),
    ("w20-defend", "Defend moat"),
]

TIER_FOR_SLICE = ["T0", "T0", "T1", "T1", "T1", "T2", "T2", "T2", "T3", "T3"]

TIER_DEPTH = {
    "T0": "Grade-A P0 — production-grade slice; stranger-visible on sourcea.app",
    "T1": "Grade-A P1 — measurable +2 score delta with receipt",
    "T2": "Grade-A P2 — harden · benchmark · document",
    "T3": "Grade-A P3 — research · competitive intel · defer",
}

DELIVERABLES: dict[str, list[str]] = {
    "t11-proof-cryptography": [
        "Ed25519-signed proof receipt JSON with public /api/proof/verify/v1",
        "SHA-256 manifest for proof pack ZIP with on-page checksum display",
        "immutable proof run ID in Cloudflare Durable Object ledger",
        "third-party verify page: paste receipt JSON → green/red verdict",
        "receipt includes git commit hash + deploy URL + timestamp chain",
        "export proof as W3C Verifiable Credential lite format",
        "anti-tamper nonce on every pulse feedback submission",
        "founder dashboard 'verify last receipt' one-click audit",
        "public proof gallery with signature badges only for valid rows",
        "compare receipt hash to on-chain anchor stub (Labs tier)",
    ],
    "t12-conversion-science": [
        "segment→proof→intake funnel chart in pulse-founder",
        "drop-off heatmap events: guided_abandon / proof_bounce / cal_escape",
        "cohort table: first segment vs conversion to feedback",
        "A/B variant field on CTA SSOT with pulse track suffix",
        "weekly conversion report email from worker cron",
        "time-to-first-receipt median KPI card on founder home",
        "Cal overlay vs proof CTA split test dashboard row",
        "learn quiz completion → start intake conversion rate",
        "sandbox started vs submitted ratio alert",
        "export funnel JSON for founder spreadsheet",
    ],
    "t13-enterprise-procurement": [
        "security.html primary CTA → /sourcea/proof/live not mailto",
        "downloadable security one-pager PDF from /trust",
        "data processing summary page /sourcea/legal/dpa",
        "procurement contact → intake worker not hello@ mailto",
        "subprocessors list table with last-reviewed date",
        "enterprise FAQ accordion on /platform",
        "SSO roadmap honest timeline on platform portal",
        "vendor assessment questionnaire auto-reply pack",
        "invoice + W-9 request intake form",
        "MSA redline intake with scope lock fields",
    ],
    "t14-instant-first-win": [
        "60-second stranger path: land → segment → live receipt open",
        "interactive proof console on hero with real KV stat tick",
        "learn quiz auto-advance with confetti on pass",
        "Forge Terminal pre-filled prompt from segment choice",
        "empty-state elimination on pulse-founder before key entered",
        "skeleton loaders on /sourcea/status stats fetch",
        "progress stepper on /start intake (3 steps max)",
        "post-feedback thank-you with share receipt link",
        "returning visitor 'continue where you left off' chip",
        "mobile-first touch targets ≥44px audit on /learn",
    ],
    "t15-distribution-seo": [
        "unique title/description per segment landing via build inject",
        "OpenGraph image per door (startup / VC / beginner / agency / cursor)",
        "sitemap.xml includes /learn /pulse-founder /sourcea/status",
        "JSON-LD Organization + WebSite on founder-home",
        "JSON-LD Product on /offer with proof offer schema",
        "canonical URLs on all /sourcea/* clean paths",
        "programmatic /compare/sourcea-vs-agency page",
        "blog stub /insights with first proof-case article",
        "llms.txt for AI crawler routing to proof surfaces",
        "hreflang stub EN-CA for founder worldwide pill",
    ],
    "t16-social-trust": [
        "live pageview counter on /sourcea/status (public safe)",
        "testimonial cards with verifiable receipt links",
        "logo wall links to case studies not dead anchors",
        "trust/index.html CTA fixes: mailto → proof live",
        "team.html CTA → proof not mailto",
        "sources.html 'See live receipt' → /sourcea/proof/live",
        "case study metric chips with pulse-backed numbers",
        "founder video embed placeholder with honest 'coming' label",
        "G2/Capterra review CTA after positive feedback submit",
        "client quote schema on case-studies pages",
    ],
    "t17-plg-virality": [
        "share proof receipt URL with UTM ref=stranger",
        "referral param ?ref= persists to pulse events",
        "embeddable proof iframe /sourcea/proof/embed for partners",
        "copy-link button on live receipt page",
        "LinkedIn share meta for proof completion",
        "template gallery: fork our segment router JSON",
        "open-source pulse client snippet on /sourcea/developers",
        "community Discord/Slack honest waitlist intake",
        "badge 'Verified by SourceA' SVG for client sites",
        "viral loop: feedback → public stats increment animation",
    ],
    "t18-developer-platform": [
        "public API doc /sourcea/developers/pulse-api",
        "webhook POST /api/site/webhook/v1 for partner events",
        "HMAC-SHA256 signature docs for intake webhooks",
        "rate limit headers on all public site APIs",
        "API key issuance for agency partners (founder-only)",
        "OpenAPI 3.1 spec published at /sourcea/openapi.json",
        "SDK stub npm @sourcea/pulse-client README",
        "sandbox API key for proof run integration tests",
        "changelog /sourcea/changelog machine-generated",
        "status webhook subscription for proof run complete",
    ],
    "t19-reliability-sla": [
        "worker /api/site/health/v1 with KV latency probe",
        "public uptime % on /sourcea/status from health checks",
        "incident banner component in site header SSOT",
        "founder alert when pulse worker 5xx > 3 in 5 min",
        "graceful degradation when pulse worker offline",
        "feedback queues locally when worker down sync later",
        "RTO/RPO honest copy on /trust",
        "deploy smoke receipt in GitHub Actions not Mac",
        "multi-region worker stub doc for scale phase",
        "SLA page: proof delivery target minutes not hours",
    ],
    "t20-competitive-moat": [
        "comparison table SourceA vs Cal-first agency",
        "comparison vs Trigger.dev (receipt + GTM not just runs)",
        "comparison vs Vercel (proof-native not deploy-only)",
        "moat narrative: governed agentic + receipt on every page",
        "forbidden pattern doc: no fake login no mailto intake",
        "category name lock: 'Proof-native agentic execution'",
        "pricing anchored to outcome not hours",
        "case study: stranger verified without call",
        "founder story page tied to receipt philosophy",
        "investor one-pager PDF with live status QR",
    ],
}

WS_ACTION = {
    "w11-architect": "Architect",
    "w12-harden": "Harden",
    "w13-measure": "Measure",
    "w14-automate": "Automate",
    "w15-integrate": "Integrate",
    "w16-optimize": "Optimize",
    "w17-comply": "Comply",
    "w18-scale": "Scale",
    "w19-monetize": "Monetize",
    "w20-defend": "Defend",
}


def load_batch1_titles() -> set[str]:
    if not BATCH1_REG.is_file():
        return set()
    reg = json.loads(BATCH1_REG.read_text(encoding="utf-8"))
    return {p["title"].lower().strip() for p in reg.get("plans", [])}


def plan_title(theme_id: str, ws_id: str, slice_n: int) -> str:
    ws_idx = next(i for i, (wid, _) in enumerate(WORKSTREAMS) if wid == ws_id)
    items = DELIVERABLES[theme_id]
    idx = (ws_idx + slice_n - 1) % len(items)
    action = WS_ACTION[ws_id]
    return f"{action} {items[idx]}"


def phase_for_rank(rank: int) -> str:
    if rank <= 60:
        return "NOW"
    if rank <= 220:
        return "NEXT"
    if rank <= 550:
        return "LATER"
    return "MOONSHOT"


def prompt_md(
    *,
    plan_id: str,
    theme_id: str,
    theme_label: str,
    score_now: int,
    score_target: int,
    market: str,
    ws_id: str,
    ws_label: str,
    slice_n: int,
    tier: str,
    phase: str,
    title: str,
    grade: str,
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""# {plan_id} — {title}

**Saved at:** {now}
**Batch:** 2 · **Grade:** {grade} · **Tier:** {tier} · **Phase:** {phase}
**Score dimension:** {theme_label} ({score_now}→{score_target})
**Market analog:** {market}
**Workstream:** {ws_id} · {ws_label}
**Slice:** {slice_n}/10
**SSOT:** `docs/SOURCEA_SITE_SCORE_UP_1000_BATCH2_LOCKED_v1.md`
**Prerequisite:** batch-1 pack or equivalent shipped slices

## North star

Batch-2 raises site score **78 → 93+** — enterprise-credible · cryptographically verifiable · conversion-measured.

## Task

{TIER_DEPTH[tier]}

**Deliverable:** {title}

## Anti-duplication

Must NOT repeat any `sa-score-*` batch-1 title. This plan is batch-2 only.

## Verify

```bash
cd ~/Desktop/SourceA && bash scripts/validate-sourcea-site-score-up-1000-batch2-v1.sh
bash scripts/validate-sourcea-modern-stack-e2e-v1.sh
```

## Closeout

1. `status: done` in batch-2 REGISTRY.json
2. Set `score_delta` (expected +0.1 to +0.5 site-wide)
3. Live proof URL in closeout note

---
agent_tag: AGENT-AUTO-SOURCEA-SITE-B2
trigger: WORK sa-score2 bounded batch-2
generator: generate_sourcea_site_score_up_1000_plans_batch2_v1.py v{GENERATOR_VERSION}
"""


def generate(now: str) -> dict:
    batch1_titles = load_batch1_titles()
    entries: list[dict] = []
    phases: list[dict] = []
    seq = 0
    dupes: list[str] = []

    for theme_id, theme_label, score_now, score_target, market in THEMES:
        phase_id = f"phase-{PREFIX}-{theme_id}"
        phases.append(
            {
                "id": phase_id,
                "theme": theme_id,
                "theme_label": theme_label,
                "score_now": score_now,
                "score_target": score_target,
                "market_analog": market,
                "batch": 2,
                "grade": "A+",
            }
        )
        for ws_id, ws_label in WORKSTREAMS:
            for slice_n in range(1, 11):
                seq += 1
                plan_id = f"{PREFIX}-{seq:04d}"
                tier = TIER_FOR_SLICE[slice_n - 1]
                phase = phase_for_rank(seq)
                title = plan_title(theme_id, ws_id, slice_n)
                norm = title.lower().strip()
                if norm in batch1_titles:
                    dupes.append(title)
                rel = f"prompts/{phase_id}/{ws_id}/slice-{slice_n:02d}.md"
                path = PACK_BASE / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                grade = "A+" if tier in ("T0", "T1") else "A"
                path.write_text(
                    prompt_md(
                        plan_id=plan_id,
                        theme_id=theme_id,
                        theme_label=theme_label,
                        score_now=score_now,
                        score_target=score_target,
                        market=market,
                        ws_id=ws_id,
                        ws_label=ws_label,
                        slice_n=slice_n,
                        tier=tier,
                        phase=phase,
                        title=title,
                        grade=grade,
                    ),
                    encoding="utf-8",
                )
                entries.append(
                    {
                        "id": plan_id,
                        "batch": 2,
                        "grade": grade,
                        "theme": theme_id,
                        "theme_label": theme_label,
                        "score_now": score_now,
                        "score_target": score_target,
                        "market_analog": market,
                        "workstream": ws_id,
                        "workstream_label": ws_label,
                        "slice": slice_n,
                        "tier": tier,
                        "phase": phase,
                        "title": title,
                        "status": "open",
                        "score_delta": None,
                        "priority_rank": seq,
                        "path": rel,
                        "lane": "sourcea-site-batch2",
                        "prerequisite_pack": "sourcea-site-score-up-1000",
                        "agent_prompt": f"WORK — {plan_id}: {title}",
                    }
                )

    if dupes:
        raise SystemExit(f"DUPLICATION with batch-1: {dupes[:5]} ... ({len(dupes)} total)")

    registry = {
        "schema": "sourcea-site-score-up-1000-batch2-registry-v1",
        "schema_version": GENERATOR_VERSION,
        "generated_at": now,
        "batch": 2,
        "grade": "A+",
        "repo": "sourcea",
        "repo_label": "SourceA site batch-2 (93+ pathway)",
        "count": len(entries),
        "grid": "10 advanced dimensions × 10 grade workstreams × 10 slices",
        "baseline_score": 78,
        "target_score": 93,
        "batch1_pack": "brain-os/plan-registry/sourcea-site-score-up-1000",
        "dedup_verified_against_batch1": True,
        "external_repo": "~/Desktop/SourceA",
        "law_doc": "docs/SOURCEA_SITE_SCORE_UP_1000_BATCH2_LOCKED_v1.md",
        "analysis_doc": "docs/SOURCEA_SITE_SCORE_ANALYSIS_v2_LOCKED_v1.md",
        "phases": phases,
        "plans": entries,
    }
    PACK_BASE.mkdir(parents=True, exist_ok=True)
    (PACK_BASE / "REGISTRY.json").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    master = {
        "schema": "sourcea-site-score-up-1000-batch2-master-v1",
        "version": "1.0.0",
        "generated_at": now,
        "generator": "scripts/generate_sourcea_site_score_up_1000_plans_batch2_v1.py",
        "law_doc": "docs/SOURCEA_SITE_SCORE_UP_1000_BATCH2_LOCKED_v1.md",
        "analysis_doc": "docs/SOURCEA_SITE_SCORE_ANALYSIS_v2_LOCKED_v1.md",
        "plan_count": 1000,
        "batch": 2,
        "baseline_score": 78,
        "target_score": 93,
        "dedup_verified_against_batch1": True,
        "pack": str(PACK_BASE),
        "phase_law": {
            "NOW": "ranks 1–60 — proof crypto · conversion · enterprise · first-win",
            "NEXT": "ranks 61–220",
            "LATER": "ranks 221–550",
            "MOONSHOT": "ranks 551–1000",
        },
    }
    master_path = SOURCEA_ROOT / "brain-os" / "plan-registry" / "SOURCEA_SITE_SCORE_UP_1000_BATCH2_MASTER_v1.json"
    master_path.write_text(json.dumps(master, indent=2) + "\n", encoding="utf-8")

    (PACK_BASE / "README_LOCKED_v1.md").write_text(
        f"# SourceA site score-up batch-2 — 1000 plans (Grade A+)\n\n"
        f"Generated: {now}\n\n"
        f"**78 → 93+** · zero batch-1 title duplication · REGISTRY: `REGISTRY.json`\n",
        encoding="utf-8",
    )
    return {"count": len(entries), "ok": len(entries) == 1000, "dupes": 0}


def main() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result = generate(now)
    print(json.dumps({"ok": result["ok"], "plan_count": result["count"], "batch": 2, "generated_at": now}, indent=2))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
