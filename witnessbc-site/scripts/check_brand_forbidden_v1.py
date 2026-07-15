#!/usr/bin/env python3
"""CLI: fail if any line in given files matches external brand denylist."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand_guard_v1 import line_is_forbidden  # noqa: E402

SCAN_SUFFIXES = {".html", ".css", ".js", ".md", ".json", ".sh", ".py"}


def _iter_paths(args: list[str]):
    for arg in args:
        path = Path(arg)
        if path.is_file():
            yield path
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix in SCAN_SUFFIXES and "node_modules" not in child.parts:
                    yield child


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check_brand_forbidden_v1.py <file-or-dir>...", file=sys.stderr)
        return 2
    for path in _iter_paths(sys.argv[1:]):
        for num, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if line_is_forbidden(line):
                print(f"FAIL: forbidden brand reference in {path}:{num}", file=sys.stderr)
                return 1
    print("OK: brand denylist check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
