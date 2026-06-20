#!/usr/bin/env python3
"""Patch command-data.json SA queue + P0 pick after hub refresh (SINA_SKIP_PANEL_BUILD path)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from align_command_data_ui_v1 import align_command_data_ui  # noqa: E402
from sina_command_lib import PANEL_DIR  # noqa: E402


def align_command_data(*, refresh_scripts: bool = False) -> dict:
    return align_command_data_ui(refresh_scripts=refresh_scripts)


def main() -> int:
    row = align_command_data()
    out = PANEL_DIR / "command-data.json"
    if not out.is_file():
        print("FAIL: command-data.json missing after align")
        return 1
    data = json.loads(out.read_text(encoding="utf-8"))
    sq = data.get("sourcea_sa_queue") or {}
    live = (sq.get("live_pick") or {}).get("id")
    na = (
        ((data.get("command_center") or {}).get("founder") or {}).get("p0") or {}
    ).get("next_action") or ""
    if not live or live not in na:
        print(f"FAIL: align incomplete live={live!r} next_action={na[:100]!r}")
        return 1
    print(f"OK: align_command_data_sa_queue_v1 live={live}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
