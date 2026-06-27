#!/usr/bin/env python3
"""Generate 6000 AgentGo/SA4 case-study plans — 3 angles × 2000 (10×10×20 grid).

SSOT: docs/AGENTGO_SA4_CASE_STUDY_6000_PLANS_LOCKED_v1.md
Angles: A factory scale · B dual deploy · C Wil L3 demo
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCEA_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_VERSION = 1
PACK_BASE = SOURCEA_ROOT / "brain-os" / "plan-registry" / "agentgo-case-study-6000"
SLICES_PER_CELL = 20

THEMES = [
    ("t01-case-copy", "Case study narrative copy"),
    ("t02-landing-ship", "Landing ship (sourcea.app)"),
    ("t03-proof-receipts", "Proof & receipts"),
    ("t04-sa4-source", "SA4 / AgentGo source tree"),
    ("t05-geo-trackers", "GEO tracker surfaces"),
    ("t06-research-hub", "Research / guides hub"),
    ("t07-compare-pages", "Compare /  pages"),
    ("t08-dual-deploy", "Dual deploy wiring"),
    ("t09-wil-gate", "Wil ship gate & separation"),
    ("t10-revenue-crm", "Revenue / CRM (SaaS ICP)"),
]

WORKSTREAMS = [
    ("w01-ship", "Ship"),
    ("w02-prove", "Prove"),
    ("w03-sell", "Sell"),
    ("w04-build", "Build"),
    ("w05-operate", "Operate"),
    ("w06-govern", "Govern"),
    ("w07-document", "Document"),
    ("w08-validate", "Validate"),
    ("w09-integrate", "Integrate"),
    ("w10-scale", "Scale"),
]

TIER_FOR_SLICE = (
    ["T0", "T0"]
    + ["T1"] * 3
    + ["T2"] * 7
    + ["T3"] * 8
)

TIER_DEPTH = {
    "T0": "P0 — smallest shippable slice with receipt",
    "T1": "P1 — next sprint outcome",
    "T2": "P2 — harden · validate · document",
    "T3": "P3 — research · defer · compare-only",
}

ANGLES = [
    {
        "key": "cs-a-factory",
        "label": "Angle A — Factory scale",
        "prefix": "ag-a",
        "lane": "sourcea",
        "agent": "AGENT-AUTO-SOURCEA",
        "angle_code": "A",
        "story": "AgentGo GEO factory scale — 1259-page surface · trackers · research · compare",
        "verify": "test -d ~/Desktop/SA4 && test -f ~/Desktop/SA4/index.html",
        "priority_md": "docs/AGENTGO_SA4_CASE_STUDY_6000_PLANS_LOCKED_v1.md",
        "external_repo": "~/Desktop/YA5/SA4",
    },
    {
        "key": "cs-b-dual",
        "label": "Angle B — Dual deploy",
        "prefix": "ag-b",
        "lane": "sourcea",
        "agent": "AGENT-AUTO-SOURCEA",
        "angle_code": "B",
        "story": "Dual desktop deploy — agentrun-app :5180 + SA4 AgentGo :8080 · landing parity",
        "verify": "bash ~/Desktop/SourceA/scripts/validate-sourcea-desktop-landing-v1.sh",
        "priority_md": "docs/AGENTGO_SA4_CASE_STUDY_6000_PLANS_LOCKED_v1.md",
        "external_repo": "~/Desktop/SA4",
    },
    {
        "key": "cs-c-wil",
        "label": "Angle C — Wil L3 demo",
        "prefix": "ag-c",
        "lane": "sourcea",
        "agent": "AGENT-AUTO-SOURCEA",
        "angle_code": "C",
        "story": "Wil L3 portfolio demo — YA5 mirror · AgentGo ≠ SourceA separation · ship gate",
        "verify": "test -f ~/Desktop/YA5/.cursor/governance/TERMINOLOGY_2026.md",
        "priority_md": "docs/AGENTGO_SA4_CASE_STUDY_6000_PLANS_LOCKED_v1.md",
        "external_repo": "~/Desktop/YA5",
    },
]

# NOW-phase concrete tasks (rank 1–30 per angle) — keyed by (angle_key, seq)
NOW_TASKS: dict[tuple[str, int], str] = {
    # Angle A — factory scale
    ("cs-a-factory", 1): "Draft AgentGo case study hero — factory scale headline · 1259 pages · GEO intelligence · not PureFlow clone",
    ("cs-a-factory", 2): "Ship `case-studies/agentgo.html` on green-unified — challenge / what shipped / build chain sections",
    ("cs-a-factory", 3): "Add agentgo.html to commercial copy gate + copy depth gate manifests",
    ("cs-a-factory", 4): "Wire footer + offer page link to AgentGo case study next to PureFlow",
    ("cs-a-factory", 5): "Document SA4 page inventory — trackers · compare · research counts on disk receipt",
    ("cs-a-factory", 6): "Select 10-page public demo subset from SA4 (homepage + 3 trackers + 3 compare + 3 research)",
    ("cs-a-factory", 7): "Case study metrics block — page count · sitemap · ship date · honest localhost caveat",
    ("cs-a-factory", 8): "CRM row — SaaS/marketing ICP prospect for GEO case study outreach",
    ("cs-a-factory", 9): "Outreach template variant — factory scale proof vs local-business PureFlow pitch",
    ("cs-a-factory", 10): "Proof receipt — screenshot or manifest JSON of SA4 structure under ~/.sina/",
    # Angle B — dual deploy
    ("cs-b-dual", 1): "Run deploy_sourcea_desktop_landing_v1.py — sync green-unified to agentrun-app + SA4/sourcea",
    ("cs-b-dual", 2): "Validate validate-sourcea-desktop-landing-v1.sh PASS — both :5180 and :8080 routes",
    ("cs-b-dual", 3): "Case study section B — dual-stack narrative · Agent Run canonical vs AgentGo cinematic",
    ("cs-b-dual", 4): "Document port map in case study — 5180 agentrun · 8080 SA4 · separation from production sourcea.app",
    ("cs-b-dual", 5): "run-recipe.sh step 3 deploy receipt — log paths to ~/.sina/agentgo-dual-deploy-receipt-v1.json",
    ("cs-b-dual", 6): "Compare PureFlow live URL vs desktop deploy proof — two case study proof models",
    ("cs-b-dual", 7): "Hub official links bar — optional SA4 local glance link for founder session",
    ("cs-b-dual", 8): "CRM outreach — agency buyer who cares about desktop demo + screen-share deploy",
    ("cs-b-dual", 9): "Case study CTA — Book proof demo with dual-deploy screen-share script",
    ("cs-b-dual", 10): "Evidence row SOURCEA-PRIORITY — dual deploy case study angle shipped",
    # Angle C — Wil L3
    ("cs-c-wil", 1): "Read YA5 TERMINOLOGY_2026.md — extract Wil vs SourceA vs AgentGo separation lines for case study",
    ("cs-c-wil", 2): "Case study footer disclaimer — AgentGo portfolio lane · not SourceA product · not live billing",
    ("cs-c-wil", 3): "Document Wil ship gate criteria — routes · browser · E2E · legacy zero in case study prose",
    ("cs-c-wil", 4): "Cross-link Wil L3 lane in SOURCEA-PRIORITY §Wil AI — case study as portfolio proof",
    ("cs-c-wil", 5): "SA4/sourcea/index.html separation audit — no AgentGo sign-in claims as production SaaS",
    ("cs-c-wil", 6): "Case study angle C section — mirror audit · crawl pipeline · L3 demo receipt",
    ("cs-c-wil", 7): "Governance row — agentgo_case_study_6000 active in manifest (no SSOT supersede of portfolio 6000)",
    ("cs-c-wil", 8): "CRM — portfolio/strategic buyer pitch using Wil demo + SourceA governance story",
    ("cs-c-wil", 9): "Compare case study #1 PureFlow · #2 AgentGo three-angle index page or offer subsection",
    ("cs-c-wil", 10): "Seal case study law doc AGENTGO_SA4_CASE_STUDY_6000 on disk — validator PASS",
}


def phase_for_rank(rank: int) -> str:
    if rank <= 30:
        return "NOW"
    if rank <= 120:
        return "NEXT"
    if rank <= 400:
        return "LATER"
    return "MOONSHOT"


def receipt_gate_for(angle_key: str, theme_id: str, ws_id: str, slice_n: int) -> str:
    if theme_id == "t02-landing-ship" and ws_id == "w01-ship" and slice_n <= 3:
        return "landing_ship"
    if theme_id == "t03-proof-receipts" and ws_id == "w02-prove" and slice_n <= 2:
        return "proof_pack_sealed"
    if theme_id == "t08-dual-deploy" and angle_key == "cs-b-dual" and slice_n <= 3:
        return "dual_deploy_pass"
    if theme_id == "t09-wil-gate" and angle_key == "cs-c-wil" and slice_n <= 3:
        return "wil_ship_gate"
    if theme_id == "t04-sa4-source" and slice_n <= 2:
        return "agentgo_pages_built"
    if theme_id == "t10-revenue-crm" and ws_id == "w03-sell" and slice_n <= 3:
        return "revenue_outreach"
    gates = [
        "landing_ship",
        "proof_pack_sealed",
        "revenue_outreach",
        "agentgo_pages_built",
        "dual_deploy_pass",
        "wil_ship_gate",
        "none",
    ]
    return gates[(slice_n + len(ws_id) + len(theme_id)) % len(gates)]


def task_text(angle: dict, theme_label: str, ws_label: str, slice_n: int, tier: str, seq: int) -> str:
    override = NOW_TASKS.get((angle["key"], seq))
    if override:
        return override
    return (
        f"{angle['label']} · {theme_label} · {ws_label} · slice {slice_n}/{SLICES_PER_CELL} — "
        f"{TIER_DEPTH[tier]}. {angle['story']}. "
        f"Bounded path only. Receipt on disk before done. "
        f"SA4: ~/Desktop/SA4 · PureFlow ref: case-studies/pureflow.html."
    )


def prompt_md(
    *,
    plan_id: str,
    angle: dict,
    theme_id: str,
    theme_label: str,
    ws_id: str,
    ws_label: str,
    slice_n: int,
    tier: str,
    phase: str,
    task: str,
    receipt_gate: str,
) -> str:
    return f"""# {plan_id} — AgentGo SA4 case study plan

**Version:** 1 · **Tier:** {tier} · **Phase:** {phase}
**Angle:** {angle['angle_code']} · {angle['label']}
**Theme:** {theme_id} · {theme_label}
**Workstream:** {ws_id} · {ws_label}
**Slice:** {slice_n}/{SLICES_PER_CELL} · **Receipt gate:** {receipt_gate}
**SSOT:** `docs/AGENTGO_SA4_CASE_STUDY_6000_PLANS_LOCKED_v1.md`

## Scope

{angle['story']}

## Task

{task}

## Verify

```bash
{angle['verify']}
```

## Closeout

1. `status: done` in REGISTRY.json for `{plan_id}`
2. Evidence row in `brain-os/plan-registry/SOURCEA-PRIORITY.md` §AgentGo case study 6000
3. No cross-lane edits without EDIT ALLOWED
4. Keep AgentGo ≠ SourceA separation in all buyer-facing copy (angle C law)

---
agent_tag: {angle['agent']}
trigger: PLAN WITH NO ASF
generator: generate_agentgo_case_study_6000_plans_v1.py v{GENERATOR_VERSION}
angle: {angle['key']}
"""


def generate_angle(angle: dict, now: str) -> dict:
    pack = PACK_BASE / angle["key"]
    entries: list[dict] = []
    phases: list[dict] = []
    seq = 0

    for theme_id, theme_label in THEMES:
        phase_id = f"phase-{angle['prefix']}-{theme_id}"
        phases.append(
            {
                "id": phase_id,
                "theme": theme_label,
                "description": f"{angle['label']} — {theme_label}",
            }
        )
        for ws_id, ws_label in WORKSTREAMS:
            for slice_n in range(1, SLICES_PER_CELL + 1):
                seq += 1
                plan_id = f"{angle['prefix']}-{seq:04d}"
                tier = TIER_FOR_SLICE[slice_n - 1]
                phase = phase_for_rank(seq)
                receipt_gate = receipt_gate_for(angle["key"], theme_id, ws_id, slice_n)
                task = task_text(angle, theme_label, ws_label, slice_n, tier, seq)
                rel = f"prompts/{phase_id}/{ws_id}/slice-{slice_n:02d}.md"
                path = pack / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                title = task.split("—")[0].strip()[:80] if seq <= 30 else f"{theme_label} · {ws_label} · slice {slice_n}"
                path.write_text(
                    prompt_md(
                        plan_id=plan_id,
                        angle=angle,
                        theme_id=theme_id,
                        theme_label=theme_label,
                        ws_id=ws_id,
                        ws_label=ws_label,
                        slice_n=slice_n,
                        tier=tier,
                        phase=phase,
                        task=task,
                        receipt_gate=receipt_gate,
                    ),
                    encoding="utf-8",
                )
                entries.append(
                    {
                        "id": plan_id,
                        "angle": angle["key"],
                        "angle_code": angle["angle_code"],
                        "angle_label": angle["label"],
                        "theme": theme_id,
                        "theme_label": theme_label,
                        "workstream": ws_id,
                        "workstream_label": ws_label,
                        "slice": slice_n,
                        "tier": tier,
                        "phase": phase,
                        "title": title,
                        "status": "open",
                        "receipt_gate": receipt_gate,
                        "priority_rank": seq,
                        "path": rel,
                        "lane": angle["lane"],
                        "agent_prompt": f"PLAN WITH NO ASF — {plan_id}: {title[:72]}",
                    }
                )

    registry = {
        "schema": "agentgo-case-study-6000-registry-v1",
        "schema_version": GENERATOR_VERSION,
        "generated_at": now,
        "angle": angle["key"],
        "angle_label": angle["label"],
        "count": len(entries),
        "grid": "10 themes × 10 workstreams × 20 slices",
        "external_repo": angle["external_repo"],
        "phases": phases,
        "plans": entries,
    }
    pack.mkdir(parents=True, exist_ok=True)
    (pack / "REGISTRY.json").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    (pack / "README_LOCKED_v1.md").write_text(
        f"# {angle['label']} — 2000 case study plans\n\n"
        f"Generated: {now}\n\n"
        f"REGISTRY: `REGISTRY.json` · Master: `../AGENTGO_CASE_STUDY_6000_MASTER_v1.json`\n",
        encoding="utf-8",
    )
    return {"angle": angle["key"], "label": angle["label"], "count": len(entries), "pack": str(pack)}


def validate_pack(pack: Path) -> list[str]:
    errors: list[str] = []
    reg_path = pack / "REGISTRY.json"
    if not reg_path.is_file():
        return [f"Missing {reg_path}"]
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    if reg.get("count") != 2000 or len(reg.get("plans", [])) != 2000:
        errors.append(f"{pack.name}: count != 2000")
    ids = [p["id"] for p in reg["plans"]]
    if len(ids) != len(set(ids)):
        errors.append(f"{pack.name}: duplicate ids")
    for p in reg["plans"][:3]:
        if not (pack / p["path"]).is_file():
            errors.append(f"Missing sample prompt {p['path']}")
            break
    return errors


def main() -> int:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results = []
    all_errors: list[str] = []

    for angle in ANGLES:
        results.append(generate_angle(angle, now))
        all_errors.extend(validate_pack(PACK_BASE / angle["key"]))

    master = {
        "schema": "agentgo-case-study-6000-master-v1",
        "version": "1.0.0",
        "generated_at": now,
        "generator": "scripts/generate_agentgo_case_study_6000_plans_v1.py",
        "law_doc": "docs/AGENTGO_SA4_CASE_STUDY_6000_PLANS_LOCKED_v1.md",
        "plan_count": 6000,
        "angle_count": 3,
        "grid": "3 angles × 2000 (10 themes × 10 workstreams × 20 slices)",
        "angles": [
            {"code": "A", "key": "cs-a-factory", "label": "Factory scale", "prefix": "ag-a"},
            {"code": "B", "key": "cs-b-dual", "label": "Dual deploy", "prefix": "ag-b"},
            {"code": "C", "key": "cs-c-wil", "label": "Wil L3 demo", "prefix": "ag-c"},
        ],
        "repos": results,
        "phase_law": {
            "NOW": "ranks 1–30 per angle — case study ship · gates · first proof",
            "NEXT": "ranks 31–120",
            "LATER": "ranks 121–400",
            "MOONSHOT": "ranks 401–2000",
        },
        "validation_errors": all_errors,
        "ok": len(all_errors) == 0,
    }
    master_path = SOURCEA_ROOT / "brain-os" / "plan-registry" / "AGENTGO_CASE_STUDY_6000_MASTER_v1.json"
    master_path.write_text(json.dumps(master, indent=2) + "\n", encoding="utf-8")

    manifest_path = SOURCEA_ROOT / "data" / "agentgo-case-study-6000-manifest-v1.json"
    manifest_path.write_text(json.dumps(master, indent=2) + "\n", encoding="utf-8")

    out = {"ok": len(all_errors) == 0, "generated_at": now, "plan_count": 6000, "angles": results}
    if all_errors:
        out["errors"] = all_errors[:30]
    print(json.dumps(out, indent=2))
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
