#!/usr/bin/env python3
"""Canonical registry — private agent workspaces, governance, and real needs per repo."""
from __future__ import annotations

from pathlib import Path

from loop_pack_registry import PACKS, resolve_noetfield_local_root

_DESKTOP = Path.home() / "Desktop"
SOURCE_A = Path(__file__).resolve().parents[1]
NOETFIELD_CLOUD = _DESKTOP / "Noetfield"
SEVEN77_ROOT = _DESKTOP / "The 777 Foundation"

GOVERNANCE_VERSION = 7


def _nf_local() -> str:
    return str(resolve_noetfield_local_root())


# id → full spec (private dir: ~/.sina/agent-workspaces/<id>/)
AGENT_WORKSPACES: list[dict] = [
    {
        "id": "trustfield",
        "label": "TrustField Technologies",
        "role": "portfolio",
        "thread": "THREAD-PORTFOLIO",
        "lane": "TrustField",
        "plane": "DELIVERY",
        "repo_root": PACKS["trustfield"]["root"],
        "forbidden_roots": [str(SOURCE_A)],
        "pack_id": "trustfield",
        "cursor_workspace_hint": "TrustField Technologies",
        "command_tabs": "Actions (infra, DB, law) · Private agent page · Repos → lane brief",
        "real_needs": [
            "Resolve B-001 law collision (postgres vs no-card) with GLOBAL_BLOCKERS",
            "Trust / compliance product lanes — no founder Terminal for deploy checks",
            "Lane brief on Repos; loop pack for 10-round doc/law passes",
        ],
        "artifacts": ["os/plan.json", "prompts/", "docs/GLOBAL_BLOCKERS.json"],
        "governance_focus": "Infra truth + law alignment before ship",
        "layer_a_training": True,
    },
    {
        "id": "virlux",
        "label": "VIRLUX",
        "role": "portfolio",
        "thread": "THREAD-PORTFOLIO",
        "lane": "VIRLUX",
        "plane": "DELIVERY",
        "repo_root": PACKS["virlux"]["root"],
        "forbidden_roots": [str(SOURCE_A)],
        "pack_id": "virlux",
        "cursor_workspace_hint": "VIRLUX",
        "command_tabs": "Actions (DNS, Vercel smoke) · Private agent page · Live products",
        "real_needs": [
            "DNS + Vercel deployment smoke — one-tap Actions, not founder shell",
            "GTM / media lane progress in plan.json",
            "Public URL verification via Live products tab",
        ],
        "artifacts": ["os/plan.json", "prompts/", "vercel.json"],
        "governance_focus": "Live site + DNS proof without Terminal for founder",
    },
    {
        "id": "ai_dev_bridge_os",
        "label": "AI Dev Bridge OS",
        "role": "portfolio",
        "thread": "THREAD-WIRE",
        "lane": "Wire",
        "plane": "WIRE",
        "repo_root": PACKS["ai_dev_bridge_os"]["root"],
        "forbidden_roots": [str(SOURCE_A)],
        "pack_id": "ai_dev_bridge_os",
        "cursor_workspace_hint": "AI Dev Bridge OS",
        "command_tabs": "Actions (G1/G2/G3 wire) · Private agent page · Track",
        "real_needs": [
            "Wire lane G1/G2/G3 evidence — WIRE_LANE_PROGRESS style artifacts",
            "Tailscale / relay proofs via executor or future Actions buttons",
            "Factory thread support for P0 RunReceipt wire stubs",
        ],
        "artifacts": ["prompts/", "brain-os/law/WIRE_LANE_PROGRESS.md", "scripts/evidence/"],
        "governance_focus": "Wire proof artifacts; executor runs shell",
    },
    {
        "id": "noetfield_local",
        "label": "Noetfield — local documents",
        "role": "portfolio",
        "thread": "THREAD-PORTFOLIO",
        "lane": "Noetfield",
        "plane": "DESIGN",
        "repo_root": _nf_local(),
        "forbidden_roots": [str(NOETFIELD_CLOUD), str(SOURCE_A)],
        "pack_id": "noetfield_local",
        "cursor_workspace_hint": "Noetfield-All-Documents",
        "command_tabs": "Private agent page (local pack) · Repos — never cloud Noetfield repo",
        "real_needs": [
            "HIERARCHY_INDEX L0–L3 laws and registry SSOT on disk",
            "golden_edge_case.schema + source_of_truth_registry.json validation",
            "_under-analysis decisions — promote or archive",
            "NEVER edit ~/Desktop/Noetfield cloud/GitHub ship repo from this workspace",
        ],
        "artifacts": [
            "HIERARCHY_INDEX.md",
            "registry/source_of_truth_registry.json",
            "prompts/loop-suggestions-100.json",
        ],
        "governance_focus": "Local SSOT only — cloud repo is separate agent (noetfield_cloud)",
        "layer_a_training": True,
    },
    {
        "id": "noetfield_cloud",
        "label": "Noetfield — cloud / GitHub ship",
        "role": "portfolio",
        "thread": "THREAD-PORTFOLIO",
        "lane": "Noetfield",
        "plane": "SHIP",
        "repo_root": str(NOETFIELD_CLOUD),
        "forbidden_roots": [_nf_local(), str(SOURCE_A)],
        "pack_id": "noetfield_cloud",
        "cursor_workspace_hint": "Desktop/Noetfield",
        "command_tabs": "Private agent page (cloud pack) · Live products · Actions",
        "real_needs": [
            "Public GitHub / Vercel ship repo — deploy, CI, README",
            "Do not move local-only hierarchy docs from Noetfield-All-Documents here",
            "Release tags and deployment protection — founder uses Actions not Terminal",
        ],
        "artifacts": ["README.md", ".github/", "vercel.json", "prompts/"],
        "governance_focus": "Ship lane only — local docs stay in noetfield_local agent",
    },
    {
        "id": "seven77",
        "label": "The 777 Foundation",
        "role": "portfolio",
        "thread": "THREAD-PORTFOLIO",
        "lane": "777",
        "plane": "DELIVERY",
        "repo_root": str(SEVEN77_ROOT),
        "forbidden_roots": [str(SOURCE_A)],
        "pack_id": "seven77",
        "cursor_workspace_hint": "The 777 Foundation",
        "command_tabs": "Actions (deploy smoke, health) · Private agent page · Live products",
        "real_needs": [
            "Gate 0 outreach + board ops (ops/gate0-week1-execution.md)",
            "C3 translation sprint — admin queue, contribution_ledger, guild stats",
            "web/ Next.js + Supabase service key + Vercel deploy:prod-close",
            "Health: /api/health adminRead — one-tap verify in Actions when wired",
        ],
        "artifacts": [
            "os/plan.json",
            "web/",
            "ops/gate0-week1-execution.md",
            "supabase/migrations/",
        ],
        "governance_focus": "Web ops + cohort throughput; no founder Terminal for npm/deploy",
        "layer_a_training": True,
    },
    {
        "id": "semej",
        "label": "SEMEJ multi-AI",
        "role": "automation",
        "thread": "THREAD-PORTFOLIO",
        "lane": "SEMEJ",
        "plane": "AUTOMATION",
        "repo_root": str(SOURCE_A),
        "forbidden_roots": [str(SOURCE_A)],
        "pack_id": None,
        "cursor_workspace_hint": "SourceA read-only + private SEMEJ dir",
        "command_tabs": "SEMEJ tab · Actions (Chrome, Playwright install)",
        "real_needs": [
            "Chrome chain across AIs — founder uses SEMEJ tab only",
            "Playwright install via Actions — not founder Terminal",
            "Do not patch sina-command-server.py — agent review if broken",
        ],
        "artifacts": ["~/.sina/semej-state.json", "scripts/semej_loop.py"],
        "governance_focus": "Browser automation lane; SourceA code is read-only",
    },
]


def get_workspace(agent_id: str) -> dict | None:
    return next((w for w in AGENT_WORKSPACES if w["id"] == agent_id), None)


def list_workspace_ids() -> list[str]:
    return [w["id"] for w in AGENT_WORKSPACES]
