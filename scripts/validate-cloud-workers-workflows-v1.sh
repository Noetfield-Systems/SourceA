#!/usr/bin/env bash
# validate-cloud-workers-workflows-v1.sh — light cockpit workflow smoke (founder session safe)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${CLOUD_WORKERS_PORT:-13027}"
PY="$ROOT/scripts/sourcea-python-v1.sh"
[[ -x "$PY" ]] || PY="/usr/bin/python3"
fail() { echo "FAIL: validate-cloud-workers-workflows-v1 — $*" >&2; exit 1; }

bash "$ROOT/scripts/serve-cloud-workers-v1.sh" >/dev/null 2>&1 || fail "could not start :${PORT}"

curl -sf --max-time 8 "http://127.0.0.1:${PORT}/health" | "$PY" -c \
  "import json,sys; d=json.load(sys.stdin); assert d.get('ok') and d.get('service')=='cloud-workers', d" \
  || fail "health"

curl -sf --max-time 8 "http://127.0.0.1:${PORT}/api/cloud-workers/v1" | "$PY" -c \
  "import json,sys; d=json.load(sys.stdin); assert d.get('schema')=='cloud-workers-hub-v1', d.get('schema')" \
  || fail "status payload"

curl -sf --max-time 8 -X POST "http://127.0.0.1:${PORT}/api/cloud-workers/v1" \
  -H "Content-Type: application/json" \
  -d '{"action":"dry_run"}' | "$PY" -c \
  "import json,sys; d=json.load(sys.stdin); assert d.get('ok'), d" \
  || fail "dry_run action"

curl -sf --max-time 15 -X POST "http://127.0.0.1:${PORT}/api/cloud-worker/dispatch/v1" \
  -H "Content-Type: application/json" \
  -d '{"plan_id":"MAC-CTL-002","dry_run":true}' | "$PY" -c \
  "import json,sys; d=json.load(sys.stdin); assert d.get('ok'), d; assert d.get('error')!='mac_observe_only', d" \
  || fail "dispatch blocked or plan_not_found"

curl -s --max-time 20 -X POST "http://127.0.0.1:${PORT}/api/cloud-workers/v1" \
  -H "Content-Type: application/json" \
  -d '{"action":"proceed","full_pack":true}' | "$PY" -c \
  "import json,sys; d=json.load(sys.stdin); assert d.get('decision')=='mac_trigger_cf_tick', d; assert d.get('error')!='mac_observe_only' or d.get('ok'), d" \
  || fail "proceed dead-ends on mac_observe_only — must upgrade to CF tick"

grep -q 'start-cloud-workers-launchd.sh' "$ROOT/scripts/mac_launchd_tcc_guard_v1.py" \
  || fail "cloud workers launchd wrapper not wired"

if grep -q '"cloud-workers-server"' "$ROOT/data/mac-pipeline-validator-pressure-registry-v1.json"; then
  fail "cloud-workers-server still listed as forbidden_body — Mac Health will SIGKILL it"
fi

echo "PASS: validate-cloud-workers-workflows-v1.sh"
