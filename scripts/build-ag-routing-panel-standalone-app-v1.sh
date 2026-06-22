#!/usr/bin/env bash
# Build AG Routing Panel — true double-click .app (agent light + full routing on :8782).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APPS_BRAND="$ROOT/brand/macos-apps"
APP_NAME="AG Routing Panel"
APP_ID="com.sina.agrouting.standalone"
DESKTOP="$HOME/Desktop/${APP_NAME}.app"
APPS_HOME="$HOME/Applications/${APP_NAME}.app"
ENT="$APPS_BRAND/entitlements-local.plist"
ICNS="$ROOT/brand/icons/icns/sina-worker-hub.icns"
LSREGISTER="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
SWIFT_SRC="$APPS_BRAND/AgRoutingPanelShell.swift"
STAGE="$APPS_BRAND/${APP_NAME}.app"
BUNDLE_STAGE="$STAGE/Contents/Resources/ag-routing-panel-bundle"
EXEC_NAME="AgRoutingPanelShell"

APP_VER="$(python3 -c "import re; m=re.search(r'VERSION = \"([^\"]+)\"', open('$ROOT/scripts/ag_routing_panel_core.py').read()); print(m.group(1) if m else '1.0.0')")"
APP_VER_BUILD="$(echo "$APP_VER" | tr -d '.')"
echo "→ Building self-contained ${APP_NAME}.app v${APP_VER}…"

bash "$ROOT/scripts/sync-official-links-bar-v1.sh" 2>/dev/null || true

python3 "$ROOT/scripts/build_sina_icons.py" 2>/dev/null || true

rm -rf "$STAGE"
mkdir -p "$STAGE/Contents/MacOS" "$STAGE/Contents/Resources" "$BUNDLE_STAGE/scripts" "$BUNDLE_STAGE/app"

for f in ag-routing-panel-server.py ag_routing_panel_core.py founder_routing_panel_v1.py orient_routing_v1.py cursor_cost_intelligence_routing_v1.py; do
  if [[ -f "$ROOT/scripts/$f" ]]; then
    cp "$ROOT/scripts/$f" "$BUNDLE_STAGE/scripts/"
  fi
done
cp -R "$ROOT/scripts/ag-routing-panel-standalone/." "$BUNDLE_STAGE/app/"
cp "$ROOT/agent-control-panel/shared/official-links-bar.js" "$BUNDLE_STAGE/app/official-links-bar.js"
cp "$ROOT/agent-control-panel/shared/sina-main-terminal.js" "$BUNDLE_STAGE/app/sina-main-terminal.js"
cp "$ROOT/agent-control-panel/shared/sina-main-terminal.css" "$BUNDLE_STAGE/app/sina-main-terminal.css"
cp "$ROOT/agent-control-panel/shared/official-links-bar.css" "$BUNDLE_STAGE/app/official-links-bar.css" 2>/dev/null || true

SWIFT_COMMON="$APPS_BRAND/SinaAppRouter.swift $APPS_BRAND/SinaStandaloneShell.swift"
/usr/bin/swiftc -O -o "$STAGE/Contents/MacOS/${EXEC_NAME}" $SWIFT_COMMON "$SWIFT_SRC" -framework Cocoa -framework WebKit
chmod +x "$STAGE/Contents/MacOS/${EXEC_NAME}"

if [[ -f "$ICNS" ]]; then
  cp "$ICNS" "$STAGE/Contents/Resources/AppIcon.icns"
fi

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
  <key>CFBundleShortVersionString</key><string>${APP_VER}</string>
  <key>CFBundleVersion</key><string>${APP_VER_BUILD}</string>
  <key>LSMinimumSystemVersion</key><string>12.0</string>
  <key>NSPrincipalClass</key><string>NSApplication</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>NSAppTransportSecurity</key>
  <dict>
    <key>NSAllowsLocalNetworking</key><true/>
  </dict>
  <key>LSEnvironment</key>
  <dict>
    <key>AG_ROUTING_PANEL_PORT</key><string>8782</string>
    <key>AG_ROUTING_PANEL_STANDALONE</key><string>1</string>
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

echo "→ Installing to Desktop + Applications…"
rm -rf "$DESKTOP" "$APPS_HOME"
ditto "$STAGE" "$DESKTOP"
ditto "$STAGE" "$APPS_HOME"
sign_app "$DESKTOP"
sign_app "$APPS_HOME"

echo "→ Smoke test (health)…"
COLD_OK=0
for _ in {1..15}; do
  if /usr/bin/curl -sf "http://127.0.0.1:8782/health" >/dev/null 2>&1; then
    echo "✓ Health OK — AG Routing Panel :8782"
    COLD_OK=1
    break
  fi
  sleep 0.5
done
if [[ "$COLD_OK" != "1" ]]; then
  echo "→ Starting server for smoke test…"
  AG_ROUTING_PANEL_PORT=8782 python3 "$ROOT/scripts/ag-routing-panel-server.py" &
  SPID=$!
  sleep 1
  for _ in {1..10}; do
    if /usr/bin/curl -sf "http://127.0.0.1:8782/health" >/dev/null 2>&1; then
      echo "✓ Health OK — AG Routing Panel :8782"
      COLD_OK=1
      break
    fi
    sleep 0.3
  done
  kill "$SPID" 2>/dev/null || true
fi
if [[ "$COLD_OK" != "1" ]]; then
  echo "WARN: health check failed — see ~/.sina/ag-routing-panel-app-launch.log" >&2
fi

echo ""
echo "✓ ${APP_NAME}.app installed:"
echo "  Desktop:      $DESKTOP"
echo "  Applications: $APPS_HOME"
echo "  URL:          http://127.0.0.1:8782/"
