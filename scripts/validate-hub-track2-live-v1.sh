#!/usr/bin/env bash
# Track 2 bundle gate — L1–L5 validators + stabilization regression.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
chmod +x "$ROOT/scripts/validate-hub-live-sse-v1.sh" \
  "$ROOT/scripts/validate-hub-sync-slim-v1.sh" \
  "$ROOT/scripts/validate-hub-state-writers-v1.sh" 2>/dev/null || true

bash "$ROOT/scripts/validate-hub-live-sse-v1.sh"
bash "$ROOT/scripts/validate-hub-sync-slim-v1.sh"
bash "$ROOT/scripts/validate-hub-state-writers-v1.sh"
bash "$ROOT/scripts/validate-hub-stabilization-e2e-light-v1.sh"
python3 "$ROOT/scripts/find_critical_bugs.py"
echo "OK: validate-hub-track2-live-v1"
