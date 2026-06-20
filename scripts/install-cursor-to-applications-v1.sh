#!/usr/bin/env bash
# install-cursor-to-applications-v1.sh — one-time fix: Cursor off DMG → /Applications
set -euo pipefail

DMG_APP="/Volumes/Cursor Installer/Cursor.app"
DMG_FILE="$HOME/Applications/Cursor-darwin-universal.dmg"
TARGET="/Applications/Cursor.app"

if [[ ! -d "$DMG_APP" ]]; then
  if [[ -f "$DMG_FILE" ]]; then
    echo "Opening DMG..."
    open "$DMG_FILE"
    sleep 4
  fi
fi

if [[ ! -d "$DMG_APP" ]]; then
  echo "FAIL: Mount Cursor installer first (double-click Cursor-darwin-universal.dmg)"
  exit 1
fi

echo "Installing Cursor to /Applications..."
osascript -e 'tell application "Cursor" to quit saving yes' 2>/dev/null || true
sleep 2
rm -rf "$TARGET"
cp -R "$DMG_APP" "$TARGET"
xattr -dr com.apple.quarantine "$TARGET" 2>/dev/null || true

echo ""
echo "✓ Cursor is now in /Applications"
echo ""
echo "NEXT (30 seconds):"
echo "  1. Open Cursor from Applications (Spotlight: Cursor → pick the one under Applications)"
echo "  2. Eject 'Cursor Installer' in Finder sidebar (or: hdiutil detach '/Volumes/Cursor Installer')"
echo "  3. Pin Applications Cursor to Dock — remove old DMG icon if it is there"
echo ""
open -a "$TARGET"
