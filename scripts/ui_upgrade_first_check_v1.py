#!/usr/bin/env python3
"""UI upgrade FIRST CHECK — mandatory before any form/app/website UI edit.

Law: brain-os/law/enforcement/SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md
Wire receipt: ~/.sina/ui-upgrade-first-check-receipt-v1.json
Surface acks: ~/.sina/ui-upgrade-surface-acks-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
SINA = Path.home() / ".sina"
WIRE_RECEIPT = SINA / "ui-upgrade-first-check-receipt-v1.json"
SURFACE_ACKS = SINA / "ui-upgrade-surface-acks-v1.json"
SESSION_RECEIPT = SINA / "agent_session_gate_receipt_v1.json"
SURFACES = SINA / "agent-live-surfaces-v1.json"

ACK_TTL_HOURS = 12
FOUNDER_BYPASS = re.compile(
    r"(UI\s*UPGRADE|UP\s*CHECKLIST|EDIT\s*ALLOWED|UPGRADE\s*UI|^\s*up\b)",
    re.I,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _parse_ts(raw: str) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _fresh_enough(raw: str, *, hours: int = ACK_TTL_HOURS) -> bool:
    ts = _parse_ts(raw)
    if not ts:
        return False
    age = datetime.now(timezone.utc) - ts
    return age.total_seconds() < hours * 3600


def _run_validator() -> tuple[bool, str]:
    cmd = ["bash", str(ROOT / "scripts/validate-ui-upgrade-mandatory-v1.sh")]
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=90)
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode == 0, out.strip()[-400:]
    except Exception as exc:
        return False, str(exc)


def wire(*, surface_id: str = "worker_hub") -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from ui_upgrade_mandatory_gate_v1 import assess, sync_receipt  # noqa: WPS433

    val_ok, val_tail = _run_validator()
    assess_row = assess(surface_id=surface_id)
    sync_receipt(surface_id=surface_id)
    zero = (SINA / "founder-zero-ui-drift-v1.flag").is_file()
    drift_tag = " · ZERO-DRIFT=ON" if zero else ""
    line = (
        f"UI-FIRST-CHECK · wired=YES · validator={'PASS' if val_ok else 'FAIL'} · "
        f"surfaces=8 · law=UP-0..UP-7 · ack_before_edit=mandatory{drift_tag}"
    )
    receipt = {
        "schema": "ui-upgrade-first-check-receipt-v1",
        "saved_at": _now(),
        "ok": val_ok,
        "wire_ok": val_ok,
        "assess_ok": bool(assess_row.get("ok")),
        "surface_id": surface_id,
        "line": line,
        "law": "SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md",
        "cursor_rules": [
            ".cursor/rules/024-ui-upgrade-mandatory-checklist.mdc",
            ".cursor/rules/025-ui-upgrade-first-check-live-wire.mdc",
            ".cursor/rules/026-ui-first-check-zero-exception.mdc",
        ],
        "validator": "scripts/validate-ui-upgrade-mandatory-v1.sh",
        "first_check_cmd": "python3 scripts/ui_upgrade_first_check_v1.py --surface <id> --ack --json",
        "classifier_cmd": "python3 scripts/ui_upgrade_path_classifier_v1.py --path <file> --json",
        "checklist": assess_row.get("checklist") or [],
        "validator_tail": val_tail,
    }
    _write(WIRE_RECEIPT, receipt)
    if SURFACES.is_file():
        surf = _read(SURFACES)
        surf["ui_upgrade_first_check_line"] = line
        surf["ui_upgrade_first_check"] = {
            "id": "ui_upgrade_first_check",
            "ok": receipt["ok"],
            "wire_ok": val_ok,
            "law": receipt["law"],
            "ack_required": True,
            "surfaces_registry": "data/ui-upgrade-surface-registry-v1.json",
        }
        _write(SURFACES, surf)
    return receipt


def acknowledge(*, surface_id: str) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from ui_upgrade_mandatory_gate_v1 import assess  # noqa: WPS433
    from ui_upgrade_ledger_v1 import show as show_surface  # noqa: WPS433

    assess_row = assess(surface_id=surface_id)
    ledger_row: dict = {}
    try:
        ledger_row = show_surface(surface_id=surface_id)
    except Exception:
        ledger_row = {}

    acks = _read(SURFACE_ACKS)
    if acks.get("schema") != "ui-upgrade-surface-acks-v1":
        acks = {"schema": "ui-upgrade-surface-acks-v1", "acks": {}}
    acks["acks"][surface_id] = {
        "saved_at": _now(),
        "surface_id": surface_id,
        "assess_ok": bool(assess_row.get("ok")),
        "ledger_last": ledger_row.get("last_upgrade_id"),
        "frozen_inventory_count": ledger_row.get("frozen_inventory_count"),
        "checklist_ids": [c.get("id") for c in (assess_row.get("checklist") or [])],
    }
    acks["saved_at"] = _now()
    _write(SURFACE_ACKS, acks)

    line = (
        f"UI-FIRST-CHECK · ack={surface_id} · UP-0..UP-7 · "
        f"ledger={'YES' if ledger_row else 'template'} · edit_allowed=YES"
    )
    return {
        "ok": bool(assess_row.get("ok")),
        "surface_id": surface_id,
        "line": line,
        "assess": assess_row,
        "ledger": ledger_row,
        "acks_path": str(SURFACE_ACKS),
        "message": "FIRST CHECK complete — general UP + per-app ledger read. Safe to edit UI for this surface.",
    }


def check_write(*, path: str, explicit_order: str = "") -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from ui_upgrade_path_classifier_v1 import classify_ui_path  # noqa: WPS433

    cls = classify_ui_path(path)
    if not cls.get("is_ui"):
        return {
            "ok": True,
            "skipped": True,
            "reason": "not_ui_path",
            "path": path,
        }

    surface_id = cls.get("surface_id") or "generic_app"
    wire_row = _read(WIRE_RECEIPT)
    wire_ok = bool(wire_row.get("wire_ok"))

    if explicit_order and FOUNDER_BYPASS.search(explicit_order):
        return {
            "ok": True,
            "surface_id": surface_id,
            "path": path,
            "reason": "founder_explicit_order",
            "classify": cls,
            "wire_ok": wire_ok,
        }

    acks = _read(SURFACE_ACKS)
    ack = (acks.get("acks") or {}).get(surface_id) or {}
    ack_fresh = _fresh_enough(str(ack.get("saved_at") or ""))

    if wire_ok and ack_fresh and ack.get("assess_ok", True):
        return {
            "ok": True,
            "surface_id": surface_id,
            "path": path,
            "reason": "surface_ack_fresh",
            "classify": cls,
            "ack_saved_at": ack.get("saved_at"),
        }

    blockers: list[str] = []
    if not wire_ok:
        blockers.append("UI_WIRE_NOT_PASS")
    if not ack_fresh:
        blockers.append("UI_SURFACE_ACK_REQUIRED")

    cmd = f"python3 scripts/ui_upgrade_first_check_v1.py --surface {surface_id} --ack --json"
    checklist = f"python3 scripts/ui_upgrade_mandatory_gate_v1.py --surface {surface_id} --print-checklist"
    ledger = f"python3 scripts/ui_upgrade_ledger_v1.py --surface {surface_id} --show --json"

    return {
        "ok": False,
        "surface_id": surface_id,
        "path": path,
        "classify": cls,
        "blockers": blockers,
        "wire_ok": wire_ok,
        "ack_fresh": ack_fresh,
        "law": "SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md",
        "message": (
            f"UI FIRST CHECK required for {surface_id} — run UP-0..UP-7 before editing. "
            f"Ack: {cmd} · Checklist: {checklist} · Ledger: {ledger}"
        ),
        "first_check_cmd": cmd,
        "checklist_cmd": checklist,
        "ledger_cmd": ledger,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="UI upgrade first check")
    ap.add_argument("--wire", action="store_true", help="Session wire — validator + receipt")
    ap.add_argument("--ack", action="store_true", help="Ack surface — read checklist + ledger")
    ap.add_argument("--check", action="store_true", help="Pre-write check for path")
    ap.add_argument("--surface", default="generic_app")
    ap.add_argument("--path", default="")
    ap.add_argument("--explicit-order", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.wire:
        row = wire(surface_id=args.surface)
    elif args.ack:
        row = acknowledge(surface_id=args.surface)
    elif args.check:
        if not args.path:
            print("FAIL: --path required for --check", file=sys.stderr)
            return 2
        row = check_write(path=args.path, explicit_order=args.explicit_order)
    else:
        row = wire(surface_id=args.surface)

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or row.get("message") or json.dumps(row, indent=2))
    if args.wire:
        return 0 if row.get("wire_ok") else 1
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
