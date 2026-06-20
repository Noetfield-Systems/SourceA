#!/usr/bin/env python3
"""Validate all five portfolio competitor-1000 packs (v2)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_portfolio_competitor_1000_plans_v1 import GENERATOR_VERSION, validate_pack

PACKS = [
    ("SourceA", ROOT / "brain-os/plan-registry/sourcea-competitor-1000"),
    ("WitnessBC", ROOT / "witnessbc-site/os/plan-library/witnessbc-competitor-1000"),
    (
        "Noetfield",
        Path.home()
        / "Desktop/Noetfield/Noetfield-All-Documents/Noetfield/os/plan-library/noetfield-competitor-1000",
    ),
    (
        "TrustField",
        Path.home() / "Desktop/TrustField Technologies/os/plan-library/trustfield-competitor-1000",
    ),
    ("VIRLUX", Path.home() / "Desktop/VIRLUX/os/plan-library/virlux-competitor-1000"),
]


def main() -> None:
    errors: list[str] = []
    for name, pack in PACKS:
        if not pack.is_dir():
            errors.append(f"{name}: missing pack dir {pack}")
            continue
        errors.extend(validate_pack(pack))

    if errors:
        print(f"FAIL portfolio-competitor-1000 validation — generator v{GENERATOR_VERSION}")
        for e in errors[:40]:
            print(f"  {e}")
        if len(errors) > 40:
            print(f"  ... and {len(errors) - 40} more")
        sys.exit(1)

    pick_val = ROOT / "scripts" / "validate-portfolio-competitor-pick-v1.sh"
    if pick_val.is_file():
        import subprocess

        proc = subprocess.run(["bash", str(pick_val)], cwd=str(ROOT), check=False)
        if proc.returncode != 0:
            sys.exit(proc.returncode)

    manifest = ROOT / "data/portfolio-competitor-1000-manifest-v1.json"
    if manifest.is_file():
        m = json.loads(manifest.read_text(encoding="utf-8"))
        if not m.get("ok"):
            print("FAIL manifest ok=false")
            sys.exit(1)

    print(f"PASS portfolio-competitor-1000 — 5 stacks × 1000 plans — generator v{GENERATOR_VERSION}")


if __name__ == "__main__":
    main()
