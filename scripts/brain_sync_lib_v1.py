#!/usr/bin/env python3
"""SSOT: brain snapshot sync after honest-count changes (INCIDENT-014 repair)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
BRAIN_VAL = SINA / "brain-goal1-validation-v1.json"
HYGIENE_PASS = SINA / "last-hygiene-pass-v1.json"
BRAIN_FRESH_SEC = 120

SyncMode = Literal["light", "full"]


def _command_retired_forever() -> bool:
    try:
        _scripts_path()
        from founder_directive_ssot_v1 import command_retired_forever  # noqa: WPS433

        return command_retired_forever()
    except Exception:
        return False


def _skip_hub_projection() -> bool:
    if os.environ.get("SINA_BRAIN_FAST", "").strip().lower() in ("1", "true", "yes"):
        return True
    return _command_retired_forever()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _scripts_path() -> None:
    p = str(SCRIPTS)
    if p not in sys.path:
        sys.path.insert(0, p)


def _live_monitor_counts() -> dict[str, Any]:
    _scripts_path()
    from monitor_honesty_lib_v1 import audit_monitor, load_dual_proof_system  # noqa: WPS433

    m = audit_monitor(filter_mode="road")
    prog = m.get("progress") or {}
    vy = int(prog.get("valid_yes") or 0)
    hy_ok = bool(m.get("ok")) and int(m.get("unproven_done") or 0) == 0
    dual = load_dual_proof_system(valid_yes=vy, hygiene_ok=hy_ok)
    brain = dual.get("brain") or {}
    brain_vy = brain.get("valid_yes")
    return {
        "live_vy": vy,
        "brain_vy": brain_vy,
        "brain_ok": bool(brain.get("ok")),
        "hygiene_ok": hy_ok,
        "dual_proof_ok": bool(dual.get("dual_proof_ok")),
        "gap": (vy - int(brain_vy)) if brain_vy is not None else None,
        "dual": dual,
        "monitor_ok": bool(m.get("ok")),
        "unproven_done": int(m.get("unproven_done") or 0),
    }


def brain_snapshot_status() -> dict[str, Any]:
    """Read-only status for monitor, gates, and hub missed-actions."""
    st = _live_monitor_counts()
    return {
        "ok": True,
        "at": _now(),
        "live_vy": st["live_vy"],
        "brain_vy": st["brain_vy"],
        "brain_ok": st["brain_ok"],
        "hygiene_ok": st["hygiene_ok"],
        "dual_proof_ok": st["dual_proof_ok"],
        "gap": st["gap"],
        "snapshot_stale": st["brain_vy"] is not None and st["brain_vy"] != st["live_vy"],
        "law": "INCIDENT-014 · brain_sync_lib_v1",
    }


def _write_brain_receipt() -> dict[str, Any]:
    _scripts_path()
    from brain_validate_goal1_v1 import validate_goal1  # noqa: WPS433

    row = validate_goal1(strict=False)
    SINA.mkdir(parents=True, exist_ok=True)
    BRAIN_VAL.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    prog = row.get("progress_honest") or {}
    return {
        "ok": bool(row.get("ok")),
        "brain_vy": prog.get("valid_yes"),
        "at": row.get("at") or _now(),
        "status": row.get("status"),
    }


def _patch_last_hygiene_pass(*, vy: int, hy_ok: bool, dual: dict[str, Any]) -> dict[str, Any]:
    dual = dict(dual)
    dual["hygiene"] = {"ok": hy_ok, "at": _now(), "valid_yes": vy}
    dual["dual_proof_ok"] = hy_ok and bool((dual.get("brain") or {}).get("ok")) and bool(
        (dual.get("maintainer") or {}).get("ok")
    )
    out = {
        "schema": "last-hygiene-pass-v1",
        "at": _now(),
        "ok": hy_ok,
        "valid_yes": vy,
        "unproven_done": 0,
        "dual_proof": dual,
        "law": "PROOF_VALIDATION_CHAIN_LOCKED_v1",
        "source": "brain_sync_lib_v1",
    }
    HYGIENE_PASS.parent.mkdir(parents=True, exist_ok=True)
    HYGIENE_PASS.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return out


def sync_brain_snapshot(*, mode: SyncMode = "light", caller: str = "") -> dict[str, Any]:
    """Light: brain receipt + last-hygiene-pass. Full: enforce-registry-hygiene-v1.sh."""
    if mode == "full":
        proc = subprocess.run(
            ["bash", str(SCRIPTS / "enforce-registry-hygiene-v1.sh")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=600,
        )
        st = brain_snapshot_status()
        factory_now: dict[str, Any] = {}
        if st.get("dual_proof_ok"):
            try:
                from factory_control_v1 import rebuild_factory_now  # noqa: WPS433

                factory_now = rebuild_factory_now(caller=f"brain_sync:{caller}", force=True)
            except Exception:
                pass
        return {
            "ok": proc.returncode == 0 and st.get("dual_proof_ok"),
            "mode": "full",
            "caller": caller,
            "returncode": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-2000:],
            "stderr_tail": (proc.stderr or "")[-1000:],
            "factory_now": factory_now,
            **st,
        }

    before = _live_monitor_counts()
    if caller != "queue_ssot_unify":
        try:
            from queue_ssot_unify_v1 import unify_queue_ssot  # noqa: WPS433

            unify_queue_ssot(write_brain=False, rebuild_factory=False, fast=True)
        except Exception:
            pass
    brain_write = _write_brain_receipt()
    after_counts = _live_monitor_counts()
    vy = after_counts["live_vy"]
    hy_ok = after_counts["hygiene_ok"]
    _patch_last_hygiene_pass(vy=vy, hy_ok=hy_ok, dual=after_counts["dual"])
    final = brain_snapshot_status()
    factory_now: dict[str, Any] = {}
    synced = before.get("brain_vy") != final.get("brain_vy") or not before.get("dual_proof_ok")
    hub_sync: dict[str, Any] = {}
    if synced and final.get("dual_proof_ok"):
        try:
            from factory_control_v1 import rebuild_factory_now  # noqa: WPS433

            factory_now = rebuild_factory_now(caller=f"brain_sync:{caller}", force=True)
        except Exception:
            pass
    try:
        from hub_projection_sync_v1 import sync_hub_projection  # noqa: WPS433

        if _skip_hub_projection():
            hub_sync = {"ok": True, "skipped": "command_retired_or_brain_fast"}
        else:
            hub_sync = sync_hub_projection(caller=f"brain_sync:{caller}")
    except Exception as exc:
        hub_sync = {"ok": False, "error": str(exc)}
    return {
        "ok": bool(brain_write.get("ok")) and bool(final.get("dual_proof_ok")),
        "mode": "light",
        "caller": caller,
        "synced": synced,
        "before": {
            "live_vy": before["live_vy"],
            "brain_vy": before["brain_vy"],
            "dual_proof_ok": before["dual_proof_ok"],
        },
        "after": final,
        "brain_write": brain_write,
        "factory_now": factory_now,
        "hub_projection_sync": hub_sync,
    }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Brain snapshot sync SSOT")
    p.add_argument("--mode", choices=("light", "full"), default="light")
    p.add_argument("--status", action="store_true", help="Status only — no sync")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    if args.status:
        out = brain_snapshot_status()
    else:
        out = sync_brain_snapshot(mode=args.mode)
    if args.json or True:
        print(json.dumps(out, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
