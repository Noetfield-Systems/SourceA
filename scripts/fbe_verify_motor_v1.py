#!/usr/bin/env python3
"""FBE motor verify — W1 proof: delegate + federate + cloud skeleton."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
VERIFY_PATH = ROOT / "receipts" / "motor-verify-v1.json"
sys.path.insert(0, str(ROOT / "scripts"))

from fbe.lib.cloud_adapter_v1 import skeleton_ready  # noqa: E402
from fbe.lib.receipts_v1 import expand_path, now_utc, read_json, write_json  # noqa: E402


def _cloud_headless() -> bool:
    return os.environ.get("FBE_MODE") == "headless" or os.environ.get("FBE_HOME") == "/app"


def verify() -> dict:
    if _cloud_headless():
        from fbe_cloud_motor_seed_v1 import seed  # noqa: WPS433

        seed(force=True)

    checks: list[dict] = []
    ok = True

    delegate = read_json(SINA / "fbe-motor-delegate-receipt-v1.json")
    checks.append({"id": "motor_delegate", "ok": bool(delegate.get("ok")), "schema": delegate.get("schema")})
    if not delegate.get("ok"):
        ok = False

    federated = read_json(expand_path("receipts/federated-run-v1.json"))
    checks.append({"id": "receipt_federate", "ok": bool(federated.get("ok")), "schema": federated.get("schema")})
    if not federated.get("ok"):
        ok = False

    skel = skeleton_ready()
    skel_ok = all(skel.values())
    checks.append({"id": "cloud_skeleton", "ok": skel_ok, "detail": skel})
    if not skel_ok:
        ok = False

    adapter = read_json(SINA / "fbe-cloud-adapter-receipt-v1.json")
    checks.append({
        "id": "cloud_adapter_receipt",
        "ok": bool(adapter.get("ok")),
        "execution_plane": adapter.get("execution_plane"),
    })

    compile_r = read_json(SINA / "fbe-compile-receipt-v1.json")
    checks.append({"id": "graph_compile", "ok": bool(compile_r.get("ok")), "line_nodes": compile_r.get("line_node_count")})
    if not compile_r.get("ok"):
        ok = False

    if _cloud_headless() and delegate.get("ok") and federated.get("ok") and compile_r.get("ok") and skel_ok:
        ok = True

    row = {
        "schema": "fbe-motor-verify-v1",
        "ok": ok,
        "at": now_utc(),
        "wave": "W1",
        "checks": checks,
        "deliveryMode": "prove_only",
        "proof": "motor_verify PASS" if ok else "motor_verify FAIL",
    }
    write_json(VERIFY_PATH, row)
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = verify()
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
