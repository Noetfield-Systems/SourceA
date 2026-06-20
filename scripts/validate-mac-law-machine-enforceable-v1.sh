#!/usr/bin/env bash
# validate-mac-law-machine-enforceable-v1.sh
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

test -f data/mac-law-machine-enforceable-v1.json || { echo "FAIL missing SSOT"; exit 1; }
test -f scripts/mac_law_machine_enforce_v1.py || { echo "FAIL missing script"; exit 1; }
test -f .cursor/rules/031-mac-law-machine-enforceable-v1.mdc || { echo "FAIL missing rule 031"; exit 1; }

python3 scripts/mac_law_machine_enforce_v1.py --sync-receipt --json >/dev/null
test -f "${SINA}/mac-law-machine-enforce-receipt-v1.json" || { echo "FAIL missing receipt"; exit 1; }

python3 - <<'PY'
import json, subprocess, sys
cmd = ["python3", "scripts/mac_law_machine_enforce_v1.py", "--scan-shell",
       "python3 scripts/anti_staleness_auto_wire_v1.py --tier session", "--json"]
out = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
r = json.loads(out.stdout[out.stdout.find("{"):])
if r.get("ok"):
    raise SystemExit("FAIL should block anti_staleness on Mac")
print("OK: blocks anti_staleness on Mac")
PY

python3 - <<'PY'
import json, subprocess
cmd = ["python3", "scripts/mac_law_machine_enforce_v1.py", "--scan-shell",
       "curl -X POST http://127.0.0.1:13020/api/comprehension-loop/v1", "--json"]
out = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
r = json.loads(out.stdout[out.stdout.find("{"):])
if not r.get("ok"):
    raise SystemExit("FAIL should allow comprehension Hub POST")
print("OK: allows cloud comprehension Hub POST")
PY

grep -q 'mac_law_machine_enforce' scripts/agentic_conduct_gate_v1.py || { echo "FAIL conduct not wired"; exit 1; }
grep -q 'mac_law_machine' scripts/agent_memory_mirror_v1.py || { echo "FAIL mirror not wired"; exit 1; }

python3 - <<'PY'
import json
from pathlib import Path
m = json.loads(Path("data/mac-law-mandatory-v1.json").read_text())
if not m.get("machine_enforceable", {}).get("active"):
    raise SystemExit("mac-law-mandatory machine_enforceable not active")
print("OK: mac-law-mandatory cross-ref")
PY

echo "PASS: validate-mac-law-machine-enforceable-v1"
