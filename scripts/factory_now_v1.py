#!/usr/bin/env python3
"""factory-now — re-exports factory_control_v1."""
from __future__ import annotations

import sys

from factory_control_v1 import format_line, load_factory_now, rebuild_factory_now

if __name__ == "__main__":
    import argparse
    import json

    p = argparse.ArgumentParser()
    p.add_argument("--rebuild", action="store_true")
    p.add_argument("--line", action="store_true")
    args = p.parse_args()
    row = rebuild_factory_now(caller="cli", force=True) if args.rebuild else load_factory_now()
    if args.line:
        print(format_line(row))
    else:
        print(json.dumps(row, indent=2))
    raise SystemExit(0)
