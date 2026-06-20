#!/usr/bin/env bash
# Lane B + C background while Worker runs INBOX in Cursor. No queue touch.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
LOG="${HOME}/.sina/sidecar-engines-v1.log"
mkdir -p "$(dirname "$LOG")"
{
  echo "=== sidecar start $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  python3 scripts/sidecar_scout_api_v1.py --json || true
  python3 scripts/sidecar_prep_cli_v1.py --json || true
  echo "=== sidecar done ==="
} >>"$LOG" 2>&1
echo "Sidecars ran — log: $LOG"
