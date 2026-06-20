#!/usr/bin/env python3
"""Founder Glance cockpit apps — single SSOT for all Mac standalone mini apps."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_REL = "data/founder-glance-cockpit-apps-v1.json"
LAW_DOC = "brain-os/law/enforcement/SINA_FOUNDER_GLANCE_COCKPIT_APPS_LOCKED_v1.md"

APPS: dict[str, dict[str, Any]] = {
    "mac_health": {
        "label": "Mac Health Guard",
        "port": 13024,
        "version": "3.3.0",
        "primary_cta": "Relieve pressure",
        "primary_button_id": "btn-heal",
        "url": "http://127.0.0.1:13024/",
        "standalone_root": "scripts/mac-health-standalone",
        "contract": "data/mac-health-founder-glance-ui-contract-v1.json",
        "validator": "scripts/validate-mac-health-founder-glance-v1.sh",
    },
    "apple_health": {
        "label": "Apple Health",
        "port": 13025,
        "version": "2.0.0",
        "primary_cta": "Open Health app",
        "primary_button_id": "btn-open-health",
        "url": "http://127.0.0.1:13025/",
        "standalone_root": "scripts/apple-health-standalone",
        "contract": "data/apple-health-founder-glance-ui-contract-v1.json",
        "validator": "scripts/validate-founder-glance-cockpit-apps-v1.sh",
    },
    "chat_unify": {
        "label": "Chat Unify",
        "port": 13023,
        "version": "1.4.0",
        "primary_cta": "Merge all & scan",
        "primary_button_id": "btn-unify-all",
        "url": "http://127.0.0.1:13023/",
        "standalone_root": "scripts/chat-unify-standalone",
        "contract": "data/chat-unify-founder-glance-ui-contract-v1.json",
        "validator": "scripts/validate-founder-glance-cockpit-apps-v1.sh",
    },
    "n8n_integration": {
        "label": "N8N Integration",
        "port": 13026,
        "version": None,
        "primary_cta": "Capture intelligence",
        "primary_button_id": "btn-primary",
        "url": "http://127.0.0.1:13026/",
        "standalone_root": "scripts/n8n-standalone",
        "contract": "data/n8n-integration-founder-glance-ui-contract-v1.json",
        "validator": "scripts/validate-founder-glance-cockpit-apps-v1.sh",
    },
}


def registry_path() -> Path:
    return ROOT / REGISTRY_REL


def load_registry() -> dict[str, Any]:
    path = registry_path()
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"schema": "founder-glance-cockpit-apps-v1", "apps": APPS}


def app_version(app_id: str) -> str:
    cfg = APPS.get(app_id) or {}
    ver = cfg.get("version")
    if ver:
        return str(ver)
    if app_id == "n8n_integration":
        try:
            from n8n_integration_core import VERSION  # noqa: WPS433

            return str(VERSION)
        except Exception:
            return "1.1.0"
    return "1.0.0"


def build_ui_contract(app_id: str, *, port: int | None = None) -> dict[str, Any]:
    cfg = APPS.get(app_id) or {}
    p = port or int(cfg.get("port") or 0)
    contract_rel = cfg.get("contract") or ""
    contract: dict[str, Any] = {}
    contract_path = ROOT / contract_rel if contract_rel else None
    if contract_path and contract_path.is_file():
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    return {
        "schema": "founder-glance-ui-contract-v1",
        "app_id": app_id,
        "surface_id": app_id,
        "ui_mode": "founder_glance",
        "label": cfg.get("label") or app_id,
        "version": app_version(app_id),
        "tab_count": 0,
        "primary_cta": cfg.get("primary_cta") or "",
        "primary_button_id": cfg.get("primary_button_id") or "",
        "url": f"http://127.0.0.1:{p}/" if p else cfg.get("url", ""),
        "law_doc": LAW_DOC,
        "contract_path": contract_rel,
        "founder_rules": contract.get("founder_rules") or [
            "zero_tabs",
            "one_primary_cta",
            "auto_default",
            "advanced_in_more_disclosure",
        ],
        "stat_tiles": contract.get("stat_tiles") or [],
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Founder glance cockpit SSOT")
    parser.add_argument("--app", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.app:
        payload = build_ui_contract(args.app)
    else:
        payload = {
            "schema": "founder-glance-cockpit-apps-v1",
            "law_doc": LAW_DOC,
            "registry": REGISTRY_REL,
            "apps": {aid: build_ui_contract(aid) for aid in APPS},
        }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"founder_glance_cockpit · {len(APPS)} apps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
