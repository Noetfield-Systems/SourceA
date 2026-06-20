#!/usr/bin/env bash
# PANIC listener via python3.12 (already in founder Accessibility list).
set -euo pipefail
SA="$(cd "$(dirname "$0")/.." && pwd)"
PY312="/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
PLIST="$HOME/Library/LaunchAgents/com.sina.mac-health-panic-listener.plist"
LOG="$HOME/.sina/mac-health-panic-hotkey.log"

if [[ ! -x "$PY312" ]]; then
  echo "FAIL: python3.12 not found at $PY312" >&2
  exit 1
fi

"$PY312" -m pip install --user -q pynput 2>/dev/null || "$PY312" -m pip install --user pynput

cat >"$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.sina.mac-health-panic-listener</string>
  <key>ProgramArguments</key>
  <array>
    <string>${PY312}</string>
    <string>${SA}/scripts/mac_health_panic_listener_v1.py</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>SINA_SOURCEA</key>
    <string>${SA}</string>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${LOG}</string>
  <key>StandardErrorPath</key>
  <string>${LOG}</string>
</dict>
</plist>
PLIST

# Stop Swift daemon — python3.12 listener replaces it
launchctl bootout "gui/$(id -u)/com.sina.mac-health-panic-hotkey" 2>/dev/null || true
launchctl bootout "gui/$(id -u)/com.sina.mac-health-panic-listener" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/com.sina.mac-health-panic-listener"
launchctl kickstart -k "gui/$(id -u)/com.sina.mac-health-panic-listener"

sleep 2
if pgrep -f mac_health_panic_listener_v1.py >/dev/null 2>&1; then
  echo "✓ PANIC listener on python3.12 (your Accessibility entry)"
  echo "  ⌃⌥⌘S  or  ⌃⌘P (easier)  or  touch ~/.sina/PANIC.now"
  grep "\[py312\]" "$LOG" 2>/dev/null | tail -4
else
  echo "FAIL — check $LOG" >&2
  tail -10 "$LOG" 2>&1
  exit 1
fi
