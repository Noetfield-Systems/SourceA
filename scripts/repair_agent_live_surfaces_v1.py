#!/usr/bin/env python3
"""Repair poisoned ~/.sina/agent-live-surfaces-v1.json from truth bundle + Mac Law receipts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SINA = Path.home() / ".sina"
TRUTH = SINA / "last-truth-bundle-v1.json"
SURFACES = SINA / "agent-live-surfaces-v1.json"
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def main() -> int:
    truth = _read(TRUTH)
    base = truth.get("live_surfaces") if isinstance(truth.get("live_surfaces"), dict) else {}
    if not base:
        print("FAIL: truth bundle missing live_surfaces", file=sys.stderr)
        return 1

    sys.path.insert(0, str(SCRIPTS))
    from mac_law_universal_wire_v1 import sync_receipt as uw_sync  # noqa: WPS433
    from mac_law_agent_execution_plane_lock_v1 import sync_receipt as lock_sync  # noqa: WPS433
    from mac_law_mandatory_v1 import sync_receipt as mandatory_sync  # noqa: WPS433
    from mac_law_machine_enforce_v1 import sync_receipt as machine_sync  # noqa: WPS433

    uw = uw_sync(enforce=False)
    lock = lock_sync(enforce=False)
    mandatory_sync(enforce=False)
    machine_sync()

    for key in (
        "mac_law_universal_line",
        "mac_law_universal_wire",
        "mac_law_agent_lock_line",
        "mac_law_agent_execution_plane_lock",
        "mac_law_agent_no_factory_on_mac",
        "mac_law_mandatory_line",
        "mac_law_mandatory",
        "mac_law_machine_line",
        "mac_law_machine_enforce",
    ):
        surf = _read(SURFACES)
        if key in surf:
            base[key] = surf[key]

    if uw.get("line"):
        base["mac_law_universal_line"] = uw["line"]
        base["mac_law_universal_wire"] = {"ok": uw.get("ok"), "ssot": "data/mac-law-universal-wire-v1.json"}
    if lock.get("line"):
        base["mac_law_agent_lock_line"] = lock["line"]
        base["mac_law_agent_execution_plane_lock"] = {
            "ok": lock.get("ok"),
            "locked_forever": True,
            "ssot": "data/mac-law-agent-execution-plane-lock-v1.json",
        }
        base["mac_law_agent_no_factory_on_mac"] = bool(lock.get("ok"))

    SINA.mkdir(parents=True, exist_ok=True)
    tmp = SURFACES.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(base, indent=2) + "\n", encoding="utf-8")
    tmp.replace(SURFACES)
    print(json.dumps({"ok": True, "keys": len(base), "path": str(SURFACES)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
