#!/usr/bin/env python3
"""Mac Law agent execution plane lock — FOREVER on disk · all nerves · all nodes.

Law: AGENTS never factory-build on Mac · cloud executes.
SSOT: data/mac-law-agent-execution-plane-lock-v1.json
Receipt: ~/.sina/mac-law-agent-execution-plane-lock-receipt-v1.json
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
SSOT = ROOT / "data" / "mac-law-agent-execution-plane-lock-v1.json"
RECEIPT = SINA / "mac-law-agent-execution-plane-lock-receipt-v1.json"
LOCK_FLAG = SINA / "mac-law-agent-no-factory-on-mac-locked-v1.flag"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_ssot() -> dict:
    return _read(SSOT)


def assess(*, sync_stack: bool = False) -> dict:
    ssot = load_ssot()
    issues: list[str] = []
    if not ssot.get("locked_forever"):
        issues.append("locked_forever_must_be_true")
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))

    stack: dict = {}
    sync_warnings: list[str] = []
    if sync_stack:
        for mod, fn in (
            ("mac_law_universal_wire_v1", "sync_receipt"),
            ("mac_law_machine_enforce_v1", "sync_receipt"),
            ("mac_law_mandatory_v1", "sync_receipt"),
        ):
            try:
                m = __import__(mod, fromlist=[fn])
                getattr(m, fn)(enforce=False)
            except Exception as exc:
                sync_warnings.append(f"sync:{mod}:{exc}")

    try:
        from mac_law_universal_wire_v1 import assess as uw_assess  # noqa: WPS433

        uw = uw_assess()
        stack["universal_wire"] = {"ok": uw.get("ok"), "line": uw.get("line")}
        if not uw.get("ok"):
            issues.extend(f"universal:{x}" for x in (uw.get("issues") or [])[:5])
    except Exception as exc:
        issues.append(f"universal_load:{exc}")

    fem = _read(ROOT / "data/founder-execution-model-v1.json")
    mer = _read(ROOT / "data/machine-execution-plane-registry-v1.json")
    mac_f = (fem.get("mac_role") or {}).get("canonical") if isinstance(fem.get("mac_role"), dict) else fem.get("mac_role")
    mac_m = mer.get("mac_role")
    role_ok = mac_f == mac_m == "control_plane_only"
    stack["execution_plane"] = {"ok": role_ok, "mac_role": mac_f}
    if not role_ok:
        issues.append("mac_role_not_control_plane_only")

    flag_ok = LOCK_FLAG.is_file()
    stack["lock_flag"] = {"path": str(LOCK_FLAG), "ok": flag_ok}
    if not flag_ok:
        issues.append("lock_flag_missing")

    ok = not issues
    line = (
        f"mac-law-agent-lock · mac-control-only=YES · no-factory-body-on-mac={'YES' if ok else 'NO'} · "
        f"cloud-body={'YES' if role_ok else 'NO'} · ok={'PASS' if ok else 'RED'}"
    )
    row = {
        "ok": ok,
        "issues": issues,
        "line": line,
        "one_law": ssot.get("one_law"),
        "locked_forever": bool(ssot.get("locked_forever")),
        "stack": stack,
    }
    if sync_warnings:
        row["sync_warnings"] = sync_warnings
    return row


def _patch_surfaces(row: dict) -> None:
    surf_path = SINA / "agent-live-surfaces-v1.json"
    patch = {
        "mac_law_agent_lock_line": row.get("line"),
        "mac_law_agent_execution_plane_lock": {
            "ok": row.get("ok"),
            "locked_forever": True,
            "ssot": "data/mac-law-agent-execution-plane-lock-v1.json",
        },
        "mac_law_agent_no_factory_on_mac": bool(row.get("ok")),
    }
    base = _read(surf_path) if surf_path.is_file() else {}
    if not isinstance(base, dict):
        base = {}
    base.update({k: v for k, v in patch.items() if v is not None})
    SINA.mkdir(parents=True, exist_ok=True)
    tmp = surf_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(base, indent=2) + "\n", encoding="utf-8")
    tmp.replace(surf_path)


def sync_receipt(*, enforce: bool = False, full_stack_sync: bool = False) -> dict:
    if enforce:
        SINA.mkdir(parents=True, exist_ok=True)
        if not LOCK_FLAG.is_file():
            LOCK_FLAG.write_text(
                f"Mac Law agent lock · Mac control only · no factory body on Mac · cloud executes · {_now()}\n",
                encoding="utf-8",
            )
    row = assess(sync_stack=full_stack_sync)
    receipt = {"schema": "mac-law-agent-execution-plane-lock-receipt-v1", "saved_at": _now(), **row}
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    _patch_surfaces(row)
    return receipt


def inject_slice() -> dict:
    ssot = load_ssot()
    row = _read(RECEIPT) or assess()
    return {
        "one_law": ssot.get("one_law"),
        "not_this_law": ssot.get("not_this_law"),
        "forbidden_phrase": ssot.get("clarification", {}).get("forbidden_phrase"),
        "clarification": ssot.get("clarification"),
        "vocabulary_ssot": ssot.get("worker_vs_factory_ssot"),
        "incident_038": ssot.get("incident_038"),
        "line": row.get("line"),
        "locked_forever": True,
        "ssot": str(SSOT.relative_to(ROOT)),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Mac Law agent execution plane lock")
    ap.add_argument("--assess", action="store_true")
    ap.add_argument("--sync-receipt", action="store_true")
    ap.add_argument("--enforce", action="store_true", help="Ensure lock flag only — no nested sync stack")
    ap.add_argument(
        "--full-stack-sync",
        action="store_true",
        help="Cloud CI / ship window only — sync child receipts (forbidden Mac founder session)",
    )
    ap.add_argument("--inject", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.inject:
        row = inject_slice()
    elif args.sync_receipt:
        row = sync_receipt(enforce=args.enforce, full_stack_sync=args.full_stack_sync)
    else:
        row = assess()

    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(row.get("line") or row.get("one_law") or json.dumps(row))
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
