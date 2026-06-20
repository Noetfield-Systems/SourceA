#!/usr/bin/env python3
"""FORGE deploy pack — deploy-only assembly manifest."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fbe_forge_lib_v1 import run_stub_step, wrapper_main


def deploy_pack(*, bay_slug: str, tenant: str) -> dict:
    manifest = {
        "schema": "fbe-forge-deploy-manifest-v1",
        "artifact": "governed_app_receipt_pack",
        "ship_gate": "G0-G3",
        "deliveryMode": "prove_only",
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
