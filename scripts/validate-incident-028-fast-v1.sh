#!/usr/bin/env bash
# validate-incident-028-fast-v1.sh — <20s INCIDENT-028 stack (no full anti-staleness)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
t0=$SECONDS

bash scripts/validate-founder-close-line-gate-v1.sh
bash scripts/validate-prompt-feed-no-autosend-copy-v1.sh

python3 scripts/agent_session_gate_run_v1.py --role worker --scan-text "Hub Safety check" --pre-ship --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('ok'), r
assert r.get('mode')=='pre_ship', r
"

elapsed=$((SECONDS - t0))
echo "OK: validate-incident-028-fast-v1 · ${elapsed}s"
