#!/usr/bin/env bash
# Restart panic hotkey after Accessibility grant — run after toggling Mac Health Panic ON.
set -euo pipefail
LOG="$HOME/.sina/mac-health-panic-hotkey.log"
echo "→ Restarting Mac Health Panic hotkey daemon…"
launchctl kickstart -k "gui/$(id -u)/com.sina.mac-health-panic-hotkey" 2>/dev/null \
  || bash "$(cd "$(dirname "$0")" && pwd)/install-mac-health-panic-hotkey-v1.sh"
sleep 2
echo ""
grep -E "start pid|accessibility|global monitor|ARMED|LIVE|WAITING" "$LOG" 2>/dev/null | tail -6
echo ""
if grep -q "global monitor LIVE\|accessibility=true\|accessibility GRANTED" "$LOG" 2>/dev/null; then
  echo "✓ Hotkey armed — press Control+Option+Command+S"
else
  echo "⚠ Still waiting for Accessibility — enable Mac Health Panic then run this script again"
fi
