#!/usr/bin/env python3
"""Cloud drain auto-runtime — mock skip · self-heal · scheduled proceed (INCIDENT-023 gated)."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SSOT = ROOT / "data/cloud-drain-auto-runtime-v1.json"
TICK_RECEIPT = SINA / "cloud-drain-auto-tick-receipt-v1.json"
HUB_RECEIPT = SINA / "hub-cloud-drain-proceed-receipt-v1.json"
AUTO_FLAG = SINA / "cloud-drain-auto-proceed-v1.flag"

sys.path.insert(0, str(SCRIPTS))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def load_ssot() -> dict[str, Any]:
    row = _read(SSOT)
    if row:
        return row
    return {
        "schema": "cloud-drain-auto-runtime-v1",
        "version": "1.0.0",
        "enabled": False,
        "cron": "*/15 * * * *",
        "min_interval_minutes": 15,
        "auto_skip_mock": True,
        "auto_proceed": False,
        "self_heal_motor_fail_mock": True,
        "self_heal_any_motor_fail": True,
        "max_skips_per_tick": 8,
        "llm_provider": "openrouter",
        "full_motor": True,
    }


def auto_proceed_enabled() -> bool:
    ssot = load_ssot()
    if str(os.environ.get("CLOUD_DRAIN_AUTO_PROCEED", "")).lower() in ("1", "true", "yes"):
        return True
    if AUTO_FLAG.is_file():
        return True
    return bool(ssot.get("enabled")) and bool(ssot.get("auto_proceed"))


def _minutes_since(iso: str) -> float:
    if not iso:
        return 9999.0
    try:
        then = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return (now - then).total_seconds() / 60.0
    except ValueError:
        return 9999.0


def _factory_stop_blocks() -> dict[str, Any] | None:
    try:
        from factory_control_v1 import stop_receipt_open  # noqa: WPS433

        if stop_receipt_open():
            return {
                "ok": False,
                "error": "factory_stop",
                "for_founder": {"show_this": "Factory STOP active — auto drain blocked (INCIDENT-023)."},
            }
    except Exception as exc:
        return {"ok": False, "error": "factory_gate_failed", "message": str(exc)[:200]}
    return None


def _cloud_queue_action(action: str, **kwargs: Any) -> dict[str, Any]:
    from forge_cloud_env_load_v1 import load_cloud_env  # noqa: WPS433
    from fbe.lib.hub_cloud_proxy_v1 import proxy_get_from_cloud, proxy_to_cloud  # noqa: WPS433

    load_cloud_env(apply=True)
    if action == "get_head":
        return proxy_get_from_cloud(path="/api/cloud-drain/queue/v1", timeout_s=60)
    body: dict[str, Any] = {"action": action, **kwargs}
    return proxy_to_cloud(path="/api/cloud-drain/queue/v1", body=body, timeout_s=120)


def _cloud_proceed(*, llm_provider: str, full_motor: bool) -> dict[str, Any]:
    from forge_cloud_env_load_v1 import load_cloud_env  # noqa: WPS433
    from fbe.lib.hub_cloud_proxy_v1 import proxy_to_cloud  # noqa: WPS433

    load_cloud_env(apply=True)
    return proxy_to_cloud(
        path="/api/cloud-drain/proceed/v1",
        body={
            "full_motor": full_motor,
            "llm_provider": llm_provider,
            "auto_tick": True,
        },
        timeout_s=300,
    )


def _sync_mac_from_cloud_queue() -> dict[str, Any]:
    try:
        from fbe.lib.cloud_drain_queue_v1 import sync_to_mac_if_newer  # noqa: WPS433

        cloud = _cloud_queue_action("get_head")
        return sync_to_mac_if_newer(cloud)
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:120]}


def run_auto_tick(*, force: bool = False, llm_provider: str = "openrouter") -> dict[str, Any]:
    from cloud_workers_hub_v1 import (  # noqa: WPS433
        auto_runtime_status,
        is_mock_at_head,
        is_mock_plan,
        skip_head,
        skip_to_next_real,
        _plan_by_id,
        _read as cw_read,
        PHASE_OBS,
    )

    ssot = load_ssot()
    at = _now()
    steps: list[dict[str, Any]] = []

    block = _factory_stop_blocks()
    if block and not force:
        block["at"] = at
        _write(TICK_RECEIPT, block)
        return block

    last_tick = _read(TICK_RECEIPT)
    min_gap = float(ssot.get("min_interval_minutes") or 15)
    if not force and _minutes_since(str(last_tick.get("at") or "")) < min_gap:
        row = {
            "ok": True,
            "schema": "cloud-drain-auto-tick-v1",
            "at": at,
            "decision": "rate_limited",
            "for_founder": {"show_this": f"Auto tick rate limit — wait {min_gap:.0f}m between runs."},
            "steps": steps,
        }
        _write(TICK_RECEIPT, row)
        return row

    hub_rcpt = _read(HUB_RECEIPT)
    if ssot.get("self_heal_motor_fail_mock", True) and hub_rcpt.get("ok") is False:
        fail_plan = _plan_by_id(str(hub_rcpt.get("plan_id") or ""))
        if is_mock_plan(fail_plan):
            heal = skip_to_next_real(reason="auto_heal_motor_fail_mock", max_skips=int(ssot.get("max_skips_per_tick") or 8))
            steps.append({"step": "self_heal_skip_mock", "result": heal})

    if ssot.get("auto_skip_mock", True) and is_mock_at_head():
        skip_row = skip_to_next_real(
            reason="auto_skip_mock_head",
            max_skips=int(ssot.get("max_skips_per_tick") or 8),
        )
        steps.append({"step": "auto_skip_mock", "result": skip_row})

    obs = cw_read(PHASE_OBS)
    head = str(obs.get("cloud_drain_head") or "")

    if not auto_proceed_enabled() and not force:
        row = {
            "ok": True,
            "schema": "cloud-drain-auto-tick-v1",
            "at": at,
            "decision": "observe_only",
            "head": head,
            "auto_proceed_enabled": False,
            "for_founder": {
                "show_this": f"Auto tick OK — head {head} · mock skipped if needed · proceed OFF (arm flag to auto-run).",
            },
            "steps": steps,
            "auto_runtime": auto_runtime_status(),
        }
        _write(TICK_RECEIPT, row)
        return row

    try:
        from factory_control_v1 import current_mode  # noqa: WPS433

        # Mac FREEZE is control-plane posture — cloud drain motor runs on Railway only.
        if current_mode() == "FREEZE" and not force and not auto_proceed_enabled():
            row = {
                "ok": True,
                "schema": "cloud-drain-auto-tick-v1",
                "at": at,
                "decision": "freeze_skip_proceed",
                "head": head,
                "for_founder": {
                    "show_this": f"Factory FREEZE — mock skip done · head {head} · arm flag for auto Proceed.",
                },
                "steps": steps,
                "auto_runtime": auto_runtime_status(),
            }
            _write(TICK_RECEIPT, row)
            return row
    except Exception:
        pass

    # Headless path: Railway queue + proceed (no Hub process required)
    proceed = _cloud_proceed(
        llm_provider=llm_provider or str(ssot.get("llm_provider") or "openrouter"),
        full_motor=bool(ssot.get("full_motor", True)),
    )
    _sync_mac_from_cloud_queue()
    # Mirror receipt for Command Center glance on Mac
    if proceed.get("ok") is not None:
        hub_mirror = {
            "schema": "hub-cloud-drain-proceed-receipt-v1",
            "at": at,
            "ok": bool(proceed.get("ok")),
            "execution_plane": "headless_cloud_auto_tick",
            "plan_id": proceed.get("plan_id"),
            "maps_registry": proceed.get("maps_registry"),
            "cloud": proceed,
            "for_founder": proceed.get("for_founder") or {"show_this": str(proceed.get("for_founder", ""))},
        }
        _write(HUB_RECEIPT, hub_mirror)

    steps.append({"step": "proceed", "result": {"ok": proceed.get("ok"), "plan_id": proceed.get("plan_id")}})

    if proceed.get("ok") is False and ssot.get("self_heal_motor_fail_mock", True):
        fail_plan = _plan_by_id(str(proceed.get("plan_id") or head))
        if is_mock_plan(fail_plan):
            heal2 = skip_to_next_real(reason="auto_heal_after_proceed_fail")
            steps.append({"step": "self_heal_after_fail", "result": heal2})
        elif ssot.get("self_heal_any_motor_fail", True) and auto_proceed_enabled():
            heal3 = skip_head(reason="auto_heal_motor_fail_real_row")
            steps.append({"step": "self_heal_skip_head", "result": heal3})

    row = {
        "ok": bool(proceed.get("ok")),
        "schema": "cloud-drain-auto-tick-v1",
        "at": at,
        "decision": "proceed" if proceed.get("ok") else "proceed_failed",
        "head": head,
        "plan_id": proceed.get("plan_id"),
        "for_founder": (proceed.get("for_founder") or {}).get("show_this")
        or proceed.get("hub_proceed_line")
        or f"Auto tick · head {head}",
        "steps": steps,
        "auto_runtime": auto_runtime_status(),
    }
    _write(TICK_RECEIPT, row)
    return row


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Cloud drain auto-runtime v1")
    ap.add_argument("--tick", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--enable", action="store_true", help="Write founder opt-in flag (auto proceed)")
    ap.add_argument("--disable", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.enable:
        AUTO_FLAG.parent.mkdir(parents=True, exist_ok=True)
        AUTO_FLAG.write_text(f"enabled_at={_now()}\n", encoding="utf-8")
        ssot = load_ssot()
        ssot["enabled"] = True
        ssot["auto_proceed"] = True
        ssot["auto_skip_mock"] = True
        ssot["self_heal_any_motor_fail"] = True
        ssot["saved_at"] = _now()
        _write(SSOT, ssot)
        out = {
            "ok": True,
            "enabled": True,
            "flag": str(AUTO_FLAG),
            "for_founder": {
                "show_this": "Auto drain ARMED — mock skip + self-heal on motor fail + scheduled proceed when cron runs.",
            },
        }
    elif args.disable:
        if AUTO_FLAG.is_file():
            AUTO_FLAG.unlink()
        out = {"ok": True, "enabled": False}
    elif args.status:
        from cloud_workers_hub_v1 import auto_runtime_status  # noqa: WPS433

        out = auto_runtime_status()
    elif args.tick:
        out = run_auto_tick(force=args.force)
    else:
        out = load_ssot()

    if args.json:
        print(json.dumps(out, indent=2))
    elif args.enable:
        print(out.get("for_founder", {}).get("show_this") or "OK — Auto drain ARMED")
        print("Flag:", AUTO_FLAG)
    elif args.disable:
        print("OK — Auto drain OFF")
    else:
        print(out.get("for_founder", {}).get("show_this") or out.get("decision") or json.dumps(out, indent=2)[:200])
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
