#!/usr/bin/env bash
# validate-mac-health-agent-mandates-v1.sh — Mac Law agent obedience gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LAW="$HOME/Desktop/MacLaw/MAC_HEALTH_AGENT_MANDATES_LOCKED.md"
fail() { echo "FAIL: validate-mac-health-agent-mandates-v1 — $*" >&2; exit 1; }

[[ -f "$LAW" ]] || fail "missing Mac Law mandate doc: $LAW"
[[ -f "$ROOT/scripts/mac_health_agent_mandates_v1.py" ]] || fail "missing mandates module"

grep -q 'notifications_enabled()' "$ROOT/scripts/mac_health_settings_v1.py" \
  || fail "settings missing notifications_enabled()"
grep -q 'if not notifications_enabled()' "$ROOT/scripts/mac_health_emergency_stop_v1.py" \
  || fail "emergency stop _notify must gate on notifications_enabled()"
grep -q 'mac-health-quiet-v1.flag' "$ROOT/scripts/mac_health_settings_v1.py" \
  || fail "settings missing QUIET_FLAG"
grep -q 'mac-health-quiet-v1.flag' "$ROOT/scripts/mac_health_agent_mandates_v1.py" \
  || fail "mandates module missing quiet flag enforce"

[[ -f "$HOME/Desktop/MacLaw/.cursor/rules/mac-health-agent-mandates.mdc" ]] \
  || [[ -f "$ROOT/.cursor/rules/mac-health-agent-mandates.mdc" ]] \
  || fail "missing Cursor rule mac-health-agent-mandates.mdc"

python3 "$ROOT/scripts/mac_health_agent_mandates_v1.py" --json >/dev/null \
  || fail "agent mandates enforce probe failed"

bash "$ROOT/scripts/validate-no-auto-screenshot-v1.sh" \
  || fail "no auto screenshot law gate failed"

echo "PASS: validate-mac-health-agent-mandates-v1.sh"
