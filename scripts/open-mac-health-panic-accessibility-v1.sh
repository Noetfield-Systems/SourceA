#!/usr/bin/env bash
# Open Accessibility settings + trigger MacHealthPanicHotkey permission prompt.
set -euo pipefail
BIN="$HOME/.sina/bin/MacHealthPanicHotkey"
echo "→ Mac Health PANIC hotkey needs Accessibility to hear ⌃⌥⌘S globally."
echo "  Binary: $BIN"
if [[ ! -x "$BIN" ]]; then
  echo "  Installing first…"
  bash "$(cd "$(dirname "$0")" && pwd)/install-mac-health-panic-hotkey-v1.sh"
fi
# Launch once — macOS should prompt for Accessibility
open "$BIN" 2>/dev/null || true
sleep 1
pkill -f MacHealthPanicHotkey 2>/dev/null || true
launchctl kickstart -k "gui/$(id -u)/com.sina.mac-health-panic-hotkey" 2>/dev/null || true
# Deep link to Accessibility pane (macOS 13+)
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility" 2>/dev/null \
  || open "x-apple.systempreferences:com.apple.settings.PrivacySecurity.extension?Privacy_Accessibility" 2>/dev/null \
  || open "/System/Applications/System Settings.app"
echo ""
echo "In System Settings → Privacy & Security → Accessibility:"
echo "  Turn ON: MacHealthPanicHotkey  (or python3 if grouped)"
echo "  Shortcut: Control + Option + Command + S"
echo ""
echo "Test: press ⌃⌥⌘S — you should hear Basso + notification."
