#!/usr/bin/env python3
"""Cloud Auto Runtime — mock skip · self-heal · scheduled Cloud Forge Run proceed."""
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
SSOT = ROOT / "data/cloud-auto-runtime-v1.json"
TICK_RECEIPT = SINA / "cloud-auto-runtime-tick-receipt-v1.json"
HUB_RECEIPT = SINA / "hub-cloud-forge-run-proceed-receipt-v1.json"
AUTO_FLAG = SINA / "cloud-forge-run-auto-proceed-v1.flag"
CYCLE_RECEIPTS_DIR = SINA / "autonomous-forge-run-cycle-receipts"
RAMP_STATE_PATH = SINA / "autonomous-forge-run-ramp-state-v1.json"

def _normalize_motor_path(path: str) -> str:
    """Legacy alias: /api/cloud-drain/* → /api/cloud-forge-run/* (physical rename v3)."""
    if path.startswith("/api/cloud-drain/"):
        return "/api/cloud-forge-run/" + path[len("/api/cloud-drain/") :]
    return path


def auto_proceed_armed() -> bool:
    """CLOUD_FORGE_RUN_AUTO_PROCEED (new) or legacy CLOUD_DRAIN_AUTO_PROCEED."""
    for key in ("CLOUD_FORGE_RUN_AUTO_PROCEED", "CLOUD_DRAIN_AUTO_PROCEED"):
        if str(os.environ.get(key, "")).lower() in ("1", "true", "yes"):
            return True
    return AUTO_FLAG.is_file()


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
        "schema": "cloud-auto-runtime-v1",
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
    if auto_proceed_armed():
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
                "for_founder": {"show_this": "Factory STOP active — Auto Runtime blocked (INCIDENT-023)."},
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
    pack = cycle.get("pack") if isinstance(cycle.get("pack"), dict) else {}
    shipped = int(pack.get("shipped") or pack.get("advanced") or 0)
    skipped = int(pack.get("skipped") or 0)
    quota = int(pack.get("mandatory_quota") or pack.get("max_advance") or 100)
    processed = shipped
    idle_batch = bool(pack.get("idle_batch")) or (processed == 0 and bool(pack.get("batch_complete")))
    registry_exhausted = bool(pack.get("registry_exhausted"))
    pack_ok = skipped == 0 and (shipped >= quota or (idle_batch and registry_exhausted and shipped > 0))
    if idle_batch and registry_exhausted:
        ship_ok = False
        verdict = "drain_complete"
    elif idle_batch:
        ship_ok = False
        verdict = "idle"
    elif pack:
        ship_ok = pack_ok
    else:
        ship_ok = bool((ship or {}).get("ok"))
    if not idle_batch:
        verdict = "approved" if prove_ok and ship_ok else "rejected"
    doc = {
        "schema": "autonomous-forge-run-cycle-receipt-v1",
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
                "Batch complete — idle tick (no rows shipped; not fake SHIP PASS)"
                if verdict == "idle"
                else (
                    "Competitor-1000 drain complete — registry exhausted; next motor forge-real-blueprints"
                    if verdict == "drain_complete"
                    else (
                        "PROVE and SHIP passed from scheduler receipts"
                        if verdict == "approved"
                        else "Halted — gate failed; no forced green"
                    )
                )
            ),
        },
        "cycle": cycle,
        "pack": pack or None,
    }
    if (ship or {}).get("artifact_path"):
        doc["forge_seed"] = {
            "pipeline": (ship or {}).get("pipeline") or ["PLAN", "BUILD", "VALIDATE", "RECEIPT"],
            "artifact_path": (ship or {}).get("artifact_path"),
            "artifact_type": (ship or {}).get("artifact_type"),
            "validator_result": (ship or {}).get("validator_result"),
        }
    pack = cycle.get("pack") if isinstance(cycle.get("pack"), dict) else {}
    batch_id = pack.get("batch_id")
    if batch_id is not None and (pack.get("batch_complete") or cycle.get("decision") in ("pack_complete", "drain_complete")):
        try:
            sys.path.insert(0, str(ROOT / "scripts"))
            from cloud_forge_run_supabase_v1 import batch_sink_invariant  # noqa: WPS433

            inv = batch_sink_invariant(batch_id=int(batch_id))
            doc["sink_invariant"] = inv
            if not inv.get("ok"):
                doc["decision"]["verdict"] = "BLOCKED_WITH_REASON"
                doc["decision"]["block_reason"] = inv.get("blocked_reason")
                doc["decision"]["rationale"] = (
                    f"Sink invariant failed — {inv.get('blocked_reason')} · no silent green"
                )
                doc["artifact"]["status"] = "blocked"
                if doc["belt"].get("SHIP"):
                    doc["belt"]["SHIP"]["ok"] = False
                    doc["belt"]["SHIP"]["gate_cleared"] = False
        except Exception as exc:
            doc["sink_invariant"] = {"ok": False, "error": str(exc)[:120]}
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
        "schema": "autonomous-forge-run-ramp-state-v1",
        "at": _now(),
        "consecutive_green": consecutive,
        "cadence_minutes": base_min,
        "parallelism_cap": 1,
        "ramp_unlocked": False,
    }
    _write(RAMP_STATE_PATH, row)
    return row


FULL_PACK_BODY: dict[str, Any] = {
    "full_pack": True,
    "max_advance": 100,
    "auto_tick": True,
    "force_reset_gate": True,
}


def _with_full_pack(body: dict[str, Any] | None) -> dict[str, Any]:
    """Anti-poison — every Cloud Forge Run trigger is full_pack × 100 (INCIDENT-042)."""
    row = {**FULL_PACK_BODY, **(body or {})}
    row["full_pack"] = True
    row["max_advance"] = int(row.get("max_advance") or 100)
    if row["max_advance"] < 100:
        row["max_advance"] = 100
    return row


def _cloud_queue_action(action: str, **kwargs: Any) -> dict[str, Any]:
    from forge_cloud_env_load_v1 import load_cloud_env  # noqa: WPS433
    from fbe.lib.hub_cloud_proxy_v1 import proxy_get_from_cloud, proxy_to_cloud  # noqa: WPS433

    load_cloud_env(apply=True)
    if action == "get_head":
        return proxy_get_from_cloud(path="/api/cloud-forge-run/queue/v1", timeout_s=60)
    body: dict[str, Any] = {"action": action, **kwargs}
    return proxy_to_cloud(path="/api/cloud-forge-run/queue/v1", body=body, timeout_s=120)


def _cloud_proceed(*, llm_provider: str, full_motor: bool, trigger_source: str = "mac_auto_tick") -> dict[str, Any]:
    from forge_cloud_env_load_v1 import load_cloud_env  # noqa: WPS433
    from fbe.lib.hub_cloud_proxy_v1 import proxy_to_cloud  # noqa: WPS433

    load_cloud_env(apply=True)
    return proxy_to_cloud(
        path="/api/cloud-forge-run/auto-tick/v1",
        body=_with_full_pack(
            {
                "full_motor": full_motor,
                "llm_provider": llm_provider,
                "trigger_source": trigger_source,
            }
        ),
        timeout_s=900,
    )


def _sync_mac_from_cloud_queue() -> dict[str, Any]:
    try:
        from fbe.lib.cloud_forge_run_queue_v1 import sync_to_mac_if_newer  # noqa: WPS433

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
    """Mac Cloud Workers — observe only. CF cron commands Railway; Mac never proxies drain."""
    from cloud_workers_hub_v1 import auto_runtime_status  # noqa: WPS433

    at = _now()
    tick = _read(TICK_RECEIPT)
    phase = _read(SINA / "phase-observed-v1.json")
    deploy = _read(SINA / "fbe-cloud-deploy-receipt-v1.json")
    observer = "https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/observer/v1"
    row = {
        "ok": True,
        "schema": "cloud-auto-runtime-tick-v1",
        "at": at,
        "decision": "mac_observe_only",
        "execution_plane": "mac_control_panel",
        "trigger_source": trigger_source,
        "anti_poison": "mac_never_commands_railway",
        "cloud_scheduler": "cloudflare_cron */10 full_pack max_advance 100",
        "local_head": phase.get("cloud_forge_run_head"),
        "local_batch_id": phase.get("batch_id"),
        "last_cloud_tick_at": tick.get("at"),
        "last_cloud_pack": (tick.get("pack") if isinstance(tick.get("pack"), dict) else None),
        "deploy_at": deploy.get("at"),
        "observer_url": observer,
        "for_founder": {
            "show_this": (
                f"Mac observe only · local head {phase.get('cloud_forge_run_head') or '—'} · "
                f"Cloud Forge Run = CF cron every 10m · proof {observer}"
            ),
        },
        "auto_runtime": auto_runtime_status(),
    }
    _write(TICK_RECEIPT, row)
    return row


def _run_contract_gate() -> dict[str, Any]:
    """Execution contract gate (shared/types · fbe_execution_contract_v1.json)."""
    from fbe.lib.execution_contract_v1 import build_contract, policy_gate, validate_contract  # noqa: WPS433

    contract = build_contract(
        factory_id="forge-app-factory-v1",
        tenant_id="forge",
        execution_mode="CLOUD_ONLY",
        work_order_id="cloud-auto-runtime-tick",
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
        return Path("/app/receipts/cloud/autonomous-forge-run-ramp-state-v1.json")
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
        "schema": "autonomous-forge-run-ramp-state-v1",
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


def _pack_in_progress(mark: bool) -> None:
    from cloud_auto_runtime_single_cycle_gate_v1 import _read_gate, _write_gate, SCHEMA  # noqa: WPS433

    state = _read_gate()
    if mark:
        state.update({"schema": SCHEMA, "pack_in_progress": True, "pack_started_at": _now()})
    else:
        state.pop("pack_in_progress", None)
        state.pop("pack_started_at", None)
    _write_gate(state)


def run_auto_runtime_pack(
    *,
    body: dict[str, Any],
    ssot: dict[str, Any],
    trigger_source: str,
    llm_provider: str,
) -> dict[str, Any]:
    """One external trigger — ship mandatory max_advance rows (NO skip-on-fail — INCIDENT-044)."""
    from hub_cloud_forge_run_proceed_v1 import proceed_on_cloud  # noqa: WPS433
    from fbe.lib.cloud_forge_run_queue_v1 import read_head  # noqa: WPS433

    max_advance = int(body.get("max_advance") or ssot.get("max_advance_per_tick") or 100)
    no_skip = bool(ssot.get("no_skip_law", True))
    advanced = 0
    skipped = 0
    pack_results: list[dict[str, Any]] = []
    last_proceed: dict[str, Any] = {}
    pack_motor = bool(body.get("full_motor", ssot.get("pack_full_motor", False)))

    _pack_in_progress(True)
    try:
        while advanced < max_advance:
            head_row = read_head()
            if head_row.get("queue_batch_complete"):
                break
            head_before = str(head_row.get("cloud_forge_run_head") or "")
            last_proceed = proceed_on_cloud(
                {
                    "plan_id": head_before,
                    "full_motor": pack_motor,
                    "llm_provider": llm_provider or str(ssot.get("llm_provider") or "openrouter"),
                    "auto_tick": True,
                    "_cycle_claimed": True,
                    "_pack_prove_done": True,
                    "_pack_internal": True,
                    "trigger_source": trigger_source,
                    **{
                        k: v
                        for k, v in body.items()
                        if k not in ("full_pack", "max_advance", "full_motor", "plan_id", "maps_registry", "plan_registry")
                    },
                }
            )
            pid = str(last_proceed.get("plan_id") or head_before)
            ok = bool(last_proceed.get("ok"))
            pack_results.append({"plan_id": pid, "ok": ok})
            if ok:
                advanced += 1
                continue
            if no_skip:
                pack_results.append({"plan_id": pid, "ok": False, "halt": "motor_fail_no_skip"})
                break
            break
    finally:
        _pack_in_progress(False)
        try:
            from cloud_auto_runtime_single_cycle_gate_v1 import reset_gate_for_pack  # noqa: WPS433

            reset_gate_for_pack()
        except Exception:
            pass

    processed = advanced
    head_now = read_head()
    batch_done = bool(head_now.get("queue_batch_complete"))
    idle_batch = processed == 0 and batch_done
    registry_exhausted = bool(head_now.get("registry_exhausted"))
    obs = head_now.get("observed") if isinstance(head_now.get("observed"), dict) else {}
    quota_met = advanced >= max_advance or (batch_done and advanced > 0)
    pack_ok = skipped == 0 and (quota_met or (idle_batch and registry_exhausted))
    return {
        "ok": pack_ok,
        "idle_batch": idle_batch,
        "registry_exhausted": registry_exhausted,
        "schema": "cloud-forge-run-pack-v1",
        "advanced": advanced,
        "skipped": skipped,
        "processed": processed,
        "shipped": advanced,
        "mandatory_quota": max_advance,
        "no_skip_law": no_skip,
        "max_advance": max_advance,
        "batch_complete": batch_done,
        "batch_id": obs.get("batch_id"),
        "head_start": pack_results[0].get("plan_id") if pack_results else "",
        "head_now": str(head_now.get("cloud_forge_run_head") or ""),
        "last_completed": str(head_now.get("cloud_forge_run_last_completed") or ""),
        "pack_results_tail": pack_results[-5:],
        "last_proceed": last_proceed,
        "for_founder": {
            "show_this": (
                f"Pack · shipped {advanced}/{max_advance} (mandatory) · skipped {skipped} (must be 0) · "
                f"head {head_now.get('cloud_forge_run_head')} · "
                + (
                    "competitor-1000 COMPLETE · registry exhausted · next: forge-real-blueprints"
                    if idle_batch and registry_exhausted
                    else (
                    "batch COMPLETE · idle (no SHIP this tick)"
                    if idle_batch
                    else ("batch COMPLETE" if batch_done else "next CF cron continues")
                    )
                )
            ),
        },
    }


def run_cloud_auto_tick(
    *,
    body: dict[str, Any] | None = None,
    force: bool = False,
    llm_provider: str = "openrouter",
    trigger_source: str = "cloudflare_cron",
) -> dict[str, Any]:
    """Server-side autonomous tick on Railway — PROVE → contract → SHIP."""
    from fbe.lib.cloud_forge_run_queue_v1 import read_head  # noqa: WPS433

    body = _with_full_pack(body or {})
    trigger_source = str(body.get("trigger_source") or trigger_source)
    force = bool(body.get("force")) or force
    ssot = load_ssot()
    at = _now()
    steps: list[dict[str, Any]] = []

    if not auto_proceed_armed() and not force:
        row = {
            "ok": True,
            "schema": "cloud-auto-runtime-tick-v1",
            "at": at,
            "decision": "observe_only",
            "trigger_source": trigger_source,
            "execution_plane": "headless_cloud",
            "for_founder": {"show_this": "Auto Runtime OFF — set CLOUD_FORGE_RUN_AUTO_PROCEED=true"},
        }
        return row

    from fbe.lib.cloud_forge_run_queue_v1 import boot_heal_queue, read_head  # noqa: WPS433

    try:
        from forge_l3_auto_runtime_v1 import list_pending, tick_forge_l3_repairs  # noqa: WPS433

        pending = list_pending()
        if pending:
            l3_tick = tick_forge_l3_repairs(dry_run=not auto_proceed_armed())
            steps.append({"step": "forge_l3_repairs", "pending": len(pending), "result": l3_tick})
    except Exception as exc:
        steps.append({"step": "forge_l3_repairs", "skipped": str(exc)[:80]})

    try:
        from forge_civilization_loop_v1 import civilization_tick  # noqa: WPS433

        civ = civilization_tick(workspace_path=str(Path.home() / "Desktop" / "SourceA"), dry_run=not auto_proceed_armed())
        steps.append({"step": "forge_civilization_tick", "processed": civ.get("processed"), "result": {"ok": civ.get("ok")}})
    except Exception as exc:
        steps.append({"step": "forge_civilization_tick", "skipped": str(exc)[:80]})

    heal = boot_heal_queue(force=True)
    steps.append({"step": "boot_heal", "result": {"ok": heal.get("ok"), "head": heal.get("head"), "reason": heal.get("activate_reason") or heal.get("heal")}})

    try:
        from cloud_forge_run_supabase_v1 import table_probe, apply_migration_if_missing  # noqa: WPS433

        sb_probe = table_probe()
        if not sb_probe.get("exists"):
            sb_apply = apply_migration_if_missing()
            steps.append({"step": "supabase_schema", "result": sb_apply})
        else:
            steps.append({"step": "supabase_schema", "result": {"ok": True, "exists": True}})
    except Exception as exc:
        steps.append({"step": "supabase_schema", "result": {"ok": False, "error": str(exc)[:120]}})

    cloud_tick_receipt = Path("/app/receipts/cloud/cloud-auto-runtime-tick-receipt-v1.json")

    full_pack_early = body.get("full_pack")
    if full_pack_early is None:
        full_pack_early = bool(ssot.get("full_pack", True))
    if full_pack_early and (
        trigger_source in ("cloudflare_cron", "cloudflare_scheduled", "hub_proceed_pack")
        or body.get("force_reset_gate")
    ):
        from cloud_auto_runtime_single_cycle_gate_v1 import reset_gate_for_pack  # noqa: WPS433

        reset_gate_for_pack()

    if not body.get("_cycle_claimed"):
        from cloud_auto_runtime_single_cycle_gate_v1 import claim_or_halt  # noqa: WPS433

        halt = claim_or_halt(path="/api/cloud-forge-run/auto-tick/v1", trigger_source=trigger_source)
        if halt:
            if halt.get("reason") == "pack_in_progress":
                return {
                    "ok": True,
                    "schema": "cloud-auto-runtime-tick-v1",
                    "at": at,
                    "decision": "pack_in_progress_skip",
                    "trigger_source": trigger_source,
                    "for_founder": {"show_this": "Pack already running on Railway — skip duplicate trigger"},
                }
            return {**halt, "schema": "cloud-auto-runtime-tick-v1"}

    head_row = read_head()
    head = str(head_row.get("cloud_forge_run_head") or "")
    if head_row.get("queue_batch_complete") and not head_row.get("registry_exhausted"):
        from fbe.lib.cloud_forge_run_queue_v1 import boot_heal_queue, seal_registry_exhausted  # noqa: WPS433

        heal = boot_heal_queue(force=True)
        steps.append({"step": "boot_heal_batch_handoff", "result": heal})
        head_row = read_head()
        if head_row.get("queue_batch_complete") and not head_row.get("registry_exhausted"):
            seal = seal_registry_exhausted(reason="auto_tick_batch_complete_no_next")
            steps.append({"step": "seal_registry_exhausted", "result": seal})
            head_row = read_head()
        head = str(head_row.get("cloud_forge_run_head") or "")
    if head_row.get("queue_batch_complete") and head_row.get("registry_exhausted"):
        row = {
            "ok": True,
            "schema": "cloud-auto-runtime-tick-v1",
            "at": at,
            "decision": "drain_complete",
            "head": head,
            "trigger_source": trigger_source,
            "execution_plane": "headless_cloud",
            "queue_batch_complete": True,
            "registry_exhausted": True,
            "for_founder": head_row.get("for_founder")
            or {
                "show_this": (
                    f"Extension wave-2 COMPLETE — {head_row.get('cloud_forge_run_last_completed') or head} · "
                    "registry exhausted · no more CLOUD-SEC rows"
                ),
            },
            "steps": steps,
        }
        _write(cloud_tick_receipt, row)
        return row

    prove = _run_prove_gate()
    steps.append({"step": "prove", "result": {"ok": prove.get("ok"), "summary_line": prove.get("summary_line")}})
    if not prove.get("ok"):
        cycle_row = {
            "ok": False,
            "schema": "cloud-auto-runtime-tick-v1",
            "at": at,
            "decision": "halt_prove",
            "head": head,
            "trigger_source": trigger_source,
            "execution_plane": "headless_cloud",
            "steps": steps,
        }
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
            "schema": "cloud-auto-runtime-tick-v1",
            "at": at,
            "decision": "halt_contract",
            "head": head,
            "trigger_source": trigger_source,
            "execution_plane": "headless_cloud",
            "steps": steps,
        }
        _write_cycle_receipt(cycle=cycle_row, trigger_source=trigger_source, head=head, prove=prove, ship=None)
        _update_ramp_state_cloud(green=False)
        _write(cloud_tick_receipt, cycle_row)
        return cycle_row

    pack = run_auto_runtime_pack(body=body, ssot=ssot, trigger_source=trigger_source, llm_provider=llm_provider)
    steps.append({"step": "pack", "result": pack})
    from cloud_auto_runtime_single_cycle_gate_v1 import claim_or_halt  # noqa: WPS433

    shipped = int(pack.get("advanced") or pack.get("shipped") or 0)
    skipped = int(pack.get("skipped") or 0)
    processed = shipped
    idle_batch = bool(pack.get("idle_batch"))
    registry_exhausted = bool(pack.get("registry_exhausted"))
    quota = int(pack.get("mandatory_quota") or pack.get("max_advance") or 100)
    if pack.get("ok") and shipped >= quota:
        claim_or_halt(path="/api/cloud-forge-run/auto-tick/v1", trigger_source=trigger_source, after_pass=True)
    if idle_batch and registry_exhausted:
        tick_decision = "drain_complete"
    elif idle_batch:
        tick_decision = "batch_idle"
    elif pack.get("batch_complete") and processed > 0:
        tick_decision = "pack_complete"
    elif pack.get("ok"):
        tick_decision = "pack"
    else:
        tick_decision = "pack_stalled"
    row = {
        "ok": bool(pack.get("ok")) or tick_decision == "drain_complete",
        "schema": "cloud-auto-runtime-tick-v1",
        "at": at,
        "decision": tick_decision,
        "head": pack.get("head_now"),
        "plan_id": (pack.get("last_proceed") or {}).get("plan_id"),
        "trigger_source": trigger_source,
        "execution_plane": "headless_cloud",
        "pack": pack,
        "prove_ok": True,
        "contract_ok": True,
        "for_founder": pack.get("for_founder"),
        "steps": steps,
        "anti_poison": "full_pack_only",
    }
    ship_row = pack.get("last_proceed") or {}
    cycle_path = _write_cycle_receipt(
        cycle=row,
        trigger_source=trigger_source,
        head=str(pack.get("head_now") or head),
        prove=prove,
        ship=ship_row,
    )
    row["cycle_receipt_path"] = str(cycle_path)
    row["ramp"] = _update_ramp_state_cloud(green=shipped >= quota and skipped == 0)
    cloud_tick_receipt.parent.mkdir(parents=True, exist_ok=True)
    _write(cloud_tick_receipt, row)
    return row


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Cloud Forge Run auto-runtime v1")
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
        ssot["auto_skip_mock"] = False
        ssot["self_heal_any_motor_fail"] = False
        ssot["self_heal_motor_fail_mock"] = False
        ssot["no_skip_law"] = True
        ssot["saved_at"] = _now()
        _write(SSOT, ssot)
        out = {
            "ok": True,
            "enabled": True,
            "flag": str(AUTO_FLAG),
            "for_founder": {
                "show_this": "Auto Runtime ARMED — 100 shipped rows per turn, zero skips, CF cron → Cloud Forge Run.",
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
        print(out.get("for_founder", {}).get("show_this") or "OK — Auto Runtime ARMED")
        print("Flag:", AUTO_FLAG)
    elif args.disable:
        print("OK — Auto Runtime OFF")
    else:
        print(out.get("for_founder", {}).get("show_this") or out.get("decision") or json.dumps(out, indent=2)[:200])
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
