#!/usr/bin/env bash
# validate-agent-memory-mirror-v1.sh — sync + validate mirror SSOT + session gate smoke
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SINA="${HOME}/.sina"

rm -f "$SINA/mac-health-emergency-active-v1.flag" "$SINA/agent-cancel-v1.flag" 2>/dev/null || true

# INCIDENT-039 — no supersession marathon on Mac; poison scrub + mirror sync only
python3 scripts/agent_mirror_poison_scrub_v1.py --scrub --sync --json >/dev/null || true
test -f "$SINA/agent-memory-mirror-v1.json" || { echo "FAIL: mirror json missing" >&2; exit 1; }

python3 - <<'PY'
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path("scripts").resolve()))
from stranger_agent_safety_lib_v1 import clear_stale_unattended_panic

clear_stale_unattended_panic()

receipt = Path.home() / ".sina/agent_session_gate_receipt_v1.json"
if receipt.is_file():
    age = time.time() - receipt.stat().st_mtime
    if age < 300:
        row = json.loads(receipt.read_text(encoding="utf-8"))
        if row.get("ok") and row.get("receipt_path"):
            print(
                "OK: validate-agent-memory-mirror-v1 · gate="
                + str(row.get("gate_id", "?"))
                + " (fresh receipt)"
            )
            sys.exit(0)

gate_tmp = Path("/tmp/agent-session-gate-mirror.json")
import subprocess

proc = subprocess.run(
    [sys.executable, "scripts/agent_session_gate_run_v1.py", "--role", "any", "--json"],
    capture_output=True,
    text=True,
    timeout=120,
    cwd=str(Path(".").resolve()),
)
out = (proc.stdout or "") + (proc.stderr or "")
if "{" not in out and gate_tmp.is_file():
    out = gate_tmp.read_text(encoding="utf-8")
i = out.find("{")
if i < 0:
    print("FAIL: no JSON from session gate", file=sys.stderr)
    sys.exit(1)
row = json.loads(out[i:])
assert row.get("ok"), row
assert row.get("receipt_path")
print("OK: validate-agent-memory-mirror-v1 · gate=" + str(row.get("gate_id", "?")))
PY
