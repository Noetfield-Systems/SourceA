#!/usr/bin/env python3
"""Platform catalog for Chat Unify enterprise home."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "chat-unify-platform-catalog-v1.json"


def _repo_root() -> Path:
    import os

    env = os.environ.get("SINA_SOURCE_A", "").strip()
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    for candidate in (
        Path.home() / "Desktop" / "SourceA",
        Path(__file__).resolve().parents[1],
    ):
        if (candidate / "data" / "chat-unify-platform-catalog-v1.json").is_file():
            return candidate
    return Path(__file__).resolve().parents[1]


def load_catalog() -> dict[str, Any]:
    path = _repo_root() / "data" / "chat-unify-platform-catalog-v1.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def catalog_payload(*, port: int = 13023) -> dict[str, Any]:
    from chat_unify_integrations_v1 import integrations_live_payload  # noqa: WPS433

    catalog = load_catalog()
    live = integrations_live_payload(port=port)
    apps = []
    for app in catalog.get("apps") or []:
        row = dict(app)
        p = row.get("port")
        if p and isinstance(p, int):
            probe = (live.get("mesh") or {}).get(
                "cloud_workers" if p == 13027 else "n8n" if p == 13026 else "chat_unify" if p == 13023 else None
            )
            if p == 13023:
                probe = live.get("mesh", {}).get("chat_unify")
            elif p == 13027:
                probe = live.get("mesh", {}).get("cloud_workers")
            elif p == 13026:
                probe = live.get("mesh", {}).get("n8n")
            else:
                probe = _probe_port(p)
            row["status"] = "live" if probe and probe.get("ok") else "offline"
        else:
            row["status"] = "web"
        apps.append(row)
    return {
        "ok": True,
        "catalog": catalog,
        "apps_live": apps,
        "integrations": {
            "lanes_live": sum(1 for x in live.get("lanes") or [] if x.get("status") == "live"),
            "lanes_total": len(live.get("lanes") or []),
            "ui_version": live.get("ui_version"),
        },
    }


def _probe_port(port: int) -> dict[str, Any]:
    import urllib.error
    import urllib.request

    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1.0) as resp:
            return {"ok": 200 <= resp.status < 300}
    except (urllib.error.URLError, OSError, TimeoutError):
        return {"ok": False}
