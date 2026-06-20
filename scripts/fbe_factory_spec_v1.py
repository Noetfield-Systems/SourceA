#!/usr/bin/env python3
"""FBE Factory Spec Language v1 — validate catalog, list specs, resolve execution."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fbe.lib.factory_spec_v1 import (  # noqa: E402
    catalog_payload,
    load_spec,
    resolve_execution,
    validate_catalog,
    validate_spec,
)


def main() -> int:
    ap = argparse.ArgumentParser(description="FBE Factory Spec Language v1")
    ap.add_argument("--validate", action="store_true", help="Validate full catalog + specs")
    ap.add_argument("--list", action="store_true", help="List catalog items")
    ap.add_argument("--catalog", action="store_true", help="Emit website-ready catalog payload")
    ap.add_argument("--resolve", metavar="FACTORY_ID", help="Resolve spec to API route + body")
    ap.add_argument("--tenant", default="")
    ap.add_argument("--tier", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.validate:
        row = validate_catalog()
    elif args.list or args.catalog:
        row = catalog_payload(tier=args.tier)
    elif args.resolve:
        row = resolve_execution(factory_id=args.resolve, tenant=args.tenant)
    else:
        row = validate_catalog()

    if args.json or not args.resolve:
        print(json.dumps(row, indent=2))
    else:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
