#!/usr/bin/env bash
# Light E2E chain validator — Railway queue · CF cron · autopilot (no Mac :13020/:13027 polling)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/living_system_chain_validate_v1.py --json
