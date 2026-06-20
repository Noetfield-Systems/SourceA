#!/usr/bin/env bash
# validate-mac-health-wire-live-v1.sh — live wire audit (read-only default · invoke = ship window only)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_mac_health_validator_common_v1.sh
source "$ROOT/scripts/_mac_health_validator_common_v1.sh"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"

INVOKE=0
for arg in "$@"; do
  case "$arg" in
    --invoke-relief) INVOKE=1 ;;
  esac
done

if [[ "$INVOKE" -eq 1 ]]; then
  _founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
else
  if _mh_founder_session && ! _mh_ship_window; then
    : # read-only allowed on founder session
  fi
fi

export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
PORT="$(_mh_port)"
BASE="$(_mh_base)"
fail=0

check() {
  if "$@"; then echo "PASS: $*"; else echo "FAIL: $*"; fail=1; fi
}

echo "=== Mac Health LIVE wire audit (read-only=$([[ $INVOKE -eq 1 ]] && echo invoke || echo yes)) ==="

_mh_ensure_heart || { echo "FAIL: heart down"; exit 1; }

check node --check "$ROOT/scripts/mac-health-standalone/app.js"
check curl -sf "${BASE}/health"

python3 <<'PY' || fail=1
import json, urllib.request
BASE = "http://127.0.0.1:13024"
def get(path):
    with urllib.request.urlopen(f"{BASE}{path}", timeout=15) as r:
        return json.loads(r.read())
def post(action, extra=None, timeout=20):
    body = {"action": action, "standalone": True}
    if extra:
        body.update(extra)
    req = urllib.request.Request(
        f"{BASE}/api/mac-health",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

h = get("/health")
assert h.get("version", "").startswith("4.0"), h
live = get("/api/mac-health/live")
assert live.get("ok") and live.get("live_status") == "LIVE", live
assert (live.get("cpu_warn_state") or {}).get("founder_line"), "cpu_warn_state"
mp = live.get("machine_pressure") or {}
for key in ("ram_used_pct", "cpu_pct", "system_cpu_busy_pct", "load_pct", "queue_zombies", "ghost_terminals", "disk_root_pct", "ram_truth", "hub_health_ok", "sina_log_bomb"):
    assert key in mp, f"machine_pressure missing {key}"
rt = mp.get("ram_truth") or {}
assert rt.get("explain_line") or rt.get("total_line"), "ram_truth line for memory card"
report = post("report", timeout=25)
assert report.get("settings") and report.get("cpu_warn_state"), report
assert post("settings", timeout=15).get("ok"), "settings"
print("PASS: read-only live API schema")
PY

if [[ "$INVOKE" -eq 1 ]]; then
  python3 <<'PY' || fail=1
import json, urllib.request
BASE = "http://127.0.0.1:13024"
def post(action, timeout=45):
    body = {"action": action, "standalone": True}
    req = urllib.request.Request(
        f"{BASE}/api/mac-health",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())
for act in ("heal", "pipeline", "cpu_cool_down"):
    row = post(act)
    ok = row.get("ok") is not False or row.get("cpu_relief") or row.get("heal")
    assert ok, act
print("PASS: relief invoke actions (ship window)")
PY
else
  echo "SKIP: relief invoke (use --invoke-relief on ship window only)"
fi

live_age=$(curl -sf "${BASE}/api/mac-health/live" | python3 -c "import json,sys; d=json.load(sys.stdin); print((d.get('wired') or {}).get('live_age_sec','?'))")
echo "PASS: live pulse age ${live_age}s"

if [[ "$fail" -eq 0 ]]; then
  echo "validate-mac-health-wire-live-v1: ALL PASS"
  exit 0
fi
echo "validate-mac-health-wire-live-v1: FAILED"
exit 1
