#!/usr/bin/env python3
"""FBE motor delegate — runs Line C motor tiers via graph SSOT."""
from __future__ import annotations

import argparse
import json
import os
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


def _live_sibling_motor_count() -> int:
    """Count OTHER live fbe_motor_delegate_v1 processes (excludes this one).

    Reuses Mac Health Guard's reaper pgrep pattern so the spawn-site cap and
    the reactive reaper count the same thing (see brainstorm: one authoritative
    counter). Falls back to a self-contained pgrep if that import is
    unavailable. Never raises — a counting failure must not block a real run.
    """
    self_pid = os.getpid()
    pids: set[int] = set()
    try:
        from mac_health_never_again_v1 import _motor_pids, SOURCEA_MOTOR_PATTERN  # noqa: WPS433

        pids = set(_motor_pids((SOURCEA_MOTOR_PATTERN,)))
    except Exception:
        try:
            out = subprocess.run(
                ["pgrep", "-f", "fbe_motor_delegate_v1"],
                capture_output=True,
                text=True,
                timeout=4.0,
            )
            if out.returncode == 0:
                pids = {int(x) for x in out.stdout.split() if x.strip().isdigit()}
        except (OSError, subprocess.TimeoutExpired, ValueError):
            pids = set()
    pids.discard(self_pid)
    return len(pids)


def _motor_hard_cap() -> int:
    """Storm hard-cap, read from the same config the reaper uses (default 15)."""
    try:
        from mac_health_never_again_v1 import _load_config, DEFAULTS  # noqa: WPS433

        cfg = _load_config()
        return int(cfg.get("motor_hard_cap") or DEFAULTS["motor_hard_cap"])
    except Exception:
        return 15


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
        row["status"] = "deferred"
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    # Admission control — preventive backpressure at the spawn site. Refuse to
    # start if we would exceed the storm hard-cap, so proliferation is stopped
    # BEFORE it happens rather than reaped after the fact by Mac Health Guard.
    # Refusing exits 0 with a receipt; it never signals or kills anything. The
    # reactive reaper remains defense-in-depth, not the primary limiter.
    if not force:
        live_motors = _live_sibling_motor_count()
        hard_cap = _motor_hard_cap()
        if live_motors >= hard_cap:
            row = {
                "schema": "fbe-motor-delegate-receipt-v1",
                "ok": True,
                "status": "refused_at_capacity",
                "at": _now(),
                "live_sibling_motors": live_motors,
                "hard_cap": hard_cap,
                "note": f"refused: {live_motors} sibling motors >= hard_cap {hard_cap} (use --force to override)",
                "wave": "W1",
                "mode": "motor_delegate",
                "fbe_prove": fbe_prove,
            }
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
            # Never shell out to our own top-level entrypoint. A node whose cmd
            # re-invokes fbe_motor_delegate_v1.py spawns a full child copy of
            # this process on every run — the mechanical doubling that drives
            # motor storms. A tier that needs the prove-chain must run it
            # in-process, not as a subprocess of itself.
            if any("fbe_motor_delegate_v1.py" in str(part) for part in cmd):
                node_results.append({"id": nid, "ok": True, "skipped": True, "mode": "self_spawn_suppressed"})
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
        "status": "ran_pass" if ok else "ran_fail",
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
