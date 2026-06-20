"""Governance client — check, execute, audit, sign."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from noetfield.catalog import get_factory, list_factories
from noetfield.hub_client import http_json, load_config


def _resolve_local(factory_id: str, tenant: str, input_payload: dict[str, Any]) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[4]
    scripts = root / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    try:
        from fbe.lib.factory_spec_v1 import resolve_execution  # noqa: WPS433

        return resolve_execution(factory_id=factory_id, tenant=tenant, input_payload=input_payload)
    except Exception as exc:
        return {"ok": False, "error": "resolve_failed", "message": str(exc)}


class Governance:
    def __init__(self, *, hub_url: str = "", api_key: str = ""):
        cfg = load_config()
        self.hub_url = (hub_url or cfg["hub_url"]).rstrip("/")
        self.api_key = api_key or cfg.get("api_key", "")

    def catalog(self, *, tier: str = "") -> dict[str, Any]:
        url = f"{self.hub_url}/api/fbe/catalog/v1"
        if tier:
            url += f"?tier={tier}"
        return http_json(method="GET", url=url, api_key=self.api_key)

    def check(
        self,
        *,
        factory_id: str,
        input: dict[str, Any] | None = None,
        tenant: str = "",
    ) -> dict[str, Any]:
        resolved = _resolve_local(factory_id, tenant, input or {})
        if not resolved.get("ok"):
            return resolved
        body = {
            **resolved.get("body", {}),
            "input": input or {},
            "dry_run": True,
        }
        route = str(resolved.get("api_route") or "")
        return {
            "ok": True,
            "factory_id": factory_id,
            "api_route": route,
            "policy_pack": body.get("policy_pack") or resolved.get("policy_pack_id"),
            "execution_mode": body.get("execution_mode"),
            "resolved": resolved,
            "note": "check is resolve + contract preview; POST omitted in dry_run",
        }

    def execute(
        self,
        *,
        factory_id: str,
        input: dict[str, Any] | None = None,
        tenant: str = "",
        work_order_id: str = "",
    ) -> dict[str, Any]:
        resolved = _resolve_local(factory_id, tenant, input or {})
        if not resolved.get("ok"):
            return resolved
        route = str(resolved.get("api_route") or "")
        body = {**resolved.get("body", {}), "input": input or {}}
        if work_order_id:
            body["work_order_id"] = work_order_id
        url = f"{self.hub_url}{route}"
        return http_json(method="POST", url=url, body=body, api_key=self.api_key, timeout=300)

    def audit(self, *, job_id: str) -> dict[str, Any]:
        url = f"{self.hub_url}/api/fbe/ledger/v1?job_id={job_id}"
        return http_json(method="GET", url=url, api_key=self.api_key)

    def sign(self, receipt: dict[str, Any]) -> dict[str, Any]:
        raw = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return {
            "ok": True,
            "sha256": digest,
            "kernel_hash": receipt.get("kernel_hash") or (receipt.get("execution_receipt") or {}).get("kernel_hash"),
            "job_id": receipt.get("job_id") or (receipt.get("execution_receipt") or {}).get("job_id"),
            "policy_pack": receipt.get("policy_pack") or (receipt.get("execution_receipt") or {}).get("policy_pack"),
        }

    def get_factory(self, factory_id: str) -> dict[str, Any] | None:
        if self.hub_url.startswith("http"):
            row = self.catalog()
            for item in row.get("items") or []:
                if item.get("factory_id") == factory_id:
                    return item
        return get_factory(factory_id)
