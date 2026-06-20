#!/usr/bin/env python3
"""Noetfield TLE reference narrative — lane keyword routing + platform-neutral gate.

Receipt: ~/.sina/noetfield-tle-reference-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "noetfield-tle-reference-narrative-v1.json"
PN = ROOT / "data" / "platform-neutral-world-model-v1.json"
RECEIPT = SINA / "noetfield-tle-reference-receipt-v1.json"

FORBIDDEN = [
    "mac only",
    "only on mac",
    "only mac",
    "mac-only",
    "requires a mac",
    "must use mac",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def assess(*, write: bool = True) -> dict:
    narr = _read(SSOT)
    pn = _read(PN)
    routes = list(pn.get("product_routes") or [])
    nf_route = next((r for r in routes if r.get("lane") == "noetfield"), None)
    route_keywords = [str(k).lower() for k in (nf_route or {}).get("keywords") or []]
    narr_keywords = [str(k).lower() for k in (narr.get("lane_keywords") or [])]
    blob = json.dumps(narr).lower()

    checks: list[dict] = []
    checks.append(
        {
            "id": "schema",
            "ok": narr.get("schema") == "noetfield-tle-reference-narrative-v1",
            "detail": narr.get("schema"),
        }
    )
    checks.append({"id": "lane", "ok": narr.get("lane") == "noetfield", "detail": narr.get("lane")})
    routed = bool(nf_route) and set(route_keywords).issubset(set(narr_keywords))
    checks.append(
        {
            "id": "lane_keywords_routed",
            "ok": routed,
            "detail": f"route={route_keywords} narr={narr_keywords}",
        }
    )
    required = ["tle", "board pack", "copilot", "governance receipt"]
    missing = [t for t in required if t not in blob]
    checks.append(
        {
            "id": "narrative_sections",
            "ok": not missing,
            "detail": "ok" if not missing else f"missing={missing}",
        }
    )
    forbidden_hit = next((f for f in FORBIDDEN if f in blob), None)
    checks.append(
        {
            "id": "platform_neutral",
            "ok": forbidden_hit is None,
            "detail": "ok" if forbidden_hit is None else f"forbidden={forbidden_hit}",
        }
    )

    ok = all(c.get("ok") for c in checks)
    row = {
        "schema": "noetfield-tle-reference-receipt-v1",
        "at": _now(),
        "ok": ok,
        "tle_reference_line": (
            f"Noetfield TLE reference · keywords_routed={routed} · "
            f"platform_neutral={forbidden_hit is None} · checks={sum(1 for c in checks if c.get('ok'))}/{len(checks)}"
        ),
        "ssot": str(SSOT.relative_to(ROOT)),
        "phase0_id": "P0-05",
        "checks": checks,
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Noetfield TLE reference narrative assess")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    row = assess(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("tle_reference_line"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
