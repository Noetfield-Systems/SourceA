#!/usr/bin/env python3
"""Cloud Auto Runtime — mock skip · self-heal · scheduled Cloud Forge Run proceed."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(ROOT / "packages" / "sourcea-sdk" / "src"))

from sourcea_sdk.workflow_health import build_heartbeat_loop, build_heartbeat_report, emit_improvement_receipt  # noqa: E402

SINA = Path.home() / ".sina"
SSOT = ROOT / "data/cloud-auto-runtime-v1.json"
TRIGGER_REGISTRY = ROOT / "data" / "trigger-registry-v1.json"
E2E_REGISTRY = ROOT / "data" / "sourcea-e2e-check-registry-v1.json"
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
        "version": "2.0.0",
        "enabled": False,
        "cron": "*/10 * * * *",
        "min_interval_minutes": 10,
        "auto_skip_mock": True,
        "auto_proceed": False,
        "self_heal_motor_fail_mock": True,
        "self_heal_any_motor_fail": True,
        "max_skips_per_tick": 0,
        "max_advance_per_tick": 1,
        "rows_per_turn_cap": 1,
        "llm_provider": "openrouter",
        "full_motor": True,
    }


def max_advance_cap(*, ssot: dict[str, Any] | None = None, body: dict[str, Any] | None = None) -> int:
    """INCIDENT-045 — worker-bounded cap per turn (default 1). No 100-row floor."""
    s = ssot or load_ssot()
    cap = int(s.get("max_advance_per_tick") or s.get("rows_per_turn_cap") or 1)
    requested = int((body or {}).get("max_advance") or cap)
    return max(1, min(requested, cap))


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


HEARTBEAT_DIR_CLOUD = Path("/app/receipts/cloud/autonomous-forge-run-heartbeat")
HEARTBEAT_DIR_LOCAL = ROOT / "receipts" / "cloud" / "autonomous-forge-run-heartbeat"
AUTONOMOUS_TRIGGER_SOURCES = frozenset(
    {"cloudflare_cron", "cloudflare_scheduled", "headless_cloud_auto_tick"}
)


def _heartbeat_dir() -> Path:
    if _is_headless_cloud():
        return HEARTBEAT_DIR_CLOUD
    return HEARTBEAT_DIR_LOCAL


def _resolve_batch_id(
    *,
    pack: dict[str, Any] | None,
    head_row: dict[str, Any] | None = None,
    cycle: dict[str, Any] | None = None,
) -> int | None:
    if isinstance(pack, dict) and pack.get("batch_id") is not None:
        try:
            return int(pack["batch_id"])
        except (TypeError, ValueError):
            pass
    if isinstance(head_row, dict):
        obs = head_row.get("observed") if isinstance(head_row.get("observed"), dict) else {}
        if obs.get("batch_id") is not None:
            try:
                return int(obs["batch_id"])
            except (TypeError, ValueError):
                pass
        if head_row.get("batch_id") is not None:
            try:
                return int(head_row["batch_id"])
            except (TypeError, ValueError):
                pass
    if isinstance(cycle, dict) and cycle.get("batch_id") is not None:
        try:
            return int(cycle["batch_id"])
        except (TypeError, ValueError):
            pass
    return None


def _cycle_op_key(*, workflow_id: str, plan_id: str, attempt_no: int | str | None) -> str:
    """D1 — idempotency key from content only (governed-autorun L13)."""
    raw = f"{workflow_id}|{plan_id}|{attempt_no or 0}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:40]


def _apply_sink_invariant(doc: dict[str, Any], batch_id: int | None) -> dict[str, Any]:
    """Every cycle receipt must carry supabase_count == railway_count or BLOCKED_WITH_REASON."""
    if batch_id is None:
        inv = {"ok": True, "skipped": True, "reason": "no_batch_id", "verdict": "PASS"}
        doc["sink_invariant"] = inv
        return inv
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from cloud_forge_run_supabase_v1 import batch_sink_invariant  # noqa: WPS433

        inv = batch_sink_invariant(batch_id=int(batch_id))
    except Exception as exc:
        inv = {"ok": False, "error": str(exc)[:120], "verdict": "BLOCKED_WITH_REASON"}
    doc["sink_invariant"] = inv
    if not inv.get("ok"):
        decision = doc.setdefault("decision", {})
        decision["verdict"] = "BLOCKED_WITH_REASON"
        decision["block_reason"] = inv.get("blocked_reason") or inv.get("error")
        decision["rationale"] = (
            f"Sink invariant failed — {decision.get('block_reason')} · supabase_count must equal railway_count"
        )
        if isinstance(doc.get("artifact"), dict):
            doc["artifact"]["status"] = "blocked"
        ship = doc.get("belt", {}).get("SHIP")
        if isinstance(ship, dict):
            ship["ok"] = False
            ship["gate_cleared"] = False
    return inv


def _git_head_sha() -> str:
    import subprocess

    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


def _wrangler_committed_truth() -> dict[str, Any]:
    path = ROOT / "cloud/workers/cloud-auto-runtime-tick-v1/wrangler.toml"
    if not path.is_file():
        return {"ok": False, "error": "wrangler_toml_missing"}
    text = path.read_text(encoding="utf-8", errors="replace")
    name = ""
    for line in text.splitlines():
        if line.strip().startswith("name"):
            name = line.split("=", 1)[-1].strip().strip('"').strip("'")
            break
    return {"ok": True, "worker_name": name, "path": str(path), "sha256_prefix": None}


def _resolve_mission_id(*, workflow_id: str) -> str:
    path = ROOT / "data" / "mission-registry-v1.json"
    row = _read(path)
    mapping = row.get("workflow_missions") if isinstance(row.get("workflow_missions"), dict) else {}
    mission_id = str(mapping.get(workflow_id) or row.get("default_mission_id") or "M2")
    return mission_id


def _trigger_registry_sweep_v1() -> dict[str, Any]:
    try:
        from sandbox_health_sweep_v1 import run_sweep  # noqa: WPS433

        return run_sweep(repo_root=ROOT)
    except Exception as exc:
        return {
            "schema": "sandbox-health-sweep-v1",
            "ok": False,
            "drift": True,
            "report_line": f"trigger_sweep_error · {exc}",
            "errors": [str(exc)[:120]],
        }


def _drift_check_v1() -> dict[str, Any]:
    ssot = load_ssot()
    committed_sha = _git_head_sha()
    live_railway_sha = (
        os.environ.get("RAILWAY_GIT_COMMIT_SHA", "").strip()
        or os.environ.get("GIT_COMMIT_SHA", "").strip()
        or os.environ.get("SOURCE_VERSION", "").strip()
    )
    wrangler = _wrangler_committed_truth()
    tick = _read(TICK_RECEIPT)
    last_cron_fire = tick.get("at")
    committed_cron = str(ssot.get("cron") or "*/10 * * * *")
    mismatches: list[dict[str, Any]] = []
    if live_railway_sha and committed_sha not in ("unknown", "") and live_railway_sha[:12] != committed_sha[:12]:
        mismatches.append(
            {
                "surface": "railway_deploy",
                "committed_truth": committed_sha[:12],
                "deployed_truth": live_railway_sha[:12],
            }
        )
    cf_meta = os.environ.get("CF_VERSION_METADATA", "").strip()
    if cf_meta and wrangler.get("worker_name") and cf_meta not in wrangler.get("worker_name", ""):
        mismatches.append(
            {
                "surface": "worker_version",
                "committed_truth": wrangler.get("worker_name"),
                "deployed_truth": cf_meta[:80],
            }
        )
    trigger_sweep = _trigger_registry_sweep_v1()
    if trigger_sweep.get("drift") or not trigger_sweep.get("ok"):
        mismatches.append(
            {
                "surface": "trigger_registry",
                "committed_truth": trigger_sweep.get("registry_path"),
                "deployed_truth": trigger_sweep.get("report_line"),
                "dead_or_mismatch": trigger_sweep.get("dead_or_mismatch"),
                "unregistered_live": trigger_sweep.get("unregistered_live"),
            }
        )
    deploy_ok = len([m for m in mismatches if m.get("surface") != "trigger_registry"]) == 0
    return {
        "schema": "drift-receipt-v1",
        "checked": True,
        "at": _now(),
        "committed_sha": committed_sha,
        "live_railway_sha": live_railway_sha or None,
        "wrangler": wrangler,
        "committed_cron": committed_cron,
        "last_cron_fire": last_cron_fire,
        "trigger_sweep": trigger_sweep,
        "mismatches": mismatches,
        "ok": deploy_ok and bool(trigger_sweep.get("ok")),
    }


def _observe_sync_health_report(
    *,
    head_row: dict[str, Any],
    sink_inv: dict[str, Any],
    trigger_source: str,
    drift: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    tick = _read(TICK_RECEIPT)
    trigger_sweep = _trigger_registry_sweep_v1()
    drift = drift or _drift_check_v1()
    runtime_registry = _read(SSOT)
    trigger_registry = _read(TRIGGER_REGISTRY)
    e2e_registry = _read(E2E_REGISTRY)
    e2e_summary = e2e_registry.get("summary") if isinstance(e2e_registry.get("summary"), dict) else {}
    e2e_slo = e2e_registry.get("slo") if isinstance(e2e_registry.get("slo"), dict) else {}

    runtime_loop = build_heartbeat_loop(
        workflow_id="cloud-auto-runtime",
        lane="observe_sync",
        targets=runtime_registry.get("slo") if isinstance(runtime_registry.get("slo"), dict) else None,
        observed={
            "last_run_at": tick.get("at"),
            "freshness_minutes": _minutes_since(str(tick.get("at") or "")),
            "success_rate": 1.0 if tick.get("ok", True) else 0.0,
            "latency_minutes": 0.0,
        },
        evidence=[
            {
                "command": "cloud_auto_runtime_tick",
                "exit_code": 0 if tick.get("ok", True) else 1,
                "output": str(tick.get("decision") or tick.get("schema") or "")[:240],
            }
        ],
        last_run_at=tick.get("at"),
        sink_invariant_ok=bool(sink_inv.get("ok", True)),
    )

    trigger_loop = build_heartbeat_loop(
        workflow_id="trigger-boundary-sweep",
        lane="boundary_check",
        targets=trigger_registry.get("slo") if isinstance(trigger_registry.get("slo"), dict) else None,
        observed={
            "last_run_at": trigger_sweep.get("at"),
            "freshness_minutes": _minutes_since(str(trigger_sweep.get("at") or "")),
            "success_rate": 1.0 if trigger_sweep.get("ok") else 0.0,
            "latency_minutes": 0.0,
        },
        evidence=[
            {
                "command": "sandbox_health_sweep_v1",
                "exit_code": 0 if trigger_sweep.get("ok") else 1,
                "output": str(trigger_sweep.get("report_line") or trigger_sweep.get("reason") or "")[:240],
            }
        ],
        last_run_at=trigger_sweep.get("at"),
        sink_invariant_ok=bool(sink_inv.get("ok", True)),
        throttled_roi=not bool(trigger_sweep.get("ok")),
    )

    e2e_loop = build_heartbeat_loop(
        workflow_id="sourcea-e2e-registry",
        lane="observe_sync",
        targets=e2e_slo or None,
        observed={
            "last_run_at": e2e_registry.get("generated_at"),
            "freshness_minutes": _minutes_since(str(e2e_registry.get("generated_at") or "")),
            "success_rate": 1.0 if e2e_summary.get("filing_registry_validator_present") else 0.0,
            "latency_minutes": float(e2e_slo.get("latency_target_minutes") or 0.0),
        },
        evidence=[
            {
                "command": "sourcea_e2e_registry_generate_v1",
                "exit_code": 0 if e2e_summary.get("filing_registry_validator_present") else 1,
                "output": str(e2e_summary.get("total_checks") or "")[:240],
            }
        ],
        last_run_at=e2e_registry.get("generated_at"),
        sink_invariant_ok=True,
    )

    report = build_heartbeat_report(
        loops=[runtime_loop, trigger_loop, e2e_loop],
        drift=drift,
        founder_blocked_total=_founder_blocked_snapshot().get("count", 0),
    )
    report["trigger_source"] = trigger_source
    report["queue_head"] = head_row.get("cloud_forge_run_head")
    receipt = emit_improvement_receipt(
        report=report,
        repo_root=ROOT,
        rollback_command="python3 scripts/cloud_auto_runtime_v1.py --disable",
    )
    if receipt:
        report["kaizen_receipt"] = {
            "id": receipt.get("id"),
            "path": receipt.get("path"),
        }
        report["founder_gated_improvements"] = [
            {
                "id": receipt.get("id"),
                "expected_roi": receipt.get("expected_roi") or {},
                "age_days": 0,
            }
        ]
    return report, receipt


def _founder_blocked_snapshot() -> dict[str, Any]:
    candidates = [
        SINA / "founder-blocked-queue-v1.json",
        ROOT / "data" / "founder-blocked-queue-v1.json",
    ]
    for path in candidates:
        row = _read(path)
        if not row:
            continue
        items = row.get("items") if isinstance(row.get("items"), list) else []
        if not items and isinstance(row.get("count"), int):
            return {
                "count": int(row.get("count") or 0),
                "oldest_id": str(row.get("oldest_id") or ""),
                "priority": str(row.get("priority") or ""),
                "age_seconds": int(row.get("age_seconds") or 0),
                "escalated": bool(row.get("escalated")),
            }
        if items:
            oldest = items[0] if isinstance(items[0], dict) else {}
            return {
                "count": len(items),
                "oldest_id": str(oldest.get("id") or oldest.get("item_id") or ""),
                "priority": str(oldest.get("priority") or ""),
                "age_seconds": int(oldest.get("age_seconds") or 0),
                "escalated": bool(oldest.get("escalated")),
            }
    return {
        "count": 0,
        "oldest_id": "",
        "priority": "",
        "age_seconds": 0,
        "escalated": False,
    }


def _cycle_cost_v2(*, cycle: dict[str, Any], shipped: int, idle: bool) -> dict[str, Any]:
    existing = cycle.get("cost") if isinstance(cycle.get("cost"), dict) else None
    if existing:
        return existing
    if idle:
        return {
            "provider": "none",
            "model": "",
            "tokens_in": 0,
            "tokens_out": 0,
            "unit_cost_usd": 0,
            "total_usd": 0,
        }
    provider = str(os.environ.get("OPENROUTER_API_KEY") and "openrouter" or load_ssot().get("llm_provider") or "openrouter")
    est_usd = round(max(0.0, shipped) * 0.002, 4)
    return {
        "provider": provider,
        "model": str(cycle.get("llm_model") or ""),
        "tokens_in": int(cycle.get("tokens_in") or 0),
        "tokens_out": int(cycle.get("tokens_out") or 0),
        "unit_cost_usd": 0.002 if shipped else 0,
        "total_usd": est_usd,
    }


def _value_class_v2(*, shipped: int, idle: bool, registry_exhausted: bool, verdict: str) -> str:
    if verdict == "IDLE_NO_WORK" and registry_exhausted:
        return "hygiene"
    if shipped > 0:
        return "proof_asset"
    if idle:
        return "hygiene"
    return "none"


def _gate_evidence_v2(
    *,
    prove: dict[str, Any] | None,
    ship: dict[str, Any] | None,
    decision: dict[str, Any],
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    if prove is not None:
        evidence.append(
            {
                "command": "living_system_chain_validate_v1",
                "exit_code": 0 if prove.get("ok") else 1,
                "output": str(prove.get("summary_line") or prove.get("error") or "")[:500],
            }
        )
    if ship is not None:
        evidence.append(
            {
                "command": "cloud_forge_run_ship",
                "exit_code": 0 if ship.get("ok") else 1,
                "output": str(ship.get("hub_proceed_line") or ship.get("validator_result") or "")[:500],
            }
        )
    evidence.append(
        {
            "command": "autonomous_drain_gate",
            "exit_code": 0 if decision.get("verdict") in ("approved", "IDLE_NO_WORK") else 1,
            "output": str(decision.get("rationale") or decision.get("verdict") or "")[:500],
        }
    )
    return evidence


def _write_daily_heartbeat_if_due(
    *,
    head_row: dict[str, Any],
    sink_inv: dict[str, Any],
    trigger_source: str,
) -> Path | None:
    """UTC-day heartbeat with L12 drift refresh on every cycle."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    hb_dir = _heartbeat_dir()
    hb_dir.mkdir(parents=True, exist_ok=True)
    path = hb_dir / f"heartbeat-{today}-v1.json"
    obs = head_row.get("observed") if isinstance(head_row.get("observed"), dict) else {}
    if path.is_file():
        doc = _read(path)
    else:
        doc = {
            "schema": "autonomous-forge-run-daily-heartbeat-v2",
            "version": "2.0.0",
            "date": today,
            "at": _now(),
            "trigger_source": trigger_source,
            "queue_head": head_row.get("cloud_forge_run_head"),
            "last_completed": head_row.get("cloud_forge_run_last_completed"),
            "batch_state": {
                "batch_id": obs.get("batch_id") or head_row.get("batch_id"),
                "queue_batch_complete": head_row.get("queue_batch_complete"),
                "registry_exhausted": head_row.get("registry_exhausted"),
                "drain_status": head_row.get("drain_status"),
            },
            "sink_status": sink_inv,
            "autonomy": {
                "zero_manual": True,
                "scheduler": "cloudflare_cron */10 * * * *",
                "law": "empty_queue=IDLE_NO_WORK · sink mismatch=BLOCKED_WITH_REASON",
            },
            "founder_blocked_total": _founder_blocked_snapshot().get("count", 0),
        }
    doc["schema"] = "autonomous-forge-run-daily-heartbeat-v2"
    doc["version"] = "2.0.0"
    doc["at"] = _now()
    doc["sink_status"] = sink_inv
    doc["drift"] = _drift_check_v1()
    doc["founder_blocked_total"] = _founder_blocked_snapshot().get("count", 0)
    try:
        from autorun_pending_v1 import write_pending_receipt  # noqa: WPS433

        pending = write_pending_receipt()
    except Exception as exc:
        pending = {
            "schema": "autorun-pending-v1",
            "ok": False,
            "count": 1,
            "items": [{"id": "pending_write_failed", "reason": str(exc)[:120]}],
            "report_line": f"pending_write_failed · {exc}",
        }
    doc["pending"] = pending
    doc["escalations"] = [str(i.get("id") or "") for i in pending.get("items") or [] if i.get("severity") == "P0"]
    workflow_health, receipt = _observe_sync_health_report(
        head_row=head_row,
        sink_inv=sink_inv,
        trigger_source=trigger_source,
        drift=doc["drift"],
    )
    doc["workflow_health"] = workflow_health
    if receipt:
        doc["workflow_health"]["kaizen_receipt_path"] = receipt.get("path")
    _write(path, doc)
    if not _is_headless_cloud():
        mirror = SINA / "autonomous-forge-run-daily-heartbeat-v1.json"
        _write(mirror, doc)
    return path


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
    head_row: dict[str, Any] | None = None,
) -> Path:
    """Append one autonomous cycle receipt — green or honest-halt."""
    CYCLE_RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    safe_at = str(cycle.get("at") or _now()).replace(":", "").replace("-", "")
    path = CYCLE_RECEIPTS_DIR / f"cycle-{safe_at}-v1.json"
    prove_ok = bool((prove or {}).get("ok"))
    pack = cycle.get("pack") if isinstance(cycle.get("pack"), dict) else {}
    shipped = int(pack.get("shipped") or pack.get("advanced") or 0)
    skipped = int(pack.get("skipped") or 0)
    quota = int(pack.get("mandatory_quota") or pack.get("max_advance") or max_advance_cap())
    processed = shipped
    idle_batch = bool(pack.get("idle_batch")) or (processed == 0 and bool(pack.get("batch_complete")))
    registry_exhausted = bool(pack.get("registry_exhausted"))
    pack_ok = skipped == 0 and (shipped >= quota or (idle_batch and registry_exhausted and shipped > 0))
    verdict = ""
    if processed == 0 and (
        idle_batch
        or cycle.get("decision") in ("batch_idle", "drain_complete")
        or (head_row or {}).get("queue_batch_complete")
    ):
        ship_ok = False
        verdict = "IDLE_NO_WORK"
    elif pack:
        ship_ok = pack_ok
    else:
        ship_ok = bool((ship or {}).get("ok"))
    if verdict != "IDLE_NO_WORK":
        verdict = "approved" if prove_ok and ship_ok else "rejected"
    to_state = (
        "IDLE_NO_WORK"
        if verdict == "IDLE_NO_WORK"
        else ("COMPLETE" if verdict == "approved" else "BLOCKED_WITH_REASON")
    )
    try:
        from autorun_legal_transitions_v1 import validate_transition  # noqa: WPS433

        transition = validate_transition("RUNNING", to_state)
    except Exception as exc:
        transition = {"ok": False, "reason": str(exc)[:80]}
    decision_block = {
        "decision_type": "autonomous_drain_gate",
        "verdict": verdict,
        "state": to_state,
        "work_packet_terminal": (
            "ACCEPTED_ARTIFACT"
            if to_state == "COMPLETE" and shipped > 0
            else "BOUNDED_FAILURE"
        ),
        "transition": transition,
        "transition_log_tail": [
            {
                "from": "RUNNING",
                "to": to_state,
                "legal": bool(transition.get("ok")),
                "at": cycle.get("at") or _now(),
            }
        ],
        "rationale": cycle.get("decision_rationale")
        or (
            "Empty queue — IDLE_NO_WORK (healthy; no manufactured work)"
            if verdict == "IDLE_NO_WORK"
            else (
                "PROVE and SHIP passed from scheduler receipts"
                if verdict == "approved"
                else "Halted — gate failed; no forced green"
            )
        ),
    }
    cost = _cycle_cost_v2(cycle=cycle, shipped=shipped, idle=verdict == "IDLE_NO_WORK")
    value_class = _value_class_v2(
        shipped=shipped,
        idle=verdict == "IDLE_NO_WORK",
        registry_exhausted=registry_exhausted,
        verdict=verdict,
    )
    founder_blocked = _founder_blocked_snapshot()
    gate_evidence = _gate_evidence_v2(prove=prove, ship=ship, decision=decision_block)
    workflow_id = "cloud-forge-run"
    mission_id = _resolve_mission_id(workflow_id=workflow_id)
    doc = {
        "schema": "autonomous-forge-run-cycle-receipt-v2",
        "version": "2.0.0",
        "at": cycle.get("at") or _now(),
        "trigger_source": trigger_source,
        "mission_id": mission_id,
        "workflow_id": workflow_id,
        "factory": "forge-drain",
        "blueprint_id": "MAC-CTL-002",
        "queue_head": head,
        "cost": cost,
        "value_class": value_class,
        "founder_blocked": founder_blocked,
        "gate_evidence": gate_evidence,
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
        "decision": decision_block,
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
    batch_id = _resolve_batch_id(pack=pack, head_row=head_row, cycle=cycle)
    doc["idempotency_key"] = _cycle_op_key(
        workflow_id="cloud-forge-run",
        plan_id=head,
        attempt_no=batch_id,
    )
    sink_inv = _apply_sink_invariant(doc, batch_id)
    if head_row:
        _write_daily_heartbeat_if_due(head_row=head_row, sink_inv=sink_inv, trigger_source=trigger_source)
    try:
        from autorun_pending_v1 import write_pending_receipt  # noqa: WPS433

        pending = write_pending_receipt()
    except Exception as exc:
        pending = {
            "schema": "autorun-pending-v1",
            "ok": False,
            "count": 1,
            "items": [{"id": "pending_write_failed", "reason": str(exc)[:120]}],
            "report_line": f"pending_write_failed · {exc}",
        }
    doc["pending"] = pending
    doc["pending_count"] = int(pending.get("count") or 0)
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
    "max_advance": 10,
    "auto_tick": True,
    "force_reset_gate": True,
}


def _with_full_pack(body: dict[str, Any] | None) -> dict[str, Any]:
    """Anti-poison — every Cloud Forge Run trigger is full_pack × capped rows (INCIDENT-045)."""
    ssot = load_ssot()
    row = {**FULL_PACK_BODY, **(body or {})}
    row["full_pack"] = True
    row["max_advance"] = max_advance_cap(ssot=ssot, body=row)
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
        "cloud_scheduler": "cloudflare_cron */10 full_pack max_advance capped",
        "local_head": phase.get("cloud_forge_run_head"),
        "local_batch_id": phase.get("batch_id"),
        "last_cloud_tick_at": tick.get("at"),
        "last_cloud_pack": (tick.get("pack") if isinstance(tick.get("pack"), dict) else None),
        "deploy_at": deploy.get("at"),
        "observer_url": observer,
        "for_founder": {
            "show_this": (
                f"Mac motor observe only · local head {phase.get('cloud_forge_run_head') or '—'} · "
                f"Cloud Forge Run = CF cron every 10m · dispatch via Hub OK · proof {observer}"
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
    """One external trigger — ship up to max_advance rows (NO skip-on-fail — INCIDENT-044)."""
    from hub_cloud_forge_run_proceed_v1 import proceed_on_cloud  # noqa: WPS433
    from fbe.lib.cloud_forge_run_queue_v1 import read_head  # noqa: WPS433

    max_advance = max_advance_cap(ssot=ssot, body=body)
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
                f"Pack · shipped {advanced}/{max_advance} (cap) · skipped {skipped} (must be 0) · "
                f"head {head_now.get('cloud_forge_run_head')} · "
                + (
                    "-1000 COMPLETE · registry exhausted · next: forge-real-blueprints"
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
        obs = head_row.get("observed") if isinstance(head_row.get("observed"), dict) else {}
        pack_idle: dict[str, Any] = {
            "ok": True,
            "idle_batch": True,
            "registry_exhausted": True,
            "schema": "cloud-forge-run-pack-v1",
            "advanced": 0,
            "skipped": 0,
            "processed": 0,
            "shipped": 0,
            "mandatory_quota": max_advance_cap(ssot=ssot),
            "max_advance": max_advance_cap(ssot=ssot),
            "batch_complete": True,
            "batch_id": obs.get("batch_id") or head_row.get("batch_id"),
            "head_now": head,
            "last_completed": str(head_row.get("cloud_forge_run_last_completed") or ""),
        }
        prove_idle = _run_prove_gate()
        steps.append({"step": "prove", "result": {"ok": prove_idle.get("ok"), "summary_line": prove_idle.get("summary_line")}})
        cycle_row = {
            "ok": True,
            "schema": "cloud-auto-runtime-tick-v1",
            "at": at,
            "decision": "batch_idle",
            "head": head,
            "trigger_source": trigger_source,
            "execution_plane": "headless_cloud",
            "queue_batch_complete": True,
            "registry_exhausted": True,
            "pack": pack_idle,
            "for_founder": head_row.get("for_founder")
            or {
                "show_this": (
                    f"Registry exhausted — {head_row.get('cloud_forge_run_last_completed') or head} · "
                    "IDLE_NO_WORK (no manufactured rows)"
                ),
            },
            "steps": steps,
        }
        cycle_path = _write_cycle_receipt(
            cycle=cycle_row,
            trigger_source=trigger_source,
            head=head,
            prove=prove_idle,
            ship=None,
            head_row=head_row,
        )
        row = {**cycle_row, "cycle_receipt_path": str(cycle_path)}
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
        _write_cycle_receipt(
            cycle=cycle_row, trigger_source=trigger_source, head=head, prove=prove, ship=None, head_row=head_row
        )
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
        _write_cycle_receipt(
            cycle=cycle_row, trigger_source=trigger_source, head=head, prove=prove, ship=None, head_row=head_row
        )
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
    quota = int(pack.get("mandatory_quota") or pack.get("max_advance") or max_advance_cap())
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
        head_row=head_row,
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
                "show_this": "Auto Runtime ARMED — up to 10 proof-gated rows per turn, zero skips, CF cron → Cloud Forge Run.",
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
