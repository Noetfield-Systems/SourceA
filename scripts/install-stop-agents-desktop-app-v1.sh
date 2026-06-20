#!/usr/bin/env bash
# Desktop double-click STOP — no keyboard, no Mac Health web UI.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_NAME="⛔ STOP AGENTS"
DESKTOP="$HOME/Desktop/${APP_NAME}.app"
APPS="$HOME/Applications/${APP_NAME}.app"
STAGE="$ROOT/brand/macos-apps/${APP_NAME}.app"
SWIFT="$ROOT/brand/macos-apps/StopAgentsClick.swift"
ICNS="$ROOT/brand/icons/icns/sina-mac-health.icns"
EXEC="StopAgents"

echo "→ Building ${APP_NAME}.app (double-click only)…"
rm -rf "$STAGE"
mkdir -p "$STAGE/Contents/MacOS" "$STAGE/Contents/Resources"
/usr/bin/swiftc -O -o "$STAGE/Contents/MacOS/${EXEC}" "$SWIFT" -framework AppKit
chmod +x "$STAGE/Contents/MacOS/${EXEC}"
[[ -f "$ICNS" ]] && cp "$ICNS" "$STAGE/Contents/Resources/AppIcon.icns"

cat >"$STAGE/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key><string>${EXEC}</string>
  <key>CFBundleIdentifier</key><string>com.sina.stopagents.desktop</string>
  <key>CFBundleName</key><string>STOP AGENTS</string>
  <key>CFBundleDisplayName</key><string>${APP_NAME}</string>
  <key>CFBundleIconFile</key><string>AppIcon</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>LSMinimumSystemVersion</key><string>12.0</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>LSEnvironment</key>
  <dict>
    <key>SINA_SOURCEA</key><string>${ROOT}</string>
  </dict>
</dict>
</plist>
PLIST

xattr -cr "$STAGE" 2>/dev/null || true
codesign --force --deep --sign - --timestamp=none "$STAGE" 2>/dev/null || true

rm -rf "$DESKTOP" "$APPS" "$HOME/Desktop/⛔ STOP AGENTS.command" 2>/dev/null || true
ditto "$STAGE" "$DESKTOP"
ditto "$STAGE" "$APPS"
xattr -cr "$DESKTOP" "$APPS" 2>/dev/null || true
codesign --force --deep --sign - --timestamp=none "$DESKTOP" 2>/dev/null || true

echo ""
echo "✓ ${APP_NAME}.app on your Desktop"
echo "  Double-click it when Mac is laggy."
echo "  Stops hub + auto-run + background agents. Does NOT close Cursor unless Mac is frozen (200%+ CPU)."
echo "  No keyboard. No Mac Health buttons. Just double-click."
echo ""
echo "  Desktop: $DESKTOP"
