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
CYCLE_RECEIPTS_DIR = SINA / "autonomous-drain-cycle-receipts"
RAMP_STATE_PATH = SINA / "autonomous-drain-ramp-state-v1.json"

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
        "cron": "*/10 * * * *",
        "min_interval_minutes": 10,
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


def _is_headless_cloud() -> bool:
    if str(os.environ.get("FBE_MODE", "")).lower() == "headless":
        return True
    if os.environ.get("FBE_HOME", "").strip() == "/app":
        return True
    return Path("/app/receipts").is_dir()


def _run_prove_gate() -> dict[str, Any]:
    """PROVE belt step — living system chains must pass before SHIP."""
    if _is_headless_cloud():
        from living_system_chain_validate_v1 import validate_chains_cloud  # noqa: WPS433

        return validate_chains_cloud(write=True)
    import subprocess

    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "living_system_chain_validate_v1.py"), "--fast", "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=90,
        env={**os.environ},
    )
    try:
        row = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        row = {"ok": False, "error": "prove_parse_failed", "raw": (proc.stdout or "")[:400]}
    row["exit"] = proc.returncode
    if proc.returncode != 0 and row.get("ok") is not False:
        row["ok"] = False
    chains = row.get("chains") or []
    if isinstance(chains, list):
        row["chains_up"] = sum(1 for c in chains if isinstance(c, dict) and c.get("ok"))
        row["chains_total"] = len(chains)
    return row


def _write_cycle_receipt(
    *,
    cycle: dict[str, Any],
    trigger_source: str,
    head: str,
    prove: dict[str, Any] | None = None,
    ship: dict[str, Any] | None = None,
) -> Path:
    """Append one autonomous cycle receipt — green or honest-halt."""
    CYCLE_RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    safe_at = str(cycle.get("at") or _now()).replace(":", "").replace("-", "")
    path = CYCLE_RECEIPTS_DIR / f"cycle-{safe_at}-v1.json"
    prove_ok = bool((prove or {}).get("ok"))
    ship_ok = bool((ship or {}).get("ok"))
    verdict = "approved" if prove_ok and ship_ok else "rejected"
    doc = {
        "schema": "autonomous-drain-cycle-receipt-v1",
        "version": "1.0.0",
        "at": cycle.get("at") or _now(),
        "trigger_source": trigger_source,
        "factory": "forge-drain",
        "blueprint_id": "MAC-CTL-002",
        "queue_head": head,
        "belt": {
            "PROVE": {
                "ok": prove_ok,
                "summary_line": (prove or {}).get("summary_line"),
                "chains_up": (prove or {}).get("chains_up"),
                "chains_total": (prove or {}).get("chains_total"),
                "gate_cleared": prove_ok,
            },
            "SHIP": {
                "ok": ship_ok,
                "plan_id": (ship or {}).get("plan_id"),
                "dry_run": (ship or {}).get("dry_run"),
                "hub_proceed_line": (ship or {}).get("hub_proceed_line"),
                "gate_cleared": ship_ok,
                "artifact_path": (ship or {}).get("artifact_path"),
                "artifact_type": (ship or {}).get("artifact_type"),
                "validator_result": (ship or {}).get("validator_result"),
            },
        },
        "artifact": {
            "artifact_type": (ship or {}).get("artifact_type") or "autonomous_drain_cycle",
            "artifact_path": (ship or {}).get("artifact_path"),
            "plan_id": (ship or {}).get("plan_id") or head,
            "status": "committed" if ship_ok else "halted",
            "validator_result": (ship or {}).get("validator_result"),
        },
        "evidence": {
            "prove_receipt": str(ROOT / "data/living-system-chain-registry-v1.json"),
            "hub_receipt": str(HUB_RECEIPT),
            "trigger_source": trigger_source,
        },
        "decision": {
            "decision_type": "autonomous_drain_gate",
            "verdict": verdict,
            "rationale": cycle.get("decision_rationale")
            or (
                "PROVE and SHIP passed from scheduler receipts"
                if verdict == "approved"
                else "Halted — gate failed; no forced green"
            ),
        },
        "cycle": cycle,
    }
    if (ship or {}).get("artifact_path"):
        doc["forge_seed"] = {
            "pipeline": (ship or {}).get("pipeline") or ["PLAN", "BUILD", "VALIDATE", "RECEIPT"],
            "artifact_path": (ship or {}).get("artifact_path"),
            "artifact_type": (ship or {}).get("artifact_type"),
            "validator_result": (ship or {}).get("validator_result"),
        }
    _write(path, doc)
    if _is_headless_cloud():
        try:
            from autonomous_drain_receipt_cloud_v1 import persist_cycle_receipt  # noqa: WPS433

            persist_cycle_receipt(doc)
        except Exception:
            pass
    return path


def _update_ramp_state(*, green: bool) -> dict[str, Any]:
    state = _read(RAMP_STATE_PATH)
    consecutive = int(state.get("consecutive_green") or 0)
    if green:
        consecutive += 1
    else:
        consecutive = 0
    ssot = load_ssot()
    base_min = float(ssot.get("min_interval_minutes") or 10)
    row = {
        "schema": "autonomous-drain-ramp-state-v1",
        "at": _now(),
        "consecutive_green": consecutive,
        "cadence_minutes": base_min,
        "parallelism_cap": 1,
        "ramp_unlocked": False,
    }
    _write(RAMP_STATE_PATH, row)
    return row


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
            "trigger_source": "mac_auto_tick",
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


def run_auto_tick(
    *,
    force: bool = False,
    llm_provider: str = "openrouter",
    trigger_source: str = "manual",
) -> dict[str, Any]:
    from cloud_workers_hub_v1 import (  # noqa: WPS433
        auto_runtime_status,
        skip_head,
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

    _read(TICK_RECEIPT)
    from cloud_drain_single_cycle_gate_v1 import claim_or_halt  # noqa: WPS433

    halt = claim_or_halt(path="/api/cloud-drain/auto-tick/v1", trigger_source=trigger_source)
    if halt:
        halt["schema"] = "cloud-drain-auto-tick-v1"
        halt["at"] = at
        halt["steps"] = steps
        _write(TICK_RECEIPT, halt)
        return halt

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

    prove = _run_prove_gate()
    steps.append(
        {
            "step": "prove",
            "result": {
                "ok": prove.get("ok"),
                "summary_line": prove.get("summary_line"),
                "chains_up": prove.get("chains_up"),
                "chains_total": prove.get("chains_total"),
            },
        }
    )
    if not prove.get("ok"):
        halt_reason = "prove_gate_failed"
        failed = [c for c in (prove.get("chains") or []) if not c.get("ok")]
        skip_row: dict[str, Any] | None = None
        if head and ssot.get("self_heal_any_motor_fail", True):
            skip_row = skip_head(reason="prove_gate_halt_advance_head")
            steps.append({"step": "halt_skip_head", "result": skip_row})
        cycle_row = {
            "ok": False,
            "schema": "cloud-drain-auto-tick-v1",
            "at": at,
            "decision": "halt_prove",
            "decision_rationale": f"PROVE failed — {prove.get('summary_line') or halt_reason}",
            "head": head,
            "trigger_source": trigger_source,
            "prove": {"ok": False, "failed_chains": failed[:3]},
            "for_founder": {
                "show_this": f"Auto drain HALT · PROVE fail · head {head} · advanced per gate law",
            },
            "steps": steps,
            "auto_runtime": auto_runtime_status(),
        }
        _write(TICK_RECEIPT, cycle_row)
        cycle_path = _write_cycle_receipt(
            cycle=cycle_row,
            trigger_source=trigger_source,
            head=head,
            prove=prove,
            ship=None,
        )
        cycle_row["cycle_receipt_path"] = str(cycle_path)
        _update_ramp_state(green=False)
        return cycle_row

    # Headless path: Railway queue + proceed (no Hub process required)
    proceed = _cloud_proceed(
        llm_provider=llm_provider or str(ssot.get("llm_provider") or "openrouter"),
        full_motor=bool(ssot.get("full_motor", True)),
    )
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

    row = {
        "ok": bool(proceed.get("ok")),
        "schema": "cloud-drain-auto-tick-v1",
        "at": at,
        "decision": "proceed" if proceed.get("ok") else "proceed_failed",
        "head": head,
        "plan_id": proceed.get("plan_id"),
        "trigger_source": trigger_source,
        "prove_ok": True,
        "for_founder": (proceed.get("for_founder") or {}).get("show_this")
        or proceed.get("hub_proceed_line")
        or f"Auto tick · head {head}",
        "steps": steps,
        "auto_runtime": auto_runtime_status(),
    }
    cycle_path = _write_cycle_receipt(
        cycle=row,
        trigger_source=trigger_source,
        head=head,
        prove=prove,
        ship=proceed,
    )
    row["cycle_receipt_path"] = str(cycle_path)
    row["ramp"] = _update_ramp_state(green=bool(proceed.get("ok")))
    _write(TICK_RECEIPT, row)
    return row


def _run_contract_gate() -> dict[str, Any]:
    """Execution contract gate (shared/types · fbe_execution_contract_v1.json)."""
    from fbe.lib.execution_contract_v1 import build_contract, policy_gate, validate_contract  # noqa: WPS433

    contract = build_contract(
        factory_id="forge-app-factory-v1",
        tenant_id="forge",
        execution_mode="CLOUD_ONLY",
        work_order_id="cloud-drain-auto-tick",
    )
    validation = validate_contract(contract)
    if not validation.get("ok"):
        return {"ok": False, "step": "contract_validate", "errors": validation.get("errors"), "contract": contract}
    gate = policy_gate(contract, freeze_active=False, cloud_url_configured=True)
    return {
        "ok": bool(gate.get("ok")),
        "step": "contract_policy_gate",
        "contract": contract,
        "policy": gate,
        "errors": gate.get("reasons") or [],
    }


def _cloud_ramp_path() -> Path:
    if _is_headless_cloud():
        return Path("/app/receipts/cloud/autonomous-drain-ramp-state-v1.json")
    return RAMP_STATE_PATH


def _update_ramp_state_cloud(*, green: bool) -> dict[str, Any]:
    state = _read(_cloud_ramp_path())
    consecutive = int(state.get("consecutive_green") or 0)
    if green:
        consecutive += 1
    else:
        consecutive = 0
    ssot = load_ssot()
    base_min = float(ssot.get("min_interval_minutes") or 10)
    row = {
        "schema": "autonomous-drain-ramp-state-v1",
        "at": _now(),
        "consecutive_green": consecutive,
        "cadence_minutes": base_min,
        "parallelism_cap": 1,
        "ramp_unlocked": False,
    }
    path = _cloud_ramp_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    _write(path, row)
    if not _is_headless_cloud():
        _write(RAMP_STATE_PATH, row)
    return row


def run_cloud_auto_tick(
    *,
    body: dict[str, Any] | None = None,
    force: bool = False,
    llm_provider: str = "openrouter",
    trigger_source: str = "cloudflare_cron",
) -> dict[str, Any]:
    """Server-side autonomous tick on Railway — PROVE → contract → SHIP."""
    from fbe.lib.cloud_drain_queue_v1 import read_head, skip_head  # noqa: WPS433

    body = body or {}
    trigger_source = str(body.get("trigger_source") or trigger_source)
    force = bool(body.get("force")) or force
    ssot = load_ssot()
    at = _now()
    steps: list[dict[str, Any]] = []

    if str(os.environ.get("CLOUD_DRAIN_AUTO_PROCEED", "")).lower() not in ("1", "true", "yes") and not force:
        row = {
            "ok": True,
            "schema": "cloud-drain-auto-tick-v1",
            "at": at,
            "decision": "observe_only",
            "trigger_source": trigger_source,
            "execution_plane": "headless_cloud",
            "for_founder": {"show_this": "Cloud auto drain OFF — set CLOUD_DRAIN_AUTO_PROCEED=true"},
        }
        return row

    cloud_tick_receipt = Path("/app/receipts/cloud/cloud-drain-auto-tick-receipt-v1.json")

    if not body.get("_cycle_claimed"):
        from cloud_drain_single_cycle_gate_v1 import claim_or_halt  # noqa: WPS433

        halt = claim_or_halt(path="/api/cloud-drain/auto-tick/v1", trigger_source=trigger_source)
        if halt:
            return {**halt, "schema": "cloud-drain-auto-tick-v1"}

    head_row = read_head()
    head = str(head_row.get("cloud_drain_head") or "")

    prove = _run_prove_gate()
    steps.append({"step": "prove", "result": {"ok": prove.get("ok"), "summary_line": prove.get("summary_line")}})
    if not prove.get("ok"):
        cycle_row = {
            "ok": False,
            "schema": "cloud-drain-auto-tick-v1",
            "at": at,
            "decision": "halt_prove",
            "head": head,
            "trigger_source": trigger_source,
            "execution_plane": "headless_cloud",
            "steps": steps,
        }
        skip_head(reason="cloud_prove_halt")
        _write_cycle_receipt(cycle=cycle_row, trigger_source=trigger_source, head=head, prove=prove, ship=None)
        _update_ramp_state_cloud(green=False)
        cloud_tick_receipt.parent.mkdir(parents=True, exist_ok=True)
        _write(cloud_tick_receipt, cycle_row)
        return cycle_row

    contract = _run_contract_gate()
    steps.append({"step": "contract_gate", "result": {"ok": contract.get("ok"), "errors": contract.get("errors")}})
    if not contract.get("ok"):
        cycle_row = {
            "ok": False,
            "schema": "cloud-drain-auto-tick-v1",
            "at": at,
            "decision": "halt_contract",
            "head": head,
            "trigger_source": trigger_source,
            "execution_plane": "headless_cloud",
            "steps": steps,
        }
        skip_head(reason="contract_gate_halt")
        _write_cycle_receipt(cycle=cycle_row, trigger_source=trigger_source, head=head, prove=prove, ship=None)
        _update_ramp_state_cloud(green=False)
        _write(cloud_tick_receipt, cycle_row)
        return cycle_row

    from hub_cloud_drain_proceed_v1 import proceed_on_cloud  # noqa: WPS433

    proceed = proceed_on_cloud(
        {
            "full_motor": bool(ssot.get("full_motor", True)),
            "llm_provider": llm_provider or str(ssot.get("llm_provider") or "openrouter"),
            "auto_tick": True,
            "_cycle_claimed": True,
            **body,
        }
    )
    steps.append({"step": "proceed", "result": {"ok": proceed.get("ok"), "plan_id": proceed.get("plan_id")}})

    row = {
        "ok": bool(proceed.get("ok")),
        "schema": "cloud-drain-auto-tick-v1",
        "at": at,
        "decision": "proceed" if proceed.get("ok") else "proceed_failed",
        "head": head,
        "plan_id": proceed.get("plan_id"),
        "trigger_source": trigger_source,
        "execution_plane": "headless_cloud",
        "prove_ok": True,
        "contract_ok": True,
        "for_founder": (proceed.get("for_founder") or {}).get("show_this")
        or f"Cloud tick · {head}",
        "steps": steps,
    }
    cycle_path = _write_cycle_receipt(
        cycle=row,
        trigger_source=trigger_source,
        head=head,
        prove=prove,
        ship=proceed,
    )
    row["cycle_receipt_path"] = str(cycle_path)
    row["ramp"] = _update_ramp_state_cloud(green=bool(proceed.get("ok")))
    cloud_tick_receipt.parent.mkdir(parents=True, exist_ok=True)
    _write(cloud_tick_receipt, row)
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
