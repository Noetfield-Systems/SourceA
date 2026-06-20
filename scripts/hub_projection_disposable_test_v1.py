#!/usr/bin/env python3
"""Track 2 P1 — canonical hub projection is disposable (delete → rebuild → same canonical view)."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "agent-control-panel"
sys.path.insert(0, str(ROOT / "scripts"))

from hub_projection_canonical_v1 import (  # noqa: E402
    canonical_fingerprint_file,
    projection_paths,
)

PATHS = projection_paths(PANEL)
CANONICAL = PATHS["canonical"]


def run_materializer() -> int:
    try:
        from align_command_data_ui_v1 import align_command_data_ui  # noqa: WPS433

        align_command_data_ui()
        return 0
    except Exception as exc:
        print(f"FAIL: align_command_data_ui — {exc}", file=sys.stderr)
        return 1


def main() -> int:
    if not CANONICAL.is_file():
        print("FAIL: command-data-canonical.json missing — run materializer first", file=sys.stderr)
        return 1

    backups: dict[Path, Path] = {}
    for label, path in PATHS.items():
        if path.is_file():
            bak = PANEL / f".hub-disposable-backup-{label}.json"
            shutil.copy2(path, bak)
            backups[path] = bak

    fp_before = canonical_fingerprint_file(CANONICAL)
    try:
        for path in PATHS.values():
            path.unlink(missing_ok=True)
        if run_materializer() != 0:
            print("FAIL: materializer align_command_data_ui_v1", file=sys.stderr)
            return 1
        if not CANONICAL.is_file():
            print("FAIL: command-data-canonical.json not recreated", file=sys.stderr)
            return 1
        fp_after = canonical_fingerprint_file(CANONICAL)
        if fp_before != fp_after:
            print(
                f"FAIL: canonical fingerprint drift before={fp_before} after={fp_after}",
                file=sys.stderr,
            )
            print(
                "NOTE: validator hashes canonical projection only — runtime mirrors excluded by split",
                file=sys.stderr,
            )
            return 1
        print(f"OK: hub_projection_disposable canonical_fp={fp_after}")
        return 0
    finally:
        for path, bak in backups.items():
            if bak.is_file():
                shutil.copy2(bak, path)
                bak.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
