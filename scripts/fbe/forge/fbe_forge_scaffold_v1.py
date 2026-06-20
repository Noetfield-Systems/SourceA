#!/usr/bin/env python3
"""FORGE scaffold — honest app scaffold subgraph stub."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fbe_forge_lib_v1 import run_stub_step, wrapper_main


def scaffold(*, bay_slug: str, tenant: str) -> dict:
    return run_stub_step(
        node_id="forge-scaffold-v1",
        bay_slug=bay_slug,
        tenant=tenant,
        line="refinery",
        mode="app_scaffold_stub",
        extra={
            "artifact_class": "governed_app_manifest",
            "note": "App scaffold subgraph — prove_only stub until FORGE SKU pipeline wired",
        },
    )


if __name__ == "__main__":
    raise SystemExit(wrapper_main(scaffold))
