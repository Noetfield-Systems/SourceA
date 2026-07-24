"""FBE execution contract — policy gate, kernel hash, receipt normalization."""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = ROOT / "data" / "fbe_execution_contract_v1.json"
GRAPH_PATH = ROOT / "data" / "fbe_node_graph_v1.json"
POLICY_REGISTRY_PATH = ROOT / "data" / "policy-packs" / "registry-v1.json"
TIMEOUT_BUDGETS_PATH = ROOT / "data" / "fbe_timeout_budgets_v1.json"
IDEMPOTENCY_INDEX_PATH = Path.home() / ".sina" / "fbe-idempotency-index-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def json_safe_dict(obj: Any) -> Any:
    """Deep-copy for JSON.dumps — break cycles on execution_receipt/raw_receipt."""
    seen: dict[int, Any] = {}

    def _walk(value: Any) -> Any:
        if isinstance(value, dict):
            oid = id(value)
            if oid in seen:
                return "<cycle>"
            out: dict[str, Any] = {}
            seen[oid] = out
            for key, item in value.items():
                out[str(key)] = _walk(item)
            return out
        if isinstance(value, (list, tuple)):
            return [_walk(item) for item in value]
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)

    return _walk(obj)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def kernel_hash() -> str:
    if not GRAPH_PATH.is_file():
        return "missing-graph"
    digest = hashlib.sha256(GRAPH_PATH.read_bytes()).hexdigest()
    return digest[:16]


def kernel_version() -> str:
    spec = _read_json(CONTRACT_PATH)
    graph = _read_json(GRAPH_PATH)
    base = spec.get("kernel_version") or graph.get("version") or "fbe-v1"
    return f"{base}+{kernel_hash()}"


def load_policy_registry() -> dict[str, Any]:
    return _read_json(POLICY_REGISTRY_PATH)


def get_policy_pack(pack_id: str) -> dict[str, Any] | None:
    reg = load_policy_registry()
    for pack in reg.get("packs") or []:
        if pack.get("id") == pack_id:
            return pack
    return None


def policy_pack_from_factory(factory_id: str) -> str:
    try:
        import sys

        scripts = str(ROOT / "scripts")
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        from fbe.lib.factory_spec_v1 import load_spec  # noqa: WPS433

        spec = load_spec(factory_id=factory_id)
        gov = spec.get("governance") or {}
        return str(gov.get("policy_pack") or "trust_motor")
    except Exception:
        return "trust_motor"


def policy_hash_for(*, policy_pack: str, factory_id: str, spec_hash: str = "") -> str:
    base = f"{policy_pack}:{factory_id}:{spec_hash or kernel_hash()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]


def load_timeout_budgets() -> dict[str, Any]:
    return _read_json(TIMEOUT_BUDGETS_PATH)


def timeout_for_capability(capability: str) -> int:
    budgets = load_timeout_budgets()
    caps = budgets.get("capabilities") or {}
    return int(caps.get(capability) or caps.get("fbe_run_job_default") or budgets.get("default_timeout_s") or 300)


def _load_idempotency_index() -> dict[str, Any]:
    return _read_json(IDEMPOTENCY_INDEX_PATH)


def _save_idempotency_index(row: dict[str, Any]) -> None:
    IDEMPOTENCY_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    IDEMPOTENCY_INDEX_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def check_idempotency(idempotency_key: str) -> dict[str, Any]:
    key = str(idempotency_key or "").strip()
    if not key:
        return {"ok": True, "duplicate": False, "reason": "no_key"}
    idx = _load_idempotency_index()
    jobs = idx.get("jobs") or {}
    prior = jobs.get(key)
    if prior and prior.get("status") in ("success", "running"):
        return {
            "ok": False,
            "duplicate": True,
            "reason": "idempotency_key_already_executed",
            "prior_job_id": prior.get("job_id"),
            "prior_receipt_path": prior.get("receipt_path"),
            "prior_at": prior.get("at"),
        }
    return {"ok": True, "duplicate": False}


def record_idempotency(
    *,
    idempotency_key: str,
    job_id: str,
    status: str,
    receipt_path: str = "",
) -> None:
    key = str(idempotency_key or "").strip()
    if not key:
        return
    idx = _load_idempotency_index()
    jobs = dict(idx.get("jobs") or {})
    jobs[key] = {
        "job_id": job_id,
        "status": status,
        "receipt_path": receipt_path,
        "at": _now(),
    }
    _save_idempotency_index({"schema": "fbe-idempotency-index-v1", "jobs": jobs, "updated_at": _now()})


def build_contract(
    *,
    factory_id: str,
    tenant_id: str,
    execution_mode: str = "CLOUD_ONLY",
    input_payload: dict[str, Any] | None = None,
    policy_hash: str = "",
    policy_pack: str = "",
    job_id: str = "",
    bay_slug: str = "",
    work_order_id: str = "",
    spec_hash: str = "",
    idempotency_key: str = "",
    timeout_s: int | None = None,
) -> dict[str, Any]:
    pack = policy_pack or policy_pack_from_factory(factory_id)
    ph = policy_hash or policy_hash_for(policy_pack=pack, factory_id=factory_id, spec_hash=spec_hash)
    cap_timeout = timeout_s if timeout_s is not None else timeout_for_capability(factory_id)
    idem = str(idempotency_key or "").strip()
    if not idem and work_order_id:
        idem = hashlib.sha256(f"{factory_id}:{work_order_id}:{tenant_id}".encode()).hexdigest()[:32]
    return {
        "schema": "fbe-execution-contract-v1",
        "job_id": job_id or str(uuid.uuid4()),
        "factory_id": factory_id,
        "kernel_version": kernel_version(),
        "kernel_hash": kernel_hash(),
        "tenant_id": tenant_id,
        "bay_slug": bay_slug,
        "work_order_id": work_order_id,
        "idempotency_key": idem,
        "timeout_s": cap_timeout,
        "input": input_payload or {},
        "policy_pack": pack,
        "policy_hash": ph,
        "execution_mode": execution_mode,
        "at": _now(),
    }


def validate_contract(contract: dict[str, Any]) -> dict[str, Any]:
    spec = _read_json(CONTRACT_PATH)
    required = spec.get("required_fields") or []
    errors: list[str] = []
    for key in required:
        if not str(contract.get(key) or "").strip():
            errors.append(f"missing:{key}")
    mode = str(contract.get("execution_mode") or "")
    allowed = spec.get("allowed_execution_modes") or ["CLOUD_ONLY", "LOCAL_ALLOWED"]
    if mode and mode not in allowed:
        errors.append(f"invalid_execution_mode:{mode}")
    if spec.get("policy_gate", {}).get("require_kernel_version_match"):
        kv = str(contract.get("kernel_version") or "")
        if kv and not kv.startswith("fbe-v") and "+" not in kv:
            errors.append("kernel_version_malformed")
    gc = contract.get("goal_contract")
    if isinstance(gc, dict) and gc:
        gc_errors = validate_goal_contract_envelope(gc)
        errors.extend(gc_errors)
    return {"ok": not errors, "errors": errors, "contract": contract}


def validate_goal_contract_envelope(goal_contract: dict[str, Any]) -> list[str]:
    """NF-GOVERNED-WORK-PACKET-CONTROL-V1 — Goal Contract fields when present."""
    spec = _read_json(CONTRACT_PATH)
    required = (spec.get("goal_contract") or {}).get("required_when_present") or []
    errors: list[str] = []
    for key in required:
        if key not in goal_contract or goal_contract.get(key) in (None, "", []):
            errors.append(f"goal_contract_missing:{key}")
    ah = str(goal_contract.get("authority_hash") or "")
    if ah and (not ah.startswith("sha256:") or len(ah) < 71):
        errors.append("goal_contract_authority_hash_malformed")
    return errors


def attach_goal_contract(
    contract: dict[str, Any],
    goal_contract: dict[str, Any] | None,
) -> dict[str, Any]:
    if not goal_contract:
        return contract
    out = dict(contract)
    out["goal_contract"] = goal_contract
    return out


def map_cycle_to_work_packet_terminal(to_state: str, *, has_artifact: bool) -> str:
    if to_state == "COMPLETE" and has_artifact:
        return "ACCEPTED_ARTIFACT"
    if to_state in {"BLOCKED_WITH_REASON", "IDLE_NO_WORK"}:
        # Idle with no work is not ACTIVE_FOREVER; bounded no-op receipt.
        return "BOUNDED_FAILURE" if to_state == "BLOCKED_WITH_REASON" else "BOUNDED_FAILURE"
    return "BOUNDED_FAILURE"


def policy_gate(
    contract: dict[str, Any],
    *,
    freeze_active: bool,
    cloud_url_configured: bool,
) -> dict[str, Any]:
    spec = _read_json(CONTRACT_PATH)
    gate = spec.get("policy_gate") or {}
    mode = str(contract.get("execution_mode") or "CLOUD_ONLY")
    reasons: list[str] = []

    if freeze_active and mode == "LOCAL_ALLOWED":
        reasons.append("freeze_blocks_local_execution")
    if freeze_active and not cloud_url_configured:
        reasons.append("freeze_requires_cloud_worker_url")
    if gate.get("require_kernel_version_match"):
        expected = kernel_version()
        submitted = str(contract.get("kernel_version") or "")
        if submitted and submitted != expected:
            reasons.append("kernel_version_mismatch")

    pack_id = str(contract.get("policy_pack") or "trust_motor")
    pack = get_policy_pack(pack_id)
    if not pack:
        reasons.append(f"unknown_policy_pack:{pack_id}")
    elif pack.get("extends_engine"):
        try:
            import sys

            scripts = str(ROOT / "scripts")
            if scripts not in sys.path:
                sys.path.insert(0, scripts)
            from fbe.lib.factory_spec_v1 import load_spec  # noqa: WPS433

            spec = load_spec(factory_id=str(contract.get("factory_id") or ""))
            extends = spec.get("extends") or spec.get("_extends")
            if extends and pack.get("extends_engine") != extends:
                reasons.append("policy_pack_engine_mismatch")
        except Exception:
            pass

    decision = "DENY" if reasons else "ALLOW"
    return {
        "ok": decision == "ALLOW",
        "decision": decision,
        "reasons": reasons,
        "policy_passed": decision == "ALLOW",
        "at": _now(),
    }


def normalize_receipt(
    job_receipt: dict[str, Any],
    *,
    contract: dict[str, Any],
    started_at: float,
    policy_passed: bool,
) -> dict[str, Any]:
    import time

    duration_ms = int(max(0.0, (time.time() - started_at) * 1000))
    graph = _read_json(GRAPH_PATH)
    nodes = graph.get("line_node_count") or graph.get("graph_total_nodes") or 0
    status = "success" if job_receipt.get("ok") else "failed"
    artifacts: list[str] = []
    for key in ("artifact_uri", "receipt_pack_uri", "partner_pack_uri"):
        val = job_receipt.get(key)
        if val:
            artifacts.append(str(val))
    raw_receipt = {
        k: v
        for k, v in job_receipt.items()
        if k not in ("execution_receipt", "execution_mode", "raw_receipt")
    }
    return {
        "schema": "fbe-execution-receipt-v1",
        "job_id": contract.get("job_id"),
        "factory_id": contract.get("factory_id"),
        "tenant_id": contract.get("tenant_id"),
        "status": status,
        "ok": job_receipt.get("ok"),
        "nodes_executed": nodes,
        "duration_ms": duration_ms,
        "cost_usd": job_receipt.get("cost_usd"),
        "artifact_urls": artifacts,
        "policy_passed": policy_passed,
        "policy_pack": contract.get("policy_pack"),
        "policy_hash": contract.get("policy_hash"),
        "kernel_hash": contract.get("kernel_hash") or kernel_hash(),
        "kernel_version": contract.get("kernel_version") or kernel_version(),
        "execution_plane": job_receipt.get("execution_plane") or "headless_cloud",
        "execution_mode": contract.get("execution_mode"),
        "tier_achieved": job_receipt.get("tier_achieved"),
        "tier_target": job_receipt.get("tier_target"),
        "federated_ok": job_receipt.get("federated_ok"),
        "at": _now(),
        "raw_receipt": raw_receipt,
    }


def contract_from_hub_body(path: str, body: dict[str, Any]) -> dict[str, Any]:
    spec = _read_json(CONTRACT_PATH)
    route = (spec.get("route_map") or {}).get(path) or {}
    factory_id = str(
        body.get("factory_id")
        or body.get("wrapper_id")
        or body.get("template_id")
        or route.get("default_template")
        or "web-product-factory-v1"
    )
    tenant_id = str(body.get("tenant_id") or body.get("tenant") or "wil_ai_design_partner")
    mode = str(body.get("execution_mode") or spec.get("default_execution_mode") or "CLOUD_ONLY")
    pack = str(body.get("policy_pack") or policy_pack_from_factory(factory_id))
    spec_hash = str(body.get("spec_hash") or "")
    return build_contract(
        factory_id=factory_id,
        tenant_id=tenant_id,
        execution_mode=mode,
        input_payload=body.get("input") if isinstance(body.get("input"), dict) else body,
        policy_hash=str(body.get("policy_hash") or ""),
        policy_pack=pack,
        job_id=str(body.get("job_id") or ""),
        bay_slug=str(body.get("bay_slug") or ""),
        work_order_id=str(body.get("work_order_id") or ""),
        spec_hash=spec_hash,
        idempotency_key=str(body.get("idempotency_key") or ""),
        timeout_s=int(body["timeout_s"]) if body.get("timeout_s") is not None else None,
    )
