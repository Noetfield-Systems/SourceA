#!/usr/bin/env python3
"""Generate 1000 SourceA site score-up plans — 10 dimensions × 10 workstreams × 10 slices.

SSOT: docs/SOURCEA_SITE_SCORE_UP_1000_PLANS_LOCKED_v1.md
Baseline scorecard: ~76/100 (2026-06-25) — target 95+.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCEA_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_VERSION = 1
PACK_BASE = SOURCEA_ROOT / "brain-os" / "plan-registry" / "sourcea-site-score-up-1000"
PREFIX = "sa-score"

# Ordered by impact gap (highest leverage first)
THEMES = [
    ("t05-self-serve-proof", "Self-serve proof", 65, 95, "Trigger.dev"),
    ("t08-market-polish", "Market polish", 55, 90, "Linear"),
    ("t09-commercial-close", "Commercial close", 60, 92, "Stripe Atlas"),
    ("t06-intake-ops", "Intake → ops loop", 70, 95, "Typeform + Zapier"),
    ("t02-client-ui", "Client-facing UI", 72, 93, "Vercel"),
    ("t04-deterministic-routing", "Deterministic routing", 80, 97, "Intercom Fin"),
    ("t01-live-wiring", "Live wiring", 88, 100, "Cloudflare Workers"),
    ("t07-analytics-feedback", "Analytics & feedback", 82, 98, "PostHog"),
    ("t03-vocabulary", "Vocabulary SSOT", 85, 99, "Notion GTM"),
    ("t10-e2e-quality", "E2E & quality gates", 88, 100, "Playwright"),
]

WORKSTREAMS = [
    ("w01-ship", "Ship"),
    ("w02-prove", "Prove"),
    ("w03-wire", "Wire"),
    ("w04-ui", "UI"),
    ("w05-copy", "Copy"),
    ("w06-worker", "Worker"),
    ("w07-deploy", "Deploy"),
    ("w08-e2e", "E2E"),
    ("w09-bench", "Market bench"),
    ("w10-receipt", "Receipt"),
]

TIER_FOR_SLICE = ["T0", "T0", "T1", "T1", "T2", "T2", "T2", "T3", "T3", "T3"]

TIER_DEPTH = {
    "T0": "P0 — smallest shippable slice; live on sourcea.app",
    "T1": "P1 — next sprint; measurable score delta",
    "T2": "P2 — harden · document · validate",
    "T3": "P3 — bench · defer · compare-only",
}

# Concrete deliverables per theme (rotated by workstream + slice)
DELIVERABLES: dict[str, list[str]] = {
    "t05-self-serve-proof": [
        "stranger POST /api/proof/run/v1 → cloud job → public receipt URL",
        "proof run progress bar on /sourcea/proof/live",
        "email receipt link after async proof completes",
        "proof run status page /sourcea/proof/run/:id",
        "Forge Terminal handoff after proof quiz pass",
        "VC proof lane ends on verifiable receipt not Cal",
        "48h MVP intake triggers scoped proof job template",
        "sandbox bounded job → worker queue not mailto",
        "proof pack download ZIP with checksum",
        "stranger proof SLA copy ≤15 min on hero",
    ],
    "t08-market-polish": [
        "hero typography pass — match Linear/Vercel rhythm",
        "mobile nav + segment strip responsive QA",
        "dark mode contrast audit on proof pages",
        "loading skeleton on pulse-founder dashboard",
        "unified button radius + shadow tokens in app.css",
        "trust page visual parity with pricing",
        "forge terminal iframe chrome polish",
        "learn quiz micro-animations",
        "footer link grid cleanup",
        "lighthouse performance budget ≥90 mobile",
    ],
    "t09-commercial-close": [
        "pricing CTA → /start not mailto",
        "Stripe payment link for Ops Health Audit $750",
        "scoped SKU cards with DONE · VERIFY bullets",
        "agency retainer intake → CRM row",
        "license inquiry → worker not mailto",
        "cal.com demoted below proof on pricing",
        "ROI calculator widget on /offer",
        "case study PDF gate with email capture",
        "self-serve MSA snippet on /trust",
        "revenue receipt in founder dashboard",
    ],
    "t06-intake-ops": [
        "sandbox-intake.js → sourcea-mvp-intake-v1 worker",
        "MVP submissions in pulse-founder inbox tab",
        "brain chat transcript KV log (founder-only)",
        "Resend notify on every feedback + MVP",
        "intake schema sourcea-site-intake-v1.json",
        "duplicate intake dedupe by email+day",
        "intake status webhook to founder Slack",
        "48h MVP scope lock UI on /start",
        "agency lane intake on case-studies",
        "unified inbox export CSV",
    ],
    "t02-client-ui": [
        "founder-home hero primary = See live receipt per CTA SSOT",
        "remove duplicate pulse script tags on founder-home",
        "data-sa-proof-cta href consistency sitewide",
        "platform portal honest beta layout pass",
        "feedback FAB z-index above Cal overlay",
        "guided tour dismiss persists per session",
        "segment strip on all dist pages via build inject",
        "proof quiz keyboard accessibility",
        "status page live stats refresh interval",
        "error states on pulse-founder auth failure",
    ],
    "t04-deterministic-routing": [
        "segment click → pulse track → correct href E2E",
        "guided prompt once-per-session localStorage key",
        "brain chip messages map to segment tracks",
        "URL utm_segment overrides default lane",
        "returning visitor last-segment hint",
        "VC proof lane skip learn redirect",
        "cursor lane deep-link Forge with query",
        "beginner lane forces /learn before /start",
        "agency lane case-study filter preset",
        "routing decision receipt in pulse events",
    ],
    "t01-live-wiring": [
        "pulse worker route on sourcea.app/api/site/*",
        "sourcea-site-pulse-config-v1.json worker URL",
        "RESEND_API_KEY verified send on feedback",
        "FOUNDER_PULSE_KEY rotation doc in SETUP",
        "KV PULSE_KV backup export cron",
        "brain-chat worker pulse event bridge",
        "mvp-intake worker linked from /start form",
        "public stats embed on /sourcea/status",
        "CORS allow sourcea.app on all site APIs",
        "worker health /api/site/health/v1",
    ],
    "t07-analytics-feedback": [
        "funnel dashboard: segment → proof → intake",
        "top_events alert threshold in founder UI",
        "feedback type filter bug/idea/praise",
        "pageview path normalization /sourcea prefix",
        "cal overlay open/close conversion metric",
        "guided_show completion rate",
        "export 7-day rollup JSON",
        "anonymize PII in public stats",
        "spam feedback rate limit per IP",
        "weekly email digest to founder",
    ],
    "t03-vocabulary": [
        "sourcea-landing-cta-v1.json version bump + changelog",
        "ban Book a demo sitewide grep gate",
        "Talk to a human only on data-sa-book-fallback",
        "technique labels in interact JSON documented",
        "proof_surface copy on all proof CTAs",
        "commercial_intake GOAL·DONE·VERIFY on /start",
        "living_ui label on Forge paths only",
        "segment labels A/B test copy variants",
        "vocabulary validator script in CI",
        "glossary page /sourcea/vocabulary",
    ],
    "t10-e2e-quality": [
        "validate-sourcea-modern-stack-e2e-v1 weekly cron",
        "Playwright proof run happy path",
        "Playwright sandbox submit no mailto",
        "Playwright pulse-founder key gate",
        "broken link crawler on dist/",
        "JSON schema validate all data/*.json",
        "visual regression founder-home screenshot",
        "accessibility axe on /learn",
        "deploy smoke after wrangler pages",
        "score-up registry validate script PASS",
    ],
}

WS_ACTION = {
    "w01-ship": "Ship",
    "w02-prove": "Prove live",
    "w03-wire": "Wire",
    "w04-ui": "Polish UI for",
    "w05-copy": "Rewrite copy for",
    "w06-worker": "Worker endpoint for",
    "w07-deploy": "Deploy",
    "w08-e2e": "E2E gate for",
    "w09-bench": "Bench vs market for",
    "w10-receipt": "Receipt logged for",
}


def phase_for_rank(rank: int) -> str:
    if rank <= 50:
        return "NOW"
    if rank <= 200:
        return "NEXT"
    if rank <= 500:
        return "LATER"
    return "MOONSHOT"


def plan_title(theme_id: str, ws_id: str, ws_label: str, slice_n: int) -> str:
    items = DELIVERABLES[theme_id]
    idx = (WORKSTREAMS.index(next(w for w in WORKSTREAMS if w[0] == ws_id)) + slice_n - 1) % len(items)
    action = WS_ACTION[ws_id]
    item = items[idx]
    return f"{action} {item}"


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
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""# {plan_id} — {title}

**Saved at:** {now}
**Version:** 1 · **Tier:** {tier} · **Phase:** {phase}
**Score dimension:** {theme_label} ({score_now}→{score_target})
**Market analog:** {market}
**Workstream:** {ws_id} · {ws_label}
**Slice:** {slice_n}/10
**SSOT:** `docs/SOURCEA_SITE_SCORE_UP_1000_PLANS_LOCKED_v1.md`

## North star

Raise SourceA site score toward **95+/100** — proof before call · stranger self-serve · deterministic routing.

## Task

{TIER_DEPTH[tier]}

**Deliverable:** {title}

Bounded paths: `SourceA-landing/green-unified/` · `cloud/workers/sourcea-site-pulse-v1/` · `scripts/validate-sourcea-modern-stack-e2e-v1.sh`

## Verify

```bash
cd ~/Desktop/SourceA && bash scripts/validate-sourcea-modern-stack-e2e-v1.sh
curl -sS https://sourcea.app/sourcea/data/sourcea-landing-cta-v1.json | python3 -m json.tool
```

## Closeout

1. `status: done` in `brain-os/plan-registry/sourcea-site-score-up-1000/REGISTRY.json` for `{plan_id}`
2. Note score delta in plan row `score_delta`
3. Deploy proof: live URL or receipt path in commit message

---
agent_tag: AGENT-AUTO-SOURCEA-SITE
trigger: WORK sa-score bounded site score-up
generator: generate_sourcea_site_score_up_1000_plans_v1.py v{GENERATOR_VERSION}
"""


def generate(now: str) -> dict:
    prompts_root = PACK_BASE / "prompts"
    entries: list[dict] = []
    phases: list[dict] = []
    seq = 0

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
            }
        )
        for ws_id, ws_label in WORKSTREAMS:
            for slice_n in range(1, 11):
                seq += 1
                plan_id = f"{PREFIX}-{seq:04d}"
                tier = TIER_FOR_SLICE[slice_n - 1]
                phase = phase_for_rank(seq)
                title = plan_title(theme_id, ws_id, ws_label, slice_n)
                rel = f"prompts/{phase_id}/{ws_id}/slice-{slice_n:02d}.md"
                path = PACK_BASE / rel
                path.parent.mkdir(parents=True, exist_ok=True)
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
                    ),
                    encoding="utf-8",
                )
                entries.append(
                    {
                        "id": plan_id,
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
                        "lane": "sourcea-site",
                        "agent_prompt": f"WORK — {plan_id}: {title}",
                    }
                )

    registry = {
        "schema": "sourcea-site-score-up-1000-registry-v1",
        "schema_version": GENERATOR_VERSION,
        "generated_at": now,
        "repo": "sourcea",
        "repo_label": "SourceA site (sourcea.app)",
        "count": len(entries),
        "grid": "10 score dimensions × 10 workstreams × 10 slices",
        "baseline_score": 76,
        "target_score": 95,
        "external_repo": "~/Desktop/SourceA",
        "law_doc": "docs/SOURCEA_SITE_SCORE_UP_1000_PLANS_LOCKED_v1.md",
        "phases": phases,
        "plans": entries,
    }
    PACK_BASE.mkdir(parents=True, exist_ok=True)
    (PACK_BASE / "REGISTRY.json").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    master = {
        "schema": "sourcea-site-score-up-1000-master-v1",
        "version": "1.0.0",
        "generated_at": now,
        "generator": "scripts/generate_sourcea_site_score_up_1000_plans_v1.py",
        "law_doc": "docs/SOURCEA_SITE_SCORE_UP_1000_PLANS_LOCKED_v1.md",
        "plan_count": 1000,
        "baseline_score": 76,
        "target_score": 95,
        "pack": str(PACK_BASE),
        "phase_law": {
            "NOW": "ranks 1–50 — self-serve proof · polish · commercial · intake",
            "NEXT": "ranks 51–200",
            "LATER": "ranks 201–500",
            "MOONSHOT": "ranks 501–1000",
        },
    }
    master_path = SOURCEA_ROOT / "brain-os" / "plan-registry" / "SOURCEA_SITE_SCORE_UP_1000_MASTER_v1.json"
    master_path.write_text(json.dumps(master, indent=2) + "\n", encoding="utf-8")

    (PACK_BASE / "README_LOCKED_v1.md").write_text(
        f"# SourceA site score-up — 1000 plans\n\n"
        f"Generated: {now}\n\n"
        f"Baseline **76/100** → target **95+** · REGISTRY: `REGISTRY.json`\n",
        encoding="utf-8",
    )
    return {"count": len(entries), "ok": len(entries) == 1000}


def main() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result = generate(now)
    print(json.dumps({"ok": result["ok"], "plan_count": result["count"], "generated_at": now}, indent=2))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
