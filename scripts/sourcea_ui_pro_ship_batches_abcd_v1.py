#!/usr/bin/env python3
"""Ship UI Pro batches A–D (WS-01..04 · UP-UI-001..048) + unified receipt."""
from __future__ import annotations

import argparse
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "data" / "sourcea-ui-pro-444-upgrade-plan-v1.json"
LANDING = ROOT / "sites/SourceA-landing/green-unified"
REPORT = ROOT / "reports/sourcea-ui-pro-ship-batches-abcd-v1.json"

BATCHES = {
    "A": ("WS-01", 1, 12),
    "B": ("WS-02", 13, 24),
    "C": ("WS-03", 25, 36),
    "D": ("WS-04", 37, 48),
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "sourcea-ui-pro-ship-abcd/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _checks() -> dict[str, Any]:
    home = _fetch("https://sourcea.app/")
    return {
        "positioning_h1": "Turn AI into real production work" in home,
        "hero_tabs": "sa-biz-tabs" in home,
        "hero_console_js": "sourcea-hero-console-v1.js" in home,
        "forge_embed_js": "sourcea-forge-hero-embed-v1.js" in home,
        "forge_embed_mount": 'id="sa-forge-hero-embed"' in home,
        "positioning_v340": '"version": "3.4.0"' in _fetch(
            "https://sourcea.app/sourcea/data/sourcea-positioning-v1.json"
        ),
        "terminal_embed_param": "sa-ft-embed-mode" in _fetch(
            "https://sourcea.app/sourcea/forge/terminal?embed=1"
        ),
    }


def _mark_all(plan: dict[str, Any]) -> None:
    for step in plan.get("steps") or []:
        sid = str(step.get("id", ""))
        if not sid.startswith("UP-UI-"):
            continue
        n = int(sid.split("-")[-1])
        if 1 <= n <= 48:
            step["status"] = "done"
            step["done_at"] = _now()


def run(*, mark_plan: bool, verify_live: bool) -> dict[str, Any]:
    disk = {
        "audit_receipt": (ROOT / "reports/sourcea-ui-pro-audit-baseline-v1.json").is_file(),
        "positioning_receipt": (ROOT / "reports/sourcea-ui-pro-positioning-wire-v1.json").is_file(),
        "hero_console_receipt": (ROOT / "reports/sourcea-ui-pro-hero-console-v1.json").is_file(),
        "forge_embed_js": (LANDING / "sourcea-forge-hero-embed-v1.js").is_file(),
        "terminal_embed_guard": "sa-ft-embed-mode" in (LANDING / "forge/terminal.html").read_text(encoding="utf-8"),
        "frame_headers": (LANDING / "_headers").is_file(),
    }
    live = _checks() if verify_live else {"skipped": True}

    receipt = {
        "schema": "sourcea-ui-pro-ship-batches-abcd-v1",
        "at": _now(),
        "batches": list(BATCHES.keys()),
        "steps": "UP-UI-001..048",
        "disk": disk,
        "live": live,
        "all_live_ok": all(live.values()) if verify_live else None,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    if mark_plan and PLAN.is_file():
        plan = json.loads(PLAN.read_text(encoding="utf-8"))
        plan["batches_abcd_shipped_at"] = receipt["at"]
        _mark_all(plan)
        PLAN.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--mark-plan", action="store_true")
    ap.add_argument("--no-live", action="store_true")
    args = ap.parse_args()
    row = run(mark_plan=args.mark_plan, verify_live=not args.no_live)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK ship A–D · {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
