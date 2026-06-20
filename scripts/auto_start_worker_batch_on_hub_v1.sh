#!/usr/bin/env bash
# Auto-start Goal 1 worker batch when hub is up — no ASF taps.
# Spawns goal1_worker_batch_loop_v1.py via gated autorun engine.
# Law: brain-os/laws/AUTO_RUN_FULLY_AUTOMATIC_LOCKED_v1.md · sa-0730
set -euo pipefail
if [[ -f "${HOME}/.sina/auto-run-disabled-v1.flag" ]]; then
  exit 0
fi
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:${PATH:-/usr/bin:/bin}"
cd "$ROOT"
exec python3 "$ROOT/scripts/auto_run_worker_batch_v1.py" --once --batch-size 5 --max-batches 6 --json
