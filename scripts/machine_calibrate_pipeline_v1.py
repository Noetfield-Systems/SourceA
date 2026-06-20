#!/usr/bin/env python3
"""P1 Machine Calibrate (Blueprint) — map machines · validators · receipts. Read-only.

Trigger: calibrate · Tier 1 SHORT
Receipt: ~/.sina/machine-calibrate-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "machine-calibrate-receipt-v1.json"
PACK = SINA / "machine-calibrate-reading-pack-v1.json"
SCHEMA = "machine-calibrate-receipt-v1"

sys.path.insert(0, str(SCRIPTS))
from machine_three_pipelines_lib_v1 import CALIBRATE_READS, TIERS, UPGRADE_BOARD, file_station, now_iso, UNIFIED_LAW  # noqa: E402


def _run_json(cmd: list[str], *, timeout: int = 90) -> dict:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, cwd=str(ROOT), timeout=timeout)
        i = out.find("{")
        return json.loads(out[i:]) if i >= 0 else {}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}


def run_calibrate(*, scope: str = "whole") -> dict:
    meta = TIERS["calibrate"]
    stations: list[dict] = []
    for sid, name, rel in CALIBRATE_READS:
        st = file_station(sid, name, rel)
        st["kind"] = "read"
        stations.append(st)

    catalog = _run_json([sys.executable, str(SCRIPTS / "ecosystem_master_catalog_v1.py"), "--json"])
    stations.append(
        {
            "id": "C8",
            "name": "ecosystem_catalog",
            "ok": bool(catalog.get("ok", True)),
            "machines": catalog.get("machine_count") or catalog.get("machines_count"),
        }
    )

    key_scripts = (
        "machine_test_ladder_run_v1.py",
        "machine_upgrade_baseline_v1.py",
        "agent_three_pipelines_router_v1.py",
        "machine_three_pipelines_router_v1.py",
    )
    scripts_ok = all((SCRIPTS / s).is_file() for s in key_scripts)
    stations.append({"id": "C9", "name": "refinement_runners", "ok": scripts_ok, "scripts": list(key_scripts)})

    pack = {
        "schema": "machine-calibrate-reading-pack-v1",
        "at": now_iso(),
        "scope": scope,
        "reads": [{"id": s["id"], "path": s["path"]} for s in stations if s.get("kind") == "read"],
        "upgrade_board": list(UPGRADE_BOARD),
        "rule": "Machines write receipts · validators prove receipts · tune daily · forge before ship",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    PACK.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    stations.append({"id": "C10", "name": "reading_pack", "ok": PACK.is_file()})

    ok = all(s.get("ok") for s in stations)
    row = {
        "schema": SCHEMA,
        "ok": ok,
        "at": now_iso(),
        **meta,
        "scope": scope,
        "calibrate_complete": ok,
        "stations": stations,
        "reading_pack": str(PACK),
        "unified_law": UNIFIED_LAW,
        "next": "Say tune for routine health · forge before any upgrade ship",
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="P1 Machine Calibrate")
    ap.add_argument("--scope", default="whole", choices=["whole", "single"])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_calibrate(scope=args.scope)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"CALIBRATE ok={row['ok']} stations={len(row['stations'])}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
