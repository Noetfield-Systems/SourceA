#!/usr/bin/env python3
"""Generate 6000 next plans — 6 portfolio repos × 1000 (10×10×10 grid).

SSOT: docs/PORTFOLIO_NEXT_6000_PLANS_LOCKED_v1.md
Anchors: Revenue Engine · Noetfield 613 · Runtime hybrid · Planning Authority Card
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCEA_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_VERSION = 1
PACK_BASE = SOURCEA_ROOT / "brain-os" / "plan-registry" / "portfolio-next-6000"

THEMES = [
    ("t01-revenue", "Revenue & outreach"),
    ("t02-proof", "Proof & receipts"),
    ("t03-landing", "Landing & web"),
    ("t04-runtime", "Factory runtime"),
    ("t05-intelligence", "Noetfield Intelligence 613"),
    ("t06-compliance", "MSB & compliance"),
    ("t07-civic", "Civic proof lab"),
    ("t08-saas", "Agentic SaaS"),
    ("t09-hub", "Hub & control plane"),
    ("t10-cloud", "Cloud & integrate"),
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

TIER_FOR_SLICE = ["T0", "T0", "T1", "T1", "T2", "T2", "T2", "T3", "T3", "T3"]

REPOS = [
    {
        "key": "sourcea",
        "label": "SourceA",
        "prefix": "sa-next",
        "lane": "sourcea",
        "agent": "AGENT-AUTO-SOURCEA",
        "priority_md": "brain-os/plan-registry/SOURCEA-PRIORITY.md",
        "verify": "cd ~/Desktop/SourceA && python3 scripts/sourcea_revenue_engine_crm_v1.py summary --json",
        "scope": "Revenue Engine · Proof Pack · landing · factory-runtime-spike",
        "external_repo": "~/Desktop/SourceA",
    },
    {
        "key": "witnessbc",
        "label": "WitnessBC",
        "prefix": "wb-next",
        "lane": "witnessbc",
        "agent": "AGENT-AUTO-WITNESSBC",
        "priority_md": "witnessbc-site/content/pricing.html",
        "verify": "bash ~/Desktop/SourceA/scripts/validate-witnessbc--1000-v1.sh",
        "scope": "witnessbc.com civic agentic install — not witness.ai",
        "external_repo": "~/Desktop/SourceA/witnessbc-site",
    },
    {
        "key": "noetfield",
        "label": "Noetfield",
        "prefix": "nf-next",
        "lane": "noetfield",
        "agent": "AGENT-AUTO-NOETFIELD",
        "priority_md": "docs/NOETFIELD_INTELLIGENCE_613_PLAN_LOCKED_v1.md",
        "verify": "test -f ~/Desktop/SourceA/docs/NOETFIELD_INTELLIGENCE_613_PLAN_LOCKED_v1.md",
        "scope": "Intelligence 613 · Copilot governance upsell · Trust Brief",
        "external_repo": "~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield",
    },
    {
        "key": "trustfield",
        "label": "TrustField",
        "prefix": "tf-next",
        "lane": "trustfield",
        "agent": "AGENT-AUTO-TRUSTFIELD",
        "priority_md": "prompts/future-plans-1000.json",
        "verify": "cd ~/Desktop/TrustField\\ Technologies && npm test",
        "scope": "FINTRAC MSB programs — payment execution only",
        "external_repo": "~/Desktop/TrustField Technologies",
    },
    {
        "key": "virlux",
        "label": "VIRLUX",
        "prefix": "vx-next",
        "lane": "virlux",
        "agent": "Auto-VIRLUX-Delivery",
        "priority_md": "os/plan-library/VIRLUX-PRIORITY.md",
        "verify": "cd ~/Desktop/VIRLUX && npm run verify:live",
        "scope": "Agentic factory SaaS — no payment/FINTRAC copy",
        "external_repo": "~/Desktop/VIRLUX",
    },
    {
        "key": "mono",
        "label": "SinaaiMonoRepo",
        "prefix": "mx-next",
        "lane": "mono",
        "agent": "AGENT-AUTO-MONO",
        "priority_md": "os/plan-library/mono-1000/REGISTRY.json",
        "verify": "test -f ~/Desktop/Noetfield/SinaaiMonoRepo/os/plan-library/mono-1000/REGISTRY.json",
        "scope": "Mono portfolio spine — cross-lane receipts only",
        "external_repo": "~/Desktop/Noetfield/SinaaiMonoRepo",
    },
]

TASK_TEMPLATE = (
    "{repo_label} · {theme_label} · {ws_label} · slice {slice_n}/10 — "
    "{tier_depth}. Bounded path only. Receipt on disk before done. "
    "Parent: {scope}. Priority doc: `{priority_md}`."
)

TIER_DEPTH = {
    "T0": "P0 — smallest shippable slice with receipt",
    "T1": "P1 — next sprint outcome",
    "T2": "P2 — harden · validate · document",
    "T3": "P3 — research · defer · compare-only",
}

RECEIPT_GATES = [
    "client_proof_pack",
    "revenue_outreach",
    "nw1_w3",
    "proof_pack_sealed",
    "landing_ship",
    "runtime_spike_pass",
    "none",
]


def phase_for_rank(rank: int) -> str:
    if rank <= 30:
        return "NOW"
    if rank <= 120:
        return "NEXT"
    if rank <= 400:
        return "LATER"
    return "MOONSHOT"


def receipt_gate_for(repo_key: str, theme_id: str, ws_id: str, slice_n: int) -> str:
    if repo_key == "sourcea" and theme_id == "t01-revenue" and slice_n <= 3:
        return "revenue_outreach"
    if repo_key == "sourcea" and theme_id == "t02-proof" and slice_n <= 2:
        return "client_proof_pack"
    if repo_key == "noetfield" and theme_id == "t05-intelligence" and slice_n <= 3:
        return "nw1_w3"
    if theme_id == "t02-proof" and ws_id == "w02-prove":
        return "proof_pack_sealed"
    if theme_id == "t04-runtime" and ws_id == "w08-validate":
        return "runtime_spike_pass"
    if theme_id == "t03-landing" and ws_id == "w01-ship":
        return "landing_ship"
    return RECEIPT_GATES[(slice_n + len(ws_id)) % len(RECEIPT_GATES)]


def prompt_md(
    *,
    plan_id: str,
    repo: dict,
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
    return f"""# {plan_id} — {repo['label']} next plan

**Version:** 1 · **Tier:** {tier} · **Phase:** {phase}
**Theme:** {theme_id} · {theme_label}
**Workstream:** {ws_id} · {ws_label}
**Slice:** {slice_n}/10 · **Receipt gate:** {receipt_gate}
**SSOT:** `docs/PORTFOLIO_NEXT_6000_PLANS_LOCKED_v1.md`

## Scope

{repo['scope']}

## Task

{task}

## Verify

```bash
{repo['verify']}
```

## Closeout

1. `status: done` in REGISTRY.json for `{plan_id}`
2. Evidence row in `{repo['priority_md']}`
3. No cross-lane edits without EDIT ALLOWED

---
agent_tag: {repo['agent']}
trigger: PLAN WITH NO ASF
generator: generate_portfolio_next_6000_plans_v1.py v{GENERATOR_VERSION}
"""


def generate_repo(repo: dict, now: str) -> dict:
    pack = PACK_BASE / repo["key"]
    prompts_root = pack / "prompts"
    entries: list[dict] = []
    phases: list[dict] = []
    seq = 0

    for t_idx, (theme_id, theme_label) in enumerate(THEMES):
        phase_id = f"phase-{repo['prefix']}-{theme_id}"
        phases.append(
            {
                "id": phase_id,
                "theme": theme_label,
                "description": f"{repo['label']} — {theme_label} next plans",
            }
        )
        for ws_id, ws_label in WORKSTREAMS:
            for slice_n in range(1, 11):
                seq += 1
                plan_id = f"{repo['prefix']}-{seq:04d}"
                tier = TIER_FOR_SLICE[slice_n - 1]
                rank = seq if repo["key"] == "sourcea" else seq + (REPOS.index(repo) * 1000)
                phase = phase_for_rank(seq)
                receipt_gate = receipt_gate_for(repo["key"], theme_id, ws_id, slice_n)
                task = TASK_TEMPLATE.format(
                    repo_label=repo["label"],
                    theme_label=theme_label,
                    ws_label=ws_label,
                    slice_n=slice_n,
                    tier_depth=TIER_DEPTH[tier],
                    scope=repo["scope"],
                    priority_md=repo["priority_md"],
                )
                rel = f"prompts/{phase_id}/{ws_id}/slice-{slice_n:02d}.md"
                path = pack / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    prompt_md(
                        plan_id=plan_id,
                        repo=repo,
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
                        "theme": theme_id,
                        "theme_label": theme_label,
                        "workstream": ws_id,
                        "workstream_label": ws_label,
                        "slice": slice_n,
                        "tier": tier,
                        "phase": phase,
                        "title": f"{theme_label} · {ws_label} · slice {slice_n}",
                        "status": "open",
                        "receipt_gate": receipt_gate,
                        "priority_rank": seq,
                        "path": rel,
                        "lane": repo["lane"],
                        "agent_prompt": f"PLAN WITH NO ASF — {plan_id}: {theme_label} · {ws_label} · slice {slice_n}",
                    }
                )

    registry = {
        "schema": "portfolio-next-6000-registry-v1",
        "schema_version": GENERATOR_VERSION,
        "generated_at": now,
        "repo": repo["key"],
        "repo_label": repo["label"],
        "count": len(entries),
        "grid": "10 themes × 10 workstreams × 10 slices",
        "external_repo": repo["external_repo"],
        "phases": phases,
        "plans": entries,
    }
    pack.mkdir(parents=True, exist_ok=True)
    (pack / "REGISTRY.json").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    (pack / "README_LOCKED_v1.md").write_text(
        f"# {repo['label']} — next 1000 plans\n\n"
        f"Generated: {now}\n\n"
        f"REGISTRY: `REGISTRY.json` · Master: `../PORTFOLIO_NEXT_6000_MASTER_v1.json`\n",
        encoding="utf-8",
    )
    return {"repo": repo["key"], "label": repo["label"], "count": len(entries), "pack": str(pack)}


def validate_pack(pack: Path) -> list[str]:
    errors: list[str] = []
    reg_path = pack / "REGISTRY.json"
    if not reg_path.is_file():
        return [f"Missing {reg_path}"]
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    if reg.get("count") != 1000 or len(reg.get("plans", [])) != 1000:
        errors.append(f"{pack.name}: count != 1000")
    ids = [p["id"] for p in reg["plans"]]
    if len(ids) != len(set(ids)):
        errors.append(f"{pack.name}: duplicate ids")
    for p in reg["plans"][:5]:
        if not (pack / p["path"]).is_file():
            errors.append(f"Missing sample prompt {p['path']}")
            break
    return errors


def main() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results = []
    all_errors: list[str] = []
    for repo in REPOS:
        results.append(generate_repo(repo, now))
        all_errors.extend(validate_pack(PACK_BASE / repo["key"]))

    master = {
        "schema": "portfolio-next-6000-master-v1",
        "version": "1.0.0",
        "generated_at": now,
        "generator": "scripts/generate_portfolio_next_6000_plans_v1.py",
        "law_doc": "docs/PORTFOLIO_NEXT_6000_PLANS_LOCKED_v1.md",
        "plan_count": 6000,
        "repo_count": 6,
        "grid": "6 repos × 1000 (10 themes × 10 workstreams × 10 slices)",
        "repos": results,
        "phase_law": {
            "NOW": "ranks 1–30 per repo — revenue · proof · ship",
            "NEXT": "ranks 31–120",
            "LATER": "ranks 121–400",
            "MOONSHOT": "ranks 401–1000",
        },
        "validation_errors": all_errors,
        "ok": len(all_errors) == 0,
    }
    master_path = SOURCEA_ROOT / "brain-os" / "plan-registry" / "PORTFOLIO_NEXT_6000_MASTER_v1.json"
    master_path.write_text(json.dumps(master, indent=2) + "\n", encoding="utf-8")

    manifest_path = SOURCEA_ROOT / "data" / "portfolio-next-6000-manifest-v1.json"
    manifest_path.write_text(json.dumps(master, indent=2) + "\n", encoding="utf-8")

    out = {"ok": len(all_errors) == 0, "generated_at": now, "plan_count": 6000, "repos": results}
    if all_errors:
        out["errors"] = all_errors[:30]
        out["error_count"] = len(all_errors)
    print(json.dumps(out, indent=2))
    sys.exit(1 if all_errors else 0)


if __name__ == "__main__":
    main()
