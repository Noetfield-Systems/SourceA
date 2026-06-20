#!/usr/bin/env python3
"""Five-Step Autonomous Progress Machine — SCAN wrapper + receipt."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
from governance_paths_v1 import FIVE_STEP_BLUEPRINT

SINA = Path.home() / ".sina"
LAW = FIVE_STEP_BLUEPRINT
RECEIPT = SINA / "five-step-progress-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def scan_disk() -> dict[str, Any]:
    fn = _read_json(SINA / "factory-now-v1.json") or {}
    pp = _read_json(ROOT / "PROGRAM_PROGRESS.json") or {}
    critical = 0
    bugs_ok = None
    try:
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "find_critical_bugs.py")],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=str(ROOT),
        )
        for line in (r.stdout + r.stderr).splitlines():
            if line.strip().startswith("{") and "critical" in line:
                try:
                    j = json.loads(line.strip())
                    critical = int(j.get("critical") or 0)
                    bugs_ok = bool(j.get("ok"))
                except json.JSONDecodeError:
                    pass
        if bugs_ok is None:
            bugs_ok = r.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        bugs_ok = False

    locks = pp.get("locks") or {}
    return {
        "schema": "five-step-scan-v1",
        "at": _now(),
        "factory_line": fn.get("line") or "unavailable",
        "valid_yes": fn.get("valid_yes"),
        "queue_sa": fn.get("queue_sa"),
        "kill_flag": fn.get("kill_flag"),
        "founder_p0": locks.get("founder_p0_id") or pp.get("founder_p0_id"),
        "critical_bugs": critical,
        "find_critical_ok": bugs_ok,
        "scan_card": {
            "pain": "CRITICAL > 0" if critical else "none from find_critical_bugs",
            "goal": str(locks.get("founder_p0_id") or "STRATEGIC-SLICE"),
            "red": f"critical={critical}" if critical else "check validators if red hub",
            "green": fn.get("line") or "",
        },
        "next": "SAY plain-language cards per SOURCEA_FIVE_STEP_AUTONOMOUS_PROGRESS_BLUEPRINT §3",
        "law": str(LAW.name),
    }


def say_template() -> str:
    return """## SAY — fork card
**Subject:** …
**Question:** …
**Locally:** …
| Key | Choice | If you pick → Effect |
|-----|--------|----------------------|
| A | … | … |
| B | … | … |
| C | … | … |
| D | … | … |
**Recommended:** … (evidence: …)
"""


def ship_template() -> str:
    return """## SHIP — closeout
| Step | Done | Proof |
|------|------|-------|
| SCAN | | |
| SAY | | |
| PICK | | |
| PROVE | | |
| SHIP | | |

### Golden insight
- **Problem:**
- **Fixed:**
- **Your next:** 1. … 2. … 3. …
"""


def write_receipt(row: dict[str, Any]) -> Path:
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return RECEIPT


def main() -> int:
    p = argparse.ArgumentParser(description="Five-Step Progress Machine v1")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="Step 1 SCAN")
    s.add_argument("--json", action="store_true")
    s.add_argument("--write-receipt", action="store_true")

    sub.add_parser("say-template", help="Step 2 SAY markdown skeleton")
    sub.add_parser("ship-template", help="Step 5 SHIP closeout skeleton")

    args = p.parse_args()

    if args.cmd == "scan":
        row = scan_disk()
        if args.write_receipt:
            write_receipt(row)
        print(json.dumps(row, indent=2) if args.json else json.dumps(row["scan_card"], indent=2))
        return 0

    if args.cmd == "say-template":
        print(say_template())
        return 0

    if args.cmd == "ship-template":
        print(ship_template())
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
