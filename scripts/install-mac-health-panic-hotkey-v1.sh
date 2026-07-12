#!/usr/bin/env bash
# Install Mac Health PANIC hotkey — ⌃⌥⌘S · .app bundle for stable Accessibility.
set -euo pipefail
SA="$(cd "$(dirname "$0")/.." && pwd)"
BIN_DIR="$HOME/.sina/bin"
BIN="$BIN_DIR/MacHealthPanicHotkey"
APP="$HOME/Applications/Mac Health Panic.app"
APP_BIN="$APP/Contents/MacOS/Mac Health Panic"
PLIST="$HOME/Library/LaunchAgents/com.sina.mac-health-panic-hotkey.plist"
SWIFT="$SA/brand/macos-apps/MacHealthPanicHotkey.swift"
CONFIG="$HOME/.sina/config/mac-health-panic-v1.json"
LOG="$HOME/.sina/mac-health-panic-hotkey.log"

mkdir -p "$BIN_DIR" "$HOME/.sina/config" "$HOME/Library/LaunchAgents"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"

if [[ ! -f "$CONFIG" ]]; then
  cat >"$CONFIG" <<'JSON'
{
  "hotkey": {
    "enabled": true,
    "modifiers": ["control", "option", "command"],
    "key": "s",
    "label": "⌃⌥⌘S"
  },
  "unattended": {
    "auto_panic_on_runaway": true,
    "consecutive_unhealthy_pulses": 24,
    "cursor_cpu_panic": 280
  }
}
JSON
fi

echo "→ Compiling panic hotkey daemon…"
/usr/bin/swiftc -O -o "$BIN" "$SWIFT" -framework AppKit -framework ApplicationServices -framework Carbon
chmod +x "$BIN"
cp "$BIN" "$APP_BIN"
chmod +x "$APP_BIN"

cat >"$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key><string>en</string>
  <key>CFBundleExecutable</key><string>Mac Health Panic</string>
  <key>CFBundleIdentifier</key><string>com.sina.machealth.panic</string>
  <key>CFBundleName</key><string>Mac Health Panic</string>
  <key>CFBundleDisplayName</key><string>Mac Health Panic</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.1</string>
  <key>CFBundleVersion</key><string>11</string>
  <key>LSMinimumSystemVersion</key><string>12.0</string>
  <key>LSUIElement</key><true/>
  <key>NSAppleEventsUsageDescription</key><string>Mac Health Panic listens for the emergency stop shortcut.</string>
</dict>
</plist>
PLIST

xattr -cr "$APP" "$BIN" 2>/dev/null || true
codesign --force --sign - --timestamp=none "$APP_BIN" 2>/dev/null || true
codesign --force --deep --sign - --timestamp=none "$APP" 2>/dev/null || true

cat >"$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.sina.mac-health-panic-hotkey</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/open</string>
    <string>-W</string>
    <string>-a</string>
    <string>Mac Health Panic</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>SINA_SOURCEA</key>
    <string>${SA}</string>
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

launchctl bootout "gui/$(id -u)/com.sina.mac-health-panic-hotkey" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/com.sina.mac-health-panic-hotkey"
launchctl kickstart -k "gui/$(id -u)/com.sina.mac-health-panic-hotkey" 2>/dev/null || true

sleep 2
if pgrep -f "Mac Health Panic" >/dev/null 2>&1 || pgrep -f MacHealthPanicHotkey >/dev/null 2>&1; then
  echo "✓ PANIC hotkey installed"
  echo "  app:     $APP"
  echo "  shortcut: Control + Option + Command + S"
  echo "  log:     $LOG"
  echo ""
  echo "  AFTER enabling Accessibility, run:"
  echo "    bash $SA/scripts/restart-mac-health-panic-hotkey-v1.sh"
  echo ""
  echo "  System Settings → Privacy → Accessibility → Mac Health Panic ON"
  open -a "Mac Health Panic" 2>/dev/null || true
  sleep 2
  open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility" 2>/dev/null || true
  grep -E "start pid|accessibility|global monitor|LIVE|GRANTED|WAITING" "$LOG" 2>/dev/null | tail -8 || true
else
  echo "WARN: daemon not running — check $LOG" >&2
  tail -10 "$LOG" 2>/dev/null || true
  exit 1
fi
