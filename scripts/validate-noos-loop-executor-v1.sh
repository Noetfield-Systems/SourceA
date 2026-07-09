#!/usr/bin/env bash
# validate-noos-loop-executor-v1.sh — auth reject + bounded one-tick (local or Fly URL)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: noos-loop-executor — $*" >&2; exit 1; }

SECRET="${NOOS_LOOP_SECRET:-noos-loop-test-secret-local}"
PORT="${NOOS_LOOP_EXECUTOR_TEST_PORT:-19876}"
BASE="${NOOS_LOOP_EXECUTOR_URL:-http://127.0.0.1:${PORT}}"
LOCAL_SERVER=0

if [[ -z "${NOOS_LOOP_EXECUTOR_URL:-}" ]]; then
  LOCAL_SERVER=1
  export NOOS_LOOP_SECRET="$SECRET"
  export NOOS_EXECUTOR_ROOT="$ROOT"
  export PYTHONPATH="$ROOT/apps/noos-loop-executor"
  python3 "$ROOT/apps/noos-loop-executor/noos_loop_executor/server.py" --port "$PORT" &
  PID=$!
  trap 'kill "$PID" 2>/dev/null || true' EXIT
  for _ in $(seq 1 30); do
    curl -sf "$BASE/health" >/dev/null 2>&1 && break
    sleep 0.2
  done
fi

echo "== GET /health =="
HEALTH="$(curl -sf "$BASE/health")" || fail "health unreachable at $BASE"
echo "$HEALTH" | python3 -c "import json,sys; r=json.load(sys.stdin); assert r.get('ok') and r.get('service')=='noos-loop-executor', r"

echo "== POST /loop without secret (expect 401) =="
CODE="$(curl -s -o /tmp/noos-loop-noauth.json -w '%{http_code}' -X POST "$BASE/loop" -H 'Content-Type: application/json' -d '{}')"
[[ "$CODE" == "401" ]] || fail "expected 401 without secret got $CODE"

echo "== POST /loop wrong secret (expect 401) =="
CODE="$(curl -s -o /tmp/noos-loop-badauth.json -w '%{http_code}' -X POST "$BASE/loop" \
  -H 'Content-Type: application/json' -H 'X-NOOS-Loop-Secret: wrong' -d '{}')"
[[ "$CODE" == "401" ]] || fail "expected 401 for bad secret got $CODE"

echo "== POST /loop good secret (bounded one tick) =="
CODE="$(curl -s -o /tmp/noos-loop-tick.json -w '%{http_code}' -X POST "$BASE/loop" \
  -H 'Content-Type: application/json' -H "X-NOOS-Loop-Secret: $SECRET" \
  -d '{"trigger_source":"validate_noos_loop_executor_v1"}')"
[[ "$CODE" == "200" || "$CODE" == "422" ]] || fail "unexpected tick status $CODE"
python3 -c "
import json
r=json.load(open('/tmp/noos-loop-tick.json'))
assert r.get('schema')=='noos-loop-tick-receipt-v1', r
assert r.get('receipt_id'), r
assert r.get('bounded') is True, r
print('OK: receipt', r.get('receipt_id'), 'decision', r.get('decision'))
"

python3 - "$ROOT" <<'PY'
import json
from pathlib import Path
root = Path(__import__('sys').argv[1])
arch = json.loads((root / "data/noos-runtime-architecture-v1.json").read_text())
if arch.get("cron_gate", {}).get("status") != "blocked_until_fly_green":
    raise SystemExit("cron_gate must stay blocked_until_fly_green until Fly verified in prod")
print("OK: NOOS CF cron gate still blocked")
PY

echo "PASS: validate-noos-loop-executor-v1"
