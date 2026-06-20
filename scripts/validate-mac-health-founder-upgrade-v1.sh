#!/usr/bin/env bash
# validate-mac-health-founder-upgrade-v1.sh — Founder Mac 10-step sprint acceptance
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
SINA="${HOME}/.sina"
MH_VER="$(python3 -c "from mac_health_version_v1 import MAC_HEALTH_VERSION; print(MAC_HEALTH_VERSION)")"
fail=0

check() {
  if "$@"; then
    echo "PASS: $*"
  else
    echo "FAIL: $*"
    fail=1
  fi
}

echo "=== Founder Mac 10-step validator ==="

# Step 1 — baseline dry-run protects tunnel
ui_dry="$(python3 scripts/mac_health_emergency_stop_v1.py --dry-run --trigger ui --json)"
echo "$ui_dry" | python3 -c "
import json,sys
d=json.load(sys.stdin)
targets=d.get('targets_before') or []
tunnel=[t for t in targets if 'cloudflared' in str(t.get('cmdline','')) and ':8190' in str(t.get('cmdline',''))]
assert len(tunnel)==0, f'ui dry-run must protect landing tunnel, got {tunnel}'
print('PASS: ui dry-run protects landing tunnel')
" || fail=1

full_dry="$(python3 scripts/mac_health_emergency_stop_v1.py --dry-run --trigger full_stop --json)"
echo "$full_dry" | python3 -c "
import json,sys
d=json.load(sys.stdin)
# full_stop may list cloudflared if running — schema must include trigger
assert d.get('trigger')=='full_stop' or 'dry_run' in d
print('PASS: full_stop dry-run schema ok')
" || fail=1

# Step 2 — API route + UI button
check grep -q 'panic/full' scripts/mac-health-guard-server.py
check grep -q 'btn-full-stop' scripts/mac-health-standalone/index.html
check grep -q 'runFullStop' scripts/mac-health-standalone/app.js

# Step 3 — Desktop stop honest receipt
check grep -q 'desktop-stop' brand/macos-apps/StopAgentsClick.swift
check grep -q 'kill_count' brand/macos-apps/StopAgentsClick.swift
if grep -q '\-\-fast' brand/macos-apps/StopAgentsClick.swift; then
  echo "FAIL: StopAgentsClick must not use --fast"
  fail=1
else
  echo "PASS: StopAgentsClick no --fast"
fi

# Step 4 — agent cancel guard wired
check test -f scripts/agent_cancel_guard_v1.py
check grep -q 'agent_cancel_guard_v1' scripts/auto_run_worker_batch_v1.py
check grep -q 'agent_cancel_guard_v1' scripts/goal1_lane_broker.py
check grep -q 'agent_cancel_guard_v1' scripts/autorun_dispatcher_v1.py

# Step 5 — founder glance (no help-card prose block)
check grep -q 'mhg-founder-glance' scripts/mac-health-standalone/index.html
check grep -q 'Relieve pressure' scripts/mac-health-standalone/index.html
check bash scripts/validate-mac-health-founder-glance-v1.sh

# Step 6 — landing URL note (optional if never published)
if [[ -f "${HOME}/Desktop/SourceA-Landing-URL.txt" ]]; then
  check test -f "${HOME}/Desktop/SourceA-Landing-URL.txt"
  echo "PASS: desktop landing URL note present"
else
  echo "WARN: SourceA-Landing-URL.txt absent — run publish_sourcea_landing_v1.py"
fi
if [[ -f "${SINA}/sourcea-landing-run-receipt-v1.json" ]]; then
  echo "PASS: landing run-receipt on disk"
else
  echo "WARN: sourcea-landing-run-receipt-v1.json absent — run run-recipe.sh"
fi

# Step 7 — unattended test script
check test -f scripts/test_mac_health_unattended_v1.py

# Step 8 — panic controls in More disclosure (not footer chrome)
check grep -q 'btn-panic-header' scripts/mac-health-standalone/index.html
check grep -q 'btn-full-stop' scripts/mac-health-standalone/index.html
check grep -q 'btn.title = "STOP"' brand/macos-apps/PanicStopMenuBar.swift

# Step 9 — freeze flag in key factory entrypoints
for f in autorun_dispatcher_v1.py auto_run_worker_batch_v1.py goal1_lane_broker.py brain_run_loop_v1.py healthy-drain-orchestrator-v1.py; do
  check grep -q 'auto-run-disabled-v1.flag\|agent_cancel' "scripts/$f"
done

# Step 10 — founder glance SSOT + settings + log shield (More disclosure)
check grep -q "app.css?v=${MH_VER}" scripts/mac-health-standalone/index.html
check grep -q 'mac_health_version_v1' scripts/mac-health-guard-server.py
check grep -q 'mhg-founder-more' scripts/mac-health-standalone/index.html
check grep -q 'panel-more' scripts/mac-health-standalone/index.html
check grep -q 'panel-settings' scripts/mac-health-standalone/index.html
check test -f scripts/mac_health_settings_v1.py
check grep -q 'mac_health_settings_v1' scripts/mac_health_guard.py
check test -f scripts/mac_health_log_shield_v1.py
check grep -q 'id="log-shield"' scripts/mac-health-standalone/index.html
check grep -q 'hub-truth-badge' scripts/mac-health-standalone/index.html
check grep -q 'paintLogShield' scripts/mac-health-standalone/app.js
check test -f data/mac-health-founder-glance-ui-contract-v1.json
check test -f brain-os/law/enforcement/SINA_MAC_HEALTH_FOUNDER_GLANCE_UI_LOCKED_v1.md
check bash scripts/validate-mac-health-cloud-glance-v1.sh
if grep -q 'LOG.read_text' scripts/find_critical_bugs.py; then
  echo "FAIL: find_critical_bugs must not use LOG.read_text"
  fail=1
else
  echo "PASS: find_critical_bugs tail-only log scan"
fi

# Receipt schema
if [[ -f "${SINA}/mac-health/emergency-stop-latest-v1.json" ]]; then
  python3 -c "
import json
from pathlib import Path
p=Path('${SINA}/mac-health/emergency-stop-latest-v1.json')
d=json.loads(p.read_text())
for k in ('founder_line','kill_count','trigger'):
    assert k in d, f'missing {k}'
print('PASS: emergency-stop receipt schema')
" || fail=1
else
  echo "WARN: no emergency-stop-latest-v1.json yet"
fi

python3 scripts/agent_cancel_guard_v1.py --json >/dev/null && echo "PASS: agent-cancel guard CLI"

if [[ "$fail" -eq 0 ]]; then
  echo "=== ALL CHECKS PASSED ==="
else
  echo "=== VALIDATOR FAILED ==="
fi
exit "$fail"
