#!/usr/bin/env python3
"""Worker Hub auto-heal — light sync + shell heal + brain sync (no strict build)."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
FACTORY = SINA / "factory-now-v1.json"
SHELL = ROOT / "agent-control-panel" / "command-data-shell.json"
sys.path.insert(0, str(ROOT / "scripts"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_factory() -> dict:
    if not FACTORY.is_file():
        return {}
    try:
        return json.loads(FACTORY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _needs_brain_sync() -> bool:
    factory = _read_factory()
    return factory.get("dual_proof_ok") is False


def _run_brain_sync_light() -> dict:
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "brain_sync_lib_v1.py"), "--mode", "light"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=45,
        )
        detail: dict = {"returncode": proc.returncode}
        if proc.stdout.strip():
            try:
                detail["result"] = json.loads(proc.stdout)
            except json.JSONDecodeError:
                detail["stdout"] = proc.stdout[:500]
        return {"step": "brain_sync_light", "ok": proc.returncode == 0, **detail}
    except Exception as exc:
        return {"step": "brain_sync_light", "ok": False, "error": str(exc)}


def _rebuild_factory(*, caller: str) -> dict:
    try:
        from factory_control_v1 import rebuild_factory_now  # noqa: WPS433

        row = rebuild_factory_now(caller=caller, force=True)
        return {
            "step": "factory_now_rebuild",
            "ok": bool(row.get("dual_proof_ok")),
            "dual_proof_ok": row.get("dual_proof_ok"),
            "valid_yes": row.get("valid_yes"),
            "brain_vy": row.get("brain_vy"),
        }
    except Exception as exc:
        return {"step": "factory_now_rebuild", "ok": False, "error": str(exc)}


def _touch_shell_built_at() -> dict:
    """Stamp shell built_at without G3 full projection write (heal cosmetic)."""
    if not SHELL.is_file():
        return {"step": "shell_touch", "ok": False, "error": "shell missing"}
    try:
        row = json.loads(SHELL.read_text(encoding="utf-8"))
        row["built_at"] = _now()
        tmp = SHELL.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(row, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        tmp.replace(SHELL)
        return {"step": "shell_touch", "ok": True, "built_at": row["built_at"]}
    except Exception as exc:
        return {"step": "shell_touch", "ok": False, "error": str(exc)}


def _disk_live_wire() -> dict:
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "disk_live_wire_sync_v1.py"), "--role", "worker", "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=90,
        )
        detail: dict = {"returncode": proc.returncode}
        if proc.stdout.strip():
            try:
                detail["result"] = json.loads(proc.stdout)
            except json.JSONDecodeError:
                detail["stdout"] = proc.stdout[:500]
        return {"step": "disk_live_wire", "ok": proc.returncode == 0, **detail}
    except Exception as exc:
        return {"step": "disk_live_wire", "ok": False, "error": str(exc)}


def _health_passes(health: dict) -> bool:
    from worker_hub_staleness_v1 import health_passes  # noqa: WPS433

    return health_passes(health)


def _refresh_honest_p0() -> dict:
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "honest_p0_screen_v1.py"), "--no-sync"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        return {"step": "honest_p0_screen", "ok": proc.returncode == 0}
    except Exception as exc:
        return {"step": "honest_p0_screen", "ok": False, "error": str(exc)}


def worker_hub_heal(*, reason: str = "auto", full: bool = False) -> dict:
    steps: list[dict] = []

    wire = _disk_live_wire()
    steps.append(wire)

    factory = _rebuild_factory(caller=f"worker_hub_heal:{reason}")
    steps.append(factory)

    try:
        from sina_command_lib import hub_light_refresh  # noqa: WPS433

        shell = hub_light_refresh()
        steps.append({"step": "light_refresh", "ok": True, "built_at": shell.get("built_at")})
    except Exception as exc:
        steps.append({"step": "light_refresh", "ok": False, "skipped": "g3_or_unavailable", "error": str(exc)})

    try:
        from sina_command_lib import heal_command_data_shell_from_disk  # noqa: WPS433

        heal_ok, msg = heal_command_data_shell_from_disk(force=True)
        steps.append({"step": "shell_heal", "ok": heal_ok, "detail": msg})
    except Exception as exc:
        steps.append({"step": "shell_heal", "ok": False, "error": str(exc)})

    steps.append(_touch_shell_built_at())

    if _needs_brain_sync() or full:
        brain = _run_brain_sync_light()
        steps.append(brain)

    from worker_hub_staleness_v1 import staleness_probe  # noqa: WPS433
    from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

    invalidate_worker_hub_cache()
    health = staleness_probe()
    honest = _refresh_honest_p0()
    steps.append(honest)

    try:
        from mac_health_live_v1 import pulse_once  # noqa: WPS433

        live = pulse_once()
        steps.append({"step": "mac_health_live_pulse", "ok": live.get("live_status") == "LIVE", "status": live.get("live_status")})
    except Exception as exc:
        steps.append({"step": "mac_health_live_pulse", "ok": False, "error": str(exc)})

    try:
        from h2_pending_registry_sync_v1 import sync_h2_registry  # noqa: WPS433

        sync_h2_registry(caller=f"worker_hub_heal:{reason}")
        steps.append({"step": "h2_registry_sync", "ok": True})
    except Exception as exc:
        steps.append({"step": "h2_registry_sync", "ok": False, "error": str(exc)})

    try:
        from machine_hub_v1 import invalidate_machine_hub_cache  # noqa: WPS433

        invalidate_machine_hub_cache()
        steps.append({"step": "h2_cache_invalidate", "ok": True})
    except Exception as exc:
        steps.append({"step": "h2_cache_invalidate", "ok": False, "error": str(exc)})

    invalidate_worker_hub_cache()
    health = staleness_probe()

    heal_ok = _health_passes(health)

    return {
        "ok": heal_ok,
        "schema": "worker-hub-heal-v1",
        "reason": reason,
        "healed_at": _now(),
        "steps": steps,
        "health_after": health,
    }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Worker hub auto-heal")
    p.add_argument("--json", action="store_true")
    p.add_argument("--reason", default="cli")
    p.add_argument("--full", action="store_true")
    args = p.parse_args()
    row = worker_hub_heal(reason=args.reason, full=args.full)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        h = row.get("health_after") or {}
        print(f"HEAL: ok={row.get('ok')} status={h.get('status')} dual={h.get('latches', {}).get('dual_proof_ok')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
