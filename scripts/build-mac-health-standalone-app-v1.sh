#!/usr/bin/env bash
# Build Mac Health Guard — true double-click .app, no Terminal, no hub, no browser.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
APPS_BRAND="$ROOT/brand/macos-apps"
APP_NAME="Mac Health Guard"
APP_ID="com.sina.machealth.standalone"
DESKTOP="$HOME/Desktop/${APP_NAME}.app"
APPS_HOME="$HOME/Applications/${APP_NAME}.app"
ENT="$APPS_BRAND/entitlements-local.plist"
ICNS="$ROOT/brand/icons/icns/sina-mac-health.icns"
LSREGISTER="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
SWIFT_SRC="$APPS_BRAND/MacHealthShell.swift"
STAGE="$APPS_BRAND/${APP_NAME}.app"
BUNDLE_STAGE="$STAGE/Contents/Resources/mac-health-bundle"
EXEC_NAME="MacHealthShell"

echo "→ Building self-contained ${APP_NAME}.app…"

python3 "$ROOT/scripts/build_sina_icons.py" 2>/dev/null || true

rm -rf "$STAGE"
mkdir -p "$STAGE/Contents/MacOS" "$STAGE/Contents/Resources" "$BUNDLE_STAGE/scripts" "$BUNDLE_STAGE/app"

for f in mac-health-guard-server.py mac_health_guard.py mac_health_live_v1.py mac_performance_snapshot.py mac_health_cpu_relief_v1.py mac_health_prevention_v1.py mac_health_emergency_stop_v1.py mac_health_settings_v1.py mac_health_version_v1.py mac_health_log_shield_v1.py mac_health_debug_bab1ff_v1.py mac_health_agent_mandates_v1.py mac_health_cloud_glance_v1.py mac_health_founder_glance_ui_v1.py mac_health_founder_glance_wire_v1.py mac_health_never_again_v1.py mac_health_panic_listener_v1.py mac_health_ram_pressure_v1.py mac_health_edition_v1.py mac_health_license_v1.py n8n_glue_runner_v1.py n8n_glue_config_v1.py; do
  cp "$ROOT/scripts/$f" "$BUNDLE_STAGE/scripts/"
done
cp -R "$ROOT/scripts/mac-health-standalone/." "$BUNDLE_STAGE/app/"

/usr/bin/swiftc -O -o "$STAGE/Contents/MacOS/${EXEC_NAME}" "$SWIFT_SRC" -framework Cocoa -framework WebKit
chmod +x "$STAGE/Contents/MacOS/${EXEC_NAME}"

if [[ -f "$ICNS" ]]; then
  cp "$ICNS" "$STAGE/Contents/Resources/AppIcon.icns"
fi

VERSION="$(python3 -c 'import sys; sys.path.insert(0, "'"$ROOT"'/scripts"); from mac_health_version_v1 import MAC_HEALTH_VERSION; print(MAC_HEALTH_VERSION)')"
BUILD_NUM="${VERSION//./}"

cat >"$STAGE/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key><string>en</string>
  <key>CFBundleExecutable</key><string>${EXEC_NAME}</string>
  <key>CFBundleIconFile</key><string>AppIcon</string>
  <key>CFBundleIdentifier</key><string>${APP_ID}</string>
  <key>CFBundleInfoDictionaryVersion</key><string>6.0</string>
  <key>CFBundleName</key><string>${APP_NAME}</string>
  <key>CFBundleDisplayName</key><string>${APP_NAME}</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>${VERSION}</string>
  <key>CFBundleVersion</key><string>${BUILD_NUM}</string>
  <key>LSMinimumSystemVersion</key><string>12.0</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>NSAppTransportSecurity</key>
  <dict>
    <key>NSAllowsLocalNetworking</key><true/>
  </dict>
  <key>LSEnvironment</key>
  <dict>
    <key>MAC_HEALTH_PORT</key><string>13024</string>
    <key>MAC_HEALTH_STANDALONE</key><string>1</string>
  </dict>
</dict>
</plist>
PLIST

sign_app() {
  local app="$1"
  xattr -cr "$app" 2>/dev/null || true
  local inner="$app/Contents/MacOS/${EXEC_NAME}"
  if [[ -f "$ENT" ]]; then
    codesign --force --sign - --entitlements "$ENT" --timestamp=none "$inner"
    codesign --force --deep --sign - --entitlements "$ENT" --timestamp=none "$app"
  else
    codesign --force --sign - --timestamp=none "$inner"
    codesign --force --deep --sign - --timestamp=none "$app"
  fi
  [[ -x "$LSREGISTER" ]] && "$LSREGISTER" -f -R -trusted "$app" 2>/dev/null || true
}

echo "→ Installing to Desktop + Applications (real .app, not alias)…"
rm -rf "$DESKTOP" "$APPS_HOME"
ditto "$STAGE" "$DESKTOP"
ditto "$STAGE" "$APPS_HOME"
sign_app "$DESKTOP"
sign_app "$APPS_HOME"

# Remove broken legacy alias/launcher if present
rm -rf "$HOME/Applications/Mac Health Guard Launcher.app" 2>/dev/null || true

echo "→ Cold-start smoke test…"
pkill -f "mac-health-guard-server.py" 2>/dev/null || true
pkill -f "MacHealthShell" 2>/dev/null || true
sleep 1
open "$DESKTOP"
sleep 5
if /usr/bin/curl -sf "http://127.0.0.1:13024/health" >/dev/null 2>&1; then
  echo "✓ Cold-start PASS — heart up after double-click"
else
  echo "WARN: cold-start failed — see ~/.sina/mac-health-app-launch.log" >&2
  tail -5 "$HOME/.sina/mac-health-app-launch.log" 2>/dev/null || true
fi

echo ""
echo "✓ ${APP_NAME} v3.1 — double-click only"
echo "  Desktop:       $DESKTOP"
echo "  Applications:  $APPS_HOME"
echo "  Entry:         native MacHealthShell (starts bundled heart + own window)"
echo "  Log:           ~/.sina/mac-health-app-launch.log"
