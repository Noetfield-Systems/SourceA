#!/usr/bin/env python3
"""RRL fleet glance — % D/E per brand from append-only history."""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
HISTORY = SINA / "response-reality-layer-history-v1.jsonl"
PASS = frozenset({"D", "E"})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_history() -> list[dict]:
    if not HISTORY.is_file():
        return []
    rows: list[dict] = []
    for line in HISTORY.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def fleet_glance() -> dict:
    rows = _read_history()
    by_brand: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        brand = str(r.get("brand") or "unknown").upper()
        if brand in ("NOETFIELD", "NF"):
            brand = "NF"
        elif brand in ("TRUSTFIELD", "TF"):
            brand = "TF"
        elif brand in ("SOURCEA", "SA"):
            brand = "SA"
        by_brand[brand].append(str(r.get("reaction") or "?"))

    lanes: list[dict] = []
    for brand in ("NF", "TF", "SA"):
        reactions = by_brand.get(brand) or []
        total = len(reactions)
        de = sum(1 for x in reactions if x in PASS)
        rate = round(100 * de / total) if total else 0
        lanes.append({"brand": brand, "sims": total, "de_count": de, "de_rate_pct": rate})

    line = " · ".join(f"{x['brand']} {x['de_rate_pct']}% D/E" for x in lanes if x["sims"]) or "rrl fleet — no history yet"
    return {
        "schema": "rrl-fleet-glance-v1",
        "at": _now(),
        "ok": True,
        "rrl_fleet_line": f"RRL fleet · {line}",
        "lanes": lanes,
        "history_path": str(HISTORY),
    }


def hub_slice() -> dict:
    return fleet_glance()


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="RRL fleet glance")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = fleet_glance()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("rrl_fleet_line"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
