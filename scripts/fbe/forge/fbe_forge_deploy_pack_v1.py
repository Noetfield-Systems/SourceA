#!/usr/bin/env python3
"""FORGE deploy pack — deploy-only assembly manifest."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fbe_forge_lib_v1 import run_stub_step, wrapper_main


def deploy_pack(*, bay_slug: str, tenant: str) -> dict:
    wo = {}
    try:
        import sys
        from pathlib import Path as _P

        sys.path.insert(0, str(_P(__file__).resolve().parents[3] / "scripts"))
        from forge_mvp_lib_v1 import load_work_order  # noqa: WPS433

        wo = load_work_order()
    except Exception:
        wo = {}
    preview_url = wo.get("preview_url")
    mock_only = not bool(preview_url)
    if mock_only:
        preview_url = f"https://mock-forge-preview.local/{tenant}/{wo.get('plan_id') or 'demo'}"
    manifest = {
        "schema": "fbe-forge-deploy-manifest-v1",
        "artifact": "controlled_app_receipt_pack",
        "ship_gate": "G0-G3",
        "deliveryMode": "prove_only",
        "preview_url": preview_url,
        "mock_only": mock_only,
        "work_order_id": wo.get("plan_id"),
        "stack": wo.get("stack"),
        "competitor": wo.get("competitor"),
    }
    return run_stub_step(
        node_id="forge-deploy-pack-v1",
        bay_slug=bay_slug,
        tenant=tenant,
        line="assembly",
        mode="deploy_only",
        extra={"manifest": manifest, "note": "Deploy-only assembly — prove_only artifact manifest"},
    )


if __name__ == "__main__":
    raise SystemExit(wrapper_main(deploy_pack))
