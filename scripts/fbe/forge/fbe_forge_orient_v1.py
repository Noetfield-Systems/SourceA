#!/usr/bin/env python3
"""FORGE orient — app spec + FORGE SKU posture."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fbe_forge_lib_v1 import run_stub_step, wrapper_main


def orient(*, bay_slug: str, tenant: str) -> dict:
    return run_stub_step(
        node_id="forge-orient-v1",
        bay_slug=bay_slug,
        tenant=tenant,
        line="refinery",
        mode="forge_orient",
        extra={
            "pattern": "FORGE_SKU_worker_inbox_no_web_clone",
            "note": "Controlled app factory orient — no web clone",
        },
    )


if __name__ == "__main__":
    raise SystemExit(wrapper_main(orient))
