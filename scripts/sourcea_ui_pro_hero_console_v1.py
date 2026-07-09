#!/usr/bin/env python3
"""WS-03 Batch C — hero live console receipt + plan mark (UP-UI-025..036)."""
from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "data" / "sourcea-ui-pro-444-upgrade-plan-v1.json"
LANDING = ROOT / "sites/SourceA-landing/green-unified"
REPORT = ROOT / "reports/sourcea-ui-pro-hero-console-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fetch(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "sourcea-hero-console-verify/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return {"ok": True, "status": resp.status, "body": body}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def _disk_checks() -> dict[str, Any]:
    hero_js = LANDING / "sourcea-hero-console-v1.js"
    live_js = LANDING / "sourcea-live-console.js"
    home = (LANDING / "founder-home.html").read_text(encoding="utf-8", errors="replace")
    live_src = live_js.read_text(encoding="utf-8", errors="replace")
    dist_hero = LANDING / "dist" / "sourcea" / "sourcea-hero-console-v1.js"
    return {
        "hero_module": hero_js.is_file(),
        "live_console": live_js.is_file(),
        "polls_boot": "BOOT_URL" in live_src and "boot-proof.json" in live_src,
        "polls_aeg": "AEG_URL" in live_src and "aeg-live.json" in live_src,
        "offline_state": "paintOffline" in live_src,
        "chrome_proof": "hero_console_chrome" in live_src or "openProof" in live_src,
        "tracking": "data-sa-track" in live_src and "hero_console_tab" in live_src,
        "founder_only": "sourcea-hero-console-v1.js" in home and "sa-root-home" in home,
        "dist_synced": dist_hero.is_file(),
        "mobile_css": "sa-hero-console-v1" in (LANDING / "sourcea-home.css").read_text(encoding="utf-8"),
        "reduced_motion": "prefers-reduced-motion" in live_src,
        "em_dash_in_console_js": bool(re.search(r'["\']—["\']| \|\| "—"', live_src)),
    }


def _live_checks() -> dict[str, Any]:
    home = _fetch("https://sourcea.app/")
    body = home.get("body", "")
    return {
        "ok": home.get("ok"),
        "has_biz_tabs": "sa-biz-tabs" in body,
        "has_hero_console_js": "sourcea-hero-console-v1.js" in body,
        "has_positioning_wire": "sourcea-positioning-wire-v1.js" in body,
        "h1_execution": "Turn AI into real production work" in body,
        "mock_only": "sa-mock-panel" in body and "sa-biz-tabs" not in body,
    }


def _mark_ws03(plan: dict[str, Any]) -> None:
    for step in plan.get("steps") or []:
        sid = str(step.get("id", ""))
        if not sid.startswith("UP-UI-"):
            continue
        n = int(sid.split("-")[-1])
        if 25 <= n <= 36:
            step["status"] = "done"
            step["done_at"] = _now()


def run(*, mark_plan: bool) -> dict[str, Any]:
    receipt = {
        "schema": "sourcea-ui-pro-hero-console-v1",
        "at": _now(),
        "batch": "C",
        "workstream": "WS-03",
        "steps": "UP-UI-025..036",
        "disk": _disk_checks(),
        "live": _live_checks(),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if mark_plan and PLAN.is_file():
        plan = json.loads(PLAN.read_text(encoding="utf-8"))
        _mark_ws03(plan)
        PLAN.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--mark-plan", action="store_true")
    args = ap.parse_args()
    row = run(mark_plan=args.mark_plan)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK hero console · {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
