#!/usr/bin/env bash
# wire-founder-session-gates-v1.sh — insert gate into all HEAVY/MEDIUM validators missing it
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/scripts/mac_pipeline_validator_pressure_v1.py" --wire-gates --json
echo "OK: wire-founder-session-gates-v1"
