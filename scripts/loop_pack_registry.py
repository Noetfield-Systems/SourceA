#!/usr/bin/env python3
"""Registry of portfolio repo loop prompt packs (100 catalog + 10 active)."""
from __future__ import annotations

from pathlib import Path

_HOME = Path.home()
_DESKTOP = _HOME / "Desktop"

# Noetfield has two Cursor workspaces — loop pack targets LOCAL documents only.
NOETFIELD_LOCAL_ROOT = _DESKTOP / "Noetfield-All-Documents"
NOETFIELD_CLOUD_ROOT = _DESKTOP / "Noetfield"


def resolve_noetfield_local_root() -> Path:
    for candidate in (
        _DESKTOP / "Noetfield-All-Documents",
        _DESKTOP / "Noetfield All Documents",
    ):
        if candidate.is_dir():
            return candidate
    return NOETFIELD_LOCAL_ROOT


PACKS: dict[str, dict[str, str]] = {
    "ai_dev_bridge_os": {
        "label": "AI Dev Bridge OS",
        "root": str(_DESKTOP / "AI Dev Bridge OS"),
        "catalog": "prompts/loop-suggestions-100.json",
        "pack": "prompts/loop-pack-10-active.json",
        "thread": "THREAD-WIRE",
        "repo": "ai_dev_bridge",
        "source": "ai_dev_bridge_os",
    },
    "trustfield": {
        "label": "TrustField Technologies",
        "root": str(_DESKTOP / "TrustField Technologies"),
        "catalog": "prompts/loop-suggestions-100.json",
        "pack": "prompts/loop-pack-10-active.json",
        "thread": "THREAD-PORTFOLIO",
        "repo": "trustfield",
        "source": "trustfield",
    },
    "virlux": {
        "label": "VIRLUX",
        "root": str(_DESKTOP / "VIRLUX"),
        "catalog": "prompts/loop-suggestions-100.json",
        "pack": "prompts/loop-pack-10-active.json",
        "thread": "THREAD-PORTFOLIO",
        "repo": "virlux",
        "source": "virlux",
    },
    "noetfield_local": {
        "label": "Noetfield (local documents)",
        "root": str(resolve_noetfield_local_root()),
        "catalog": "prompts/loop-suggestions-100.json",
        "pack": "prompts/loop-pack-10-active.json",
        "thread": "THREAD-PORTFOLIO",
        "repo": "noetfield",
        "source": "noetfield_local",
        "workspace_forbidden": str(NOETFIELD_CLOUD_ROOT),
        "workspace_rule": (
            "LOCAL only: Noetfield-All-Documents — never edit Desktop/Noetfield cloud/GitHub repo"
        ),
        "cursor_workspace": "Users-sinakazemnezhad-Desktop-Noetfield-All-Documents",
    },
    "noetfield_cloud": {
        "label": "Noetfield (cloud / GitHub ship)",
        "root": str(NOETFIELD_CLOUD_ROOT),
        "catalog": "prompts/loop-suggestions-100.json",
        "pack": "prompts/loop-pack-10-active.json",
        "thread": "THREAD-PORTFOLIO",
        "repo": "noetfield",
        "source": "noetfield_cloud",
        "workspace_forbidden": str(resolve_noetfield_local_root()),
        "workspace_rule": (
            "CLOUD ship only: Desktop/Noetfield — never edit Noetfield-All-Documents local SSOT"
        ),
        "cursor_workspace": "Users-sinakazemnezhad-Desktop-Noetfield",
    },
    "seven77": {
        "label": "The 777 Foundation",
        "root": str(_DESKTOP / "The 777 Foundation"),
        "catalog": "prompts/loop-suggestions-100.json",
        "pack": "prompts/loop-pack-10-active.json",
        "thread": "THREAD-PORTFOLIO",
        "repo": "seven77",
        "source": "seven77",
        "workspace_rule": "777 web ops — Gate 0, C3 cohort, Supabase, Vercel deploy",
        "cursor_workspace": "Users-sinakazemnezhad-Desktop-The-777-Foundation",
    },
}


def pack_paths(pack_id: str) -> tuple[Path | None, Path | None, dict | None]:
    spec = PACKS.get(pack_id)
    if not spec:
        return None, None, None
    if pack_id == "noetfield_local":
        root = resolve_noetfield_local_root()
    elif pack_id == "noetfield_cloud":
        root = NOETFIELD_CLOUD_ROOT if NOETFIELD_CLOUD_ROOT.is_dir() else Path(spec["root"])
    else:
        root = Path(spec["root"])
    catalog = root / spec["catalog"]
    pack = root / spec["pack"]
    return catalog, pack, spec


def list_pack_ids() -> list[str]:
    return list(PACKS.keys())
