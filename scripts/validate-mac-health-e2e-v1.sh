#!/usr/bin/env bash
# validate-mac-health-e2e-v1.sh — FULL recipe · cloud CI / ASF ship window ONLY (MARATHON — not Mac session)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_mac_health_validator_common_v1.sh
source "$ROOT/scripts/_mac_health_validator_common_v1.sh"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"

TIER="${MH_VALIDATOR_TIER:-}"
for arg in "$@"; do
  case "$arg" in
    --tier=*) TIER="${arg#*=}" ;;
    --tier) shift; TIER="${1:-}" ;;
  esac
done

# Mac control plane → NEVER marathon (even if stale ship-window flag on disk)
if [[ -f "${HOME}/.sina/mac-control-plane-v1.flag" ]] \
  && [[ "${SOURCEA_CI:-}${GITHUB_ACTIONS:-}" == "" ]] \
  && [[ "${MH_FORCE_E2E_MARATHON:-}" != "1" ]] \
  && [[ "$TIER" != "full" ]]; then
  _mh_red_flag_marathon
  exec bash "$ROOT/scripts/validate-mac-health-ship-fast-v1.sh"
fi

# Mac founder session without CI → ship-fast redirect
if _mh_founder_session && ! _mh_ship_window && [[ "$TIER" != "full" ]] && [[ "${SOURCEA_CI:-}${GITHUB_ACTIONS:-}" == "" ]]; then
  _mh_red_flag_marathon
  exec bash "$ROOT/scripts/validate-mac-health-ship-fast-v1.sh"
fi

_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
SINA="${HOME}/.sina"
PORT="$(_mh_port)"
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
  version=$(curl -sf "$(_mh_base)/health" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null || echo "?")
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
    "tier": "full",
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

echo "=== Mac Health Guard E2E FULL (ship window / CI only — not founder session) ==="

_mh_ensure_heart || { echo "FAIL: heart not up"; exit 1; }

curl -sf "$(_mh_base)/health" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok'), d
v=d.get('version','')
assert v.startswith('4.0'), f'version={v!r} expected 4.0.x'
print(f'heart v{v} on :${PORT}')
" || { echo "FAIL: heart not up"; exit 1; }

# No SASCIP / anti-staleness stack here — separate CI job (marathon removed)

_run "ship-fast baseline" bash "$ROOT/scripts/validate-mac-health-ship-fast-v1.sh"
_run "bundle parity" bash "$ROOT/scripts/validate-mac-health-bundle-parity-v1.sh"
_run "standalone stale copy" bash "$ROOT/scripts/validate-standalone-apps-stale-copy-v1.sh"
_run "founder upgrade" bash "$ROOT/scripts/validate-mac-health-founder-upgrade-v1.sh"
_run "log shield" bash "$ROOT/scripts/validate-mac-health-log-shield-v1.sh"
_run "prevention" bash "$ROOT/scripts/validate-mac-health-prevention-v1.sh"
_run "panic hotkey" bash "$ROOT/scripts/validate-mac-health-panic-hotkey-v1.sh"
_run "cooldown E2E" bash "$ROOT/scripts/validate-mac-health-cooldown-e2e-v1.sh"
_run "settings" bash "$ROOT/scripts/validate-mac-health-settings-v1.sh"
_run "unattended dry-run" bash "$ROOT/scripts/validate-mac-health-unattended-v1.sh"
_run "live wire read-only" bash "$ROOT/scripts/validate-mac-health-wire-live-v1.sh"
_run "all UI actions read-only" bash "$ROOT/scripts/validate-mac-health-all-actions-v1.sh"

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
  echo "=== validate-mac-health-e2e-v1: ALL PASS (full tier) ==="
  echo "Heart: $(_mh_base)/"
  exit 0
fi
echo "=== validate-mac-health-e2e-v1: FAILED (full tier) ==="
exit 1
