#!/usr/bin/env bash
# Build + install Panic Stop menu bar app (⛔) — reliable keyboard + click.
set -euo pipefail
SA="$(cd "$(dirname "$0")/.." && pwd)"
APP="$HOME/Applications/Panic Stop.app"
EXEC="$APP/Contents/MacOS/Panic Stop"
PLIST="$HOME/Library/LaunchAgents/com.sina.panic-stop-menubar.plist"
SWIFT="$SA/brand/macos-apps/PanicStopMenuBar.swift"
LOG="$HOME/.sina/mac-health-panic-hotkey.log"

echo "→ Building Panic Stop menu bar app…"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
/usr/bin/swiftc -O -o "$EXEC" "$SWIFT" -framework AppKit -framework ApplicationServices -framework Carbon
chmod +x "$EXEC"

cat >"$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key><string>Panic Stop</string>
  <key>CFBundleIdentifier</key><string>com.sina.panicstop.menubar</string>
  <key>CFBundleName</key><string>Panic Stop</string>
  <key>CFBundleDisplayName</key><string>Panic Stop</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>LSMinimumSystemVersion</key><string>12.0</string>
  <key>LSUIElement</key><true/>
</dict>
</plist>
PLIST

xattr -cr "$APP" 2>/dev/null || true
codesign --force --deep --sign - --timestamp=none "$APP" 2>/dev/null || true

# Stop old listeners (background daemons can't hear keys on macOS)
launchctl bootout "gui/$(id -u)/com.sina.mac-health-panic-listener" 2>/dev/null || true
launchctl bootout "gui/$(id -u)/com.sina.mac-health-panic-hotkey" 2>/dev/null || true
pkill -f mac_health_panic_listener_v1.py 2>/dev/null || true
pkill -f "Mac Health Panic" 2>/dev/null || true

cat >"$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.sina.panic-stop-menubar</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/open</string>
    <string>-W</string>
    <string>-a</string>
    <string>Panic Stop</string>
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
</dict>
</plist>
PLIST

launchctl bootout "gui/$(id -u)/com.sina.panic-stop-menubar" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/com.sina.panic-stop-menubar"

# Launch now + prompt Accessibility for THIS app
/usr/bin/open -a "$APP" 2>/dev/null || /usr/bin/open "$APP" 2>/dev/null || true
sleep 2

echo ""
echo "✓ Panic Stop installed — look for ⛔ in your menu bar (top right)"
echo ""
echo "  REQUIRED in System Settings → Privacy & Security → Accessibility:"
echo "    Turn ON:  Panic Stop"
echo ""
echo "  Shortcuts:"
echo "    ⌃⌘P  — Control+Command+P"
echo "    ⌃⌥⌘S — Control+Option+Command+S"
echo "    Click ⛔ in menu bar → PANIC STOP now"
echo "    touch ~/.sina/PANIC.now"
echo ""
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility" 2>/dev/null || true
grep "\[menubar\]" "$LOG" 2>/dev/null | tail -5 || true
