#!/usr/bin/env bash
# sessionStart — Worker INBOX context (Brain gets heads-up only; full prompt Worker chat only).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
INPUT="$(cat)"
export WORKER_HOOK_INPUT="$INPUT"
python3 "$ROOT/scripts/worker_inject_lib.py" --session-start
