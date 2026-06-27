#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
API_URL="${FORGE_CORE_API_URL:-http://127.0.0.1:13040}"
export SOURCEA_ROOT="${SOURCEA_ROOT:-$ROOT}"
export REDIS_URL="${REDIS_URL:-redis://127.0.0.1:6379}"
export FORGE_GOVERNANCE_DRY_RUN="${FORGE_GOVERNANCE_DRY_RUN:-true}"

echo "[smoke] health"
curl -sf "$API_URL/health" >/dev/null

echo "[smoke] submit task"
RESP="$(curl -sf -X POST "$API_URL/tasks" \
  -H 'content-type: application/json' \
  -d '{"goal":"Reply with exactly: forge-mvp-ok"}')"

TASK_ID="$(echo "$RESP" | python3 -c 'import json,sys; print(json.load(sys.stdin)["task_id"])')"
echo "[smoke] task_id=$TASK_ID"

for i in $(seq 1 30); do
  STATUS="$(curl -sf "$API_URL/tasks/$TASK_ID" | python3 -c 'import json,sys; print(json.load(sys.stdin)["status"])')"
  echo "[smoke] poll $i status=$STATUS"
  if [[ "$STATUS" == "completed" || "$STATUS" == "denied" || "$STATUS" == "failed" ]]; then
    break
  fi
  sleep 1
done

if [[ "$STATUS" != "completed" ]]; then
  echo "[smoke] FAIL final_status=$STATUS"
  curl -sf "$API_URL/tasks/$TASK_ID" | python3 -m json.tool
  exit 1
fi

echo "[smoke] state"
curl -sf "$API_URL/state/$TASK_ID" | python3 -m json.tool

echo "[smoke] PASS"
