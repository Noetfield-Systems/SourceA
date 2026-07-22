#!/usr/bin/env bash
# SourceA Worker connected gate — one command proof chain is live
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/validate_sourcea_worker_connected_v1.py --json >/dev/null
echo "OK: validate-sourcea-worker-connected-v1 · coherence · receipt · acceptance · honesty · hub"
