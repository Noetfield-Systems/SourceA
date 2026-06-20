#!/usr/bin/env python3
"""P3 Machine Forge — full upgrade gauntlet · before/after baseline · passport.

Trigger: forge · tune escalation · pre-ship upgrade
Receipt: ~/.sina/machine-forge-receipt-v1.json
Passport: ~/.sina/machine-forge-passport-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "machine-forge-receipt-v1.json"
PASSPORT = SINA / "machine-forge-passport-v1.json"
QUARANTINE = SINA / "machine-forge-quarantine-v1.json"
ATTEST = SINA / "machine-forge-proven-lines-v1.json"
SCHEMA = "machine-forge-receipt-v1"

sys.path.insert(0, str(SCRIPTS))
from machine_three_pipelines_lib_v1 import TIERS, critical_count, load_json, now_iso  # noqa: E402


def run_forge(*, upgrade_id: str = "", role: str = "worker") -> dict:
    meta = TIERS["forge"]
    phases: list[dict] = []
    stations: list[dict] = []

    from machine_upgrade_baseline_v1 import capture_baseline  # noqa: WPS433
    from machine_calibrate_pipeline_v1 import run_calibrate  # noqa: WPS433
    from machine_test_ladder_run_v1 import run_ladder  # noqa: WPS433

    before = capture_baseline(tag="before", upgrade_id=upgrade_id)
    stations.append({"id": "F-A1", "phase": "A_baseline", "name": "baseline_before", "ok": True, "critical": before.get("critical_count")})

    cal = run_calibrate(scope="whole")
    stations.append({"id": "F-B1", "phase": "B_recalibrate", "name": "calibrate_replay", "ok": cal.get("ok") is True})

    for tier, fid in (("weekly", "F-C1"), ("monthly", "F-C2")):
        lad = run_ladder(tier=tier, role=role)
        stations.append(
            {
                "id": fid,
                "phase": "C_ladder_proof",
                "name": f"ladder_{tier}",
                "ok": lad.get("ok"),
                "passed": lad.get("steps_passed"),
                "total": lad.get("steps_total"),
            }
        )

    crit = critical_count()
    stations.append({"id": "F-C3", "phase": "C_ladder_proof", "name": "critical_zero", "ok": crit == 0, "critical_count": crit})

    attest = load_json(ATTEST)
    lines = [x for x in (attest.get("proven_lines") or []) if isinstance(x, str) and len(x.strip()) > 25]
    stations.append(
        {
            "id": "F-D1",
            "phase": "D_upgrade_proof",
            "name": "three_proven_lines",
            "ok": len(lines) >= 3,
            "count": len(lines),
            "upgrade_id": upgrade_id or "unspecified",
            "instruction": "Write 3 PROVEN lines to ~/.sina/machine-forge-proven-lines-v1.json · re-run with --write-proven",
        }
    )

    after = capture_baseline(tag="after", upgrade_id=upgrade_id)
    improved = (after.get("critical_count") or 99) <= (before.get("critical_count") or 0)
    stations.append(
        {
            "id": "F-D2",
            "phase": "D_upgrade_proof",
            "name": "baseline_after",
            "ok": improved,
            "before_critical": before.get("critical_count"),
            "after_critical": after.get("critical_count"),
        }
    )

    for phase_id in ("A_baseline", "B_recalibrate", "C_ladder_proof", "D_upgrade_proof"):
        ps = [s for s in stations if s.get("phase") == phase_id]
        phases.append({"phase": phase_id, "passed": sum(1 for s in ps if s.get("ok")), "total": len(ps), "ok": all(s.get("ok") for s in ps)})

    passed = sum(1 for s in stations if s.get("ok"))
    all_ok = passed == len(stations)

    row = {
        "schema": SCHEMA,
        "ok": all_ok,
        "at": now_iso(),
        **meta,
        "upgrade_id": upgrade_id or None,
        "role": role,
        "phases": phases,
        "stations_passed": passed,
        "stations_total": len(stations),
        "stations": stations,
        "wins": "Must cite W1/W2/W3 or H1 truth delta in PROVEN lines",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    if all_ok:
        PASSPORT.write_text(json.dumps({"schema": "machine-forge-passport-v1", "ok": True, "at": now_iso(), "upgrade_id": upgrade_id}, indent=2) + "\n", encoding="utf-8")
        if QUARANTINE.is_file():
            QUARANTINE.unlink()
    else:
        QUARANTINE.write_text(json.dumps({"active": True, "reason": "forge_incomplete", "passed": passed, "total": len(stations)}, indent=2) + "\n", encoding="utf-8")

    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="P3 Machine Forge")
    ap.add_argument("--upgrade-id", default="")
    ap.add_argument("--role", default="worker")
    ap.add_argument("--write-proven", action="append", default=[])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.write_proven:
        prev = load_json(ATTEST)
        lines = list(prev.get("proven_lines") or [])
        lines.extend(args.write_proven)
        ATTEST.write_text(json.dumps({"proven_lines": lines, "at": now_iso()}, indent=2) + "\n", encoding="utf-8")
    row = run_forge(upgrade_id=args.upgrade_id, role=args.role)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"FORGE ok={row['ok']} {row['stations_passed']}/{row['stations_total']}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
