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
import os
import shutil
import subprocess
import sys
import urllib.request
from typing import Any
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
STAGING = SINA / "fbe-railway-staging-v1"
CONFIG = ROOT / "data" / "fbe_cloud_worker_config_v1.json"
RECEIPT = SINA / "fbe-cloud-deploy-receipt-v1.json"

COMPREHENSION_VERIFY_SKIPPED = {"ok": None, "skipped": True, "tail": ""}


def _comprehension_verify_enabled(explicit: bool) -> bool:
    return explicit or os.environ.get("FBE_VERIFY_COMPREHENSION", "").strip() == "1"


def _write_receipt(row: dict) -> None:
    row.setdefault("comprehension_verify", dict(COMPREHENSION_VERIFY_SKIPPED))
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _run_comprehension_verify(row: dict) -> None:
    vcode = subprocess.run(
        ["bash", str(ROOT / "scripts" / "validate-cloud-comprehension-railway-v1.sh")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env={**os.environ},
    )
    row["comprehension_verify"] = {
        "ok": vcode.returncode == 0,
        "skipped": False,
        "tail": (vcode.stdout or vcode.stderr or "")[-600:],
    }
    if vcode.returncode != 0:
        row["ok"] = False
        row["error"] = "comprehension_railway_verify_failed"

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
    "comprehension-golden-v1.json",
    "loop-specialist-cloud-contract-v1.json",
    "signal-factory-v1.json",
    "signal-factory-queue-v1.json",
    "signal-factory-synthetic-seed-v1.json",
    "signal-factory-cloud-contract-v1.json",
    "secondary-cloud-forge-run-next-100-v1.json",
    "cloud-forge-run-queue-active-v1.json",
    "cloud-forge-run--5000-patch-v1.json",
    "cloud-forge-run-extension-wave2-patch-v1.json",
    "portfolio-extension-wave2-manifest-v1.json",
    "cloud-forge-run-queue-path-v1.py",
    "hub-cloud-forge-run-proceed-v1.json",
    "cloud-forge-run-full-pack-pattern-v1.json",
    "truth-log-cloud-contract-v1.json",
    "cloud-auto-runtime-v1.json",
    "living-system-chain-registry-cloud-v1.json",
    "forge-scoring-ssot-v01.json",
    "forge-github-source-v02.json",
    "forge-mvp-router-rules-v0.1.json",
    "forge-v02-cloud-contract-v1.json",
    "forge-real-blueprints-v01.json",
    "gmail-sweep-ssot-v1.json",
    "kaizen-fix-handlers-v1.json",
    "trigger-registry-v1.json",
    "portfolio-vault-email-tags-v1.json",
    "copilot-scheduled-automations-v1.json",
    "client-proof-founder-review-pack-v1.json",
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
    "fbe_comprehension_eval_batch_v1.py",
    "agent_runtime_config_v1.py",
    "fbe_cloud_loop_specialist_tick_v1.py",
    "fbe_cloud_signal_factory_tick_v1.py",
    "signal_factory_core_v1.py",
    "signal_factory_tick_v1.py",
    "founder_reply_translator_v1.py",
    "agent_report_language_gate_v1.py",
    "cloud_worker_dispatch_v1.py",
    "forge_v01_engine_v1.py",
    "forge_v02_github_v1.py",
    "forge_v02_implement_v1.py",
    "implement_run_detail_slice_v1.py",
    "implement__evidence_slice_v1.py",
    "forge_v02_status_v1.py",
    "forge_v02_drain_v1.py",
    "forge_mvp_lib_v1.py",
    "forge_router_execute_v01.py",
    "forge_critic_loop_v01.py",
    "forge_task_graph_emit_v01.py",
    "fbe_sign_work_order_v1.py",
    "fbe_cloud_motor_seed_v1.py",
    "hub_cloud_forge_run_proceed_v1.py",
    "truth_log_v1.py",
    "truth_layer_receipt_writer_v1.py",
    "truth_layer_verifier_v1.py",
    "cloud_forge_run_queue_path_v1.py",
    "cloud_auto_runtime_single_cycle_gate_v1.py",
    "cloud_auto_runtime_v1.py",
    "cloud_forge_seed_v1.py",
    "cloud_forge_run_supabase_v1.py",
    "sourcea_plan_registry_client_v1.py",
    "autonomous_drain_receipt_cloud_v1.py",
    "living_system_chain_validate_v1.py",
    "portfolio__forge_dispatch_v1.py",
    "portfolio__pick_lib.py",
    "forge_cloud_env_load_v1.py",
    "task_plan_priority_v1.py",
    "gmail_inbox_sweep_v1.py",
    "signal_factory_triage_v1.py",
    "kaizen_nightly_tick_v1.py",
    "daily_ops_heartbeat_v1.py",
    "fbe_cloud_ops_motors_v1.py",
    "telegram_alert_v1.py",
    "improvement_queue_insert_v1.py",
    "kaizen_handler_pgrst_reload_v1.py",
    "kaizen_handler_workflow_lint_v1.py",
    "kaizen_handler_repo_policy_v1.py",
    "verify_client_proof_founder_review_v1.py",
    "check_sourcea_repo_policy.py",
    "validate-github-workflows-v1.sh",
    "portfolio_mail_hub_v1.py",
    "autorun_pending_v1.py",
    "sandbox_health_sweep_v1.py",
    "validate-noetfield-nerve-probe-v1.sh",
    "build_external_verify_l4_receipt_v1.py",
    "post_external_verify_l4_truth_v1.py",
    "ops_motors_status_v1.py",
    "gmail_triage_e2e_v1.py",
    "fbe_cloud_scheduled_loops_v1.py",
    "gha_repo_health_sweep_v1.py",
    "gha_security_sweep_v1.py",
    "validate_locked_definitions_anatomy_v1.py",
    "verify_autorun_determinism_v1.py",
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
    repo_policy = ROOT / "repo-policy.json"
    if repo_policy.is_file():
        _copy_file(repo_policy, STAGING / "repo-policy.json")
        copied.append("repo-policy.json")

    for name in _STAGING_DATA_FILES:
        src = ROOT / "data" / name
        if src.is_file():
            _copy_file(src, STAGING / "data" / name)
            copied.append(f"data/{name}")
    for path in sorted((ROOT / "data").glob("secondary-cloud-forge-run-batch-*.json")):
        rel = f"data/{path.name}"
        if rel not in copied:
            _copy_file(path, STAGING / "data" / path.name)
            copied.append(rel)
    for sub in ("factory-specs", "policy-packs", "schemas"):
        src = ROOT / "data" / sub
        if src.is_dir():
            shutil.copytree(src, STAGING / "data" / sub)
            copied.append(f"data/{sub}/")

    fbe_src = ROOT / "scripts" / "fbe"
    if fbe_src.is_dir():
        shutil.copytree(fbe_src, STAGING / "scripts" / "fbe")
        copied.append("scripts/fbe/")
    sdk_src = ROOT / "packages" / "sourcea-sdk"
    if sdk_src.is_dir():
        shutil.copytree(sdk_src, STAGING / "packages" / "sourcea-sdk")
        copied.append("packages/sourcea-sdk/")
    trust = ROOT / "scripts" / "fbe" / "lib" / "trust_ledger_v1.py"
    if trust.is_file():
        _copy_file(trust, STAGING / "scripts" / "fbe" / "lib" / "trust_ledger_v1.py")

    for name in _STAGING_SCRIPT_FILES:
        src = ROOT / "scripts" / name
        if src.is_file():
            _copy_file(src, STAGING / "scripts" / name)
            copied.append(f"scripts/{name}")

    wf_src = ROOT / ".github" / "workflows"
    if wf_src.is_dir():
        shutil.copytree(wf_src, STAGING / ".github" / "workflows")
        copied.append(".github/workflows/")

    plans_src = ROOT / "plans"
    if plans_src.is_dir():
        shutil.copytree(plans_src, STAGING / "plans")
        copied.append("plans/")

    reg_src = ROOT / "brain-os" / "plan-registry" / "sourcea--1000"
    reg_dst = STAGING / "data" / "sourcea--1000-registry"
    if reg_src.is_dir():
        shutil.copytree(reg_src, reg_dst)
        copied.append("data/sourcea--1000-registry/")

    cloud_dir = STAGING / "cloud"
    cloud_dir.mkdir(parents=True)
    for name in ("Dockerfile.fbe-runner", "railway.toml"):
        src = ROOT / "cloud" / name
        if src.is_file():
            _copy_file(src, cloud_dir / name)
            copied.append(f"cloud/{name}")

    seed_src = ROOT / "cloud" / "seed"
    if seed_src.is_dir():
        shutil.copytree(seed_src, cloud_dir / "seed")
        copied.append("cloud/seed/")

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


def _probe_cloud_proceed_route(url: str) -> dict:
    """Dry-run POST — route live when hub-cloud-forge-run-proceed schema returns (not unknown_route/import)."""
    try:
        req = urllib.request.Request(
            f"{url.rstrip('/')}/api/cloud-forge-run/proceed/v1",
            data=json.dumps(
                {
                    "dry_run": True,
                    "llm_provider": "openrouter",
                    "plan_id": "CLOUD-SEC-006",
                    "maps_registry": "sa-mkt-0006",
                    "full_motor": True,
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            row = json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            row = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            row = {"error": str(exc)[:120]}
    except Exception as exc:
        return {"ok": False, "url": url, "error": str(exc)[:200]}

    err = str(row.get("error") or "")
    schema = str(row.get("schema") or "")
    if err == "unknown_route":
        return {"ok": False, "url": url, "route_error": err, "sample": row}
    if "No module named" in str(row.get("message") or ""):
        return {"ok": False, "url": url, "route_error": "import_missing", "sample": row}
    ok = schema == "hub-cloud-forge-run-proceed-v1" or (bool(row) and err not in ("unknown_route", "execution_failed"))
    return {"ok": ok, "url": url, "route_error": err or None, "sample": row}


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


def _validate_dockerfile_batch_sync() -> dict[str, Any]:
    """Fail deploy early if Dockerfile COPY omits active/next batch queue files."""
    dockerfile = ROOT / "cloud" / "Dockerfile.fbe-runner"
    ptr = _read(ROOT / "data" / "cloud-forge-run-queue-active-v1.json")
    required: list[str] = ["cloud-forge-run-queue-active-v1.json"]
    qrel = str(ptr.get("queue_path") or "").strip()
    if qrel.startswith("data/"):
        required.append(qrel.replace("data/", "", 1))
    nxt = ptr.get("next_batch") or {}
    nrel = str(nxt.get("queue_path") or "").strip()
    if nrel.startswith("data/"):
        required.append(nrel.replace("data/", "", 1))
    text = dockerfile.read_text(encoding="utf-8") if dockerfile.is_file() else ""
    if "secondary-cloud-forge-run-batch-*" in text or "secondary-cloud-forge-run-batch-*.json" in text:
        qrel = str(ptr.get("queue_path") or "").strip()
        if qrel.startswith("data/"):
            fname = qrel.replace("data/", "", 1)
            missing = [] if fname in text or "secondary-cloud-forge-run-batch-*" in text else [fname]
        else:
            missing = []
        return {"ok": not missing, "missing_in_dockerfile": missing, "required": required, "mode": "glob"}
    missing = [name for name in required if name not in text]
    return {"ok": not missing, "missing_in_dockerfile": missing, "required": required}


def _load_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def _sync_portfolio_spine_supabase_to_railway() -> dict[str, Any]:
    """Keep FBE on portfolio-spine host — never the paused mmdhnktybjpwlwdczgbq ref."""
    env = _load_env_file(Path.home() / ".sourcea-secrets/portfolio-spine.env")
    url = env.get("SUPABASE_URL", "").strip()
    key = env.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key or "mmdhnktybjpwlwdczgbq" in url:
        return {"ok": False, "skipped": True, "reason": "portfolio_spine_secrets_missing_or_stale"}
    results: dict[str, Any] = {"ok": True, "host": url.replace("https://", "").split("/")[0]}
    for name, val in (("SUPABASE_URL", url), ("SUPABASE_SERVICE_ROLE_KEY", key)):
        code, out = _run(["railway", "variables", "--set", f"{name}={val}"], cwd=ROOT, timeout=60)
        results[name] = {"code": code}
        if code != 0:
            results["ok"] = False
            results["error"] = out[-200:]
    return results


def deploy(*, link: bool = True, verify_comprehension: bool = False) -> dict:
    os.environ["SOURCEA_RAILWAY_DEPLOY"] = "1"
    guard_proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "deploy_dirty_tree_guard_v1.py"), "--scope", "fbe", "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    dirty_guard: dict[str, Any] = {"ok": guard_proc.returncode == 0}
    try:
        dirty_guard = json.loads(guard_proc.stdout or "{}")
    except json.JSONDecodeError:
        dirty_guard["parse_error"] = True
    if not dirty_guard.get("ok"):
        row = {
            "schema": "fbe-cloud-deploy-receipt-v1",
            "at": _now(),
            "ok": False,
            "error": "dirty_tree_guard_blocked",
            "dirty_tree_guard": dirty_guard,
            "founder_action": "Commit or stash scoped FBE deploy files before deploy",
        }
        _write_receipt(row)
        return row

    cfg = _read(CONFIG)
    rail = cfg.get("railway") or {}
    project_id = str(rail.get("project_id") or "")
    service = str(rail.get("service_name") or "sourcea-fbe-runner")
    environment = str(rail.get("environment") or "production")
    row: dict = {
        "schema": "fbe-cloud-deploy-receipt-v1",
        "at": _now(),
        "deployment": "railway",
        "comprehension_verify": dict(COMPREHENSION_VERIFY_SKIPPED),
    }
    row["supabase_env_sync"] = _sync_portfolio_spine_supabase_to_railway()
    row["dirty_tree_guard"] = dirty_guard

    batch_sync = _validate_dockerfile_batch_sync()
    row["dockerfile_batch_sync"] = batch_sync
    if not batch_sync.get("ok"):
        row["ok"] = False
        row["error"] = "dockerfile_missing_batch_queue_copy"
        row["founder_action"] = f"Add COPY lines to cloud/Dockerfile.fbe-runner: {batch_sync.get('missing_in_dockerfile')}"
        _write_receipt(row)
        return row

    if link and project_id:
        ensure = _ensure_railway_service(project_id=project_id, service=service, environment=environment)
        row["ensure_service"] = ensure
        if not ensure.get("ok"):
            row["ok"] = False
            row["error"] = ensure.get("error") or "railway_service_setup_failed"
            row["founder_action"] = f"railway login · then re-run deploy_fbe_railway_v1.py · create service {service}"
            _write_receipt(row)
            return row

    stage = _stage_deploy_context()
    row["staging"] = stage
    if not stage.get("ok"):
        row["ok"] = False
        row["error"] = "staging_failed"
        _write_receipt(row)
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
        _write_receipt(row)
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
        _write_receipt(row)
        return row

    import time

    probe: dict = {"ok": False}
    route_probe: dict = {"ok": False}
    for attempt in range(1, 4):
        probe = _health(url)
        if probe.get("ok"):
            route_probe = _probe_cloud_proceed_route(url)
            if route_probe.get("ok"):
                break
        time.sleep(5)
    row.update(
        {
            "ok": bool(probe.get("ok")) and bool(route_probe.get("ok")),
            "worker_url": url,
            **probe,
            "health_attempts": attempt,
            "cloud_proceed_route": route_probe,
        }
    )
    if probe.get("ok") and not route_probe.get("ok"):
        row["error"] = "cloud_proceed_route_not_live"
    if probe.get("ok"):
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "cloud_factory_10_steps_v1.py"), "--step", "2", "--json"],
            cwd=str(ROOT),
            check=False,
        )
        if verify_comprehension:
            _run_comprehension_verify(row)
    _write_receipt(row)
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-link", action="store_true")
    ap.add_argument("--verify-comprehension", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = deploy(
        link=not args.no_link,
        verify_comprehension=_comprehension_verify_enabled(bool(args.verify_comprehension)),
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("worker_url") or row.get("error"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
