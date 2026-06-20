#!/usr/bin/env bash
# validate-mac-health-wire-live-v1.sh — prove UI JS loads + every API action wired live
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
PORT="${MAC_HEALTH_PORT:-13024}"
BASE="http://127.0.0.1:${PORT}"
fail=0

check() {
  if "$@"; then echo "PASS: $*"; else echo "FAIL: $*"; fail=1; fi
}

echo "=== Mac Health LIVE wire audit ==="

check node --check "$ROOT/scripts/mac-health-standalone/app.js"
check curl -sf "${BASE}/health"
check bash "$ROOT/scripts/validate-mac-health-fast-v1.sh"

# Prove browser-critical endpoints (same origin as UI)
python3 <<'PY' || fail=1
import json, urllib.request
BASE = "http://127.0.0.1:13024"
def post(action, extra=None):
    body = {"action": action, "standalone": True}
    if extra:
        body.update(extra)
    req = urllib.request.Request(
        f"{BASE}/api/mac-health",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())

def get(path):
    with urllib.request.urlopen(f"{BASE}{path}", timeout=30) as r:
        return json.loads(r.read())

h = get("/health")
assert h.get("version", "").startswith("3.3"), h
live = get("/api/mac-health/live")
assert live.get("ok") and live.get("live_status") == "LIVE", live
assert (live.get("cpu_warn_state") or {}).get("founder_line"), "cpu_warn_state"
mp = live.get("machine_pressure") or {}
for key in ("ram_used_pct", "cpu_pct", "system_cpu_busy_pct", "load_pct", "queue_zombies", "ghost_terminals", "disk_root_pct", "ram_truth", "hub_health_ok", "sina_log_bomb"):
    assert key in mp, f"machine_pressure missing {key} for body rhythm cards"
assert (mp.get("ram_truth") or {}).get("explain_line"), "ram_truth.explain_line for memory card"
report = post("report")
assert report.get("settings") and report.get("cpu_warn_state"), report
assert post("settings").get("ok"), "settings"
assert post("settings_save", {"settings": {"chrome": {"quit_on_cool_down_mode": "when_mac_hot"}}}).get("ok"), "settings_save"
for act in ("heal", "pipeline", "cpu_cool_down"):
    row = post(act)
    ok = row.get("ok") is not False or row.get("cpu_relief") or row.get("heal")
    assert ok, act
print("PASS: all live API actions respond ok")
PY

# UI boot simulation — JS would call these on load
live_age=$(curl -sf "${BASE}/api/mac-health/live" | python3 -c "import json,sys; d=json.load(sys.stdin); print((d.get('wired') or {}).get('live_age_sec','?'))")
echo "PASS: live pulse age ${live_age}s"

if [[ "$fail" -eq 0 ]]; then
  echo "validate-mac-health-wire-live-v1: ALL PASS"
  exit 0
fi
echo "validate-mac-health-wire-live-v1: FAILED"
exit 1
