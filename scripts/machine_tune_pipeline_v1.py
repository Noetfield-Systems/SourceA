#!/usr/bin/env python3
"""P2 Machine Tune (Tune-up) — routine test ladder + heal. Medium · shorter than Forge.

Trigger: tune · Escalates to Forge if critical_count > 0
Receipt: ~/.sina/machine-tune-receipt-v1.json
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
RECEIPT = SINA / "machine-tune-receipt-v1.json"
QUARANTINE = SINA / "machine-forge-quarantine-v1.json"
SCHEMA = "machine-tune-receipt-v1"

sys.path.insert(0, str(SCRIPTS))
from machine_three_pipelines_lib_v1 import TIERS, critical_count, load_json, now_iso  # noqa: E402


def _run(cmd: list[str], *, timeout: int = 180) -> dict:
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        out = (proc.stdout or "") + (proc.stderr or "")
        j = {}
        if "{" in out:
            try:
                j = json.loads(out[out.find("{") :])
            except json.JSONDecodeError:
                j = {}
        return {"ok": proc.returncode == 0, "exit": proc.returncode, "json": j}
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit": -1}


def run_tune(*, ladder_tier: str = "daily", role: str = "worker") -> dict:
    py = sys.executable
    meta = TIERS["tune"]
    steps: list[dict] = []

    cal = load_json(SINA / "machine-calibrate-receipt-v1.json")
    steps.append(
        {
            "id": "T0",
            "step": "calibrate_certificate",
            "ok": cal.get("calibrate_complete") or cal.get("ok"),
            "note": "Run calibrate first for new machine work",
        }
    )

    from machine_test_ladder_run_v1 import run_ladder  # noqa: WPS433

    ladder = run_ladder(tier=ladder_tier, role=role)
    steps.append(
        {
            "id": "T1",
            "step": f"test_ladder_{ladder_tier}",
            "ok": ladder.get("ok"),
            "passed": ladder.get("steps_passed"),
            "total": ladder.get("steps_total"),
        }
    )

    heal = _run([py, str(SCRIPTS / "hub_dual_heal_v1.py"), "--json"], timeout=90)
    steps.append({"id": "T2", "step": "dual_hub_heal", "ok": heal.get("ok")})

    baseline = _run([py, str(SCRIPTS / "machine_upgrade_baseline_v1.py"), "--tag", "current", "--json"], timeout=60)
    steps.append({"id": "T3", "step": "baseline_snapshot", "ok": baseline.get("ok")})

    crit = critical_count()
    steps.append({"id": "T4", "step": "critical_bugs_check", "ok": crit == 0, "critical_count": crit})

    escalate_forge = crit > 0
    core = [s for s in steps if s["step"] not in ("calibrate_certificate", "critical_bugs_check")]
    ok = all(s.get("ok") for s in core) and cal.get("ok", cal.get("calibrate_complete")) and not escalate_forge

    discharge = f"Ladder {ladder_tier} green · factory may run · read machine-test-ladder-receipt"
    row = {
        "schema": SCHEMA,
        "ok": ok,
        "at": now_iso(),
        **meta,
        "shorter_than": "forge",
        "ladder_tier": ladder_tier,
        "role": role,
        "steps": steps,
        "escalate_forge": escalate_forge,
        "discharge_note": discharge if ok else "ESCALATE TO FORGE — critical bugs or ladder fail",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if escalate_forge:
        QUARANTINE.write_text(
            json.dumps({"active": True, "reason": "tune_escalation", "at": now_iso(), "critical_count": crit}, indent=2) + "\n",
            encoding="utf-8",
        )
    elif QUARANTINE.is_file():
        QUARANTINE.unlink()
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="P2 Machine Tune")
    ap.add_argument("--ladder-tier", default="daily", choices=["daily", "3day"])
    ap.add_argument("--role", default="worker")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_tune(ladder_tier=args.ladder_tier, role=args.role)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"TUNE ok={row['ok']} escalate_forge={row['escalate_forge']}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
