#!/usr/bin/env bash
# Refresh PROGRAM_PROGRESS.json signals + command center auto block.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
exec python3 "$ROOT/scripts/update-program-progress.py"
