"""Noetfield CLI."""
from __future__ import annotations

import argparse
import json
import sys

from noetfield.governance import Governance


def main() -> int:
    ap = argparse.ArgumentParser(prog="noetfield")
    ap.add_argument("--hub-url", default="")
    ap.add_argument("--api-key", default="")
    sub = ap.add_subparsers(dest="cmd", required=True)

    cat = sub.add_parser("catalog", help="List factory catalog")
    cat.add_argument("--tier", default="")
    cat.add_argument("--json", action="store_true")

    chk = sub.add_parser("check", help="Dry-run policy check for factory")
    chk.add_argument("factory_id")
    chk.add_argument("--tenant", default="")
    chk.add_argument("--json", action="store_true")

    ex = sub.add_parser("execute", help="Execute factory via Hub")
    ex.add_argument("factory_id")
    ex.add_argument("--tenant", default="")
    ex.add_argument("--json", action="store_true")

    aud = sub.add_parser("audit", help="Audit job ledger")
    aud.add_argument("job_id")
    aud.add_argument("--json", action="store_true")

    args = ap.parse_args()
    gov = Governance(hub_url=args.hub_url, api_key=args.api_key)

    if args.cmd == "catalog":
        row = gov.catalog(tier=args.tier)
    elif args.cmd == "check":
        row = gov.check(factory_id=args.factory_id, tenant=args.tenant)
    elif args.cmd == "execute":
        row = gov.execute(factory_id=args.factory_id, tenant=args.tenant)
    elif args.cmd == "audit":
        row = gov.audit(job_id=args.job_id)
    else:
        row = {"ok": False, "error": "unknown_cmd"}

    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
