"""Portfolio competitor-1000 pick order — competitor-first drain + FORGE cloud envelope.

Law: Mac observes only — implementation runs on cloud FORGE (forge-bay / Railway FBE).
SSOT packs: data/portfolio-competitor-1000-manifest-v1.json
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCEA_ROOT = Path(__file__).resolve().parents[1]

WORKSTREAM_ORDER = ("ws-ux", "ws-pricing", "ws-run", "ws-onboard", "ws-integrate")
TIER_ORDER = ("T0", "T1", "T2", "T3")

FORGE_CORE = {
    "bay_slug": "forge-bay",
    "template_id": "forge-app-factory-v1",
    "run_mode": "forge",
    "dispatch_path": "/api/fbe/run-forge/v1",
    "execution_mode": "CLOUD_ONLY",
    "mac_build_forbidden": True,
    "engine": "FORGE",
    "stack_loop": [
        "reasoning",
        "planning_dag",
        "routing_openrouter",
        "execution_workers",
        "verification_critic",
        "aggregation",
        "meta_replan",
    ],
}

STACKS: dict[str, dict[str, Any]] = {
    "sourcea": {
        "stack": "SourceA",
        "prefix": "sa-mkt",
        "lane": "sourcea",
        "tenant": "forge",
        "agent": "AGENT-AUTO-SOURCEA",
        "pick_script": "scripts/pick-sourcea-competitor-mkt-plan.py",
        "pack_root": SOURCEA_ROOT / "brain-os/plan-registry/sourcea-competitor-1000",
        "repo_root": SOURCEA_ROOT,
    },
    "witnessbc": {
        "stack": "WitnessBC",
        "prefix": "wb-mkt",
        "lane": "witnessbc",
        "tenant": "witnessbc",
        "agent": "AGENT-AUTO-WITNESSBC",
        "pick_script": "scripts/pick-witnessbc-competitor-mkt-plan.py",
        "pack_root": SOURCEA_ROOT / "witnessbc-site/os/plan-library/witnessbc-competitor-1000",
        "repo_root": SOURCEA_ROOT / "witnessbc-site",
    },
    "noetfield": {
        "stack": "Noetfield",
        "prefix": "nf-mkt",
        "lane": "noetfield",
        "tenant": "noetfield",
        "agent": "AGENT-AUTO-NOETFIELD",
        "pick_script": "scripts/pick-noetfield-competitor-mkt-plan.py",
        "pack_root": Path.home()
        / "Desktop/Noetfield/Noetfield-All-Documents/Noetfield/os/plan-library/noetfield-competitor-1000",
        "repo_root": Path.home() / "Desktop/Noetfield/Noetfield-All-Documents/Noetfield",
    },
    "trustfield": {
        "stack": "TrustField",
        "prefix": "tf-mkt",
        "lane": "trustfield",
        "tenant": "trustfield",
        "agent": "AGENT-AUTO-TRUSTFIELD",
        "pick_script": "scripts/pick-trustfield-competitor-mkt-plan.py",
        "pack_root": Path.home() / "Desktop/TrustField Technologies/os/plan-library/trustfield-competitor-1000",
        "repo_root": Path.home() / "Desktop/TrustField Technologies",
    },
    "virlux": {
        "stack": "VIRLUX",
        "prefix": "vx-mkt",
        "lane": "virlux",
        "tenant": "virlux",
        "agent": "Auto-VIRLUX-Delivery",
        "pick_script": "scripts/pick-virlux-competitor-mkt-plan.py",
        "pack_root": Path.home() / "Desktop/VIRLUX/os/plan-library/virlux-competitor-1000",
        "repo_root": Path.home() / "Desktop/VIRLUX",
    },
}


def resolve_stack(raw: str) -> str:
    key = (raw or "").strip().lower().replace("_", "").replace("-", "")
    aliases = {
        "sourcea": "sourcea",
        "sa": "sourcea",
        "witnessbc": "witnessbc",
        "wb": "witnessbc",
        "noetfield": "noetfield",
        "nf": "noetfield",
        "trustfield": "trustfield",
        "tf": "trustfield",
        "virlux": "virlux",
        "vx": "virlux",
    }
    if key not in aliases:
        raise ValueError(f"unknown stack {raw!r} — use: {', '.join(STACKS)}")
    return aliases[key]


def load_registry(stack_key: str) -> dict[str, Any]:
    cfg = STACKS[stack_key]
    reg_path = cfg["pack_root"] / "REGISTRY.json"
    if not reg_path.is_file():
        raise FileNotFoundError(f"Missing {reg_path} — run generate_portfolio_competitor_1000_plans_v1.py")
    return json.loads(reg_path.read_text(encoding="utf-8"))


def phase_order(registry: dict[str, Any]) -> tuple[str, ...]:
    phases = registry.get("phases") or []
    ordered = [p["id"] for p in phases if p.get("id")]
    if len(ordered) == 20:
        return tuple(ordered)
    seen: list[str] = []
    for pl in registry.get("plans") or []:
        pid = pl.get("phase")
        if pid and pid not in seen:
            seen.append(pid)
    return tuple(seen)


def pick_backlog_plans(
    plans: list[dict[str, Any]],
    *,
    phases: tuple[str, ...],
    tiers: tuple[str, ...] | list[str] = TIER_ORDER,
    limit: int = 1,
    order: str = "competitor-first",
) -> list[dict[str, Any]]:
    tier_list = list(tiers)
    picked: list[dict[str, Any]] = []

    if order == "tier-global":
        for tier in tier_list:
            for phase in phases:
                for ws in WORKSTREAM_ORDER:
                    for pl in _candidates(plans, phase=phase, tier=tier, workstream=ws):
                        picked.append(pl)
                        if len(picked) >= limit:
                            return picked
        return picked

    if order != "competitor-first":
        raise ValueError(f"unknown pick order: {order}")

    for phase in phases:
        for tier in tier_list:
            for ws in WORKSTREAM_ORDER:
                for pl in _candidates(plans, phase=phase, tier=tier, workstream=ws):
                    picked.append(pl)
                    if len(picked) >= limit:
                        return picked
    return picked


def _candidates(
    plans: list[dict[str, Any]],
    *,
    phase: str,
    tier: str,
    workstream: str,
) -> list[dict[str, Any]]:
    rows = [
        pl
        for pl in plans
        if pl.get("phase") == phase
        and pl.get("tier") == tier
        and pl.get("workstream") == workstream
        and pl.get("status") == "backlog"
    ]
    rows.sort(key=lambda pl: pl.get("id", ""))
    return rows


def read_prompt_markdown(pack_root: Path, rel_path: str) -> str:
    path = pack_root / rel_path
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return ""


def forge_envelope(*, stack_key: str, plan: dict[str, Any]) -> dict[str, Any]:
    cfg = STACKS[stack_key]
    return {
        **FORGE_CORE,
        "tenant": cfg["tenant"],
        "stack": cfg["stack"],
        "lane": cfg["lane"],
        "work_order_id": plan.get("id"),
        "plan_id": plan.get("id"),
        "competitor": plan.get("competitor"),
        "competitor_row": plan.get("competitor_row"),
        "workstream": plan.get("workstream"),
        "phase": plan.get("phase"),
        "implementation": plan.get("implementation"),
        "hub_dispatch": "POST http://127.0.0.1:13020/api/fbe/run-forge/v1",
        "cloud_dispatch": "Railway FBE — mode railway_fbe via portfolio_competitor_forge_dispatch_v1.py",
        "model_routing_hint": {
            "bulk_parallel": "OpenRouter",
            "code_quality": "Claude Sonnet",
            "control_logic": "GPT-4.1 mini",
            "long_context": "Gemini",
        },
    }


def enrich_pick(stack_key: str, plan: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    cfg = STACKS[stack_key]
    pack_root = cfg["pack_root"]
    rel = plan.get("path") or ""
    md = read_prompt_markdown(pack_root, rel)
    row = dict(plan)
    row["stack"] = cfg["stack"]
    row["stack_key"] = stack_key
    row["lane"] = cfg["lane"]
    row["repo_root"] = str(cfg["repo_root"])
    row["pack_root"] = str(pack_root)
    row["prompt_abs"] = str(pack_root / rel) if rel else ""
    row["prompt_markdown"] = md
    row["execution_plane"] = "cloud_forge"
    row["forge"] = forge_envelope(stack_key=stack_key, plan=plan)
    if md and not row.get("agent_prompt"):
        row["agent_prompt"] = f"PLAN WITH NO ASF — {plan.get('id')}: {plan.get('title', '')[:120]}"
    row["pick_script"] = cfg["pick_script"]
    row["market_ssot"] = registry.get("market_ssot")
    row["generator_version"] = registry.get("generator_version")
    return row
