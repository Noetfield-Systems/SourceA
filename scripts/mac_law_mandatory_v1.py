#!/usr/bin/env python3
"""Mac Law mandatory — boss order · control plane · health mandates on every session.

Law: data/mac-law-mandatory-v1.json
Docs: ~/Desktop/MacLaw/MAC_LAW_SSOT_LOCKED.md · MAC_CONTROL_PLANE_LOCKED.md
Receipt: ~/.sina/mac-law-mandatory-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "mac-law-mandatory-v1.json"
RECEIPT = SINA / "mac-law-mandatory-receipt-v1.json"
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


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _expand(path: str) -> Path:
    return Path(path.replace("~", str(Path.home())))


def load_ssot() -> dict:
    return _read(SSOT)


def _law_docs_ok(ssot: dict) -> tuple[list[str], dict]:
    issues: list[str] = []
    docs: dict = {}
    for key, rel in (ssot.get("law_docs") or {}).items():
        path = _expand(str(rel))
        ok = path.is_file()
        docs[key] = {"path": str(path), "ok": ok}
        if not ok:
            issues.append(f"missing_law:{key}")
    return issues, docs


def _flags_ok(ssot: dict) -> tuple[list[str], dict]:
    issues: list[str] = []
    row: dict = {"present": {}, "absent": {}}
    for rel in ssot.get("mandatory_flags", {}).get("present") or []:
        path = _expand(str(rel))
        ok = path.is_file()
        row["present"][rel] = ok
        if not ok:
            issues.append(f"flag_missing:{Path(rel).name}")
    for rel in ssot.get("mandatory_flags", {}).get("absent") or []:
        path = _expand(str(rel))
        ok = not path.is_file()
        row["absent"][rel] = ok
        if not ok:
            issues.append(f"flag_must_be_absent:{Path(rel).name}")
    return issues, row


def _cursor_rules_ok(ssot: dict) -> tuple[list[str], dict]:
    issues: list[str] = []
    rules: dict = {}
    for rel in ssot.get("cursor_rules") or []:
        path = ROOT / rel
        ok = path.is_file()
        rules[rel] = ok
        if not ok:
            issues.append(f"missing_cursor_rule:{rel}")
    return issues, rules


def assess(*, enforce: bool = False) -> dict:
    ssot = load_ssot()
    issues: list[str] = []
    if not ssot:
        issues.append("missing SSOT data/mac-law-mandatory-v1.json")

    law_issues, law_docs = _law_docs_ok(ssot) if ssot else ([], {})
    issues.extend(law_issues)

    flag_issues, flags = _flags_ok(ssot) if ssot else ([], {})
    issues.extend(flag_issues)

    rule_issues, cursor_rules = _cursor_rules_ok(ssot) if ssot else ([], {})
    issues.extend(rule_issues)

    control_plane: dict = {}
    health_mandates: dict = {}
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))

    try:
        from mac_control_plane_v1 import assess as cp_assess  # noqa: WPS433

        control_plane = cp_assess()
        if not control_plane.get("ok"):
            issues.extend(f"control_plane:{x}" for x in (control_plane.get("issues") or []))
    except Exception as exc:
        issues.append(f"control_plane_load:{exc}")
        control_plane = {"ok": False, "error": str(exc)[:120]}

    try:
        from mac_health_agent_mandates_v1 import run_agent_mandates_probe  # noqa: WPS433

        health_mandates = run_agent_mandates_probe(side_effects=enforce)
        if not health_mandates.get("ok"):
            issues.extend(f"health_mandate:{v.get('id', v)}" for v in (health_mandates.get("violations") or []))
    except Exception as exc:
        issues.append(f"health_mandates_load:{exc}")
        health_mandates = {"ok": False, "error": str(exc)[:120]}

    ok = not issues
    line = (
        f"MAC-LAW · boss=YES · control_plane={'PASS' if control_plane.get('ok') else 'RED'} · "
        f"health={'PASS' if health_mandates.get('ok') else 'RED'} · ok={'YES' if ok else 'NO'}"
    )
    return {
        "ok": ok,
        "issues": issues,
        "line": line,
        "law_docs": law_docs,
        "flags": flags,
        "cursor_rules": cursor_rules,
        "control_plane": {"ok": control_plane.get("ok"), "issues": control_plane.get("issues")},
        "health_mandates": {"ok": health_mandates.get("ok"), "violations": health_mandates.get("violations")},
        "one_law": ssot.get("one_law") if ssot else "",
    }


def sync_receipt(*, enforce: bool = False, full_stack_sync: bool = False) -> dict:
    row = assess(enforce=enforce)
    receipt = {
        "schema": "mac-law-mandatory-receipt-v1",
        "saved_at": _now(),
        **row,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    _write(RECEIPT, receipt)

    if SURFACES.is_file():
        surf = _read(SURFACES)
        surf["mac_law_mandatory_line"] = row.get("line")
        surf["mac_law_mandatory"] = {
            "id": "mac_law_mandatory",
            "ok": row.get("ok"),
            "ssot": "data/mac-law-mandatory-v1.json",
        }
        _write(SURFACES, surf)
    if full_stack_sync and str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    if full_stack_sync:
        try:
            from mac_law_universal_wire_v1 import sync_receipt as universal_sync  # noqa: WPS433
            from mac_law_agent_execution_plane_lock_v1 import sync_receipt as lock_sync  # noqa: WPS433

            universal_sync(enforce=False, full_stack_sync=False)
            lock_sync(enforce=False, full_stack_sync=False)
        except Exception:
            pass
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Mac Law mandatory gate")
    ap.add_argument("--assess", action="store_true")
    ap.add_argument("--sync-receipt", action="store_true")
    ap.add_argument("--enforce", action="store_true", help="Run health mandate side-effects if needed")
    ap.add_argument(
        "--full-stack-sync",
        action="store_true",
        help="Cloud CI / ship window only — sync child Mac Law receipts (forbidden Mac founder session)",
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.sync_receipt:
        row = sync_receipt(enforce=args.enforce, full_stack_sync=args.full_stack_sync)
    else:
        row = assess(enforce=args.enforce)

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
