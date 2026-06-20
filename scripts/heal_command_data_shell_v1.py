#!/usr/bin/env python3
"""Re-strip heavy keys from command-data.json into command-data-shell.json (sa-0016)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sina_command_lib import heal_command_data_shell_from_disk  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Heal command-data-shell.json from command-data.json")
    p.add_argument("--force", action="store_true", help="Rewrite shell even when verify passes")
    args = p.parse_args()
    ok, msg = heal_command_data_shell_from_disk(force=args.force)
    if ok:
        print(f"OK: heal_command_data_shell_v1 · {msg}")
        return 0
    print(f"FAIL: heal_command_data_shell_v1 · {msg}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
