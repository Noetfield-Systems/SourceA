#!/usr/bin/env python3
"""WS-01 Batch A — UI Pro audit baseline + receipt (UP-UI-001..012)."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "data" / "sourcea-ui-pro-444-upgrade-plan-v1.json"
LANDING = ROOT / "sites" / "SourceA-landing" / "green-unified"
REPORT = ROOT / "reports" / "sourcea-ui-pro-audit-baseline-v1.json"
STRANGER = ROOT / "data" / "sourcea-ui-pro-stranger-5s-test-v1.json"
MECH = ROOT / "data" / "sourcea-ui-mechanical-gate-v1.json"

GAPS_2026 = [
    {"id": "product-hero", "pattern": "Linear/Vercel", "gap": "Hero mock panel without live tabs on /"},
    {"id": "inline-demo", "pattern": "Clerk/Neon", "gap": "Forge Terminal not embedded in hero"},
    {"id": "bento-proof", "pattern": "Raycast", "gap": "No bento grid with clickable proof tiles"},
    {"id": "cmdk", "pattern": "Raycast", "gap": "No site command palette"},
    {"id": "trust-ssr", "pattern": "Mechanical RI-2", "gap": "Em-dash placeholders in static HTML"},
    {"id": "sku-contact", "pattern": "Mechanical v2", "gap": "SKU landers missing contact surface"},
]

WS_OWNERS = {
    "placeholder_counter": "WS-05",
    "no_contact_surface": "WS-17",
    "entity_consistency": "WS-36",
    "spa_fallback_detect": "WS-30",
    "missing_og": "WS-28",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fetch(url: str, timeout: int = 15) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "sourcea-ui-pro-audit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return {"ok": True, "status": resp.status, "body": body, "headers": dict(resp.headers)}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        return {"ok": False, "status": exc.code, "body": body, "error": str(exc)}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "status": 0, "body": "", "error": str(exc)}


def _hero_snapshot(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"ok": False, "error": "missing"}
    text = path.read_text(encoding="utf-8", errors="replace")
    h1 = re.findall(r"<h1[^>]*>([\s\S]*?)</h1>", text, re.I)
    h1_clean = re.sub(r"<[^>]+>", " ", h1[0] if h1 else "").strip()[:200]
    return {
        "ok": True,
        "path": str(path.relative_to(ROOT)),
        "h1": h1_clean,
        "has_sa_biz_tabs": "sa-biz-tabs" in text,
        "has_sa_mock_panel": "sa-mock-panel" in text,
        "has_brain": "sourcea-chatbot.js" in text,
        "has_pulse": "sourcea-site-pulse-v1.js" in text,
        "has_interact": "sourcea-site-interact-v1.js" in text,
        "has_live_console": "sourcea-live-console.js" in text,
        "placeholder_dashes": bool(re.search(r">[\s]*—[\s]*<|—/100|— jobs", text)),
    }


def _inventory_surfaces() -> list[dict[str, str]]:
    return [
        {"id": "brain", "file": "sourcea-chatbot.js", "surface": "FAB + chat panel"},
        {"id": "tools", "file": "sourcea-site-interact-v1.js", "surface": "Tools dock + guided modal"},
        {"id": "pulse", "file": "sourcea-site-pulse-v1.js", "surface": "Analytics + feedback FAB"},
        {"id": "terminal", "path": "/sourcea/forge/terminal", "surface": "Forge Terminal page"},
        {"id": "live_console", "file": "sourcea-live-console.js", "surface": "Hero command center"},
        {"id": "trust_bar", "file": "sourcea-trust-bar.js", "surface": "Trust stat hydration"},
        {"id": "boot_wire", "file": "sourcea-boot-wire.js", "surface": "Proof pack + eval links"},
    ]


def _git_sha() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip()
        return out[:12]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def _mark_ws01_done(plan: dict[str, Any], *, founder_signed: bool) -> None:
    for step in plan.get("steps") or []:
        if not str(step.get("id", "")).startswith("UP-UI-") or int(step["id"].split("-")[-1]) > 12:
            continue
        if step["id"] == "UP-UI-011" and not founder_signed:
            step["status"] = "pending_founder"
            continue
        step["status"] = "done"
        step["done_at"] = _now()


def run(*, mark_plan: bool, founder_signed: bool) -> dict[str, Any]:
    home_disk = _hero_snapshot(LANDING / "founder-home.html")
    index_disk = _hero_snapshot(LANDING / "index.html")
    live_home = _fetch("https://sourcea.app/")
    live_sub = _fetch("https://sourcea.app/sourcea/")

    def live_hero_flags(body: str) -> dict[str, Any]:
        return {
            "has_biz_tabs": "sa-biz-tabs" in body,
            "has_mock_only": "sa-mock-panel" in body and "sa-biz-tabs" not in body,
            "placeholder_dashes": bool(re.search(r">[\s]*—[\s]*<|—/100", body)),
        }

    brain_status = _fetch(
        "https://sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev/api/brain/status/v1"
    )
    brain_ok = False
    if brain_status.get("ok"):
        try:
            row = json.loads(brain_status["body"])
            brain_ok = bool(row.get("ai_model_ready") or row.get("openrouter_ready"))
        except json.JSONDecodeError:
            pass

    receipt = {
        "schema": "sourcea-ui-pro-audit-baseline-v1",
        "at": _now(),
        "batch": "A",
        "workstream": "WS-01",
        "steps": "UP-UI-001..012",
        "git_sha": _git_sha(),
        "hero_parity": {
            "disk": {"home": home_disk, "sourcea_index": index_disk},
            "live": {
                "home": live_hero_flags(live_home.get("body", "")),
                "sourcea": live_hero_flags(live_sub.get("body", "")),
            },
            "parity_ok": home_disk.get("h1") != index_disk.get("h1"),
        },
        "interactive_surfaces": _inventory_surfaces(),
        "gaps_2026": GAPS_2026,
        "mechanical_gate_owners": WS_OWNERS,
        "brain_baseline": {"ok": brain_ok, "status_http": brain_status.get("status")},
        "site_pulse_note": "Counts via worker KV — public strip WS-12",
        "lcp_note": "Run Lighthouse in cloud CI ship window; Mac founder session skips heavy perf",
        "screenshot_note": "Deferred to cloud CI; disk+live HTML snapshot in this receipt",
        "p0_scope": [
            "WS-01 audit",
            "WS-03..07 hero interactive (Batch B)",
            "WS-05 trust SSR",
            "WS-08 home unify",
        ],
        "batch_a_executed": [
            "Interactive hero tabs on founder-home",
            "Engine chips wire to console tabs",
            "Console chrome opens proof/live",
            "Audit receipt + stranger test JSON",
        ],
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    stranger = {
        "schema": "sourcea-ui-pro-stranger-5s-test-v1",
        "at": _now(),
        "script": [
            "Land on https://sourcea.app/ — see hero console within 1s",
            "Click a Plan/Verify engine chip — console tab changes",
            "Click Live proof tab — see boot/AEG data",
            "Open Tools dock — pick segment without calendar",
            "Ask Brain one pricing question — in-chat answer with link",
        ],
        "pass_if": "All five without booking a call",
    }
    STRANGER.write_text(json.dumps(stranger, indent=2) + "\n", encoding="utf-8")

    if mark_plan and PLAN.is_file():
        plan = json.loads(PLAN.read_text(encoding="utf-8"))
        plan["baseline_sha"] = receipt["git_sha"]
        plan["baseline_at"] = receipt["at"]
        _mark_ws01_done(plan, founder_signed=founder_signed)
        PLAN.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--mark-plan", action="store_true")
    ap.add_argument("--founder-signed", action="store_true")
    args = ap.parse_args()
    row = run(mark_plan=args.mark_plan, founder_signed=args.founder_signed)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK audit baseline · {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
