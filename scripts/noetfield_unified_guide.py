#!/usr/bin/env python3
"""Structured Noetfield unified guide for Sina Command UI."""
from __future__ import annotations

from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
DOC = "brain-os/law/NOETFIELD_CLOUD_GIT_AND_AGENT_ENTRY_UNIFIED_LOCKED_v1.md"


def noetfield_unified_guide_payload() -> dict:
    return {
        "ok": True,
        "doc_path": DOC,
        "title": "Noetfield — cloud git & agent entry",
        "tagline": "Two workspaces · three SSOT layers · what goes in git vs Mac only",
        "policy_one_liner": (
            "Noetfield git = product + ship + in-repo entry. "
            "Ecosystem law = SourceA on Mac. Cloud reads git; never treat repo as newer than SourceA."
        ),
        "workspaces": [
            {
                "id": "noetfield_local",
                "label": "Local documents",
                "folder": "~/Desktop/Noetfield-All-Documents",
                "thread": "THREAD-PORTFOLIO",
                "role": "Hierarchy & registry — not runnable stack",
                "notice": "founder/repo-agent-notices/REPO_NOTICE_noetfield_v1.md",
                "forbidden": "~/Desktop/Noetfield (cloud ship)",
            },
            {
                "id": "noetfield_cloud",
                "label": "Cloud / GitHub ship",
                "folder": "~/Desktop/Noetfield",
                "thread": "THREAD-PORTFOLIO",
                "role": "Implementation SSOT — TLE, console, :13080",
                "notice": "founder/repo-agent-notices/SEMI_NOTICE_noetfield_cloud_v1.md",
                "forbidden": "Noetfield-All-Documents + SourceA edits",
            },
        ],
        "layers": [
            {"id": "A", "name": "Git (cloud clone)", "paths": "docs/ops/* · os/plan.json · code"},
            {"id": "B", "name": "Mac gitignored mirror", "paths": "Noetfield/ops/private/sourceA/ (after sync)"},
            {"id": "C", "name": "Mac founder", "paths": "SourceA · hub :13020 · build_repo_agent_notices.py"},
        ],
        "mac_vs_cloud": [
            {"surface": "Hub :13020", "mac": True, "cloud": False},
            {"surface": "sync-sourceA-desktop.sh", "mac": True, "cloud": False},
            {"surface": "docs/ops/AGENT_READ_LINKS_LOCKED_v1.md", "mac": True, "cloud": True},
            {"surface": "os/SHIP_NOW.md + plan.json", "mac": True, "cloud": True},
            {"surface": "Full ecosystem link index", "mac": True, "cloud": "After sync or paste only"},
        ],
        "cloud_how": [
            "git clone — repo files are the entry path (not your Mac)",
            "Read docs/ops/AGENT_READ_LINKS_LOCKED_v1.md → § Cloud ship",
            "Read NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md",
            "Ship from os/SHIP_NOW.md → os/plan.json",
            "Ecosystem law: founder syncs ops/private/sourceA/ on Mac or pastes notices",
        ],
        "cloud_read_order": [
            "docs/ops/AGENT_READ_LINKS_LOCKED_v1.md",
            "docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md",
            "os/SHIP_NOW.md → os/plan.json",
            "SEMI_NOTICE_noetfield_cloud_v1.md (after Mac sync)",
            "ready_to_paste_noetfield_cloud.txt",
        ],
        "local_read_order": [
            "REPO_NOTICE_noetfield_v1.md",
            "HIERARCHY_INDEX.md + source_of_truth_registry.json",
            "Never edit Desktop/Noetfield from this chat",
        ],
        "share_in_git": [
            "Product code + tests",
            "os/plan.json · os/SHIP_NOW.md",
            "docs/ops locked agent entry files",
            "Strategy/spec locks · PRODUCT_TRUTH",
            "Repo .cursor/rules · cloud loop pack",
        ],
        "do_not_share": [
            "Full SourceA tree in git",
            "ops/private/sourceA/ committed",
            "Hub URLs as required dependency",
            "Secrets · full fleet paste files",
            "Duplicate AGENT_READ_LINKS_INDEX as second SSOT",
        ],
        "mac_actions": [
            {
                "label": "Sync SourceA → Noetfield mirror",
                "hint": "Actions tab → Sync Noetfield mirror (one tap — maintainer ships button if missing)",
            },
            {
                "label": "Rebuild agent notices",
                "hint": "Actions tab → Rebuild repo agent notices — agents run build, not founder Terminal",
            },
            {
                "label": "Hub / refresh",
                "hint": "Worker Hub → Safety check or Light refresh — :13020 stays up without Terminal",
            },
        ],
        "repo_mirror_path": str(
            Path.home() / "Desktop/Noetfield/docs/ops/AGENT_READ_LINKS_LOCKED_v1.md"
        ),
    }
