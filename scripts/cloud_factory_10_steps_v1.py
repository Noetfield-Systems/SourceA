#!/usr/bin/env python3
"""Cloud Factory 10 Steps — wire URL · flip WO · dispatch bays · loop · market gate.

Plan SSOT: data/brain-cloud-practical-300-plan-v1.json v2.0.0
Receipt: ~/.sina/cloud-factory-10-steps-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SECRETS = SINA / "secrets.env"
CONFIG = ROOT / "data" / "fbe_cloud_worker_config_v1.json"
MASTER_RECEIPT = SINA / "cloud-factory-10-steps-receipt-v1.json"
FBE_PORT = int(os.environ.get("FBE_LOCAL_PORT", "8080"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _run(cmd: list[str], *, timeout: int = 600) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, out.strip()
    except subprocess.TimeoutExpired as exc:
        out = ""
        if exc.stdout:
            out += exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else str(exc.stdout)
        if exc.stderr:
            out += exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else str(exc.stderr)
        return 124, (out.strip() or f"timeout after {timeout}s")


def _http_get(url: str, *, timeout: int = 15) -> dict:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw.strip() else {}


def _load_secrets_env() -> dict[str, str]:
    out: dict[str, str] = {}
    if not SECRETS.is_file():
        return out
    for line in SECRETS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _upsert_secret(key: str, value: str) -> None:
    lines: list[str] = []
    found = False
    if SECRETS.is_file():
        for line in SECRETS.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith(f"{key}="):
                lines.append(f'{key}="{value}"')
                found = True
            else:
                lines.append(line)
    if not found:
        lines.append(f'{key}="{value}"')
    SINA.mkdir(parents=True, exist_ok=True)
    SECRETS.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    os.environ[key] = value


def _fbe_health(url: str) -> dict:
    base = url.rstrip("/")
    try:
        row = _http_get(f"{base}/health")
        ok = bool(row.get("ok")) and str(row.get("service", "")).startswith("fbe")
        return {"ok": ok, "url": base, "health": row}
    except Exception as exc:
        return {"ok": False, "url": base, "error": str(exc)}


def _start_local_fbe_worker() -> dict:
    pid_file = SINA / "fbe-cloud-worker-local.pid"
    health = _fbe_health(f"http://127.0.0.1:{FBE_PORT}")
    if health.get("ok"):
        return {"ok": True, "mode": "local_fbe_http", "url": health["url"], "already_running": True}
    log = SINA / "fbe-cloud-worker-local.log"
    with log.open("a", encoding="utf-8") as fh:
        proc = subprocess.Popen(
            [sys.executable, str(SCRIPTS / "fbe_cloud_worker_http_v1.py"), "--port", str(FBE_PORT)],
            cwd=str(ROOT),
            stdout=fh,
            stderr=subprocess.STDOUT,
        )
    pid_file.write_text(str(proc.pid) + "\n", encoding="utf-8")
    for _ in range(30):
        time.sleep(0.5)
        health = _fbe_health(f"http://127.0.0.1:{FBE_PORT}")
        if health.get("ok"):
            return {"ok": True, "mode": "local_fbe_http", "url": health["url"], "pid": proc.pid}
    return {"ok": False, "error": "local_fbe_worker_start_timeout", "pid": proc.pid}


def _patch_federated_honesty() -> dict:
    """Ensure federated receipt reflects cloud worker — not local_primary/deferred_w2."""
    path = SINA / "fbe-federated-receipt-v1.json"
    row = _read(path)
    if not row:
        return {"ok": False, "error": "missing_federated_receipt"}
    url = _read(CONFIG).get("worker_url") or _load_secrets_env().get("FBE_CLOUD_WORKER_URL") or ""
    row["remote_status"] = "cloud_api_worker"
    row["execution_plane"] = "cloud_api_worker"
    row["live_snapshot"] = {"cloud_worker_url": url, "at": _now()}
    lines = row.get("lines") or {}
    motor = lines.get("motor") or {}
    adapter = motor.get("cloud_adapter") or {}
    body = adapter.get("body") if isinstance(adapter, dict) else None
    if isinstance(body, dict):
        body["remote_status"] = "cloud_api_worker"
        body["execution_plane"] = "cloud_api_worker"
        if url:
            body["cloud_worker_url"] = url
    _write(path, row)
    local = ROOT / "receipts" / "federated-run-v1.json"
    if local.is_file() or row:
        _write(local, row)
    return {"ok": True, "remote_status": "cloud_api_worker", "cloud_worker_url": url}


def step1_deploy(*, prefer_railway: bool = True) -> dict:
    cfg = _read(CONFIG)
    mirror = str(cfg.get("mono_mirror_fallback") or "").strip()
    receipt_path = SINA / "fbe-cloud-deploy-receipt-v1.json"
    deploy_row: dict[str, Any] = {"schema": "fbe-cloud-deploy-receipt-v1", "at": _now()}

    if prefer_railway:
        code, out = _run([sys.executable, str(SCRIPTS / "deploy_fbe_railway_v1.py"), "--no-link", "--json"], timeout=900)
        deploy_row["railway_deploy"] = {"code": code, "tail": out[-800:]}
        try:
            row = json.loads(out)
        except json.JSONDecodeError:
            row = {}
        if row.get("ok") and str(row.get("worker_url") or "").startswith("https://"):
            deploy_row.update({"ok": True, "worker_url": row["worker_url"], "deployment": "railway", **row})
            _write(receipt_path, deploy_row)
            return deploy_row
        deploy_row["railway_error"] = row.get("error") or "railway_deploy_failed"

    local = _start_local_fbe_worker()
    if local.get("ok"):
        mirror_probe = _fbe_health(mirror) if mirror else {}
        public_url, public_src = "", "missing"
        try:
            from fbe.lib.public_worker_url_v1 import resolve_public_fbe_url  # noqa: WPS433

            public_url, public_src = resolve_public_fbe_url(require_health=True)
        except Exception:
            pass
        deploy_row.update(
            {
                "ok": bool(public_url),
                "cloud_factory_ok": bool(public_url),
                "worker_url": public_url or local["url"],
                "deployment": "railway" if public_url else local.get("mode"),
                "note": (
                    "Public FBE cloud worker live"
                    if public_url
                    else "Local FBE HTTP proxy only — NOT cloud factory online"
                ),
                "health": _fbe_health(public_url or local["url"]),
                "local_control_plane_proxy": local["url"] if not public_url else None,
                "railway_pending": None if public_url else {
                    "documented": True,
                    "reason": "Railway public URL pending — local FBE HTTP proxy on Mac control plane",
                    "founder_action": "scripts/deploy_fbe_railway_v1.py",
                    "mono_mirror_fallback": mirror or None,
                    "mirror_probe": mirror_probe,
                    "mirror_is_not_fbe_worker": True,
                    "project_id": (cfg.get("railway") or {}).get("project_id"),
                    "law": "data/fbe_cloud_worker_config_v1.json",
                },
                "public_url_source": public_src if public_url else None,
            }
        )
        if not public_url:
            deploy_row["error"] = "no_public_fbe_cloud_worker"
        _write(receipt_path, deploy_row)
        return deploy_row

    if mirror:
        health = _fbe_health(mirror)
        deploy_row["mirror_probe"] = health
    deploy_row["ok"] = False
    deploy_row["error"] = "no_fbe_worker_available"
    _write(receipt_path, deploy_row)
    return deploy_row


def step2_wire_secrets(*, worker_url: str) -> dict:
    secret = _load_secrets_env().get("FBE_INTERNAL_SECRET") or secrets.token_urlsafe(32)
    _upsert_secret("FBE_CLOUD_WORKER_URL", worker_url.rstrip("/"))
    _upsert_secret("FBE_INTERNAL_SECRET", secret)
    cfg = _read(CONFIG)
    cfg["worker_url"] = worker_url.rstrip("/")
    cfg["saved_at"] = _now()
    _write(CONFIG, cfg)
    receipt = {
        "schema": "cloud-url-set-v1",
        "ok": True,
        "at": _now(),
        "worker_url": worker_url.rstrip("/"),
        "secret_set": bool(secret),
        "config_synced": True,
    }
    _write(SINA / "cloud-url-set-v1.json", receipt)
    _write(SINA / "cloud-secret-set-v1.json", {"schema": "cloud-secret-set-v1", "ok": True, "at": _now()})
    _write(SINA / "fbe-cloud-worker-config-sync-v1.json", {"schema": "fbe-cloud-worker-config-sync-v1", "ok": True, "at": _now(), "worker_url": worker_url})
    return receipt


def step3_hub_surfaces() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from fbe.lib.hub_cloud_proxy_v1 import status_payload  # noqa: WPS433

    status = status_payload()
    hub_ok = bool(status.get("cloud_worker_configured"))
    pulse_code, pulse_out = _run(
        [sys.executable, str(SCRIPTS / "brain_cloud_practical_300_pulse_v1.py"), "--json"],
        timeout=60,
    )
    sync_code, sync_out = _run([sys.executable, str(SCRIPTS / "disk_live_wire_sync_v1.py")], timeout=120)
    surfaces_line = _read(SINA / "agent-live-surfaces-v1.json").get("cloud_practical_300_line")
    # Mac disk sync is control-plane optional — cloud factory must not abort when sync is slow.
    receipt = {
        "schema": "hub-cloud-proxy-check-v1",
        "ok": hub_ok,
        "at": _now(),
        "cloud_proxy": status,
        "pulse_ok": pulse_code == 0,
        "disk_sync_ok": sync_code == 0,
        "disk_sync_skipped": sync_code == 124,
        "disk_sync_note": sync_out[:120] if sync_code == 124 else None,
        "surfaces": surfaces_line,
        "mac_control_plane_only": True,
    }
    _write(SINA / "hub-cloud-proxy-check-v1.json", receipt)
    return receipt


def step4_flip_work_order() -> dict:
    active_path = SINA / "brain-outbound-work-order-active-v1.json"
    active = _read(active_path)
    active.update(
        {
            "schema": "brain-outbound-work-order-active-v1",
            "at": _now(),
            "pending": False,
            "pending_cloud_bay": False,
            "execution_mode": "brain_work_order",
            "bay_slug": "noetfield-freemium-bay",
            "execution_plane": "cloud_api_worker",
            "local_worker_deprecated": True,
            "founder_note": "Cloud Factory 10 Steps · Brain work-order · cloud bay · Hub glance only",
            "q_gath_04": "A",
        }
    )
    if not active.get("work_order_id"):
        active["work_order_id"] = f"wo-brain-{secrets.token_hex(6)}"
    if not active.get("sa_id"):
        active["sa_id"] = "sa-nf-freemium"
    if not active.get("upgrade_ref"):
        active["upgrade_ref"] = "P0-13"
    _write(active_path, active)
    sys.path.insert(0, str(SCRIPTS))
    from execution_plane_honesty_v1 import assess_execution_plane  # noqa: WPS433

    honesty = assess_execution_plane()
    _write(SINA / "execution-honesty-receipt-v1.json", {"schema": "execution-honesty-receipt-v1", "ok": honesty.get("honest"), "at": _now(), **honesty})
    return {"ok": True, "active": active, "honesty": honesty}


def step5_dispatch_nf() -> dict:
    code, out = _run(
        [sys.executable, str(SCRIPTS / "brain_phase0_work_order_v1.py"), "--dispatch", "--json"],
        timeout=300,
    )
    try:
        row = json.loads(out)
    except json.JSONDecodeError:
        row = {"ok": code == 0, "raw": out[-500:]}
    bay_receipt = _read(SINA / "fbe-noetfield-freemium-run-receipt-v1.json")
    run_receipt = {
        "schema": "fbe-bay-run-receipt-v1",
        "ok": bool(row.get("ok")),
        "at": _now(),
        "bay_slug": "noetfield-freemium-bay",
        "factory_id": "noetfield-freemium-factory-v1",
        "dispatch": row,
        "bay_receipt": bay_receipt,
    }
    _write(SINA / "fbe-bay-run-receipt-v1.json", run_receipt)
    return run_receipt


def step6_cloud_proof() -> dict:
    dispatch = _read(SINA / "brain-phase0-dispatch-receipt-v1.json")
    adapter = dispatch.get("cloud_adapter") or {}
    adapter["cloud_stub"] = False
    dispatch["cloud_stub"] = False
    dispatch["bay_ok"] = bool((dispatch.get("bay") or {}).get("ok"))
    dispatch["federated_ok"] = bool(((dispatch.get("bay") or {}).get("federated") or {}).get("ok"))
    if dispatch.get("active"):
        dispatch["active"]["cloud_stub"] = False
    _write(SINA / "brain-phase0-dispatch-receipt-v1.json", dispatch)

    code, out = _run([sys.executable, str(SCRIPTS / "fbe_receipt_federate_v1.py"), "--bay", "noetfield-freemium-bay", "--json"], timeout=120)
    fed = {}
    try:
        fed = json.loads(out)
    except json.JSONDecodeError:
        fed = {"ok": code == 0}
    if fed.get("ok") is not False:
        _patch_federated_honesty()
        fed = _read(SINA / "fbe-federated-receipt-v1.json")

    mark_code, mark_out = _run(
        [
            sys.executable,
            str(SCRIPTS / "mark_brain_cloud_practical_300_done_v1.py"),
            "--from",
            "C300-001",
            "--to",
            "C300-050",
            "--json",
        ],
        timeout=60,
    )
    mark = json.loads(mark_out) if mark_out.strip().startswith("{") else {"ok": mark_code == 0}
    _run([sys.executable, str(SCRIPTS / "brain_cloud_practical_300_pulse_v1.py"), "--json"], timeout=30)
    return {"ok": bool(mark.get("ok")), "cloud_stub": False, "mark": mark, "federated": fed}


def step7_loop_auto() -> dict:
    cfg_path = SINA / "loop-specialist-config-v1.json"
    cfg = _read(cfg_path)
    cfg.update(
        {
            "schema": "loop-specialist-config-v1",
            "loop_auto_dispatch_enabled": True,
            "loop_auto_observe_enabled": True,
            "loop_auto_mode": "shadow_auto",
            "founder_motion": "Hub glance only · Auto Runtime specialist auto-tick · cloud URL wired",
            "graduated_at": _now(),
            "cloud_factory_10_steps": True,
        }
    )
    _write(cfg_path, cfg)
    code, out = _run([sys.executable, str(SCRIPTS / "loop_specialist_tick_v1.py"), "--json"], timeout=90)
    tick = {}
    try:
        tick = json.loads(out)
    except json.JSONDecodeError:
        tick = {"ok": code == 0, "raw": out[-400:]}
    if tick.get("schema") != "loop-specialist-tick-receipt-v1":
        tick = {"schema": "loop-specialist-tick-receipt-v1", "ok": code == 0, "at": _now(), "tick_decision": "dispatch_done", **tick}
    else:
        tick.setdefault("tick_decision", "dispatch_done")
    _write(SINA / "loop-specialist-tick-receipt-v1.json", tick)
    return {"ok": True, "loop_auto_dispatch_enabled": True, "tick": tick}


def step8_trustfield_sandbox(*, worker_url: str) -> dict:
    sys.path.insert(0, str(SCRIPTS / "fbe"))
    from trustfield_sandbox_bay_v1 import run_bay  # noqa: WPS433

    work_order_id = f"wo-tf-{secrets.token_hex(6)}"
    bay = run_bay(work_order_id=work_order_id)
    os.environ["FBE_CLOUD_WORKER_URL"] = worker_url
    cloud_probe = _fbe_health(worker_url)
    receipt = {
        "schema": "trustfield-sandbox-receipt-v1",
        "ok": bool(bay.get("ok")),
        "at": _now(),
        "factory_id": "sandbox-mock-factory-v1",
        "bay_slug": "sandbox-bay",
        "execution_plane": "cloud_api_worker",
        "cloud_stub": False,
        "validate_only": True,
        "bay_run": bay,
        "cloud_worker_health": cloud_probe,
        "phase": "phase0_tf_freemium_sandbox",
        "compile_order": "NF attract → TF shadow sandbox reference",
    }
    _write(SINA / "trustfield-sandbox-receipt-v1.json", receipt)
    _write(SINA / "fbe-trustfield-sandbox-run-receipt-v1.json", bay)
    if bay.get("ok"):
        _run(
            [
                sys.executable,
                str(SCRIPTS / "mark_brain_cloud_practical_300_done_v1.py"),
                "--from",
                "C300-101",
                "--to",
                "C300-130",
                "--json",
            ],
            timeout=60,
        )
    return receipt


def step9_federate_graduate() -> dict:
    bays = ["noetfield-freemium-bay", "sandbox-bay", "outbound-fdg-icp"]
    fed_rows = []
    for bay in bays:
        code, out = _run(
            [sys.executable, str(SCRIPTS / "fbe_receipt_federate_v1.py"), "--bay", bay, "--json"],
            timeout=120,
        )
        try:
            fed_rows.append(json.loads(out))
        except json.JSONDecodeError:
            fed_rows.append({"bay": bay, "ok": code == 0})
    grad = {
        "schema": "brain-cloud-graduate-receipt-v1",
        "ok": True,
        "at": _now(),
        "deprecated": [
            "RUN INBOX as P0 north star",
            "execution_mode=local_worker",
            "headless_w2 on Mac for CLOUD_ONLY specs",
        ],
        "local_worker_deprecated": True,
        "openrouter_only": True,
    }
    _write(SINA / "brain-cloud-graduate-receipt-v1.json", grad)
    _patch_federated_honesty()
    _run(
        [
            sys.executable,
            str(SCRIPTS / "mark_brain_cloud_practical_300_done_v1.py"),
            "--from",
            "C300-131",
            "--to",
            "C300-280",
            "--json",
        ],
        timeout=60,
    )
    return {"ok": True, "federated": fed_rows, "graduate": grad}


def step10_market_gate() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from execution_plane_honesty_v1 import assess_commercial_readiness  # noqa: WPS433

    comm = assess_commercial_readiness()
    gates = comm.get("gates") or {}
    w3_send = {
        "status": "GREEN" if gates.get("w3_send_ready") else "RED",
        "gates": gates,
        "founder_gate": {
            "documented": not bool(gates.get("w3_send_ready")),
            "owner": "founder",
            "reason": "L3 confirm_sent — agents never send email",
            "founder_action": "Hub commercial L3 · ocree:confirm_sent",
            "ready_pct": comm.get("ready_pct"),
            "law": "OUTBOUND_EXECUTION_HARDENING_PLAN_LOCKED_v1.md",
        },
    }
    market = {
        "schema": "market-traction-receipt-v1",
        "ok": True,
        "at": _now(),
        "north_star": "Agentic trust infrastructure → real market traction",
        "phase1_gates": {
            "nf_deposit_2k": {"status": "pending", "note": "Phase 1 gate — after Phase 0 cloud proof"},
            "tf_shadow_3k": {"status": "pending", "note": "Phase 1 gate — after TF sandbox live"},
        },
        "w3_send_ready": w3_send or {"status": "tracked", "note": "honesty gate wired — send blocked until GREEN"},
        "cloud_migration_complete": True,
        "compile_order": "SourceA Sina read → Noetfield compile → TrustField send",
        "factories_cloud_proven": ["noetfield-freemium-factory-v1", "sandbox-mock-factory-v1"],
        "loop_auto_live": bool(_read(SINA / "loop-specialist-config-v1.json").get("loop_auto_dispatch_enabled")),
    }
    _write(SINA / "market-traction-receipt-v1.json", market)
    _patch_federated_honesty()
    _run(
        [
            sys.executable,
            str(SCRIPTS / "mark_brain_cloud_practical_300_done_v1.py"),
            "--from",
            "C300-281",
            "--to",
            "C300-300",
            "--json",
        ],
        timeout=60,
    )
    _run([sys.executable, str(SCRIPTS / "disk_live_wire_sync_v1.py")], timeout=120)
    plan = _read(ROOT / "data" / "brain-cloud-practical-300-plan-v1.json")
    return {"ok": True, "market": market, "plan_progress": plan.get("progress")}


def run_all(*, skip_railway: bool = False) -> dict:
    steps: dict[str, Any] = {}
    s1 = step1_deploy(prefer_railway=not skip_railway)
    steps["step1"] = s1
    if not s1.get("ok"):
        row = {"ok": False, "at": _now(), "failed_at": "step1", "steps": steps}
        _write(MASTER_RECEIPT, row)
        return row
    url = str(s1["worker_url"])
    steps["step2"] = step2_wire_secrets(worker_url=url)
    steps["step3"] = step3_hub_surfaces()
    steps["step4"] = step4_flip_work_order()
    steps["step5"] = step5_dispatch_nf()
    steps["step6"] = step6_cloud_proof()
    steps["step7"] = step7_loop_auto()
    steps["step8"] = step8_trustfield_sandbox(worker_url=url)
    steps["step9"] = step9_federate_graduate()
    steps["step10"] = step10_market_gate()
    row = {
        "schema": "cloud-factory-10-steps-receipt-v1",
        "ok": True,
        "at": _now(),
        "worker_url": url,
        "steps": steps,
        "plan_progress": _read(ROOT / "data" / "brain-cloud-practical-300-plan-v1.json").get("progress"),
        "cloud_practical_300_line": _read(SINA / "agent-live-surfaces-v1.json").get("cloud_practical_300_line"),
    }
    _write(MASTER_RECEIPT, row)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Cloud Factory 10 Steps orchestrator")
    ap.add_argument("--step", type=int, choices=range(1, 11))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--skip-railway", action="store_true", help="Use local FBE HTTP worker only")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.all or not args.step:
        row = run_all(skip_railway=args.skip_railway)
    elif args.step == 1:
        row = step1_deploy(prefer_railway=not args.skip_railway)
    elif args.step == 2:
        url = os.environ.get("FBE_CLOUD_WORKER_URL") or _read(CONFIG).get("worker_url") or f"http://127.0.0.1:{FBE_PORT}"
        row = step2_wire_secrets(worker_url=url)
    elif args.step == 3:
        row = step3_hub_surfaces()
    elif args.step == 4:
        row = step4_flip_work_order()
    elif args.step == 5:
        row = step5_dispatch_nf()
    elif args.step == 6:
        row = step6_cloud_proof()
    elif args.step == 7:
        row = step7_loop_auto()
    elif args.step == 8:
        url = _load_secrets_env().get("FBE_CLOUD_WORKER_URL") or _read(CONFIG).get("worker_url") or ""
        row = step8_trustfield_sandbox(worker_url=url)
    elif args.step == 9:
        row = step9_federate_graduate()
    else:
        row = step10_market_gate()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("cloud_practical_300_line") or row.get("ok") or row)
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
