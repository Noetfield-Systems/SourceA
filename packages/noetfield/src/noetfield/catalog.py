"""Catalog helpers — list factories from Hub."""
from __future__ import annotations

from typing import Any

from noetfield.hub_client import http_json, load_config


def list_factories(*, tier: str = "") -> dict[str, Any]:
    cfg = load_config()
    url = f"{cfg['hub_url']}/api/fbe/catalog/v1"
    if tier:
        url += f"?tier={tier}"
    return http_json(method="GET", url=url, api_key=cfg.get("api_key", ""))


def get_factory(factory_id: str) -> dict[str, Any] | None:
    row = list_factories()
    for item in row.get("items") or []:
        if item.get("factory_id") == factory_id:
            return item
    return None
