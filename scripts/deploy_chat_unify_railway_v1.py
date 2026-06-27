#!/usr/bin/env python3
"""Deploy Chat Unify API to Railway — sourcea.app/unify upstream.

Receipt: ~/.sina/chat-unify-cloud-deploy-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
STAGING = SINA / "chat-unify-railway-staging-v1"
CONFIG = ROOT / "data" / "chat_unify_cloud_config_v1.json"
RECEIPT = SINA / "chat-unify-cloud-deploy-receipt-v1.json"

CU_SCRIPTS = (
    "chat-unify-server.py",
    "chat_unify_merge.py",
    "chat_unify_proof_pack_v1.py",
    "chat_unify_prompt_forge_v1.py",
    "chat_unify_vocabulary_intelligence_v1.py",
    "vocabulary_intelligence_scan_v1.py",
    "chat_unify_integrations_v1.py",
    "chat_unify_platform_catalog_v1.py",
    "chat_unify_kernel_v1.py",
    "chat_unify_truth_gate_v1.py",
    "chat_ord_loop_v1.py",
    "chat_ord_atoms_v1.py",
    "chat_ord_claim_rules_v1.py",
    "chat_founder_loop_v1.py",
    "chat_founder_language_v1.py",
    "chat_founder_reasoning_v1.py",
    "prompt_forge_pipeline_v1.py",
    "chat_unify_live_http_verify_v1.py",
    "ai_unify_api_v1.py",
    "clipboard_safe.py",
    "cursor_window_preflight_v1.py",
    "chat_unify_update_check_v1.py",
    "hub_form_submit_v1.py",
    "live_founder_decision_form_v1.py",
    "form_official_canvas_route_v1.py",
    "form_founder_supremacy_guard_v1.py",
    "governance_paths_v1.py",
    "api_station_v1.py",
    "founder_glance_cockpit_v1.py",
    "canvas_form_apply_picks_v1.py",
    "canvas_form_submit_v1.py",
    "hub_pro_skills_v1.py",
    "chat_unify_ide_v1.py",
    "chat_unify_terminal_motor_v1.py",
    "chat_unify_engine_v1.py",
    "chat_unify_smart_router_v1.py",
    "forge_terminal_v1.py",
    "workspace_kernel_v2.py",
    "model_dispatch.py",
    "worker_inject_lib.py",
)

CU_DATA = (
    "chat-unify-platform-catalog-v1.json",
    "chat-unify-integrations-v1.json",
    "chat-unify-cursor-plugin-v1.json",
    "founder-reply-glossary-v1.json",
    "agent-report-language-standard-v1.json",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 900) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd or ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        env=os.environ,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _stage() -> dict:
    if STAGING.is_dir():
        shutil.rmtree(STAGING)
    copied: list[str] = []
    for name in CU_SCRIPTS:
        src = ROOT / "scripts" / name
        if src.is_file():
            _copy_file(src, STAGING / "scripts" / name)
            copied.append(f"scripts/{name}")
    shutil.copytree(ROOT / "scripts" / "chat-unify-standalone", STAGING / "scripts" / "chat-unify-standalone")
    copied.append("scripts/chat-unify-standalone/")
    shutil.copytree(ROOT / "agent-control-panel" / "form", STAGING / "agent-control-panel" / "form")
    copied.append("agent-control-panel/form/")
    shutil.copytree(ROOT / "agent-control-panel" / "shared", STAGING / "agent-control-panel" / "shared")
    copied.append("agent-control-panel/shared/")
    for name in CU_DATA:
        src = ROOT / "data" / name
        if src.is_file():
            _copy_file(src, STAGING / "data" / name)
            copied.append(f"data/{name}")
    cloud = STAGING / "cloud"
    cloud.mkdir(parents=True)
    for name in ("Dockerfile.chat-unify", "railway.chat-unify.toml", "chat-unify-entrypoint.sh"):
        _copy_file(ROOT / "cloud" / name, cloud / name)
        copied.append(f"cloud/{name}")
    _copy_file(ROOT / "cloud" / "railway.chat-unify.toml", STAGING / "railway.toml")
    copied.append("railway.toml")
    size = sum(f.stat().st_size for f in STAGING.rglob("*") if f.is_file())
    return {"ok": True, "staging": str(STAGING), "files": len(copied), "bytes": size}


def _ensure_service(project_id: str, service: str, environment: str) -> dict:
    steps: list[dict] = []
    code, out = _run(["railway", "link", "-p", project_id, "-e", environment], timeout=120)
    steps.append({"step": "link_project", "code": code})
    if code != 0:
        return {"ok": False, "steps": steps, "error": "railway_link_project_failed", "tail": out[-400:]}
    code, out = _run(["railway", "service", "link", service], timeout=120)
    steps.append({"step": "link_service", "code": code})
    if code != 0:
        if "not found" in out.lower() or "available:" in out.lower():
            code, out = _run(["railway", "add", "-s", service], timeout=180)
            steps.append({"step": "add_service", "code": code})
            if code != 0:
                return {"ok": False, "steps": steps, "error": "railway_add_service_failed", "tail": out[-400:]}
            code, out = _run(["railway", "service", "link", service], timeout=120)
            steps.append({"step": "link_service_retry", "code": code})
        if code != 0:
            return {"ok": False, "steps": steps, "error": "railway_link_service_failed", "tail": out[-400:]}
    return {"ok": True, "steps": steps}


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


def _sync_railway_vars() -> dict:
    env = _load_env_file(Path.home() / ".sourcea-secrets" / "portfolio-spine.env")
    secrets = _load_env_file(Path.home() / ".sina" / "secrets.env")
    merged = {**secrets, **env}
    keys = (
        "OPENROUTER_API_KEY",
        "OPENROUTER_API_KEY_FORGE",
        "OPENROUTER_API_KEY_EVAL",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
    )
    results: dict = {"ok": True, "set": []}
    for key in keys:
        val = merged.get(key, "").strip()
        if not val:
            continue
        code, out = _run(["railway", "variables", "--set", f"{key}={val}"], timeout=60)
        results["set"].append({"key": key, "code": code})
        if code != 0:
            results["ok"] = False
            results["error"] = out[-200:]
    for key, val in (
        ("CHAT_UNIFY_CLOUD", "1"),
        ("CHAT_UNIFY_STATE_DIR", "/data/chat-unify"),
        ("SINA_SOURCE_A", "/app"),
    ):
        code, _ = _run(["railway", "variables", "--set", f"{key}={val}"], timeout=60)
        results["set"].append({"key": key, "code": code})
    return results


def _health(url: str) -> dict:
    try:
        with urllib.request.urlopen(f"{url.rstrip('/')}/health", timeout=45) as resp:
            raw = resp.read().decode("utf-8")
            row = json.loads(raw) if raw.strip() else {}
            return {"ok": bool(row.get("ok")), "url": url, "health": row}
    except Exception as exc:
        return {"ok": False, "url": url, "error": str(exc)[:200]}


def _parse_domain(dout: str, service: str) -> str:
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
    except json.JSONDecodeError:
        pass
    if not url and "sourcea-chat-unify" in service:
        url = "https://sourcea-chat-unify-production.up.railway.app"
    return url


def deploy(*, link: bool = True) -> dict:
    cfg = _read(CONFIG)
    rail = cfg.get("railway") or {}
    project_id = str(rail.get("project_id") or "109939ed-697c-4211-b0b4-a96fbba51db3")
    service = str(rail.get("service_name") or "sourcea-chat-unify")
    environment = str(rail.get("environment") or "production")
    row: dict = {
        "schema": "chat-unify-cloud-deploy-receipt-v1",
        "at": _now(),
        "service": service,
    }
    stage = _stage()
    row["staging"] = stage
    if not stage.get("ok"):
        row["ok"] = False
        row["error"] = "staging_failed"
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row
    if link:
        ensure = _ensure_service(project_id, service, environment)
        row["ensure_service"] = ensure
        if not ensure.get("ok"):
            row["ok"] = False
            row["error"] = ensure.get("error")
            RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
            return row
    row["env_sync"] = _sync_railway_vars()
    code, out = _run(
        ["railway", "up", "--detach", "-y", "-s", service, "--path-as-root", str(STAGING)],
        timeout=900,
    )
    row["up"] = {"code": code, "tail": out[-800:]}
    if code != 0:
        row["ok"] = False
        row["error"] = "railway_up_failed"
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row
    dcode, dout = _run(["railway", "domain", "--json", "-s", service], timeout=60)
    url = _parse_domain(dout, service)
    row["domain"] = {"code": dcode, "url": url}
    if not url:
        row["ok"] = False
        row["error"] = "no_public_domain"
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row
    probe = {"ok": False}
    for _ in range(24):
        probe = _health(url)
        if probe.get("ok"):
            break
        time.sleep(10)
    row["health"] = probe
    row["url"] = url
    row["upstream_url"] = url.rstrip("/")
    row["ok"] = bool(probe.get("ok"))
    if not row["ok"]:
        row["error"] = "health_failed"
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    cfg_path = ROOT / "data" / "chat_unify_cloud_config_v1.json"
    if cfg_path.is_file():
        live = _read(cfg_path)
        live["worker_url"] = row["upstream_url"]
        live["saved_at"] = _now()
        cfg_path.write_text(json.dumps(live, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-link", action="store_true")
    args = parser.parse_args()
    row = deploy(link=not args.no_link)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
