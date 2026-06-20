#!/usr/bin/env bash
# n8n_loop_specialist_tick_hook_v1.sh — external cron glue (n8n executeCommand only)
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
SINA="${HOME}/.sina"
HUB="${SINA_COMMAND_HUB_URL:-http://127.0.0.1:13020}"
DISPATCH="${LOOP_SPECIALIST_DISPATCH:-0}"

if [[ "${1:-}" == "--local" ]]; then
  exec python3 "${ROOT}/scripts/loop_specialist_tick_v1.py" --json ${DISPATCH:+--dispatch}
fi

payload='{}'
if [[ "${DISPATCH}" == "1" ]]; then
  payload='{"dispatch":true}'
fi

curl -sf -X POST "${HUB}/api/loop-specialist/tick/v1" \
  -H "Content-Type: application/json" \
  -d "${payload}" \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('loop_specialist_line') or r.get('tick_decision'))"
