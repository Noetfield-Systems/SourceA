"""Portable .sourcea/ paths — mirrors sourcea-boot contract."""
from __future__ import annotations

from pathlib import Path

SCHEMA = "sourcea-sdk-portable-v1"


def sourcea_dir(cwd: Path | None = None) -> Path:
    root = cwd or Path.cwd()
    return root / ".sourcea"


def receipts_dir(cwd: Path | None = None) -> Path:
    return sourcea_dir(cwd) / "receipts"


def spine_path(cwd: Path | None = None) -> Path:
    return sourcea_dir(cwd) / "spine-v1.jsonl"


def latest_receipt_path(cwd: Path | None = None) -> Path:
    return receipts_dir(cwd) / "latest.json"
