#!/usr/bin/env bash
# Light gate — validator machine registry + probe tier
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
test -f data/validator-machine-registry-v1.json
test -f scripts/validator_machine_v1.py
python3 scripts/validator_machine_v1.py --all --tier probe --json >/dev/null
echo "OK: validate-validator-machine-v1"
