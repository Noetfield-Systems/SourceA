#!/usr/bin/env python3
"""E2E governance chain debug — writes NDJSON to .cursor/debug-baabac.log."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
DEBUG_LOG = ROOT / ".cursor" / "debug-baabac.log"
BASE = "http://127.0.0.1:13020"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _log(*, hypothesis_id: str, location: str, message: str, data: dict) -> None:
    # #region agent log
    row = {
        "sessionId": "baabac",
        "runId": "post-fix",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
    with DEBUG_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    # #endregion


def _run(cmd: list[str], *, timeout: int = 120) -> dict:
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        out = (proc.stdout or "") + (proc.stderr or "")
        row: dict = {"exit": proc.returncode, "ok": proc.returncode == 0}
        if out.strip():
            try:
                row["json"] = json.loads(out[out.find("{") :])
            except json.JSONDecodeError:
                row["tail"] = out.strip()[-240:]
        return row
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit": -1, "tail": "timeout"}
    except OSError as exc:
        return {"ok": False, "exit": -1, "tail": str(exc)}


def probe_hub() -> dict:
    try:
        with urllib.request.urlopen(f"{BASE}/health", timeout=5) as r:
            health = json.loads(r.read().decode())
        with urllib.request.urlopen(f"{BASE}/api/worker-hub/v1", timeout=90) as r:
            hub = json.loads(r.read().decode())
        ok = bool(health.get("ok")) and bool(hub.get("ok"))
        _log(
            hypothesis_id="H1",
            location="debug_e2e_governance_chain_v1.py:probe_hub",
            message="hub health + worker-hub payload",
            data={"ok": ok, "health": health, "hub_schema": hub.get("schema")},
        )
        return {"id": "hub", "ok": ok}
    except Exception as exc:
        _log(
            hypothesis_id="H1",
            location="debug_e2e_governance_chain_v1.py:probe_hub",
            message="hub probe failed",
            data={"error": str(exc)[:200]},
        )
        return {"id": "hub", "ok": False, "error": str(exc)}


def _script_probe_ok(row: dict) -> bool:
    """Exit 1 with valid JSON = honest RED probes (better-loop / nerve), not a crash."""
    if row.get("exit") == 0:
        return True
    j = row.get("json") or {}
    if row.get("exit") == 1 and isinstance(j, dict) and j:
        return bool(
            j.get("ship_checks")
            or j.get("better_loop_line")
            or j.get("nerve_system_line")
            or j.get("ship_gates")
        )
    return False


def probe_staleness() -> dict:
    pulse = _run([sys.executable, str(SCRIPTS / "better_loop_pulse_v1.py"), "--json"])
    nerve = _run([sys.executable, str(SCRIPTS / "agent_nerve_system_v1.py"), "--json"])
    comm = _run([sys.executable, str(SCRIPTS / "commercial_command_pulse_v1.py"), "--json"])

    bl = _read_json(SINA / "better-loop-pulse-receipt-v1.json")
    nerve_row = _read_json(SINA / "agent-nerve-system-receipt-v1.json")
    ship = nerve_row.get("ship_gates") or {}
    chk = {c.get("id"): c for c in (bl.get("ship_checks") or [])}

    sys.path.insert(0, str(SCRIPTS))
    from execution_plane_honesty_v1 import assess_commercial_readiness  # noqa: WPS433

    comm_assess = assess_commercial_readiness()
    gates = comm_assess.get("gates") or {}
    pulse_sina = bool((chk.get("w3_sina_read") or {}).get("ok"))
    assess_sina = bool(gates.get("w3_sina_read"))
    sina_aligned = assess_sina == pulse_sina
    data = {
        "pulse_ok": _script_probe_ok(pulse),
        "nerve_ok": _script_probe_ok(nerve),
        "comm_pulse_ok": comm.get("exit") == 0,
        "nerve_at": nerve_row.get("at"),
        "pulse_at": bl.get("at"),
        "nerve_w3_sina_read_pass": ship.get("w3_sina_read_pass"),
        "pulse_w3_sina_read_ok": (chk.get("w3_sina_read") or {}).get("ok"),
        "pulse_w3_mail_from_ok": (chk.get("w3_mail_from") or {}).get("ok"),
        "pulse_w3_send_ready_ok": (chk.get("w3_send_ready") or {}).get("ok"),
        "nerve_w3_mail_from_configured": ship.get("w3_mail_from_configured"),
        "nerve_w3_send_ready": ship.get("w3_send_ready"),
        "prefer_pulse": comm_assess.get("prefer_pulse"),
        "gates": comm_assess.get("gates"),
        "commercial_line": comm_assess.get("commercial_readiness_line"),
        "commercial_red_count": bl.get("commercial_red_count"),
        "system_red_count": bl.get("system_red_count"),
    }
    _log(
        hypothesis_id="H2",
        location="debug_e2e_governance_chain_v1.py:probe_staleness",
        message="nerve vs pulse commercial gates",
        data=data,
    )
    ok = (
        _script_probe_ok(pulse)
        and _script_probe_ok(nerve)
        and sina_aligned
        and bool(gates.get("w3_oqg"))
        and assess_sina
    )
    return {"id": "staleness", "ok": ok, "sina_aligned": sina_aligned, **data}


def probe_validators() -> dict:
    hub_val = _run(["bash", str(SCRIPTS / "validate-super-fast-hub-v1.sh")], timeout=120)
    _log(
        hypothesis_id="H3",
        location="debug_e2e_governance_chain_v1.py:probe_validators",
        message="super-fast hub validator",
        data={"ok": hub_val.get("ok"), "exit": hub_val.get("exit")},
    )
    return {"id": "validators", "ok": bool(hub_val.get("ok"))}


def probe_bootstrap() -> dict:
    val = _run(["bash", str(SCRIPTS / "validate-cursor-bootstrap-v1.sh")], timeout=120)
    _log(
        hypothesis_id="H4",
        location="debug_e2e_governance_chain_v1.py:probe_bootstrap",
        message="cursor corporate bootstrap pack",
        data={"ok": val.get("ok"), "exit": val.get("exit")},
    )
    return {"id": "bootstrap", "ok": bool(val.get("ok"))}


def run_e2e() -> dict:
    probes = [probe_hub(), probe_staleness(), probe_validators(), probe_bootstrap()]
    ok = all(p.get("ok") for p in probes)
    row = {
        "schema": "debug-e2e-governance-chain-v1",
        "ok": ok,
        "at": _now(),
        "probes": probes,
        "debug_log": str(DEBUG_LOG),
    }
    _log(
        hypothesis_id="E2E",
        location="debug_e2e_governance_chain_v1.py:run_e2e",
        message="e2e_complete",
        data={"ok": ok, "probe_ids": [p.get("id") for p in probes]},
    )
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_e2e()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"{'OK' if row.get('ok') else 'FAIL'}: debug-e2e-governance-chain · probes={len(row.get('probes') or [])}")
        for p in row.get("probes") or []:
            print(f"  · {p.get('id')}: {'PASS' if p.get('ok') else 'FAIL'}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
