#!/usr/bin/env python3
"""Merge UP-888 registry into portfolio-next-6000 SourceA pack (canonical supersession).

SSOT: docs/PORTFOLIO_UPGRADE_PLANS_CANONICAL_LOCKED_v1.md
Law: docs/PORTFOLIO_NEXT_6000_PLANS_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCEA_ROOT = Path(__file__).resolve().parents[1]
UP_PATH = SOURCEA_ROOT / "brain-os/roadmap/SOURCEA_UPGRADE_PLANS_888_REGISTRY_v1.json"
SA_REG = SOURCEA_ROOT / "brain-os/plan-registry/portfolio-next-6000/sourcea/REGISTRY.json"
SA_PACK = SA_REG.parent
MAPPING_PATH = SOURCEA_ROOT / "data/upgrade-888-to-sa-next-mapping-v1.json"
MERGER_VERSION = 1

CATEGORY_THEME = {
    "REV": "t01-revenue",
    "WEB": "t03-landing",
    "PRF": "t02-proof",
    "CU": "t09-hub",
    "HUB": "t09-hub",
    "CLD": "t10-cloud",
    "INT": "t10-cloud",
    "OBS": "t10-cloud",
    "GOV": "t06-compliance",
    "ENT": "t06-compliance",
    "SAS": "t08-saas",
    "MED": "t03-landing",
    "LNG": "t10-cloud",
}

GATE_STRICTNESS = {
    "client_proof_pack": 5,
    "revenue_outreach": 4,
    "nw1_w3": 4,
    "proof_pack_sealed": 3,
    "landing_ship": 2,
    "runtime_spike_pass": 2,
    "none": 0,
    "enterprise_signal": 1,
    "design_partner": 1,
    "t1_client": 5,
}

SLICE_SUFFIX = re.compile(r"\s*·\s*slice\s+\d+\s*$", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _expand(path: str) -> Path:
    return Path(path.replace("~", str(Path.home())))


def clean_title(title: str) -> str:
    return SLICE_SUFFIX.sub("", title).strip()


def pick_receipt_gate(sa_gate: str, up_gate: str) -> str:
    sa_score = GATE_STRICTNESS.get(sa_gate, 1)
    up_score = GATE_STRICTNESS.get(up_gate, 1)
    return up_gate if up_score >= sa_score else sa_gate


def prompt_md(
    *,
    plan: dict,
    up: dict,
    title: str,
    receipt_gate: str,
) -> str:
    plan_id = plan["id"]
    legacy = up["id"]
    return f"""# {plan_id} — SourceA next plan

**Version:** 1 · **Tier:** {plan['tier']} · **Phase:** {plan['phase']}
**Theme:** {plan['theme']} · {plan['theme_label']}
**Workstream:** {plan['workstream']} · {plan['workstream_label']}
**Slice:** {plan['slice']}/10 · **Receipt gate:** {receipt_gate}
**Legacy upgrade:** {legacy} ({up['category']} · {up['category_name']})
**SSOT:** `docs/PORTFOLIO_UPGRADE_PLANS_CANONICAL_LOCKED_v1.md`

## Scope

Revenue Engine · Proof Pack · landing · factory-runtime-spike

## Task

**{title}** — {up['category_name']} ({up['category']}).

{plan['theme_label']} · {plan['workstream_label']} · slice {plan['slice']}/10.
Bounded path only. Receipt on disk before done.
Parent: Revenue Engine · Proof Pack · landing · factory-runtime-spike.
Priority doc: `brain-os/plan-registry/SOURCEA-PRIORITY.md`.

## Verify

```bash
cd ~/Desktop/SourceA && python3 scripts/sourcea_revenue_engine_crm_v1.py summary --json
```

## Closeout

1. `status: done` in REGISTRY.json for `{plan_id}`
2. Evidence row in `brain-os/plan-registry/SOURCEA-PRIORITY.md`
3. No cross-lane edits without EDIT ALLOWED

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: merge_upgrade_888_into_portfolio_next_v1.py v{MERGER_VERSION}
legacy_upgrade_id: {legacy}
"""


def load_receipt_flags() -> dict[str, bool]:
    flags: dict[str, bool] = {
        "proof_pack_sealed": False,
        "revenue_outreach": False,
        "landing_ship": False,
        "runtime_spike_pass": False,
    }

    proof = _expand("~/.sina/chat-unify-proof-pack-v1.json")
    if proof.is_file():
        try:
            row = json.loads(proof.read_text(encoding="utf-8"))
            flags["proof_pack_sealed"] = bool(row.get("ok") or row.get("sealed") or row.get("verdict") == "PASS")
        except (json.JSONDecodeError, OSError):
            pass

    crm_runtime = _expand("~/.sina/sourcea-revenue-engine-crm-v1.json")
    crm_seed = SOURCEA_ROOT / "data/sourcea-revenue-engine-crm-pipeline-v1.json"
    for crm_path in (crm_runtime, crm_seed):
        if not crm_path.is_file():
            continue
        try:
            crm = json.loads(crm_path.read_text(encoding="utf-8"))
            contacts = crm.get("contacts") or crm.get("pipeline") or []
            stages = {"outreach_sent", "conversation", "proposal", "paid", "won"}
            if any((c.get("stage") in stages) for c in contacts):
                flags["revenue_outreach"] = True
                break
        except (json.JSONDecodeError, OSError):
            pass

    landing = SOURCEA_ROOT / "SourceA-landing/green-unified"
    offer = landing / "offer.html"
    pureflow = landing / "case-studies/pureflow.html"
    flags["landing_ship"] = offer.is_file() and pureflow.is_file()

    spike = SOURCEA_ROOT / "apps/factory-runtime-spike/factory_runtime_spike/dry_run_v1.py"
    if spike.is_file():
        try:
            proc = subprocess.run(
                [sys.executable, str(spike), "--fixture", "pureflow", "--json"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(SOURCEA_ROOT),
            )
            if proc.returncode == 0:
                row = json.loads(proc.stdout)
                flags["runtime_spike_pass"] = bool(row.get("ok"))
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
            pass

    return flags


def gate_satisfied(gate: str, flags: dict[str, bool]) -> bool:
    if gate in flags:
        return flags[gate]
    if gate == "proof_pack_sealed":
        return flags.get("proof_pack_sealed", False)
    return False


def merge(*, bootstrap: bool = True) -> dict:
    if not UP_PATH.is_file():
        raise SystemExit(f"Missing {UP_PATH}")
    if not SA_REG.is_file():
        raise SystemExit(f"Missing {SA_REG}")

    up_reg = json.loads(UP_PATH.read_text(encoding="utf-8"))
    sa_reg = json.loads(SA_REG.read_text(encoding="utf-8"))
    up_plans = {p["priority_rank"]: p for p in up_reg["plans"]}
    sa_by_rank = {p["priority_rank"]: p for p in sa_reg["plans"]}

    mapping_entries: list[dict] = []
    merged = 0
    now = _now()

    for rank in range(1, 889):
        up = up_plans.get(rank)
        sa = sa_by_rank.get(rank)
        if not up or not sa:
            continue

        title = clean_title(up["title"])
        receipt_gate = pick_receipt_gate(sa.get("receipt_gate", "none"), up.get("receipt_gate", "none"))

        sa["legacy_upgrade_id"] = up["id"]
        sa["legacy_category"] = up["category"]
        sa["legacy_category_name"] = up["category_name"]
        sa["title"] = title
        sa["receipt_gate"] = receipt_gate
        sa["agent_prompt"] = f"PLAN WITH NO ASF — {sa['id']}: {title} (legacy {up['id']})"

        prompt_path = SA_PACK / sa["path"]
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(
            prompt_md(plan=sa, up=up, title=title, receipt_gate=receipt_gate),
            encoding="utf-8",
        )

        mapping_entries.append(
            {
                "up_id": up["id"],
                "sa_next_id": sa["id"],
                "category": up["category"],
                "category_theme": CATEGORY_THEME.get(up["category"], sa["theme"]),
                "theme": sa["theme"],
                "phase": sa["phase"],
                "receipt_gate": receipt_gate,
                "title": title,
            }
        )
        merged += 1

    bootstrapped = 0
    if bootstrap:
        flags = load_receipt_flags()
        for plan in sa_reg["plans"]:
            if plan.get("status") == "done":
                continue
            gate = plan.get("receipt_gate", "none")
            if gate != "none" and gate_satisfied(gate, flags):
                plan["status"] = "done"
                plan["closed_at"] = now
                plan["close_reason"] = f"receipt_bootstrap:{gate}"
                bootstrapped += 1
            elif plan.get("legacy_upgrade_id") == "UP-0002" and flags.get("proof_pack_sealed"):
                plan["status"] = "done"
                plan["closed_at"] = now
                plan["close_reason"] = "receipt_bootstrap:proof_pack_sealed"
                bootstrapped += 1

    sa_reg["merged_at"] = now
    sa_reg["merge_source"] = "scripts/merge_upgrade_888_into_portfolio_next_v1.py"
    sa_reg["legacy_upgrade_count"] = merged
    SA_REG.write_text(json.dumps(sa_reg, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "schema": "upgrade-888-to-sa-next-mapping-v1",
        "version": "1.0.0",
        "generated_at": now,
        "merger": "scripts/merge_upgrade_888_into_portfolio_next_v1.py",
        "canonical": "brain-os/plan-registry/PORTFOLIO_NEXT_6000_MASTER_v1.json",
        "superseded": "brain-os/ssot/superseded/SOURCEA_UPGRADE_PLANS_888_REGISTRY_v1.json",
        "entry_count": len(mapping_entries),
        "receipt_flags": load_receipt_flags() if bootstrap else {},
        "entries": mapping_entries,
    }
    MAPPING_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    return {
        "ok": True,
        "merged": merged,
        "bootstrapped": bootstrapped,
        "mapping": str(MAPPING_PATH),
        "registry": str(SA_REG),
    }


def supersede_888() -> dict:
    if not UP_PATH.is_file():
        raise SystemExit(f"Missing {UP_PATH}")
    if not MAPPING_PATH.is_file():
        raise SystemExit(f"Run merge first — missing {MAPPING_PATH}")

    now = _now()
    up_reg = json.loads(UP_PATH.read_text(encoding="utf-8"))
    up_reg["status"] = "superseded"
    up_reg["superseded_at"] = now
    up_reg["superseded_by"] = "brain-os/plan-registry/PORTFOLIO_NEXT_6000_MASTER_v1.json"
    up_reg["mapping_manifest"] = "data/upgrade-888-to-sa-next-mapping-v1.json"
    up_reg["canonical_law"] = "docs/PORTFOLIO_UPGRADE_PLANS_CANONICAL_LOCKED_v1.md"

    superseded_dir = SOURCEA_ROOT / "brain-os/ssot/superseded"
    superseded_dir.mkdir(parents=True, exist_ok=True)
    superseded_path = superseded_dir / "SOURCEA_UPGRADE_PLANS_888_REGISTRY_v1.json"
    superseded_path.write_text(json.dumps(up_reg, indent=2) + "\n", encoding="utf-8")

    stub = f"""{{
  "schema": "sourcea-upgrade-plans-888-registry-redirect-v1",
  "status": "superseded",
  "superseded_at": "{now}",
  "message": "UP-888 superseded by portfolio-next-6000 canonical registry.",
  "canonical_master": "brain-os/plan-registry/PORTFOLIO_NEXT_6000_MASTER_v1.json",
  "canonical_law": "docs/PORTFOLIO_UPGRADE_PLANS_CANONICAL_LOCKED_v1.md",
  "mapping_manifest": "data/upgrade-888-to-sa-next-mapping-v1.json",
  "lineage_copy": "brain-os/ssot/superseded/SOURCEA_UPGRADE_PLANS_888_REGISTRY_v1.json"
}}
"""
    UP_PATH.write_text(stub, encoding="utf-8")

    gov_path = SOURCEA_ROOT / "data/sourcea-governance-ssot-registry-v1.json"
    gov = json.loads(gov_path.read_text(encoding="utf-8"))
    entries = gov.get("entries") or []
    ids = {e["id"] for e in entries}
    if "upgrade_plans_888" not in ids:
        entries.append(
            {
                "id": "upgrade_plans_888",
                "family": "upgrade_plans",
                "title": "SourceA Upgrade Plans 888",
                "version": "1",
                "status": "superseded",
                "path": "brain-os/ssot/superseded/SOURCEA_UPGRADE_PLANS_888_REGISTRY_v1.json",
                "supersedes": [],
                "superseded_by": "portfolio_next_6000",
                "notes": "Legacy UP-0001..UP-0888 — mapped to sa-next-0001..0888",
            }
        )
    if "portfolio_next_6000" not in ids:
        entries.append(
            {
                "id": "portfolio_next_6000",
                "family": "upgrade_plans",
                "title": "Portfolio Next 6000 Plans",
                "version": "1",
                "status": "active",
                "path": "brain-os/plan-registry/PORTFOLIO_NEXT_6000_MASTER_v1.json",
                "supersedes": ["upgrade_plans_888"],
                "superseded_by": None,
                "notes": "Canonical upgrade plan registry — 6 repos × 1000",
            }
        )
    gov["entries"] = entries
    gov["saved_at"] = now
    gov_path.write_text(json.dumps(gov, indent=2) + "\n", encoding="utf-8")

    return {
        "ok": True,
        "superseded_path": str(superseded_path),
        "stub_path": str(UP_PATH),
        "governance": str(gov_path),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Merge UP-888 into portfolio-next-6000 SourceA pack")
    p.add_argument("--no-bootstrap", action="store_true", help="Skip receipt-aware status bootstrap")
    p.add_argument("--supersede", action="store_true", help="Supersede 888 registry after merge")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    result = merge(bootstrap=not args.no_bootstrap)
    if args.supersede:
        result["supersede"] = supersede_888()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"OK: merged {result['merged']} UP plans into sa-next pack")
        print(f"     bootstrapped {result['bootstrapped']} rows from receipts")
        print(f"     mapping: {result['mapping']}")
        if args.supersede:
            print(f"     superseded: {result['supersede']['superseded_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
