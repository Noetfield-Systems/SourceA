#!/usr/bin/env bash
# validate-mac-law-universal-wire-v1.sh — LIGHT · assess-only · no --enforce · no nested validators
# Law: INCIDENT-039/040 · Mac Law validators must not heat Mac during founder session
set -euo pipefail
cd "$(dirname "$0")/.."

test -f data/mac-law-universal-wire-v1.json || { echo "FAIL missing SSOT"; exit 1; }
test -f scripts/mac_law_universal_wire_v1.py || { echo "FAIL missing script"; exit 1; }
test -f .cursor/rules/032-mac-law-universal-wire-v1.mdc || { echo "FAIL missing rule 032"; exit 1; }

python3 scripts/mac_law_validator_light_assess_v1.py --module universal --json >/dev/null

python3 - <<'PY'
import json, subprocess
cmd = ["python3", "scripts/mac_law_universal_wire_v1.py", "--scan-text",
       "python3 scripts/fbe_motor_delegate_v1.py", "--json"]
out = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
r = json.loads(out.stdout[out.stdout.find("{"):])
if r.get("ok"):
    raise SystemExit("FAIL should block motor on Mac")
print("OK: scan blocks fbe_motor_delegate")
PY

echo "PASS: validate-mac-law-universal-wire-v1 (light assess-only)"
