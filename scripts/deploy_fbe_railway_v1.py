#!/usr/bin/env python3
"""Deploy FBE runner to Railway — founder/executor only (requires railway CLI login).

Reverse-engineered path:
  mergepack-api project (109939ed) → create sourcea-fbe-runner if missing →
  docker deploy via cloud/railway.toml → public HTTPS → FBE_CLOUD_WORKER_URL

Receipt: ~/.sina/fbe-cloud-deploy-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
STAGING = SINA / "fbe-railway-staging-v1"
CONFIG = ROOT / "data" / "fbe_cloud_worker_config_v1.json"
RECEIPT = SINA / "fbe-cloud-deploy-receipt-v1.json"

# Minimal COPY set from cloud/Dockerfile.fbe-runner — avoids 413 on full-repo railway up.
_STAGING_DATA_FILES = (
    "fbe_node_graph_v1.json",
    "fbe_factory_builder_bundle_v1.json",
    "fbe_execution_contract_v1.json",
    "fbe_cloud_worker_config_v1.json",
    "fbe_catalog_v1.json",
    "fbe_factory_spec_schema_v1.json",
    "fbe_bay_jobs_v1.json",
    "fbe_pipelines_v1.json",
    "fbe_cloud_workspace_map_v1.json",
    "fbe_exchange_job_v1.json",
    "fbe_forge_job_v1.json",
    "fbe_fleet_job_v1.json",
    "fbe_full_job_v1.json",
    "founder-reply-glossary-v1.json",
    "agent-report-language-standard-v1.json",
    "cloud-comprehension-bay-v1.json",
    "loop-specialist-cloud-contract-v1.json",
    "secondary-cloud-drain-next-100-v1.json",
)
_STAGING_SCRIPT_FILES = (
    "fbe_cloud_worker_http_v1.py",
    "fbe_pipeline_runner_v1.py",
    "fbe_refinery_runner_v1.py",
    "fbe_verify_refinery_v1.py",
    "fbe_assembly_runner_v1.py",
    "fbe_verify_assembly_v1.py",
    "fbe_exchange_runner_v1.py",
    "fbe_verify_exchange_v1.py",
    "fbe_forge_runner_v1.py",
    "fbe_verify_forge_v1.py",
    "fbe_run_job_v1.py",
    "fbe_run_bay_v1.py",
    "fbe_run_fleet_v1.py",
    "fbe_spawn_factory_v1.py",
    "fbe_motor_delegate_v1.py",
    "fbe_receipt_federate_v1.py",
    "fbe_verify_motor_v1.py",
    "fbe_verify_market_ready_v1.py",
    "fbe_run_receipt_pack_v1.py",
    "fbe_mono_bridge_v1.py",
    "fbe_cloud_sync_v1.py",
    "fbe_billing_meter_v1.py",
    "fbe_design_partner_receipt_v1.py",
    "fbe_hub_projection_v1.py",
    "fbe_factory_spec_v1.py",
    "mac_focus_freeze_v1.py",
    "fbe_comprehension_bay_v1.py",
    "fbe_cloud_loop_specialist_tick_v1.py",
    "founder_reply_translator_v1.py",
    "agent_report_language_gate_v1.py",
    "cloud_worker_dispatch_v1.py",
    "fbe_sign_work_order_v1.py",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 900) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd or ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return proc.returncode, ((proc.stdout or "") + (proc.stderr or "")).strip()


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _stage_deploy_context() -> dict:
    """Build ~/.sina/fbe-railway-staging-v1 — small upload, same paths Dockerfile expects."""
    if STAGING.is_dir():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)

    copied: list[str] = []
    for name in _STAGING_DATA_FILES:
        src = ROOT / "data" / name
        if src.is_file():
            _copy_file(src, STAGING / "data" / name)
            copied.append(f"data/{name}")
    for sub in ("factory-specs", "policy-packs", "schemas"):
        src = ROOT / "data" / sub
        if src.is_dir():
            shutil.copytree(src, STAGING / "data" / sub)
            copied.append(f"data/{sub}/")

    fbe_src = ROOT / "scripts" / "fbe"
    if fbe_src.is_dir():
        shutil.copytree(fbe_src, STAGING / "scripts" / "fbe")
        copied.append("scripts/fbe/")
    trust = ROOT / "scripts" / "fbe" / "lib" / "trust_ledger_v1.py"
    if trust.is_file():
        _copy_file(trust, STAGING / "scripts" / "fbe" / "lib" / "trust_ledger_v1.py")

    for name in _STAGING_SCRIPT_FILES:
        src = ROOT / "scripts" / name
        if src.is_file():
            _copy_file(src, STAGING / "scripts" / name)
            copied.append(f"scripts/{name}")

    cloud_dir = STAGING / "cloud"
    cloud_dir.mkdir(parents=True)
    for name in ("Dockerfile.fbe-runner", "railway.toml"):
        src = ROOT / "cloud" / name
        if src.is_file():
            _copy_file(src, cloud_dir / name)
            copied.append(f"cloud/{name}")

    canonical_entry = ROOT / "scripts" / "fbe" / "fbe_cloud_entrypoint_v1.sh"
    if canonical_entry.is_file():
        _copy_file(canonical_entry, cloud_dir / "fbe-worker-entrypoint.sh")
        copied.append("cloud/fbe-worker-entrypoint.sh:from_scripts_fbe")

    rail_toml = ROOT / "cloud" / "railway.toml"
    if rail_toml.is_file():
        _copy_file(rail_toml, STAGING / "railway.toml")
        copied.append("railway.toml")

    dockerignore = ROOT / "cloud" / ".dockerignore"
    if dockerignore.is_file():
        _copy_file(dockerignore, STAGING / ".dockerignore")
        _copy_file(dockerignore, STAGING / ".railwayignore")

    size = sum(f.stat().st_size for f in STAGING.rglob("*") if f.is_file())
    return {"ok": True, "staging": str(STAGING), "files": len(copied), "bytes": size}


def _parse_railway_domain(dout: str, *, service: str) -> str:
    url = ""
    try:
        parsed = json.loads(dout)
        if isinstance(parsed, list) and parsed:
            dom = str(parsed[0])
            url = dom if dom.startswith("http") else f"https://{dom}"
        elif isinstance(parsed, dict):
            domains = parsed.get("domains") or []
            if domains:
                dom = str(domains[0])
                url = dom if dom.startswith("http") else f"https://{dom}"
            else:
                dom = str(parsed.get("domain") or parsed.get("url") or "")
                if dom:
                    url = dom if dom.startswith("http") else f"https://{dom}"
    except json.JSONDecodeError:
        pass
    if not url and "sourcea-fbe-runner" in service:
        url = "https://sourcea-fbe-runner-production.up.railway.app"
    return url


def _health(url: str) -> dict:
    try:
        with urllib.request.urlopen(f"{url.rstrip('/')}/health", timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            health = json.loads(raw) if raw.strip() else {}
            return {"ok": bool(health.get("ok")), "url": url, "health": health}
    except Exception as exc:
        return {"ok": False, "url": url, "error": str(exc)[:200]}


def _wait_health(url: str, *, attempts: int = 36, delay_sec: float = 10.0) -> dict:
    import time

    last: dict = {"ok": False, "error": "health_timeout"}
    for _ in range(attempts):
        last = _health(url)
        if last.get("ok"):
            return last
        time.sleep(delay_sec)
    return last


def _ensure_railway_service(*, project_id: str, service: str, environment: str = "production") -> dict:
    """Link project, create service if missing, link service."""
    steps: list[dict] = []
    code, out = _run(["railway", "link", "-p", project_id, "-e", environment], timeout=120)
    steps.append({"step": "link_project", "code": code, "tail": out[-500:]})
    if code != 0:
        return {"ok": False, "steps": steps, "error": "railway_link_project_failed"}

    code, out = _run(["railway", "service", "link", service], timeout=120)
    steps.append({"step": "link_service", "code": code, "tail": out[-500:]})
    if code != 0:
        lower = out.lower()
        if "not found" in lower or "available:" in lower:
            code, out = _run(["railway", "add", "-s", service], timeout=180)
            steps.append({"step": "add_service", "code": code, "tail": out[-500:]})
            if code != 0:
                return {"ok": False, "steps": steps, "error": "railway_add_service_failed"}
            code, out = _run(["railway", "service", "link", service], timeout=120)
            steps.append({"step": "link_service_retry", "code": code, "tail": out[-500:]})
        if code != 0:
            return {"ok": False, "steps": steps, "error": "railway_link_service_failed"}
    return {"ok": True, "steps": steps}


def deploy(*, link: bool = True) -> dict:
    cfg = _read(CONFIG)
    rail = cfg.get("railway") or {}
    project_id = str(rail.get("project_id") or "")
    service = str(rail.get("service_name") or "sourcea-fbe-runner")
    environment = str(rail.get("environment") or "production")
    row: dict = {"schema": "fbe-cloud-deploy-receipt-v1", "at": _now(), "deployment": "railway"}

    if link and project_id:
        ensure = _ensure_railway_service(project_id=project_id, service=service, environment=environment)
        row["ensure_service"] = ensure
        if not ensure.get("ok"):
            row["ok"] = False
            row["error"] = ensure.get("error") or "railway_service_setup_failed"
            row["founder_action"] = f"railway login · then re-run deploy_fbe_railway_v1.py · create service {service}"
            RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
            return row

    stage = _stage_deploy_context()
    row["staging"] = stage
    if not stage.get("ok"):
        row["ok"] = False
        row["error"] = "staging_failed"
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    code, out = _run(
        ["railway", "up", "--detach", "-y", "-s", service, "--path-as-root", str(STAGING)],
        cwd=ROOT,
        timeout=900,
    )
    row["up"] = {"code": code, "tail": out[-800:], "from_staging": str(STAGING), "staging_bytes": stage.get("bytes")}
    if code != 0:
        row["ok"] = False
        row["error"] = "railway_up_failed"
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    dcode, dout = _run(["railway", "domain", "--json", "-s", service], cwd=ROOT, timeout=60)
    row["domain"] = {"code": dcode, "raw": dout[-400:]}
    url = ""
    try:
        parsed = json.loads(dout)
        if isinstance(parsed, list) and parsed:
            url = f"https://{parsed[0]}" if not str(parsed[0]).startswith("http") else str(parsed[0])
        elif isinstance(parsed, dict):
            dom = str(parsed.get("domain") or parsed.get("url") or "")
            if dom:
                url = dom if dom.startswith("http") else f"https://{dom}"
            domains = parsed.get("domains")
            if not url and isinstance(domains, list) and domains:
                first = str(domains[0])
                url = first if first.startswith("http") else f"https://{first}"
    except json.JSONDecodeError:
        pass
    if not url and "sourcea-fbe-runner" in service:
        url = "https://sourcea-fbe-runner-production.up.railway.app"
    if not url:
        row["ok"] = False
        row["error"] = "no_public_domain"
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    import time

    probe: dict = {"ok": False}
    for attempt in range(1, 41):
        probe = _health(url)
        if probe.get("ok"):
            break
        time.sleep(15)
    row.update({"ok": probe.get("ok"), "worker_url": url, **probe, "health_attempts": attempt})
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if probe.get("ok"):
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "cloud_factory_10_steps_v1.py"), "--step", "2", "--json"],
            cwd=str(ROOT),
            check=False,
        )
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-link", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = deploy(link=not args.no_link)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("worker_url") or row.get("error"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
