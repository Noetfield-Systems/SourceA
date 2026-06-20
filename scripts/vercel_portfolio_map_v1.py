#!/usr/bin/env python3
"""Vercel portfolio map — SSOT sync + migration drift report.

Law: data/vercel-portfolio-map-v1.json
Receipt: ~/.sina/vercel-portfolio-map-v1.json
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "vercel-portfolio-map-v1.json"
RECEIPT = SINA / "vercel-portfolio-map-v1.json"
SURFACES = SINA / "agent-live-surfaces-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def compose_line(ssot: dict, *, migrate: list[dict]) -> str:
    owner = ssot.get("canonical_owner") or {}
    slug = owner.get("vercel_team_slug") or "the-777-foundation"
    n = len(migrate)
    if n:
        names = ",".join(p.get("vercel_name") or p.get("id") or "?" for p in migrate[:3])
        return f"vercel · home={slug} · redeploy_not_transfer={n} ({names})"
    return f"vercel · home={slug} · all projects on canonical owner"


def build_report() -> dict:
    ssot = _read(SSOT)
    projects = ssot.get("projects") or []
    migrate = [p for p in projects if p.get("status") in (
        "migrate_out", "redeploy_on_main", "redeploy_on_witnessbc_lane",
        "create_on_main_vercel", "delete_after_main_green",
    )]
    review = [p for p in projects if p.get("status") == "review"]
    ok = not migrate
    row = {
        "schema": "vercel-portfolio-map-v1",
        "at": _now(),
        "ok": ok,
        "canonical_owner": ssot.get("canonical_owner"),
        "migrate_out": migrate,
        "review": review,
        "migrate_count": len(migrate),
        "review_count": len(review),
        "line": compose_line(ssot, migrate=migrate),
        "ssot_path": str(SSOT.relative_to(ROOT)),
    }
    if migrate:
        first = migrate[0]
        mig = first.get("migration") or {}
        steps = mig.get("founder_steps_noetfield_chrome_now") or mig.get("founder_steps_noetfield_chrome") or []
        row["next_founder_action"] = steps[0] if steps else "Transfer sourcea-landing to the-777-foundation"
    return row


def wire_surfaces(line: str) -> None:
    surf = _read(SURFACES)
    if not surf:
        return
    surf["vercel_portfolio_map_line"] = line
    try:
        SURFACES.write_text(json.dumps(surf, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def main() -> int:
    p = argparse.ArgumentParser(description="Vercel portfolio map sync")
    p.add_argument("--json", action="store_true")
    p.add_argument("--wire", action="store_true")
    args = p.parse_args()
    row = build_report()
    try:
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    except OSError:
        row["receipt_write_ok"] = False
    if args.wire:
        wire_surfaces(str(row.get("line") or ""))
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or "")
        if not row.get("ok"):
            print(f"MIGRATE: {row.get('next_founder_action')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
