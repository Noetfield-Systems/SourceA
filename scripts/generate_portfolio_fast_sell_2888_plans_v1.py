#!/usr/bin/env python3
"""Generate 2888 fast-sell plans — 8 lanes × 361 (19 wedges × 19 actions).

Completes portfolio master 8888 = 6000 (portfolio-next-6000) + 2888 (this pack).
SSOT: docs/PORTFOLIO_TWO_TIER__PRO_ANALYSIS_LOCKED_v1.md
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCEA_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_VERSION = 1
PACK_BASE = SOURCEA_ROOT / "brain-os" / "plan-registry" / "portfolio-fast-sell-2888"
PLANS_PER_LANE = 361  # 19 × 19
LANE_COUNT = 8
TOTAL = PLANS_PER_LANE * LANE_COUNT

WEDGES = [
    ("w01-diagnostic", "Tier-1 diagnostic / audit wedge"),
    ("w02-implementation", "Tier-2 build & integrate"),
    ("w03-retainer", "Monthly ops retainer"),
    ("w04-freemium-pro", "Freemium → Pro SaaS packaging"),
    ("w05-hybrid-usage", "Base fee + usage overage"),
    ("w06-outcome", "Per-outcome pricing (ticket/meeting/resolution)"),
    ("w07-vertical", "Vertical wedge (diaspora · RCIC · broker · trades)"),
    ("w08-landing", "Landing + pricing page ship"),
    ("w09-demo", "Live demo URL + proof"),
    ("w10-outreach", "Cold outreach + book meeting"),
    ("w11-case-study", "Client case study on disk"),
    ("w12-receipt-pdf", "Receipt / Proof Pack PDF"),
    ("w13-hub-action", "Hub one-tap Action"),
    ("w14-cloud-forge", "Cloud forge run + Supabase row"),
    ("w15-", "Study one market pattern"),
    ("w16-onboard", "Client onboard checklist"),
    ("w17-upsell", "Tier-1 → Tier-2 upsell motion"),
    ("w18-referral", "Partner / accountant channel"),
    ("w19-scale", "Repeatable playbook + template"),
]

ACTIONS = [
    ("a01-research", "Research comp pricing page"),
    ("a02-copy", "Write buyer-facing copy"),
    ("a03-wire", "Wire SKU on landing"),
    ("a04-crm", "Add CRM / pipeline row"),
    ("a05-email", "Outreach email draft"),
    ("a06-call", "Discovery call script"),
    ("a07-proposal", "1-page proposal PDF"),
    ("a08-contract", "SOW / order form"),
    ("a09-build", "Ship smallest build slice"),
    ("a10-verify", "Verify PASS receipt"),
    ("a11-seal", "Seal Proof Pack"),
    ("a12-post", "LinkedIn proof post"),
    ("a13-form", "Founder decision form row"),
    ("a14-metrics", "Log W3 / NW economic signal"),
    ("a15-retain", "Retainer renewal touch"),
    ("a16-template", "Save reusable template"),
    ("a17-train", "Client handoff doc"),
    ("a18-nps", "Ask for referral"),
    ("a19-archive", "Archive lesson to knowledge-library"),
]

LANES = [
    {
        "key": "sourcea",
        "label": "SourceA",
        "prefix": "fs-sa",
        "lane": "sourcea",
        "agent": "AGENT-AUTO-SOURCEA",
        "comp_anchor": "Trigger.dev · Langfuse",
        "tier1": "Asset B diagnostic $3K slice",
        "tier2": "DFY $3–10K + retainer",
        "verify": "python3 ~/Desktop/SourceA/scripts/sourcea_revenue_engine_crm_v1.py summary --json",
        "external_repo": "~/Desktop/SourceA",
    },
    {
        "key": "witnessbc",
        "label": "WitnessBC",
        "prefix": "fs-wb",
        "lane": "witnessbc",
        "agent": "AGENT-AUTO-WITNESSBC",
        "comp_anchor": "LowerPlane · Delve",
        "tier1": "Public proof page pilot",
        "tier2": "Civic annual + audit export",
        "verify": "curl -sf https://witnessbc.com/health || test -f ~/Desktop/SourceA/witnessbc-site/content/pricing.html",
        "external_repo": "~/Desktop/SourceA/witnessbc-site",
    },
    {
        "key": "noetfield",
        "label": "Noetfield",
        "prefix": "fs-nf",
        "lane": "noetfield",
        "agent": "AGENT-AUTO-NOETFIELD",
        "comp_anchor": "Pickaxe agency · Vanta scan",
        "tier1": "Intelligence diagnostic $2.5–5K",
        "tier2": "Build $8–25K + retainer",
        "verify": "test -f ~/Desktop/SourceA/docs/NOETFIELD_INTELLIGENCE_613_PLAN_LOCKED_v1.md",
        "external_repo": "~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield",
    },
    {
        "key": "trustfield",
        "label": "TrustField",
        "prefix": "fs-tf",
        "lane": "trustfield",
        "agent": "AGENT-AUTO-TRUSTFIELD",
        "comp_anchor": "Wise Business · FINTRAC vendors",
        "tier1": "FINTRAC readiness scan",
        "tier2": "MSB program + settlement",
        "verify": "test -d ~/Desktop/TrustField\\ Technologies",
        "external_repo": "~/Desktop/TrustField Technologies",
    },
    {
        "key": "virlux",
        "label": "VIRLUX",
        "prefix": "fs-vx",
        "lane": "virlux",
        "agent": "Auto-VIRLUX-Delivery",
        "comp_anchor": "Windmill · Activepieces",
        "tier1": "One factory recipe demo",
        "tier2": "Team + usage tier",
        "verify": "test -d ~/Desktop/VIRLUX",
        "external_repo": "~/Desktop/VIRLUX",
    },
    {
        "key": "mono",
        "label": "SinaaiMonoRepo",
        "prefix": "fs-mx",
        "lane": "mono",
        "agent": "AGENT-AUTO-MONO",
        "comp_anchor": "PLG demo products",
        "tier1": "Live :8000 demo URL",
        "tier2": "White-label spine",
        "verify": "test -f ~/Desktop/Noetfield/SinaaiMonoRepo/os/plan-library/mono-1000/REGISTRY.json",
        "external_repo": "~/Desktop/Noetfield/SinaaiMonoRepo",
    },
    {
        "key": "agency-b",
        "label": "SourceA Agency Asset B",
        "prefix": "fs-ab",
        "lane": "sourcea",
        "agent": "AGENT-AUTO-SOURCEA",
        "comp_anchor": "Pickaxe 3-tier agency",
        "tier1": "Workflow audit $1.5–3K",
        "tier2": "Build + $1–5K/mo optimize",
        "verify": "test -f ~/Desktop/SourceA/brain-os/law/SOURCEA_ASSET_B_GOVERNED_AGENTIC_AUTOMATION_LOCKED_v1.md",
        "external_repo": "~/Desktop/SourceA",
    },
    {
        "key": "gtm-sku",
        "label": "Vertical GTM SKUs",
        "prefix": "fs-gt",
        "lane": "portfolio",
        "agent": "AGENT-AUTO-SOURCEA",
        "comp_anchor": "11x · vertical SaaS",
        "tier1": "$99–199/mo self-serve",
        "tier2": "$499/mo + onboarding",
        "verify": "test -f ~/Desktop/SourceA/docs/PORTFOLIO_TWO_TIER__PRO_ANALYSIS_LOCKED_v1.md",
        "external_repo": "~/Desktop/SourceA",
    },
]

TIER_FOR_ACTION = ["T0", "T0", "T1", "T1", "T1", "T2", "T2", "T2", "T1", "T0", "T1", "T1", "T2", "T1", "T2", "T3", "T2", "T1", "T3"]


def phase_for_seq(seq: int) -> str:
    if seq <= 40:
        return "NOW"
    if seq <= 120:
        return "NEXT"
    if seq <= 240:
        return "LATER"
    return "MOONSHOT"


def prompt_md(
    *,
    plan_id: str,
    lane: dict,
    wedge_id: str,
    wedge_label: str,
    act_id: str,
    act_label: str,
    tier: str,
    phase: str,
) -> str:
    return f"""# {plan_id} — Fast-sell plan

**Version:** 1 · **Tier:** {tier} · **Phase:** {phase}
**Lane:** {lane['label']} · **Wedge:** {wedge_id} · {wedge_label}
**Action:** {act_id} · {act_label}
**Comp anchor:** {lane['comp_anchor']}
**Tier 1:** {lane['tier1']}
**Tier 2:** {lane['tier2']}
**SSOT:** `docs/PORTFOLIO_TWO_TIER__PRO_ANALYSIS_LOCKED_v1.md`

## Task

Fast-sell: {lane['label']} · {wedge_label} · {act_label}. Ship smallest slice that moves a buyer toward **{lane['tier1']}** with a path to **{lane['tier2']}**. Receipt on disk before done.

## Verify

```bash
{lane['verify']}
```

## Closeout

1. `status: done` in REGISTRY.json for `{plan_id}`
2. Log economic signal if outreach closed (W3 / NW)
3. Bounded path only — no cross-lane without EDIT ALLOWED

---
agent_tag: {lane['agent']}
trigger: FAST SELL · PLAN WITH NO ASF
generator: generate_portfolio_fast_sell_2888_plans_v1.py v{GENERATOR_VERSION}
"""


def generate_lane(lane: dict, now: str) -> dict:
    pack = PACK_BASE / lane["key"]
    entries: list[dict] = []
    seq = 0
    for wedge_id, wedge_label in WEDGES:
        phase_dir = f"phase-{lane['prefix']}-{wedge_id}"
        for act_idx, (act_id, act_label) in enumerate(ACTIONS):
            seq += 1
            plan_id = f"{lane['prefix']}-{seq:04d}"
            tier = TIER_FOR_ACTION[act_idx]
            phase = phase_for_seq(seq)
            rel = f"prompts/{phase_dir}/{act_id}.md"
            path = pack / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                prompt_md(
                    plan_id=plan_id,
                    lane=lane,
                    wedge_id=wedge_id,
                    wedge_label=wedge_label,
                    act_id=act_id,
                    act_label=act_label,
                    tier=tier,
                    phase=phase,
                ),
                encoding="utf-8",
            )
            entries.append(
                {
                    "id": plan_id,
                    "wedge": wedge_id,
                    "wedge_label": wedge_label,
                    "action": act_id,
                    "action_label": act_label,
                    "tier": tier,
                    "phase": phase,
                    "title": f"{wedge_label} · {act_label}",
                    "status": "open",
                    "comp_anchor": lane["comp_anchor"],
                    "tier1_sku": lane["tier1"],
                    "tier2_sku": lane["tier2"],
                    "priority_rank": seq,
                    "path": rel,
                    "lane": lane["lane"],
                    "agent_prompt": f"FAST SELL — {plan_id}: {wedge_label} · {act_label}",
                }
            )

    registry = {
        "schema": "portfolio-fast-sell-2888-registry-v1",
        "schema_version": GENERATOR_VERSION,
        "generated_at": now,
        "repo": lane["key"],
        "repo_label": lane["label"],
        "count": len(entries),
        "grid": "19 wedges × 19 actions = 361",
        "external_repo": lane["external_repo"],
        "comp_anchor": lane["comp_anchor"],
        "plans": entries,
    }
    pack.mkdir(parents=True, exist_ok=True)
    (pack / "REGISTRY.json").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return {
        "lane": lane["key"],
        "label": lane["label"],
        "count": len(entries),
        "pack": str(pack),
    }


def build_8888_master(now: str, lane_results: list[dict], errors: list[str]) -> None:
    next_manifest = SOURCEA_ROOT / "data" / "portfolio-next-6000-manifest-v1.json"
    next_count = 6000
    if next_manifest.is_file():
        next_count = int(json.loads(next_manifest.read_text()).get("plan_count") or 6000)

    master = {
        "schema": "portfolio-8888-master-manifest-v1",
        "version": "1.0.0",
        "generated_at": now,
        "law_doc": "docs/PORTFOLIO_TWO_TIER__PRO_ANALYSIS_LOCKED_v1.md",
        "analysis_doc": "docs/PORTFOLIO_TWO_TIER__PRO_ANALYSIS_LOCKED_v1.md",
        "plan_count": next_count + TOTAL,
        "breakdown": {
            "portfolio_next_6000": next_count,
            "portfolio_fast_sell_2888": TOTAL,
        },
        "fast_sell_generator": "scripts/generate_portfolio_fast_sell_2888_plans_v1.py",
        "next_generator": "scripts/generate_portfolio_next_6000_plans_v1.py",
        "lanes": lane_results,
        "validation_errors": errors,
        "ok": len(errors) == 0,
    }
    out = SOURCEA_ROOT / "data" / "portfolio-8888-master-manifest-v1.json"
    out.write_text(json.dumps(master, indent=2) + "\n", encoding="utf-8")
    reg = SOURCEA_ROOT / "brain-os" / "plan-registry" / "PORTFOLIO_8888_MASTER_v1.json"
    reg.write_text(json.dumps(master, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results: list[dict] = []
    errors: list[str] = []
    for lane in LANES:
        results.append(generate_lane(lane, now))
        reg = PACK_BASE / lane["key"] / "REGISTRY.json"
        doc = json.loads(reg.read_text())
        if doc.get("count") != PLANS_PER_LANE:
            errors.append(f"{lane['key']}: count {doc.get('count')} != {PLANS_PER_LANE}")

    build_8888_master(now, results, errors)
    out = {
        "ok": len(errors) == 0,
        "generated_at": now,
        "fast_sell_count": TOTAL,
        "master_total": 6000 + TOTAL,
        "lanes": results,
    }
    if errors:
        out["errors"] = errors
    print(json.dumps(out, indent=2))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
