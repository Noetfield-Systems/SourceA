#!/usr/bin/env python3
"""n8n automation — status, start, starter test flow for standalone glue layer."""
from __future__ import annotations

import json
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

def _source_a_root() -> Path:
    import os

    env = os.environ.get("SINA_SOURCE_A", "").strip()
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    return Path(__file__).resolve().parents[1]


SOURCE_A = _source_a_root()
MONO_ROOT = Path.home() / "Desktop/SinaaiMonoRepo"
N8N_PORT = int(__import__("os").environ.get("N8N_PORT", "5678"))
RUNTIME_PORT = 8000
N8N_URL = f"http://127.0.0.1:{N8N_PORT}/"
RUNTIME_HEALTH = f"http://127.0.0.1:{RUNTIME_PORT}/health"
RUNTIME_LIAISON = f"http://127.0.0.1:{RUNTIME_PORT}/api/v1/liaison/status"
WORKFLOW_DIR = MONO_ROOT / "n8n/workflows"
WORKFLOW_PATH = WORKFLOW_DIR / "sinaai-telegram-agents.json"
HEALTH_PING_WORKFLOW = WORKFLOW_DIR / "sinaai-stack-health-ping.json"
FIXTURE_DIR = SOURCE_A / "scripts/fixtures/n8n"
MANIFEST_PATH = FIXTURE_DIR / "workflow_manifest.json"
START_SCRIPT = SOURCE_A / "scripts/founder-start-n8n.sh"
LAW_PATH = SOURCE_A / "SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md"
SETUP_DOC = MONO_ROOT / "SinaaiDataBase/governance/N8N_SETUP.md"
HUB_HEALTH = "http://127.0.0.1:13020/health"
MAC_HEALTH_HEALTH = "http://127.0.0.1:13024/health"
MAC_HEALTH_LIVE = "http://127.0.0.1:13024/api/mac-health/live"
N8N_INTEGRATION_HEALTH = "http://127.0.0.1:13026/health"
N8N_HEALTHZ = f"http://127.0.0.1:{N8N_PORT}/healthz"


def _probe(url: str, *, timeout: float = 3.0) -> dict:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(512).decode("utf-8", errors="replace")
            return {
                "ok": resp.status in (200, 201, 204),
                "status": resp.status,
                "url": url,
                "snippet": body[:200],
            }
    except urllib.error.HTTPError as e:
        return {"ok": e.code in (200, 201, 204), "status": e.code, "url": url, "error": str(e)}
    except Exception as e:
        return {"ok": False, "url": url, "error": str(e)}


def _tcp_open(port: int, host: str = "127.0.0.1") -> bool:
    import socket

    try:
        with socket.create_connection((host, port), timeout=1.5):
            return True
    except OSError:
        return False


def n8n_status_payload() -> dict:
    n8n_up = _tcp_open(N8N_PORT)
    rt_up = _tcp_open(RUNTIME_PORT)
    hub_up = _tcp_open(13020)
    return {
        "ok": True,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "n8n_url": N8N_URL,
        "n8n_port": N8N_PORT,
        "n8n_running": n8n_up,
        "runtime_port": RUNTIME_PORT,
        "runtime_running": rt_up,
        "hub_running": hub_up,
        "workflow_path": str(WORKFLOW_PATH),
        "workflow_exists": WORKFLOW_PATH.is_file(),
        "health_ping_workflow": str(HEALTH_PING_WORKFLOW),
        "health_ping_exists": HEALTH_PING_WORKFLOW.is_file(),
        "fixtures_dir": str(FIXTURE_DIR),
        "start_script": str(START_SCRIPT),
        "law_path": str(LAW_PATH.relative_to(SOURCE_A)),
        "setup_doc": str(SETUP_DOC) if SETUP_DOC.is_file() else None,
        "warning": (
            "Built-in Telegram on :8000 is default. Disable TELEGRAM_V4 before activating "
            "n8n Telegram workflow — one listener only."
        ),
    }


def start_n8n(*, wait_seconds: int = 120) -> dict:
    if _tcp_open(N8N_PORT):
        return {
            "ok": True,
            "message": f"n8n already running on :{N8N_PORT}",
            "n8n_url": N8N_URL,
            "started": False,
        }
    if not START_SCRIPT.is_file():
        return {"ok": False, "error": f"start script missing: {START_SCRIPT}"}
    try:
        proc = subprocess.run(
            ["bash", str(START_SCRIPT)],
            cwd=SOURCE_A,
            capture_output=True,
            text=True,
            timeout=wait_seconds,
        )
        out = ((proc.stdout or "") + (proc.stderr or "")).strip()
        up = _tcp_open(N8N_PORT)
        return {
            "ok": up,
            "message": "n8n ready" if up else "n8n start timed out or failed",
            "output": out,
            "exit_code": proc.returncode,
            "n8n_url": N8N_URL,
            "open_url": N8N_URL if up else None,
            "started": True,
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": _tcp_open(N8N_PORT),
            "message": "Start still running — check log ~/.sina/n8n.log",
            "n8n_url": N8N_URL,
            "started": True,
        }


def test_starter_flow(*, auto_start_n8n: bool = True) -> dict:
    steps: list[dict] = []

    hub = _probe("http://127.0.0.1:13020/health")
    steps.append(
        {
            "id": "hub",
            "title": "Hub probe (optional · offline OK)",
            "ok": hub.get("ok"),
            "detail": hub.get("snippet") or hub.get("error", ""),
        }
    )

    rt = _probe(RUNTIME_HEALTH)
    steps.append(
        {
            "id": "runtime_health",
            "title": "SinaaiRuntime /health",
            "ok": rt.get("ok"),
            "detail": rt.get("snippet") or rt.get("error", "Start Runtime: mono scripts/start-all.sh"),
            "required": False,
        }
    )

    n8n_running = _tcp_open(N8N_PORT)
    if not n8n_running and auto_start_n8n:
        start = start_n8n(wait_seconds=90)
        steps.append(
            {
                "id": "n8n_start",
                "title": "Start n8n",
                "ok": start.get("ok"),
                "detail": start.get("message") or start.get("error", ""),
            }
        )
        n8n_running = _tcp_open(N8N_PORT)
    else:
        steps.append(
            {
                "id": "n8n_port",
                "title": "n8n port open",
                "ok": n8n_running,
                "detail": N8N_URL if n8n_running else "Tap Start n8n in hub",
            }
        )

    n8n = _probe(N8N_URL)
    steps.append(
        {
            "id": "n8n_ui",
            "title": "n8n UI HTTP",
            "ok": n8n.get("ok"),
            "detail": f"status {n8n.get('status', '?')}" if n8n.get("ok") else str(n8n.get("error", "")),
        }
    )

    liaison = _probe(RUNTIME_LIAISON) if rt.get("ok") else {"ok": False, "error": "runtime down"}
    steps.append(
        {
            "id": "liaison",
            "title": "GET /api/v1/liaison/status",
            "ok": liaison.get("ok"),
            "detail": liaison.get("snippet") or liaison.get("error", "skipped"),
            "required": False,
        }
    )

    wf_ok = WORKFLOW_PATH.is_file()
    steps.append(
        {
            "id": "workflow_file",
            "title": "Starter workflow JSON on disk",
            "ok": wf_ok,
            "detail": str(WORKFLOW_PATH),
        }
    )

    n8n_ok = any(s["ok"] for s in steps if s["id"] in ("n8n_ui", "n8n_port", "n8n_start"))
    hub_mode = _glue_hub_mode()
    hub_step_ok = steps[0]["ok"] or hub_mode == "quarantined"
    core_ok = hub_step_ok and wf_ok and n8n_ok

    next_steps = [
        "Open n8n UI → import workflow file (Apps → Open n8n UI)",
        "Add Telegram credential in n8n — only if disabling built-in TELEGRAM_V4_ENABLED",
        "Activate workflow OR keep built-in bot (one listener)",
        "Re-run starter test after import",
    ]

    return {
        "ok": core_ok,
        "partial": core_ok and not all(s["ok"] for s in steps),
        "message": "Starter test PASS" if core_ok else "Starter test FAIL — see steps",
        "steps": steps,
        "n8n_url": N8N_URL,
        "workflow_path": str(WORKFLOW_PATH),
        "next_steps": next_steps,
        "output": "\n".join(
            f"[{'PASS' if s['ok'] else 'FAIL'}] {s['title']}: {s.get('detail', '')}" for s in steps
        ),
    }


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_workflow_path(spec: dict) -> tuple[Path, str]:
    """Resolve workflow JSON — MonoRepo first, then SourceA stub fallback."""
    rel = spec.get("path", "")
    mono_path = MONO_ROOT / rel
    if mono_path.is_file():
        return mono_path, "mono"
    sa_raw = (spec.get("source_a_path") or "").strip()
    if sa_raw:
        sa_path = Path(sa_raw.replace("~", str(Path.home())))
        if sa_path.is_file():
            return sa_path, "source_a"
    return mono_path, "missing"


def sync_governance_stubs() -> dict:
    """Copy governance stub workflows from SourceA into MonoRepo (founder one-tap)."""
    import shutil

    if not MANIFEST_PATH.is_file():
        return {"ok": False, "error": f"manifest missing: {MANIFEST_PATH}"}
    manifest = _load_json(MANIFEST_PATH)
    copied: list[dict] = []
    skipped: list[dict] = []
    for spec in manifest.get("workflows", []):
        sa_raw = (spec.get("source_a_path") or "").strip()
        if not sa_raw:
            continue
        sa_path = Path(sa_raw.replace("~", str(Path.home())))
        mono_path = MONO_ROOT / spec.get("path", "")
        wf_id = spec.get("id")
        if not sa_path.is_file():
            skipped.append({"id": wf_id, "reason": "source_a missing", "path": str(sa_path)})
            continue
        if mono_path.is_file():
            skipped.append({"id": wf_id, "reason": "already in mono", "path": str(mono_path)})
            continue
        mono_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(sa_path, mono_path)
        copied.append({"id": wf_id, "path": str(mono_path)})
    return {
        "ok": True,
        "message": f"Synced {len(copied)} stub(s) to MonoRepo",
        "copied": copied,
        "skipped": skipped,
        "mono_root": str(MONO_ROOT),
    }


def validate_workflow_files() -> dict:
    """Validate on-disk workflow JSON against fixture manifest."""
    if not MANIFEST_PATH.is_file():
        return {"ok": False, "error": f"manifest missing: {MANIFEST_PATH}"}
    manifest = _load_json(MANIFEST_PATH)
    checks: list[dict] = []
    all_ok = True
    for spec in manifest.get("workflows", []):
        if spec.get("deferred"):
            checks.append({"id": spec.get("id"), "ok": True, "skipped": True, "role": spec.get("role")})
            continue
        path, source = _resolve_workflow_path(spec)
        row: dict = {"id": spec.get("id"), "path": str(path), "ok": False, "source": source, "role": spec.get("role")}
        if source == "missing" or not path.is_file():
            row["error"] = "file missing"
            all_ok = False
            checks.append(row)
            continue
        try:
            wf = _load_json(path)
        except json.JSONDecodeError as e:
            row["error"] = f"invalid JSON: {e}"
            all_ok = False
            checks.append(row)
            continue
        nodes = wf.get("nodes") or []
        types = {n.get("type") for n in nodes if isinstance(n, dict)}
        min_nodes = int(spec.get("min_nodes", 1))
        required_types = set(spec.get("required_node_types") or [])
        missing_types = required_types - types
        if len(nodes) < min_nodes or missing_types:
            row["error"] = (
                f"nodes={len(nodes)} (min {min_nodes}); missing types={sorted(missing_types)}"
            )
            all_ok = False
        else:
            row["ok"] = True
            row["node_count"] = len(nodes)
            row["name"] = wf.get("name", path.stem)
        checks.append(row)
    return {
        "ok": all_ok,
        "message": "Workflow files PASS" if all_ok else "Workflow file validation FAIL",
        "checks": checks,
        "manifest": str(MANIFEST_PATH),
        "ok_count": sum(1 for c in checks if c.get("ok")),
        "total": len(checks),
    }


def _glue_hub_mode() -> str:
    try:
        from n8n_glue_config_v1 import detect_hub_mode  # noqa: WPS433

        return detect_hub_mode()
    except Exception:
        quarantine = Path.home() / ".sina" / "sina-command-quarantine-v1.json"
        return "quarantined" if quarantine.is_file() or not _tcp_open(13020) else "live"


def test_health_ping_dry_run() -> dict:
    """Agent-runnable ping — quarantine-aware; Mac Health + n8n required."""
    hub_mode = _glue_hub_mode()
    mac_health = _probe(MAC_HEALTH_HEALTH)
    n8n_hz = _probe(N8N_HEALTHZ)
    n8n_integration = _probe(N8N_INTEGRATION_HEALTH)
    hub = _probe(HUB_HEALTH)
    rt = _probe(RUNTIME_HEALTH)
    hub["warn_only"] = hub_mode == "quarantined"
    rt["warn_only"] = True
    n8n_integration["warn_only"] = True
    core_ok = mac_health.get("ok") and n8n_hz.get("ok")
    overall = "green"
    if not core_ok:
        overall = "red"
    elif hub_mode == "quarantined" or not hub.get("ok") or not rt.get("ok"):
        overall = "yellow"
    ok = overall in ("green", "yellow")
    return {
        "ok": ok,
        "overall": overall,
        "hub_mode": hub_mode,
        "message": f"Health ping {overall.upper()} (hub_mode={hub_mode})",
        "mac_health": mac_health,
        "n8n": n8n_hz,
        "n8n_integration": n8n_integration,
        "hub": hub,
        "runtime": rt,
        "workflow_path": str(HEALTH_PING_WORKFLOW),
        "workflow_exists": HEALTH_PING_WORKFLOW.is_file(),
    }


def test_extended_flow(*, auto_start_n8n: bool = True) -> dict:
    """Starter test + manifest validation + health ping dry-run + n8n healthz."""
    starter = test_starter_flow(auto_start_n8n=auto_start_n8n)
    wf = validate_workflow_files()
    ping = test_health_ping_dry_run()
    healthz = _probe(f"http://127.0.0.1:{N8N_PORT}/healthz")
    intel_step: dict = {"id": "intelligence_api", "title": "Intelligence capture API", "ok": False, "detail": "skipped"}
    try:
        from n8n_intelligence import capture_and_save  # noqa: WPS433

        cap = capture_and_save(include_runtime_ask=False)
        intel_step = {
            "id": "intelligence_api",
            "title": "Intelligence capture API",
            "ok": cap.get("ok"),
            "detail": cap.get("message", "")[:120],
        }
    except Exception as e:
        intel_step["detail"] = str(e)

    extra_steps = [
        {
            "id": "workflow_manifest",
            "title": "Workflow manifest on disk",
            "ok": wf.get("ok"),
            "detail": wf.get("message", ""),
        },
        {
            "id": "health_ping_dry",
            "title": "Stack health ping (HTTP dry-run)",
            "ok": ping.get("ok"),
            "detail": ping.get("message", ""),
        },
        {
            "id": "n8n_healthz",
            "title": "n8n /healthz",
            "ok": healthz.get("ok"),
            "detail": f"status {healthz.get('status', '?')}" if healthz.get("ok") else str(healthz.get("error", "")),
        },
    ]

    extra_steps.append(intel_step)
    mac_step = {
        "id": "mac_health",
        "title": "Mac Health Guard :13024",
        "ok": ping.get("mac_health", {}).get("ok"),
        "detail": ping.get("mac_health", {}).get("snippet") or ping.get("mac_health", {}).get("error", ""),
        "required": True,
    }
    extra_steps.insert(0, mac_step)
    steps = list(starter.get("steps", [])) + extra_steps
    hub_mode = ping.get("hub_mode", _glue_hub_mode())
    ping_ok = ping.get("ok") and ping.get("mac_health", {}).get("ok") and ping.get("n8n", {}).get("ok")
    intel_ok = intel_step.get("ok") or hub_mode == "quarantined"
    core_ok = ping_ok and wf.get("ok") and intel_ok
    return {
        "ok": core_ok,
        "message": "Extended n8n test PASS" if core_ok else "Extended n8n test FAIL",
        "steps": steps,
        "starter": starter,
        "workflow_validation": wf,
        "health_ping": ping,
        "output": "\n".join(
            f"[{'PASS' if s['ok'] else 'FAIL'}] {s['title']}: {s.get('detail', '')}" for s in steps
        ),
        "n8n_url": N8N_URL,
        "next_steps": starter.get("next_steps", [])
        + [
            "Import sinaai-stack-health-ping.json in n8n (no Telegram creds) and run manually",
            "Import sinaai-telegram-agents.json only if disabling TELEGRAM_V4_ENABLED",
        ],
    }


def run_n8n_suite(*, auto_start_n8n: bool = True) -> dict:
    """Full agent suite: status, extended test, workflow validation."""
    status = n8n_status_payload()
    extended = test_extended_flow(auto_start_n8n=auto_start_n8n)
    return {
        "ok": extended.get("ok"),
        "status": status,
        "extended": extended,
        "output": extended.get("output", ""),
    }


def handle_n8n_action(action: str) -> dict:
    if action == "status":
        return n8n_status_payload()
    if action == "start":
        return start_n8n()
    if action == "test_flow":
        return test_starter_flow()
    if action == "test_extended":
        return test_extended_flow()
    if action == "validate":
        return validate_workflow_files()
    if action == "sync_stubs":
        return sync_governance_stubs()
    if action == "health_ping":
        return test_health_ping_dry_run()
    if action == "run_suite":
        return run_n8n_suite()
    if action == "capture_intelligence":
        from n8n_intelligence import capture_and_save  # noqa: WPS433

        return capture_and_save(include_runtime_ask=True)
    if action == "intelligence":
        from n8n_intelligence import intelligence_payload  # noqa: WPS433

        return intelligence_payload(refresh=False)
    return {"ok": False, "error": f"unknown n8n action: {action}"}


def _intelligence_panel() -> dict:
    try:
        from n8n_intelligence import intelligence_payload  # noqa: WPS433

        return intelligence_payload(refresh=False)
    except Exception as e:
        return {"ok": False, "error": str(e)}


def automation_payload() -> dict:
    st = n8n_status_payload()
    manifest = validate_workflow_files()
    intel = _intelligence_panel()
    workflows = [
        {
            "id": c.get("id"),
            "name": c.get("name", c.get("id")),
            "path": c.get("path"),
            "ok": c.get("ok"),
            "source": c.get("source"),
            "role": c.get("role")
            or (
                "intelligence"
                if c.get("id") and "intelligence" in str(c.get("id"))
                else "health"
                if c.get("id") and "health" in str(c.get("id"))
                else "telegram"
            ),
        }
        for c in (manifest.get("checks") or [])
    ]
    return {
        "ok": True,
        "title": "Automation & n8n Intelligence",
        "law_path": "SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md",
        "tagline": "Capture stack signals → product opportunities → n8n schedules & webhooks",
        "status": st,
        "workflows": workflows,
        "intelligence": intel,
        "webhook_url": "http://127.0.0.1:13020/api/n8n/intelligence",
        "actions": [
            {"id": "founder-n8n-start", "label": "Start n8n", "icon": "▶"},
            {"id": "founder-n8n-capture-intel", "label": "Capture intelligence", "icon": "◎"},
            {"id": "founder-n8n-test-extended", "label": "Run extended test", "icon": "✓✓"},
            {"id": "founder-n8n-test-flow", "label": "Starter test", "icon": "✓"},
            {"id": "founder-n8n-open-brief", "label": "Open intel brief", "icon": "📊"},
            {"id": "founder-n8n-open", "label": "Open n8n UI", "icon": "⎇"},
            {"id": "founder-n8n-doc", "label": "Automation law", "icon": "📜"},
        ],
        "starter_workflow": str(WORKFLOW_PATH),
        "health_ping_workflow": str(HEALTH_PING_WORKFLOW),
        "fixtures_dir": str(FIXTURE_DIR),
    }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="n8n automation CLI")
    p.add_argument(
        "action",
        choices=["status", "start", "test", "extended", "validate", "health_ping", "suite"],
        nargs="?",
        default="suite",
    )
    p.add_argument("--no-auto-start", action="store_true")
    args = p.parse_args()
    auto = not args.no_auto_start
    mapping = {
        "status": lambda: n8n_status_payload(),
        "start": start_n8n,
        "test": lambda: test_starter_flow(auto_start_n8n=auto),
        "extended": lambda: test_extended_flow(auto_start_n8n=auto),
        "validate": validate_workflow_files,
        "health_ping": test_health_ping_dry_run,
        "suite": lambda: run_n8n_suite(auto_start_n8n=auto),
    }
    result = mapping[args.action]()
    print(result.get("output") or json.dumps(result, indent=2))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
