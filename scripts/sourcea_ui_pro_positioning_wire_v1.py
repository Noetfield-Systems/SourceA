#!/usr/bin/env python3
"""WS-02 Batch B — positioning SSOT wire + receipt (UP-UI-013..024)."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "data" / "sourcea-ui-pro-444-upgrade-plan-v1.json"
POSITIONING = ROOT / "sites/SourceA-landing/green-unified/data/sourcea-positioning-v1.json"
LANDING = ROOT / "sites/SourceA-landing/green-unified"
REPORT = ROOT / "reports/sourcea-ui-pro-positioning-wire-v1.json"
WIRE_JS = LANDING / "sourcea-positioning-wire-v1.js"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _fetch(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "sourcea-ui-pro-positioning-wire/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read()
            return {"ok": True, "status": resp.status, "body": body, "sha256": hashlib.sha256(body).hexdigest()[:16]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def _hero_markers(path: Path, pos: dict[str, Any]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    hero = pos.get("hero") or {}
    h1_line = str(hero.get("h1_line1") or "")
    accent = str(hero.get("h1_accent") or "")
    deny = pos.get("hero_denylist") or []
    hero_band = text.split("</section>", 1)[0] if "<section" in text else text[:8000]
    hits = [p for p in deny if p and p.lower() in hero_band.lower()]
    return {
        "path": str(path.relative_to(ROOT)),
        "h1_present": bool(h1_line and h1_line in text and accent in text),
        "taxonomy_present": (hero.get("taxonomy_html") or "")[:24] in text,
        "wire_script": "sourcea-positioning-wire-v1.js" in text,
        "primary_cta_forge": 'data-sa-primary-cta href="/sourcea/forge/terminal"' in text,
        "denylist_hits_in_hero": hits,
        "legal_entity": "Noetfield Systems Inc." in text,
    }


def _mark_ws02_done(plan: dict[str, Any]) -> None:
    for step in plan.get("steps") or []:
        sid = str(step.get("id", ""))
        if not sid.startswith("UP-UI-"):
            continue
        n = int(sid.split("-")[-1])
        if 13 <= n <= 24:
            step["status"] = "done"
            step["done_at"] = _now()


def run(*, mark_plan: bool, refresh_brain: bool) -> dict[str, Any]:
    pos = json.loads(POSITIONING.read_text(encoding="utf-8"))
    if pos.get("schema") != "sourcea-positioning-v1":
        raise SystemExit("FAIL: invalid positioning schema")

    disk_sha = _sha(POSITIONING)
    live = _fetch("https://sourcea.app/sourcea/data/sourcea-positioning-v1.json")
    live_match = None
    if live.get("ok"):
        try:
            live_row = json.loads(live["body"].decode("utf-8"))
            live_match = live_row.get("version") == pos.get("version") and live.get("sha256") == disk_sha
        except json.JSONDecodeError:
            live_match = False

    brain_refresh = {"ok": True, "skipped": True}
    if refresh_brain:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts/distill_brain_public_rules_v1.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=90,
        )
        brain_refresh = {"ok": proc.returncode == 0, "stdout": proc.stdout.strip()[:500]}

    receipt: dict[str, Any] = {
        "schema": "sourcea-ui-pro-positioning-wire-v1",
        "at": _now(),
        "batch": "B",
        "workstream": "WS-02",
        "steps": "UP-UI-013..024",
        "positioning_version": pos.get("version"),
        "one_line": pos.get("one_line"),
        "hero_denylist_count": len(pos.get("hero_denylist") or []),
        "disk_sha256_prefix": disk_sha,
        "wire_js": WIRE_JS.is_file(),
        "pages": {
            "founder_home": _hero_markers(LANDING / "founder-home.html", pos),
            "sourcea_index": _hero_markers(LANDING / "index.html", pos),
        },
        "live_positioning": {
            "ok": live.get("ok"),
            "matches_disk": live_match,
            "note": "Deploy landing to sync live JSON",
        },
        "brain_rules_refresh": brain_refresh,
        "mechanical_gate": "hero_denylist mirrored in positioning SSOT; gate patterns unchanged",
        "publish_note": "Disk ready — deploy landing for live H1 + JSON parity",
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    if mark_plan and PLAN.is_file():
        plan = json.loads(PLAN.read_text(encoding="utf-8"))
        _mark_ws02_done(plan)
        PLAN.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--mark-plan", action="store_true")
    ap.add_argument("--refresh-brain", action="store_true")
    args = ap.parse_args()
    row = run(mark_plan=args.mark_plan, refresh_brain=args.refresh_brain)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK positioning wire · {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
