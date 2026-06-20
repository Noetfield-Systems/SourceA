#!/usr/bin/env bash
# validate-mac-law-machine-enforceable-v1.sh — LIGHT · assess-only · fast scan probes
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

test -f data/mac-law-machine-enforceable-v1.json || { echo "FAIL missing SSOT"; exit 1; }
test -f scripts/mac_law_machine_enforce_v1.py || { echo "FAIL missing script"; exit 1; }
test -f .cursor/rules/031-mac-law-machine-enforceable-v1.mdc || { echo "FAIL missing rule 031"; exit 1; }

python3 scripts/mac_law_validator_light_assess_v1.py --module machine --json >/dev/null

python3 - <<'PY'
import json, subprocess
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
       "bash scripts/validate-mac-law-universal-wire-v1.sh && bash scripts/validate-mac-law-agent-execution-plane-lock-v1.sh", "--json"]
out = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
r = json.loads(out.stdout[out.stdout.find("{"):])
if r.get("ok"):
    raise SystemExit("FAIL should block mac-law validator chains on Mac")
print("OK: blocks mac-law validator && chains")
PY

echo "PASS: validate-mac-law-machine-enforceable-v1 (light assess-only)"
