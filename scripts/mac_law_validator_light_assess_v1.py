#!/usr/bin/env python3
"""Mac Law validator light assess — ONE python process · no nested sync · no bash chains.

Law: INCIDENT-039 · INCIDENT-040 · Mac Law validators must NOT heat Mac body.
Use: bash validate-mac-law-*-v1.sh → calls this for disk proof (assess only).
Heavy --full-stack-sync / surfaces boot → cloud CI or validate-mac-law-mandatory-ship-v1.sh only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _grep(rel: str, needle: str) -> bool:
    p = ROOT / rel
    if not p.is_file():
        return False
    try:
        return needle in p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def light_assess(*, module: str = "all") -> dict:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))

    checks: list[dict] = []
    modules = (
        ["universal", "lock", "machine", "mandatory"]
        if module == "all"
        else [module]
    )

    if "universal" in modules:
        from mac_law_universal_wire_v1 import assess as uw_assess  # noqa: WPS433

        uw = uw_assess()
        rec = _read(SINA / "mac-law-universal-wire-receipt-v1.json")
        checks.append(
            {
                "id": "universal_assess",
                "ok": bool(uw.get("ok")),
                "line": (uw.get("line") or "")[:120],
            }
        )
        checks.append(
            {
                "id": "universal_receipt",
                "ok": bool(rec.get("ok")) if rec else bool(uw.get("ok")),
                "present": bool(rec),
            }
        )
        for rel, needle, cid in (
            ("scripts/agent_session_gate_run_v1.py", "mac_law_universal_wire", "wire_session_gate"),
            ("scripts/pre_write_guard_v1.py", "mac_law_universal", "wire_pre_write"),
            ("scripts/agent_memory_mirror_v1.py", "mac_law_universal", "wire_mirror"),
        ):
            ok = _grep(rel, needle)
            checks.append({"id": cid, "ok": ok})

    if "lock" in modules:
        from mac_law_agent_execution_plane_lock_v1 import assess as lock_assess  # noqa: WPS433

        lk = lock_assess(sync_stack=False)
        rec = _read(SINA / "mac-law-agent-execution-plane-lock-receipt-v1.json")
        flag = SINA / "mac-law-agent-no-factory-on-mac-locked-v1.flag"
        ssot = _read(ROOT / "data/mac-law-agent-execution-plane-lock-v1.json")
        checks.append({"id": "lock_assess", "ok": bool(lk.get("ok")), "line": (lk.get("line") or "")[:120]})
        checks.append({"id": "lock_receipt", "ok": bool(rec.get("ok")) if rec else bool(lk.get("ok")), "present": bool(rec)})
        checks.append({"id": "lock_flag", "ok": flag.is_file()})
        checks.append({"id": "locked_forever", "ok": bool(ssot.get("locked_forever"))})
        checks.append(
            {
                "id": "wire_nerve_ship_gate",
                "ok": _grep("scripts/agent_nerve_system_v1.py", "mac_law_agent_no_factory_on_mac"),
            }
        )

    if "machine" in modules:
        from mac_law_machine_enforce_v1 import assess as ml_assess  # noqa: WPS433

        ml = ml_assess()
        rec = _read(SINA / "mac-law-machine-enforce-receipt-v1.json")
        checks.append({"id": "machine_assess", "ok": bool(ml.get("ok")), "line": (ml.get("line") or "")[:120]})
        checks.append({"id": "machine_receipt", "ok": bool(rec.get("ok")) if rec else bool(ml.get("ok")), "present": bool(rec)})
        checks.append({"id": "wire_conduct", "ok": _grep("scripts/agentic_conduct_gate_v1.py", "mac_law_machine_enforce")})

    if "mandatory" in modules:
        from mac_law_mandatory_v1 import assess as mand_assess  # noqa: WPS433

        md = mand_assess(enforce=False)
        rec = _read(SINA / "mac-law-mandatory-receipt-v1.json")
        checks.append({"id": "mandatory_assess", "ok": bool(md.get("ok")), "line": (md.get("line") or "")[:120]})
        checks.append({"id": "mandatory_receipt", "ok": bool(rec.get("ok")) if rec else bool(md.get("ok")), "present": bool(rec)})
        for path in (
            Path.home() / "Desktop/MacLaw/MAC_LAW_SSOT_LOCKED.md",
            Path.home() / "Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md",
            Path.home() / "Desktop/MacLaw/MAC_HEALTH_AGENT_MANDATES_LOCKED.md",
        ):
            checks.append({"id": f"law_doc_{path.stem[:24]}", "ok": path.is_file()})

    ok = all(c.get("ok") for c in checks)
    passed = sum(1 for c in checks if c.get("ok"))
    return {
        "ok": ok,
        "schema": "mac-law-validator-light-assess-v1",
        "module": module,
        "checks": checks,
        "passed": passed,
        "total": len(checks),
        "line": f"mac-law-light · {passed}/{len(checks)} PASS · assess-only · no-nested-sync",
        "one_law": "Mac Law validators = assess + read receipts — never --enforce chains on Mac founder session",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Mac Law light validator assess (single process)")
    ap.add_argument("--module", default="all", choices=["all", "universal", "lock", "machine", "mandatory"])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = light_assess(module=args.module)
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(row.get("line"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
