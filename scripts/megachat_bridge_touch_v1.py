#!/usr/bin/env python3
"""Megachat SAVE → machine propagate: skills sync · ACTIVE_NOW · anchors RT."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
LATEST = ROOT / "brain-os/narrative-bridge/LATEST_TOUCH_BASE_LOCKED_v1.md"
PROPAGATE_RECEIPT = Path.home() / ".sina/megachat-bridge-propagate-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, label: str) -> dict:
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, check=False)
    return {
        "label": label,
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-400:],
        "stderr_tail": (proc.stderr or "")[-400:],
    }


def propagate(*, source: str = "megachat_save") -> dict:
    steps: list[dict] = []
    if not LATEST.is_file():
        steps.append({"label": "LATEST_TOUCH_BASE", "ok": False, "error": "missing"})
    else:
        steps.append({"label": "LATEST_TOUCH_BASE", "ok": True, "path": str(LATEST)})

    steps.append(_run(["bash", str(SCRIPTS / "sync-cursor-agent-skills.sh")], label="sync_skills"))
    steps.append(_run(["bash", str(SCRIPTS / "validate-narrative-bridge-v1.sh")], label="validate_narrative_bridge"))

    sys.path.insert(0, str(SCRIPTS))
    try:
        from active_now_sync_from_factory_now_v1 import sync_active_now  # noqa: WPS433

        an = sync_active_now()
        steps.append({"label": "sync_active_now_factory_now", "ok": bool(an.get("ok")), "result": an})
    except Exception as exc:
        steps.append({"label": "sync_active_now", "ok": False, "error": str(exc)})

    try:
        from ecosystem_master_catalog_v1 import mega_chat_anchors_payload  # noqa: WPS433

        anchors = mega_chat_anchors_payload()
        steps.append({"label": "mega_chat_anchors", "ok": True, "count": len(anchors), "ids": [a["id"] for a in anchors]})
    except Exception as exc:
        steps.append({"label": "mega_chat_anchors", "ok": False, "error": str(exc)})

    ok = all(s.get("ok") for s in steps if s.get("label") != "sync_skills" or s.get("ok"))
    # skills sync failure is warn-only if validate-narrative passes
    hard = [s for s in steps if s.get("label") in ("LATEST_TOUCH_BASE", "validate_narrative_bridge", "mega_chat_anchors")]
    ok = all(s.get("ok") for s in hard)

    receipt = {"schema": "megachat-bridge-propagate-v1", "at": _now(), "source": source, "ok": ok, "steps": steps}
    PROPAGATE_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    PROPAGATE_RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    p = argparse.ArgumentParser(description="Propagate megachat bridge SAVE to machine layer")
    p.add_argument("--propagate", action="store_true", help="Run full propagate chain")
    p.add_argument("--json", action="store_true")
    p.add_argument("--source", default="cli")
    args = p.parse_args()
    if not args.propagate:
        p.print_help()
        return 1
    row = propagate(source=args.source)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print("OK" if row.get("ok") else "FAIL", "megachat_bridge_touch_v1")
        for s in row.get("steps") or []:
            print(f" - {s.get('label')}: {'PASS' if s.get('ok') else 'FAIL'}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
