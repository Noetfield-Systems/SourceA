#!/usr/bin/env python3
"""Mac Health UI contract — founder glance (v3.3+) for /health."""
from __future__ import annotations

from mac_health_version_v1 import (
    CSS_CACHE_BUSTER,
    MAC_HEALTH_VERSION,
    UI_CONTRACT_REL,
    UI_LAW_DOC,
    UI_PRIMARY_CTA,
    UI_SURFACE_ID,
    UI_TAB_COUNT,
    UI_VERSION_TAG,
)


def build_ui_contract(*, port: int = 13024):
    return {
        "schema": "founder-glance-ui-contract-v1",
        "app_id": "mac_health",
        "surface_id": "mac_health",
        "ui_mode": UI_SURFACE_ID,
        "label": "Mac Health Guard",
        "version": MAC_HEALTH_VERSION,
        "version_tag": UI_VERSION_TAG,
        "css_buster": CSS_CACHE_BUSTER,
        "tab_count": UI_TAB_COUNT,
        "primary_cta": UI_PRIMARY_CTA,
        "primary_button_id": "btn-heal",
        "more_disclosure_id": "panel-more",
        "url": f"http://127.0.0.1:{port}/",
        "law_doc": UI_LAW_DOC,
        "contract_path": UI_CONTRACT_REL,
    }


def load_contract():
    from founder_glance_cockpit_v1 import APPS, ROOT
    import json

    rel = APPS["mac_health"]["contract"]
    path = ROOT / rel
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def main() -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Mac Health founder-glance ui_contract")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = build_ui_contract()
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"{payload['ui_mode']} v{payload['version']} · {payload['primary_cta']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
