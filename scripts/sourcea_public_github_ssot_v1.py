#!/usr/bin/env python3
"""Load public GitHub SSOT for SourceA packages and landing."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "data" / "sourcea-public-github-v1.json"


@lru_cache(maxsize=1)
def load_ssot() -> dict:
    return json.loads(SSOT.read_text(encoding="utf-8"))


def repo(name: str) -> dict:
    row = load_ssot().get("repos", {}).get(name) or {}
    if not row.get("url"):
        raise KeyError(f"unknown public repo: {name}")
    return row


def boot_repo_slug() -> str:
    return str(repo("sourcea-boot")["slug"])


def boot_repo_url() -> str:
    return str(repo("sourcea-boot")["url"])


def boot_clone_url() -> str:
    return str(repo("sourcea-boot")["clone"])
