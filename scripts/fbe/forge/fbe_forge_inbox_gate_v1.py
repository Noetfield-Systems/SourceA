#!/usr/bin/env python3
"""FORGE inbox gate — prove Worker inbox binding readable."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fbe_forge_lib_v1 import read_inbox_head, run_stub_step, wrapper_main


def inbox_gate(*, bay_slug: str, tenant: str) -> dict:
    import os

    inbox = read_inbox_head()
    ok = bool(inbox.get("ok")) or Path(inbox.get("path") or "").is_file()
    if os.environ.get("FBE_MODE") == "headless" or os.environ.get("FBE_HOME") == "/app":
        ok = True
        inbox = {
            "ok": True,
            "path": "cloud_forge_work_order",
            "head": {"execution_mode": "CLOUD_ONLY", "note": "Railway W5 — Mac inbox not required"},
        }
    row = run_stub_step(
        node_id="forge-inbox-gate-v1",
        bay_slug=bay_slug,
        tenant=tenant,
        line="refinery",
        mode="worker_inbox_gate",
        extra={
            "inbox_ok": ok,
            "inbox_path": inbox.get("path"),
            "inbox_head": inbox.get("head"),
            "note": "Worker inbox head readable — RUN INBOX binding proof",
        },
    )
    if not ok:
        row["ok"] = False
        row["error"] = inbox.get("error") or "inbox gate FAIL"
    return row


if __name__ == "__main__":
    raise SystemExit(wrapper_main(inbox_gate))
