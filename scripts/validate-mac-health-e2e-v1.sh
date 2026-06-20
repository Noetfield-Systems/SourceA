#!/usr/bin/env bash
# validate-mac-health-e2e-v1.sh — full Mac Health Guard E2E (v3.1.0 + SASCIP + UI gate)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
SINA="${HOME}/.sina"
PORT="${MAC_HEALTH_PORT:-13024}"
RECEIPT="${SINA}/mac-health/e2e-latest-v1.json"
STEPS_FILE=$(mktemp)
fail=0
started_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

_run() {
  local name="$1"
  shift
  echo ""
  echo "=== $name ==="
  if "$@"; then
    echo "OK: $name"
    python3 -c "import json,sys; print(json.dumps({'name': sys.argv[1], 'ok': True}))" "$name" >>"$STEPS_FILE"
  else
    echo "FAIL: $name"
    python3 -c "import json,sys; print(json.dumps({'name': sys.argv[1], 'ok': False}))" "$name" >>"$STEPS_FILE"
    fail=1
  fi
}

_write_receipt() {
  mkdir -p "$(dirname "$RECEIPT")"
  local version
  version=$(curl -sf "http://127.0.0.1:${PORT}/health" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null || echo "?")
  STEPS_FILE="$STEPS_FILE" RECEIPT="$RECEIPT" VERSION="$version" STARTED="$started_at" FAIL="$fail" PORT="$PORT" python3 <<'PY'
import json, os
from datetime import datetime, timezone
steps = []
path = os.environ.get("STEPS_FILE", "")
if path and os.path.isfile(path):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                steps.append(json.loads(line))
out = {
    "schema": "mac-health-e2e-latest-v1",
    "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "started_at": os.environ.get("STARTED", ""),
    "version": os.environ.get("VERSION", "?"),
    "port": int(os.environ.get("PORT", "13024")),
    "overall_ok": os.environ.get("FAIL", "1") == "0",
    "steps": steps,
}
receipt = os.environ.get("RECEIPT", "")
with open(receipt, "w") as f:
    json.dump(out, f, indent=2)
    f.write("\n")
print(f"receipt: {receipt}")
PY
  rm -f "$STEPS_FILE"
}

trap '_write_receipt' EXIT

echo "=== Mac Health Guard E2E (recipe gate) ==="

pkill -f 'mac-health-guard-server.py' 2>/dev/null || true
sleep 0.5
nohup python3 "$ROOT/scripts/mac-health-guard-server.py" >>"$SINA/mac-health-guard-server.log" 2>&1 &
for _ in {1..40}; do
  curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 && break
  sleep 0.25
done

if ! curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
  bash "$ROOT/scripts/serve-mac-health-guard.sh" || true
fi

curl -sf "http://127.0.0.1:${PORT}/health" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok'), d
v=d.get('version','')
assert v.startswith('3.3'), f'version={v!r} expected 3.3.x'
print(f'heart v{v} on :${PORT}')
" || { echo "FAIL: heart not up"; exit 1; }

rm -f "$SINA/mac-health-emergency-active-v1.flag" "$SINA/agent-cancel-v1.flag" 2>/dev/null || true
if ! python3 scripts/stranger_agent_safety_live_wire_v1.py --role worker --tier session --json >/dev/null; then
  echo "WARN: SASCIP live wire retry after flag clear…"
  rm -f "$SINA/mac-health-emergency-active-v1.flag" "$SINA/agent-cancel-v1.flag" 2>/dev/null || true
  python3 scripts/stranger_agent_safety_live_wire_v1.py --role worker --tier session --json >/dev/null \
    || { echo "FAIL: SASCIP live wire"; exit 1; }
fi
python3 scripts/stranger_agent_safety_pipeline_v1.py --watch --json >/dev/null
python3 scripts/mac_health_live_v1.py --json >/dev/null

_run "founder glance SSOT" bash "$ROOT/scripts/validate-mac-health-founder-glance-v1.sh"
_run "sync bundles" bash "$ROOT/scripts/sync-standalone-apps-to-bundles-v1.sh"
_run "bundle parity" bash "$ROOT/scripts/validate-mac-health-bundle-parity-v1.sh"
_run "standalone stale copy" bash "$ROOT/scripts/validate-standalone-apps-stale-copy-v1.sh"
_run "founder upgrade v3" bash "$ROOT/scripts/validate-mac-health-founder-upgrade-v1.sh"
_run "log shield" bash "$ROOT/scripts/validate-mac-health-log-shield-v1.sh"
_run "prevention" bash "$ROOT/scripts/validate-mac-health-prevention-v1.sh"
_run "panic hotkey" bash "$ROOT/scripts/validate-mac-health-panic-hotkey-v1.sh"
_run "cooldown E2E" bash "$ROOT/scripts/validate-mac-health-cooldown-e2e-v1.sh"
_run "UI theme gate" bash "$ROOT/scripts/validate-mac-health-ui-v1.sh"
_run "settings" bash "$ROOT/scripts/validate-mac-health-settings-v1.sh"
_run "unattended dry-run" bash "$ROOT/scripts/validate-mac-health-unattended-v1.sh"
_run "live wire full" bash "$ROOT/scripts/validate-mac-health-wire-live-v1.sh"
_run "all UI actions" bash "$ROOT/scripts/validate-mac-health-all-actions-v1.sh"

if curl -sf "http://127.0.0.1:13020/health" >/dev/null 2>&1; then
  _run "live wire H1 bridge" bash "$ROOT/scripts/fix-mac-health-live-wire-v1.sh"
else
  echo ""
  echo "=== live wire H1 bridge ==="
  echo "WARN: H1 hub :13020 down — skipping H1 bridge (heart standalone OK)"
  python3 -c "import json; print(json.dumps({'name': 'live wire H1 bridge', 'ok': True, 'skipped': True}))" >>"$STEPS_FILE"
fi

echo ""
if [[ "$fail" -eq 0 ]]; then
  echo "=== validate-mac-health-e2e-v1: ALL PASS ==="
  echo "Heart: http://127.0.0.1:${PORT}/"
  exit 0
fi
echo "=== validate-mac-health-e2e-v1: FAILED ==="
exit 1
