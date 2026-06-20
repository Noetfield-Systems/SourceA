"""Hub FBE cloud proxy — freeze → CLOUD_ONLY, no dual execution hazard."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[3]
SINA = Path.home() / ".sina"
CONFIG_PATH = ROOT / "data" / "fbe_cloud_worker_config_v1.json"

sys_path_inserted = False


def _ensure_scripts_path() -> None:
    global sys_path_inserted
    if sys_path_inserted:
        return
    import sys

    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    sys_path_inserted = True


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _freeze_active() -> bool:
    _ensure_scripts_path()
    try:
        from mac_focus_freeze_v1 import is_focus_freeze  # noqa: WPS433

        return bool(is_focus_freeze())
    except Exception:
        flag = SINA / "auto-run-disabled-v1.flag"
        return flag.is_file()


def cloud_worker_url() -> str:
    cfg = _read_json(CONFIG_PATH)
    for key in (cfg.get("worker_url_env") or "FBE_CLOUD_WORKER_URL", "RAILWAY_WORKER_URL"):
        val = os.environ.get(key, "").strip()
        if val:
            return val.rstrip("/")
    return str(cfg.get("worker_url") or "").strip().rstrip("/")


def internal_secret() -> str:
    cfg = _read_json(CONFIG_PATH)
    for key in (cfg.get("secret_env") or "FBE_INTERNAL_SECRET",):
        val = os.environ.get(key, "").strip()
        if val:
            return val
    return ""


def execution_mode() -> str:
    if _freeze_active():
        return "CLOUD_ONLY"
    cfg = _read_json(CONFIG_PATH)
    if cfg.get("force_cloud_only"):
        return "CLOUD_ONLY"
    return str(os.environ.get("FBE_EXECUTION_MODE") or cfg.get("default_execution_mode") or "CLOUD_ONLY")


def cloud_execution_required() -> bool:
    return execution_mode() == "CLOUD_ONLY"


def proxy_to_cloud(*, path: str, body: dict[str, Any], timeout_s: int = 300) -> dict[str, Any]:
    url_base = cloud_worker_url()
    if not url_base:
        return {
            "ok": False,
            "error": "cloud_worker_unreachable",
            "message": "FBE_CLOUD_WORKER_URL not configured — set env or data/fbe_cloud_worker_config_v1.json",
            "execution_mode": execution_mode(),
            "execution_plane": "cloud_deferred",
        }
    target = f"{url_base}{path}"
    payload = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    secret = internal_secret()
    if secret:
        headers["Authorization"] = f"Bearer {secret}"
    req = urllib.request.Request(target, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
            row = json.loads(raw) if raw.strip() else {}
            row.setdefault("execution_plane", "headless_cloud")
            row.setdefault("proxied", True)
            return row
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8"))
        except Exception:
            detail = {"message": str(exc)}
        return {
            "ok": False,
            "error": "cloud_proxy_http_error",
            "status": exc.code,
            "message": "Cloud runner failed during headless execution handoff.",
            "details": detail,
            "execution_plane": "headless_cloud",
            "proxied": True,
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": "cloud_proxy_fatal",
            "message": "Cloud runner unreachable during headless execution handoff.",
            "details": str(exc),
            "execution_plane": "cloud_deferred",
            "proxied": True,
        }


def dispatch_fbe(
    *,
    path: str,
    body: dict[str, Any],
    local_fn: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    """Single source of truth: CLOUD_ONLY when freeze or forced."""
    _ensure_scripts_path()
    from fbe.lib.execution_contract_v1 import (  # noqa: WPS433
        contract_from_hub_body,
        normalize_receipt,
        policy_gate,
        validate_contract,
    )

    contract = contract_from_hub_body(path, body)
    if not body.get("execution_mode"):
        contract["execution_mode"] = execution_mode()
    validation = validate_contract(contract)
    if not validation.get("ok"):
        return {
            "ok": False,
            "error": "invalid_execution_contract",
            "errors": validation.get("errors"),
            "contract": contract,
        }

    gate = policy_gate(
        contract,
        freeze_active=_freeze_active(),
        cloud_url_configured=bool(cloud_worker_url()),
    )
    if not gate.get("ok"):
        return {
            "ok": False,
            "error": "policy_gate_deny",
            "decision": gate.get("decision"),
            "reasons": gate.get("reasons"),
            "contract": contract,
            "execution_mode": contract.get("execution_mode"),
        }

    try:
        from fbe.lib.trust_ledger_v1 import append_event as ledger_append  # noqa: WPS433

        ledger_append(
            event_type="JOB_QUEUED",
            job_id=str(contract.get("job_id") or ""),
            factory_id=str(contract.get("factory_id") or ""),
            policy_pack=str(contract.get("policy_pack") or ""),
            kernel_hash=str(contract.get("kernel_hash") or ""),
            payload={"path": path, "execution_mode": contract.get("execution_mode")},
        )
        ledger_append(
            event_type="POLICY_CHECKED",
            job_id=str(contract.get("job_id") or ""),
            factory_id=str(contract.get("factory_id") or ""),
            policy_pack=str(contract.get("policy_pack") or ""),
            kernel_hash=str(contract.get("kernel_hash") or ""),
            payload={"decision": gate.get("decision"), "reasons": gate.get("reasons")},
        )
    except Exception:
        pass

    started = time.time()
    if cloud_execution_required():
        row = proxy_to_cloud(path=path, body={**body, **contract})
        if row.get("execution_receipt"):
            return row
        raw = row.get("raw_receipt") or row
        if "schema" in raw and raw.get("schema") == "fbe-run-job-receipt-v1":
            row["execution_receipt"] = normalize_receipt(
                raw,
                contract=contract,
                started_at=started,
                policy_passed=bool(gate.get("policy_passed")),
            )
        _ledger_sign(contract, row)
        return row

    local_row = local_fn()
    local_row["execution_mode"] = "LOCAL_ALLOWED"
    local_row["execution_plane"] = local_row.get("execution_plane") or "local_mac"
    local_row["execution_receipt"] = normalize_receipt(
        local_row,
        contract=contract,
        started_at=started,
        policy_passed=bool(gate.get("policy_passed")),
    )
    _ledger_sign(contract, local_row)
    return local_row


def _ledger_sign(contract: dict[str, Any], row: dict[str, Any]) -> None:
    try:
        from fbe.lib.trust_ledger_v1 import append_event as ledger_append  # noqa: WPS433

        jid = str(contract.get("job_id") or "")
        ledger_append(
            event_type="KERNEL_STARTED",
            job_id=jid,
            factory_id=str(contract.get("factory_id") or ""),
            policy_pack=str(contract.get("policy_pack") or ""),
            kernel_hash=str(contract.get("kernel_hash") or ""),
        )
        ledger_append(
            event_type="JOB_COMPLETED",
            job_id=jid,
            factory_id=str(contract.get("factory_id") or ""),
            policy_pack=str(contract.get("policy_pack") or ""),
            kernel_hash=str(contract.get("kernel_hash") or ""),
            payload={"ok": row.get("ok")},
        )
        ledger_append(
            event_type="LEDGER_SIGNED",
            job_id=jid,
            factory_id=str(contract.get("factory_id") or ""),
            policy_pack=str(contract.get("policy_pack") or ""),
            kernel_hash=str(contract.get("kernel_hash") or ""),
            payload={"execution_receipt": row.get("execution_receipt")},
            bridge_spine=True,
        )
    except Exception:
        pass


def status_payload() -> dict[str, Any]:
    contract = _read_json(ROOT / "data" / "loop-specialist-cloud-contract-v1.json")
    hub_url = os.environ.get("SINA_COMMAND_HUB_URL", "http://127.0.0.1:13020").rstrip("/")
    loop_cloud_ready = bool(hub_url) and contract.get("schema") == "loop-specialist-cloud-contract-v1"
    return {
        "schema": "fbe-hub-cloud-proxy-status-v1",
        "freeze_active": _freeze_active(),
        "execution_mode": execution_mode(),
        "cloud_execution_required": cloud_execution_required(),
        "cloud_worker_url": cloud_worker_url() or None,
        "cloud_worker_configured": bool(cloud_worker_url()),
        "loop_specialist_cloud_ready": loop_cloud_ready,
        "loop_specialist_hub_api": f"{hub_url}/api/loop-specialist/tick/v1",
        "loop_specialist_contract": str(ROOT / "data" / "loop-specialist-cloud-contract-v1.json"),
    }
