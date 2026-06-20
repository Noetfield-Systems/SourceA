"""FBE cloud adapter — W2 local_docker + railway_fbe HTTP + mono_mirror."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SINA = Path.home() / ".sina"
RECEIPT_PATH = SINA / "fbe-cloud-adapter-receipt-v1.json"
ENTRYPOINT = ROOT / "cloud" / "fbe-worker-entrypoint.sh"
DOCKERFILE = ROOT / "cloud" / "Dockerfile.fbe-runner"
IMAGE = "fbe-runner:w2"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def skeleton_ready() -> dict[str, bool]:
    return {
        "dockerfile": DOCKERFILE.is_file(),
        "entrypoint": ENTRYPOINT.is_file(),
        "entrypoint_executable": ENTRYPOINT.is_file() and bool(ENTRYPOINT.stat().st_mode & 0o111),
        "bay_jobs": (ROOT / "data" / "fbe_bay_jobs_v1.json").is_file(),
    }


def _cloud_worker_url() -> str:
    cfg_path = ROOT / "data" / "fbe_cloud_worker_config_v1.json"
    cfg: dict[str, Any] = {}
    if cfg_path.is_file():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cfg = {}
    for key in (cfg.get("worker_url_env") or "FBE_CLOUD_WORKER_URL", "RAILWAY_WORKER_URL"):
        val = os.environ.get(key, "").strip()
        if val:
            return val.rstrip("/")
    return str(cfg.get("worker_url") or "").strip().rstrip("/")


def _route_for_run_mode(run_mode: str) -> str:
    return {
        "refinery": "/api/fbe/run-bay/v1",
        "assembly": "/api/fbe/run-bay/v1",
        "full_job": "/api/fbe/run-job/v1",
        "exchange": "/api/fbe/run-exchange/v1",
        "forge": "/api/fbe/run-forge/v1",
        "fleet": "/api/fbe/run-fleet/v1",
    }.get(run_mode, "/api/fbe/run-bay/v1")


def _run_railway_http(
    *,
    bay_slug: str,
    run_mode: str,
    template_id: str,
    tenant: str,
    work_order_id: str,
    forge_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    base = _cloud_worker_url()
    if not base:
        return {"ok": False, "error": "missing_cloud_worker_url", "mode": "railway_fbe"}
    path = _route_for_run_mode(run_mode)
    body: dict[str, Any] = {
        "bay_slug": bay_slug,
        "template_id": template_id,
        "tenant": tenant,
        "work_order_id": work_order_id,
        "execution_mode": "CLOUD_ONLY",
    }
    if forge_context:
        body["forge_context"] = forge_context
        for key in ("stack", "competitor", "workstream", "prompt_abs", "task_graph_path", "run_id"):
            if forge_context.get(key) is not None:
                body[key] = forge_context[key]
    payload = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    secret = os.environ.get("FBE_INTERNAL_SECRET", "").strip()
    if secret:
        headers["Authorization"] = f"Bearer {secret}"
    req = urllib.request.Request(f"{base}{path}", data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            raw = resp.read().decode("utf-8")
            row = json.loads(raw) if raw.strip() else {}
            row["mode"] = "railway_fbe"
            row["run_mode"] = run_mode
            return row
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8"))
        except Exception:
            detail = {"message": str(exc)}
        return {"ok": False, "mode": "railway_fbe", "error": "http_error", "status": exc.code, "detail": detail}
    except Exception as exc:
        return {"ok": False, "mode": "railway_fbe", "error": "unreachable", "message": str(exc)}


def _freeze_blocks_local() -> bool:
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from mac_focus_freeze_v1 import is_focus_freeze  # noqa: WPS433

        return bool(is_focus_freeze())
    except Exception:
        return (Path.home() / ".sina" / "auto-run-disabled-v1.flag").is_file()


def _run_local_docker(*, bay_slug: str, run_mode: str = "refinery") -> dict[str, Any]:
    """Try docker; fall back to local python runner."""
    mode_flag = {
        "refinery": "--run-bay",
        "assembly": "--run-assembly",
        "full_job": "--run-full-job",
        "exchange": "--run-exchange",
        "forge": "--run-forge",
        "fleet": "--run-fleet",
    }.get(run_mode, "--run-bay")
    fallback_scripts = {
        "refinery": ROOT / "scripts" / "fbe_refinery_runner_v1.py",
        "assembly": ROOT / "scripts" / "fbe_assembly_runner_v1.py",
        "full_job": ROOT / "scripts" / "fbe_run_job_v1.py",
        "exchange": ROOT / "scripts" / "fbe_exchange_runner_v1.py",
        "forge": ROOT / "scripts" / "fbe_forge_runner_v1.py",
        "fleet": ROOT / "scripts" / "fbe_run_fleet_v1.py",
    }
    fallback = fallback_scripts.get(run_mode, fallback_scripts["refinery"])
    try:
        subprocess.check_output(
            ["docker", "info"],
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
        subprocess.check_output(
            ["docker", "build", "-f", str(DOCKERFILE), "-t", IMAGE, str(ROOT)],
            stderr=subprocess.STDOUT,
            text=True,
            timeout=300,
        )
        creed = Path.home() / "Desktop/YA5/PLUS ONE/CREED"
        church = Path.home() / "Desktop/YA5/PLUS ONE/CHURCH"
        cmd = ["docker", "run", "--rm"]
        if creed.is_dir():
            cmd.extend(["-v", f"{creed}:/creed:ro"])
        if church.is_dir():
            cmd.extend(["-v", f"{church}:/church:ro"])
        cmd.extend([IMAGE, mode_flag, bay_slug])
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=900)
        return {"ok": True, "mode": "local_docker", "run_mode": run_mode, "tail": out[-400:]}
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as exc:
        fallback_cmd = [sys.executable, str(fallback), "--json"]
        if run_mode not in ("fleet",):
            fallback_cmd = [sys.executable, str(fallback), "--bay", bay_slug, "--json"]
        out = subprocess.check_output(
            fallback_cmd,
            cwd=str(ROOT),
            stderr=subprocess.STDOUT,
            text=True,
            timeout=900,
        )
        return {"ok": True, "mode": "local_python_fallback", "run_mode": run_mode, "note": str(exc), "tail": out[-400:]}


def submit_job(
    *,
    template_id: str,
    work_order_id: str,
    tenant: str = "wil_ai_design_partner",
    bay_slug: str = "sample-bay",
    dry_run: bool = False,
    mode: str = "railway_fbe",
    run_mode: str = "refinery",
    forge_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    skel = skeleton_ready()
    ok = all(skel.values())
    run_result: dict[str, Any] = {}
    wave = "W4" if run_mode == "exchange" else ("W3" if run_mode in ("assembly", "full_job") else "W2")
    plane = "headless_w4" if wave == "W4" else ("headless_w3" if wave == "W3" else "headless_w2")

    if ok and not dry_run:
        if mode == "railway_fbe":
            run_result = _run_railway_http(
                bay_slug=bay_slug,
                run_mode=run_mode,
                template_id=template_id,
                tenant=tenant,
                work_order_id=work_order_id,
                forge_context=forge_context,
            )
            ok = bool(run_result.get("ok"))
        elif mode == "local_docker":
            if _freeze_blocks_local():
                run_result = {
                    "ok": False,
                    "error": "freeze_blocks_local_docker",
                    "message": "CLOUD_ONLY — configure FBE_CLOUD_WORKER_URL or use railway_fbe mode",
                }
                ok = False
            else:
                run_result = _run_local_docker(bay_slug=bay_slug, run_mode=run_mode)
                ok = bool(run_result.get("ok"))
        if mode == "mono_mirror":
            from fbe_mono_bridge_v1 import mirror_bay  # noqa: WPS433
            run_result = mirror_bay(bay_slug=bay_slug, template_id=template_id)
            ok = bool(run_result.get("ok", True))

    row: dict[str, Any] = {
        "schema": "fbe-cloud-adapter-receipt-v1",
        "ok": ok,
        "at": _now(),
        "mode": f"{wave.lower()}_headless" if not dry_run else "w1_skeleton",
        "submit_mode": mode,
        "run_mode": run_mode,
        "template_id": template_id,
        "work_order_id": work_order_id,
        "tenant": tenant,
        "bay_slug": bay_slug,
        "execution_plane": plane if not dry_run else "cloud_skeleton",
        "dry_run": dry_run,
        "skeleton": skel,
        "run_result": run_result,
        "forge_context": forge_context,
        "remote_status": "local_primary" if not dry_run else "deferred_w2",
        "wave": wave,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def status_payload() -> dict[str, Any]:
    skel = skeleton_ready()
    receipt = {}
    if RECEIPT_PATH.is_file():
        try:
            receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            receipt = {}
    return {
        "ok": all(skel.values()),
        "schema": "fbe-cloud-adapter-status-v1",
        "at": _now(),
        "wave": receipt.get("wave") or "W2",
        "skeleton": skel,
        "last_submit": receipt,
        "execution_plane": receipt.get("execution_plane") or "headless_w2",
    }
