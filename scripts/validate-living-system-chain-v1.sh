#!/usr/bin/env bash
# Light E2E chain validator — Hub · Cloud Workers · N8N · Railway · CF cron · autopilot
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/living_system_chain_validate_v1.py --json
