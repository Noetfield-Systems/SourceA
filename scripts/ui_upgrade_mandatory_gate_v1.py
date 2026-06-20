#!/usr/bin/env python3
"""UI upgrade mandatory gate — UP checklist assess + receipt.

Law: brain-os/enforcement/SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md
SSOT: data/ui-upgrade-surface-registry-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "ui-upgrade-surface-registry-v1.json"
RECEIPT = Path.home() / ".sina" / "ui-upgrade-mandatory-receipt-v1.json"
SURFACES = Path.home() / ".sina" / "agent-live-surfaces-v1.json"

CHECKLIST = [
    {"id": "UP-0", "step": "Declare surface_id + target files + founder URL"},
    {"id": "UP-1", "step": "Read all blueprint paths for surface (law + incident + baseline)"},
    {"id": "UP-2", "step": "Inventory last good version — pre_edit command + section list"},
    {"id": "UP-3", "step": "Plan additive edit only — nothing deleted without UI BASELINE BUMP"},
    {"id": "UP-4", "step": "Edit governed paths — pre_write_guard + landing baseline check"},
    {"id": "UP-5", "step": "Run surface verify command — machine PASS"},
    {"id": "UP-6", "step": "Prove live — e2e / browser / DOM markers"},
    {"id": "UP-7", "step": "Paste UI UPGRADE SHIP SUMMARY in founder reply (same turn)"},
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def load_registry() -> dict:
    if not REGISTRY.is_file():
        raise SystemExit(f"FAIL: registry missing — {REGISTRY}")
    row = _read(REGISTRY)
    if row.get("schema") != "ui-upgrade-surface-registry-v1":
        raise SystemExit(f"FAIL: bad schema — {row.get('schema')}")
    return row


def _resolve_blueprints(surface: dict) -> list[dict]:
    out: list[dict] = []
    for raw in surface.get("blueprint") or []:
        p = Path(str(raw).replace("~/", str(Path.home()) + "/"))
        out.append({"path": str(raw), "exists": p.is_file()})
    return out


def _resolve_ledger(surface: dict) -> dict:
    ledger_md = surface.get("ledger_md")
    ledger_json = surface.get("ledger_json")
    info = {"ledger_md": ledger_md, "ledger_json": ledger_json}
    if ledger_md:
        p = ROOT / ledger_md
        info["ledger_md_exists"] = p.is_file()
    if ledger_json:
        p = ROOT / ledger_json
        info["ledger_json_exists"] = p.is_file()
        if p.is_file():
            try:
                led = _read(p)
                upgrades = led.get("upgrades") or []
                info["upgrade_count"] = len(upgrades)
                info["last_upgrade_id"] = upgrades[-1].get("upgrade_id") if upgrades else None
                info["frozen_inventory_count"] = len(led.get("frozen_inventory") or [])
            except Exception:
                info["ledger_json_parse"] = False
    return info


def assess(*, surface_id: str) -> dict:
    reg = load_registry()
    surfaces = reg.get("surfaces") or {}
    if surface_id not in surfaces:
        return {
            "ok": False,
            "surface_id": surface_id,
            "issues": [f"unknown_surface:{surface_id}"],
            "known_surfaces": sorted(surfaces.keys()),
        }
    surface = surfaces[surface_id]
    issues: list[str] = []
    blueprints = _resolve_blueprints(surface)
    for bp in blueprints:
        if not bp["exists"]:
            issues.append(f"blueprint_missing:{bp['path']}")

    ledger_info = _resolve_ledger(surface)
    ledger_ok = True
    if surface_id != "generic_app":
        if not ledger_info.get("ledger_md_exists"):
            issues.append("ledger_md_missing")
            ledger_ok = False
        if surface.get("ledger_json") and not ledger_info.get("ledger_json_exists"):
            issues.append("ledger_json_missing")
            ledger_ok = False

    line = (
        f"UI-UP · surface={surface_id} · "
        f"blueprints={sum(1 for b in blueprints if b['exists'])}/{len(blueprints)} · "
        f"ledger={'YES' if ledger_ok else 'NO'} · "
        f"ok={'YES' if not issues else 'NO'}"
    )
    return {
        "ok": not issues,
        "surface_id": surface_id,
        "label": surface.get("label"),
        "repo": surface.get("repo"),
        "url": surface.get("url"),
        "issues": issues,
        "line": line,
        "checklist": CHECKLIST,
        "blueprints": blueprints,
        "ledger": ledger_info,
        "commands": {
            "pre_edit": surface.get("pre_edit"),
            "verify": surface.get("verify"),
            "e2e": surface.get("e2e"),
        },
        "dom_must_contain": surface.get("dom_must_contain"),
        "dom_must_not_contain": surface.get("dom_must_not_contain"),
        "ship_summary_template": "brain-os/enforcement/SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md §5",
        "one_law": reg.get("one_law"),
        "founder_triggers": reg.get("founder_triggers"),
    }


def sync_receipt(*, surface_id: str) -> dict:
    row = assess(surface_id=surface_id)
    receipt = {
        "schema": "ui-upgrade-mandatory-receipt-v1",
        "saved_at": _now(),
        **row,
    }
    _write(RECEIPT, receipt)
    if SURFACES.is_file():
        surf = _read(SURFACES)
        surf["ui_upgrade_mandatory_line"] = row.get("line")
        surf["ui_upgrade_mandatory"] = {
            "id": "ui_upgrade_mandatory",
            "ok": row.get("ok"),
            "surface_id": surface_id,
            "ssot": "data/ui-upgrade-surface-registry-v1.json",
        }
        _write(SURFACES, surf)
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="UI upgrade mandatory gate")
    ap.add_argument("--surface", default="generic_app")
    ap.add_argument("--assess", action="store_true")
    ap.add_argument("--sync-receipt", action="store_true")
    ap.add_argument("--print-checklist", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.sync_receipt:
        row = sync_receipt(surface_id=args.surface)
    else:
        row = assess(surface_id=args.surface)

    if args.print_checklist and not args.json:
        print(f"UI UP checklist — surface={args.surface}")
        for item in CHECKLIST:
            print(f"  {item['id']}: {item['step']}")
        return 0 if row.get("ok") else 1

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
