#!/usr/bin/env python3
"""Emit cursor cost intelligence routing SSOT + surfaces line."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "data" / "cursor-cost-intelligence-routing-v1.json"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    data = json.loads(SSOT.read_text(encoding="utf-8"))
    line = (
        "cursor-cost · Auto/Composer daily · API pool ship-only · "
        f"alwaysApply≤{data['alwaysapply_cap']['max_count']} · "
        "paths: apps|brain-os|scripts|receipts|labs"
    )
    payload = {**data, "cursor_cost_intelligence_line": line}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(line)


if __name__ == "__main__":
    main()
