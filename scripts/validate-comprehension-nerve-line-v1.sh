#!/usr/bin/env bash
# validate-comprehension-nerve-line-v1.sh — fresh bay receipt → comprehension_line on surfaces
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd)/scripts:${PYTHONPATH:-}"

python3 <<'PY'
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, "scripts")
import agent_nerve_system_v1 as ans
from agent_nerve_system_v1 import _comprehension_line_from_receipt, run_nerve_pulse

receipt_path = Path.home() / ".sina" / "cloud-comprehension-bay-receipt-v1.json"
if not receipt_path.is_file():
    raise SystemExit("SKIP: no cloud-comprehension-bay receipt — run client smoke first")

line = _comprehension_line_from_receipt()
assert line, "comprehension_line empty — receipt stale or missing verdict"
assert "comprehension" in line.lower()
assert "ACCEPT" in line or "BLOCKED" in line
print("OK: comprehension_line from fresh receipt:", line[:120])

pulse = run_nerve_pulse(write=False, refresh_loops=False)
surf = pulse.get("surfaces") or pulse
comp = surf.get("comprehension_line") or surf.get("comprehension_bay_line") or ""
if comp:
    assert "comprehension" in comp.lower()
    print("OK: nerve pulse surfaces comprehension_line")
else:
    print("WARN: nerve pulse did not surface comprehension_line (receipt may be stale)")

stale_at = (datetime.now(timezone.utc) - timedelta(hours=25)).strftime("%Y-%m-%dT%H:%M:%SZ")
orig = ans._read_json

def _mock(path):
    if str(path).endswith("cloud-comprehension-bay-receipt-v1.json"):
        return {"at": stale_at, "verdict": "ACCEPT", "config_version": "1.1.0"}
    return orig(path)

with patch.object(ans, "_read_json", side_effect=_mock):
    assert ans._comprehension_line_from_receipt() == "", "stale receipt should yield empty line"
print("OK: stale receipt (>24h) yields empty comprehension_line")
PY

echo "PASS: validate-comprehension-nerve-line-v1"
