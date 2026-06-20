#!/usr/bin/env python3
"""Executor/hub: enforce honest REGISTRY — revert YAML inflate instantly."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from registry_honest_lib_v1 import audit_registry_done, enforce_honest_registry  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    out = enforce_honest_registry(dry_run=args.dry_run)
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        if out.get("enforced"):
            print(
                f"ENFORCED: reverted {out.get('reverted_count', 0)} · "
                f"honest {out['after']['honest_done']}/{out['after']['total']}"
            )
        else:
            a = out if out.get("honest_done") is not None else audit_registry_done()
            print(f"OK: already honest · {a.get('honest_done', a['after']['honest_done'])}/{a.get('total', 1000)}")
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
