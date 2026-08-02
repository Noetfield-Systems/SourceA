#!/usr/bin/env bash
# Package Mac Health Guard.app into a distributable, drag-to-install .dmg.
# Builds the .app via build-mac-health-standalone-app-v1.sh (not duplicated here),
# stages it with an /Applications symlink, and compresses it with hdiutil.
#
# Optional Developer ID signing + notarization (skipped cleanly if unset):
#   MAC_HEALTH_DEVELOPER_ID="Developer ID Application: Your Name (TEAMID)"
#   MAC_HEALTH_NOTARIZE_PROFILE="<xcrun notarytool store-credentials profile name>"
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_NAME="Mac Health Guard"
DESKTOP_APP="$HOME/Desktop/${APP_NAME}.app"
DIST_DIR="$ROOT/dist"
ENT="$ROOT/brand/macos-apps/entitlements-local.plist"
STAGE_DIR="$(mktemp -d)"

cleanup() { rm -rf "$STAGE_DIR"; }
trap cleanup EXIT

echo "→ Building fresh ${APP_NAME}.app…"
bash "$ROOT/scripts/build-mac-health-standalone-app-v1.sh"

if [[ ! -d "$DESKTOP_APP" ]]; then
  echo "FAIL: expected app not found: $DESKTOP_APP" >&2
  exit 1
fi

VERSION="$(python3 -c 'import sys; sys.path.insert(0, "'"$ROOT"'/scripts"); from mac_health_version_v1 import MAC_HEALTH_VERSION; print(MAC_HEALTH_VERSION)')"
DMG_NAME="${APP_NAME}-${VERSION}.dmg"
mkdir -p "$DIST_DIR"
DMG_PATH="$DIST_DIR/$DMG_NAME"

echo "→ Staging drag-to-install layout…"
ditto "$DESKTOP_APP" "$STAGE_DIR/${APP_NAME}.app"
ln -s /Applications "$STAGE_DIR/Applications"

if [[ -n "${MAC_HEALTH_DEVELOPER_ID:-}" ]]; then
  echo "→ [optional] Codesigning .app with Developer ID: ${MAC_HEALTH_DEVELOPER_ID}"
  if [[ -f "$ENT" ]]; then
    codesign --force --deep --options runtime --timestamp --sign "$MAC_HEALTH_DEVELOPER_ID" --entitlements "$ENT" "$STAGE_DIR/${APP_NAME}.app"
  else
    codesign --force --deep --options runtime --timestamp --sign "$MAC_HEALTH_DEVELOPER_ID" "$STAGE_DIR/${APP_NAME}.app"
  fi
  codesign --verify --deep --strict "$STAGE_DIR/${APP_NAME}.app"
else
  echo "SKIP: [optional] Developer ID signing — MAC_HEALTH_DEVELOPER_ID not set (.app stays ad-hoc signed)."
fi

echo "→ Building compressed, read-only DMG…"
rm -f "$DMG_PATH"
hdiutil create -volname "$APP_NAME" -srcfolder "$STAGE_DIR" -ov -format UDZO "$DMG_PATH"

if [[ -n "${MAC_HEALTH_DEVELOPER_ID:-}" ]]; then
  echo "→ [optional] Codesigning DMG with Developer ID: ${MAC_HEALTH_DEVELOPER_ID}"
  codesign --force --sign "$MAC_HEALTH_DEVELOPER_ID" --timestamp "$DMG_PATH"
else
  echo "SKIP: [optional] DMG codesigning — MAC_HEALTH_DEVELOPER_ID not set."
fi

if [[ -n "${MAC_HEALTH_NOTARIZE_PROFILE:-}" ]]; then
  echo "→ [optional] Submitting DMG for notarization (profile: ${MAC_HEALTH_NOTARIZE_PROFILE})…"
  xcrun notarytool submit "$DMG_PATH" --keychain-profile "$MAC_HEALTH_NOTARIZE_PROFILE" --wait
  echo "→ [optional] Stapling notarization ticket…"
  xcrun stapler staple "$DMG_PATH"
  echo "✓ Notarized + stapled: $DMG_PATH"
else
  echo "SKIP: [optional] Notarization — MAC_HEALTH_NOTARIZE_PROFILE not set."
fi

if [[ -z "${MAC_HEALTH_DEVELOPER_ID:-}" && -z "${MAC_HEALTH_NOTARIZE_PROFILE:-}" ]]; then
  echo ""
  echo "NOTE: This DMG is ad-hoc signed only — it will NOT pass Gatekeeper on another Mac."
  echo "  To ship a real release, get a paid Apple Developer Program account, then set:"
  echo "    MAC_HEALTH_DEVELOPER_ID=\"Developer ID Application: Your Name (TEAMID)\""
  echo "    MAC_HEALTH_NOTARIZE_PROFILE=\"<xcrun notarytool store-credentials profile name>\""
  echo "  and re-run this script. This script never fabricates or guesses these credentials."
fi

echo ""
echo "✓ DMG ready: $DMG_PATH"
