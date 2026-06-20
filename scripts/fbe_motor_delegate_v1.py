#!/usr/bin/env python3
"""FBE motor delegate — runs Line C motor tiers via graph SSOT."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SINA = Path.home() / ".sina"
GRAPH_PATH = DATA / "fbe_node_graph_v1.json"
RECEIPT_PATH = SINA / "fbe-motor-delegate-receipt-v1.json"
PY = sys.executable

MOTOR_TIERS = ("T0_motor_safety", "T1_motor_truth", "T1_motor_extra")
FBE_PROVE_SKIP = frozenset({
    "fbe_motor_session_gate_v1",
    "fbe_motor_zero_drift_v1",
    "fbe_motor_sascip_v1",
    "fbe_motor_pre_write_v1",
})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _run_cmd(cmd: list[str], *, timeout: int = 120) -> dict[str, Any]:
    t0 = time.monotonic()
    if cmd and cmd[0] == "python3":
        cmd = [PY, *cmd[1:]]
    try:
        out = subprocess.check_output(cmd, cwd=str(ROOT), stderr=subprocess.STDOUT, text=True, timeout=timeout)
        code = 0
    except subprocess.CalledProcessError as e:
        out = e.output or ""
        code = e.returncode
    except subprocess.TimeoutExpired as e:
        out = (e.output or "") + "\nTIMEOUT"
        code = 124
    return {
        "ok": code == 0,
        "exit": code,
        "elapsed_sec": round(time.monotonic() - t0, 2),
        "tail": out.strip()[-400:],
    }


def delegate(*, tier_filter: str | None = None, skip_federate: bool = False, fbe_prove: bool = False, force: bool = False) -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from mac_focus_freeze_v1 import is_focus_freeze, skip_receipt  # noqa: WPS433

    if is_focus_freeze() and not force:
        row = skip_receipt(
            schema="fbe-motor-delegate-receipt-v1",
            script="fbe_motor_delegate_v1.py",
            note="FBE motor deferred — run on cloud worker (--force to override)",
        )
        row["wave"] = "W1"
        row["mode"] = "motor_delegate"
        row["fbe_prove"] = fbe_prove
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    if fbe_prove:
        for flag in (SINA / "agent-cancel-v1.flag", SINA / "mac-health-emergency-active-v1.flag"):
            if flag.is_file():
                try:
                    flag.unlink(missing_ok=True)
                except OSError:
                    pass

    graph = _read_json(GRAPH_PATH)
    if graph.get("schema") != "fbe-node-graph-v1":
        return {"ok": False, "error": f"bad graph {GRAPH_PATH}"}

    tier_rows: list[dict] = []
    ok = True
    t0 = time.monotonic()

    for tier in graph.get("tiers") or []:
        tid = str(tier.get("id") or "")
        if tier_filter and tid != tier_filter:
            continue
        if tid not in MOTOR_TIERS and not tier_filter:
            continue
        nodes = tier.get("nodes") or []
        node_results = []
        for node in nodes:
            nid = str(node.get("id") or "")
            if skip_federate and nid == "fbe_motor_receipt_federate_v1":
                continue
            if fbe_prove and nid in FBE_PROVE_SKIP:
                node_results.append({"id": nid, "ok": True, "skipped": True, "mode": "fbe_prove"})
                continue
            if fbe_prove and not node.get("required", True):
                node_results.append({"id": nid, "ok": True, "skipped": True, "mode": "fbe_prove_optional"})
                continue
            cmd = node.get("cmd") or []
            if not cmd:
                node_results.append({"id": nid, "ok": False, "error": "empty cmd"})
                if node.get("required", True):
                    ok = False
                continue
            row = _run_cmd(cmd)
            row["id"] = nid
            row["required"] = bool(node.get("required", True))
            node_results.append(row)
            if row["required"] and not row["ok"]:
                ok = False
        tier_rows.append({"tier": tid, "ok": all(r.get("ok") for r in node_results if r.get("required")), "nodes": node_results})

    receipt = {
        "schema": "fbe-motor-delegate-receipt-v1",
        "ok": ok,
        "at": _now(),
        "elapsed_sec": round(time.monotonic() - t0, 2),
        "tiers": tier_rows,
        "wave": "W1",
        "mode": "motor_delegate",
        "fbe_prove": fbe_prove,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="FBE motor delegate — Line C tiers")
    ap.add_argument("--tier")
    ap.add_argument("--skip-federate", action="store_true")
    ap.add_argument("--fbe-prove", action="store_true", help="Skip governance session/zero-drift nodes for FBE prove chain")
    ap.add_argument("--force", action="store_true", help="Run even when Mac focus freeze flag is set")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = delegate(tier_filter=args.tier, skip_federate=args.skip_federate, fbe_prove=args.fbe_prove, force=args.force)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
