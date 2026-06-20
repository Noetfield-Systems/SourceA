#!/usr/bin/env python3
"""Audit Layer A markdown entries under SinaaiDataBase/data/."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sina_command_lib import parse_frontmatter  # noqa: E402

MONO_ROOT = Path.home() / "Desktop/SinaaiMonoRepo/SinaaiDataBase"
MONO_DATA = MONO_ROOT / "data"
SKIP_FILES = {"SCOPE.md", "README.md", "readme.md"}

REQUIRED = ("id", "title", "layer", "access", "status")
VALID_LAYERS = {"L0-meta", "L1-identity", "L2-knowledge", "L3-process", "L4-agents"}
VALID_STATUS = {"draft", "active", "archived"}


def audit() -> list[str]:
    errors: list[str] = []
    if not MONO_DATA.is_dir():
        errors.append(f"missing Layer A dir: {MONO_DATA}")
        return errors

    seen_ids: dict[str, str] = {}
    for path in sorted(MONO_DATA.rglob("*.md")):
        if path.name.startswith("."):
            continue
        rel = path.relative_to(MONO_ROOT)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            errors.append(f"{rel}: read error {e}")
            continue
        meta = parse_frontmatter(text)
        if not meta.get("id"):
            if path.name in SKIP_FILES:
                continue
            errors.append(f"{rel}: missing frontmatter id")
            continue
        for key in REQUIRED:
            if not meta.get(key):
                errors.append(f"{rel}: missing {key}")
        layer = meta.get("layer", "")
        if layer and layer not in VALID_LAYERS:
            errors.append(f"{rel}: invalid layer {layer!r}")
        status = meta.get("status", "")
        if status and status not in VALID_STATUS:
            errors.append(f"{rel}: invalid status {status!r}")
        eid = meta["id"]
        if eid in seen_ids:
            errors.append(f"{rel}: duplicate id {eid!r} (also {seen_ids[eid]})")
        else:
            seen_ids[eid] = str(rel)

    imports = MONO_ROOT / "imports" / "raw"
    staging = MONO_ROOT / "pipeline" / "staging"
    if not imports.is_dir():
        errors.append(f"missing imports/raw (create): {imports}")
    if not staging.is_dir():
        errors.append(f"missing pipeline/staging (create): {staging}")

    return errors


def main() -> int:
    errs = audit()
    if errs:
        print("PERSONAL DB LAYER A AUDIT FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"OK: Layer A audit · {MONO_DATA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
