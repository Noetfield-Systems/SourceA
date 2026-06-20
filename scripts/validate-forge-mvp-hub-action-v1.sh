#!/usr/bin/env bash
# validate-forge-mvp-hub-action-v1.sh — Hub forge--run route smoke
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

[[ -f "$ROOT/scripts/forge__run_v1.py" ]] || { echo "FAIL missing forge__run_v1.py"; exit 1; }
grep -q "forge--run/v1" "$ROOT/scripts/sina-command-server.py" \
  || { echo "FAIL hub route not wired"; exit 1; }

python3 "$ROOT/scripts/forge__run_v1.py" --stack sourcea --dry-run --json >/dev/null \
  || { echo "FAIL forge__run dry-run"; exit 1; }

echo "PASS validate-forge-mvp-hub-action-v1"
