#!/usr/bin/env python3
"""CLI: fail if any line in given files matches WitnessBC brand denylist."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand_guard_v1 import line_is_forbidden  # noqa: E402


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check_brand_forbidden_v1.py <file>...", file=sys.stderr)
        return 2
    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.is_file():
            continue
        for num, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if line_is_forbidden(line):
                print(f"FAIL: forbidden brand reference in {path}:{num}", file=sys.stderr)
                return 1
    print("OK: brand denylist check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
