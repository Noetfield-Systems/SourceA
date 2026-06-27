"""FBE Factory Spec Language v1 — load, validate, resolve catalog → execution."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = ROOT / "data" / "fbe_catalog_v1.json"
SCHEMA_PATH = ROOT / "data" / "fbe_factory_spec_schema_v1.json"
SPECS_DIR = ROOT / "data" / "factory-specs"
BAY_JOBS_PATH = ROOT / "data" / "fbe_bay_jobs_v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def spec_path_for(factory_id: str) -> Path:
    return SPECS_DIR / f"{factory_id}.json"


def load_spec(*, factory_id: str) -> dict[str, Any]:
    path = spec_path_for(factory_id)
    if not path.is_file():
        cat = load_catalog()
        for item in cat.get("items") or []:
            if item.get("factory_id") == factory_id:
                rel = item.get("spec_path") or ""
                path = ROOT / rel if rel else path
                break
    spec = _read_json(path)
    if spec.get("extends"):
        base = load_spec(factory_id=str(spec["extends"]))
        merged = {**base, **spec}
        merged["factory_id"] = spec.get("factory_id") or factory_id
        merged["kind"] = spec.get("kind") or base.get("kind")
        merged["_extends"] = spec["extends"]
        return merged
    return spec


def load_catalog() -> dict[str, Any]:
    return _read_json(CATALOG_PATH)


def _has(obj: dict[str, Any], key: str) -> bool:
    val = obj.get(key)
    if val is None:
        return False
    if isinstance(val, str):
        return bool(val.strip())
    if isinstance(val, list):
        return len(val) > 0
    return True


def validate_spec(spec: dict[str, Any]) -> dict[str, Any]:
    schema = _read_json(SCHEMA_PATH)
    required = schema.get("required") or []
    errors: list[str] = []

    for key in required:
        if not _has(spec, key):
            errors.append(f"missing:{key}")

    if spec.get("schema") != "fbe-factory-spec-v1":
        errors.append("invalid_schema")

    kernel = spec.get("kernel") or {}
    if kernel.get("id") != "fbe-v1":
        errors.append("kernel_id_must_be_fbe-v1")

    lines = spec.get("lines") or []
    allowed_lines = {"trust_motor", "refinery", "assembly"}
    for line in lines:
        if line not in allowed_lines:
            errors.append(f"invalid_line:{line}")

    runtime = spec.get("runtime") or {}
    for key in ("bay_slug", "api_route", "cloud_entry"):
        if not str(runtime.get(key) or "").strip():
            errors.append(f"missing:runtime.{key}")

    io = spec.get("io") or {}
    for key in ("input_schema", "output_artifact"):
        if not str(io.get(key) or "").strip():
            errors.append(f"missing:io.{key}")
        else:
            rel = str(io[key])
            if rel.endswith(".json") and not (ROOT / rel).is_file():
                errors.append(f"missing_file:{rel}")

    commercial = spec.get("commercial") or {}
    for key in ("name", "tier_label", "buyer"):
        if not str(commercial.get(key) or "").strip():
            errors.append(f"missing:commercial.{key}")

    bay_jobs = _read_json(BAY_JOBS_PATH)
    factories = bay_jobs.get("factories") or {}
    fid = spec.get("factory_id")
    kind = spec.get("kind") or "engine"
    if kind == "engine" and fid and fid not in factories:
        errors.append(f"engine_not_in_bay_jobs:{fid}")

    return {"ok": not errors, "errors": errors, "factory_id": fid}


def validate_catalog() -> dict[str, Any]:
    cat = load_catalog()
    errors: list[str] = []
    items = cat.get("items") or []
    if not items:
        errors.append("catalog_empty")
    seen: set[str] = set()
    specs_ok = 0
    for item in items:
        cid = str(item.get("catalog_id") or "")
        fid = str(item.get("factory_id") or "")
        if cid in seen:
            errors.append(f"duplicate_catalog_id:{cid}")
        seen.add(cid)
        rel = str(item.get("spec_path") or "")
        if not (ROOT / rel).is_file():
            errors.append(f"missing_spec:{rel}")
            continue
        spec = load_spec(factory_id=fid)
        v = validate_spec(spec)
        if not v.get("ok"):
            errors.extend([f"{fid}:{e}" for e in v.get("errors") or []])
        else:
            specs_ok += 1
    return {
        "ok": not errors,
        "errors": errors,
        "item_count": len(items),
        "specs_valid": specs_ok,
        "hero_factory_id": cat.get("hero_factory_id"),
    }


def spec_hash(spec: dict[str, Any]) -> str:
    payload = json.dumps(spec, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def resolve_execution(
    *,
    factory_id: str,
    tenant: str = "",
    input_payload: dict[str, Any] | None = None,
    work_order_id: str = "",
) -> dict[str, Any]:
    """Resolve catalog spec → Hub API body + route (runtime only executes)."""
    spec = load_spec(factory_id=factory_id)
    validation = validate_spec(spec)
    if not validation.get("ok"):
        return {"ok": False, "error": "invalid_spec", "errors": validation.get("errors")}

    runtime = spec.get("runtime") or {}
    io = spec.get("io") or {}
    gov = spec.get("governance") or {}
    policy_pack = str(gov.get("policy_pack") or "trust_motor")
    body = {
        "factory_id": factory_id,
        "template_id": factory_id if spec.get("kind") == "engine" else spec.get("extends", factory_id),
        "bay_slug": runtime.get("bay_slug"),
        "tenant": tenant or runtime.get("default_tenant"),
        "work_order_id": work_order_id,
        "execution_mode": runtime.get("execution_mode") or "CLOUD_ONLY",
        "policy_pack": policy_pack,
        "input": input_payload or {},
        "spec_version": spec.get("spec_version"),
        "spec_hash": spec_hash(spec),
    }
    if spec.get("kind") == "wrapper":
        body["wrapper_id"] = factory_id
        body["template_id"] = spec.get("extends") or body["template_id"]

    return {
        "ok": True,
        "factory_id": factory_id,
        "api_route": runtime.get("api_route"),
        "cloud_entry": runtime.get("cloud_entry"),
        "body": body,
        "output_artifact": io.get("output_artifact"),
        "certainty_report": io.get("certainty_report", True),
        "tier_cap_honest": gov.get("tier_cap_honest"),
        "policy_pack_id": policy_pack,
        "commercial_name": (spec.get("commercial") or {}).get("name"),
    }


def catalog_payload(*, tier: str = "") -> dict[str, Any]:
    cat = load_catalog()
    items = []
    for item in cat.get("items") or []:
        if tier and item.get("tier") != tier:
            continue
        fid = str(item.get("factory_id") or "")
        spec = load_spec(factory_id=fid)
        commercial = spec.get("commercial") or {}
        io = spec.get("io") or {}
        kernel = spec.get("kernel") or {}
        items.append(
            {
                **item,
                "name": commercial.get("name"),
                "tagline": commercial.get("tagline"),
                "buyer": commercial.get("buyer"),
                "hero": commercial.get("hero") or item.get("hero"),
                "maintenance_fee_usd": commercial.get("maintenance_fee_usd"),
                "inputs": io.get("input_schema"),
                "operational_nodes": kernel.get("line_node_count"),
                "guaranteed_output": io.get("output_artifact"),
                "tier_cap_honest": (spec.get("governance") or {}).get("tier_cap_honest"),
                "policy_pack_id": item.get("policy_pack_id")
                or (spec.get("governance") or {}).get("policy_pack"),
                "install_label": item.get("install_label") or "Deploy",
                "api_route": (spec.get("runtime") or {}).get("api_route"),
                "spec_version": spec.get("spec_version"),
                "spec_hash": spec_hash(spec),
            }
        )
    validation = validate_catalog()
    return {
        "ok": validation.get("ok"),
        "schema": "fbe-catalog-v1",
        "at": _now(),
        "platform": cat.get("platform"),
        "tagline": cat.get("tagline"),
        "hero_factory_id": cat.get("hero_factory_id"),
        "hero_wrapper_id": cat.get("hero_wrapper_id"),
        "item_count": len(items),
        "items": items,
        "api": cat.get("api"),
        "validation": validation,
    }
