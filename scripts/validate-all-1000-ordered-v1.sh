#!/usr/bin/env bash
# Machine-check all 1000 sa rows in order — receipt + registry + proof audit.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/validate-registry-1000-steps-v1.py --json
python3 scripts/validator_list_v1.py --filter road
echo "OK: validate-all-1000-ordered-v1"
