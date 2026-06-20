#!/usr/bin/env bash
# Build N8N Integration — true double-click .app, no Terminal, no hub, no browser.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APPS_BRAND="$ROOT/brand/macos-apps"
APP_NAME="N8N Integration"
APP_ID="com.sina.n8nintegration.standalone"
DESKTOP="$HOME/Desktop/${APP_NAME}.app"
APPS_HOME="$HOME/Applications/${APP_NAME}.app"
ENT="$APPS_BRAND/entitlements-local.plist"
ICNS="$ROOT/brand/icons/icns/sina-n8n-integration.icns"
LSREGISTER="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
SWIFT_SRC="$APPS_BRAND/N8nIntegrationShell.swift"
STAGE="$APPS_BRAND/${APP_NAME}.app"
BUNDLE_STAGE="$STAGE/Contents/Resources/n8n-integration-bundle"
EXEC_NAME="N8nIntegrationShell"

echo "→ Building self-contained ${APP_NAME}.app…"

python3 "$ROOT/scripts/build_sina_icons.py" 2>/dev/null || true

rm -rf "$STAGE"
mkdir -p "$STAGE/Contents/MacOS" "$STAGE/Contents/Resources" "$BUNDLE_STAGE/scripts" "$BUNDLE_STAGE/app"

for f in n8n-integration-server.py n8n_integration_core.py n8n_automation.py n8n_intelligence.py n8n_glue_runner_v1.py n8n_glue_config_v1.py n8n_bootstrap_substrate_v1.py n8n_workflow_factory_v1.py governance_n8n_openrouter_wire_v1.py founder-start-n8n.sh; do
  cp "$ROOT/scripts/$f" "$BUNDLE_STAGE/scripts/"
done
cp -R "$ROOT/scripts/fixtures/n8n" "$BUNDLE_STAGE/scripts/fixtures/" 2>/dev/null || mkdir -p "$BUNDLE_STAGE/scripts/fixtures"
if [[ -d "$ROOT/scripts/fixtures/n8n" ]]; then
  cp -R "$ROOT/scripts/fixtures/n8n" "$BUNDLE_STAGE/scripts/fixtures/"
fi
cp -R "$ROOT/scripts/n8n-standalone/." "$BUNDLE_STAGE/app/"

/usr/bin/swiftc -O -o "$STAGE/Contents/MacOS/${EXEC_NAME}" "$SWIFT_SRC" -framework Cocoa -framework WebKit
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
  <key>CFBundleShortVersionString</key><string>1.1</string>
  <key>CFBundleVersion</key><string>11</string>
  <key>LSMinimumSystemVersion</key><string>12.0</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>NSAppTransportSecurity</key>
  <dict>
    <key>NSAllowsLocalNetworking</key><true/>
  </dict>
  <key>LSEnvironment</key>
  <dict>
    <key>N8N_INTEGRATION_PORT</key><string>13026</string>
    <key>N8N_INTEGRATION_STANDALONE</key><string>1</string>
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

echo "→ Cold-start smoke test…"
pkill -f "n8n-integration-server.py" 2>/dev/null || true
pkill -f "N8nIntegrationShell" 2>/dev/null || true
sleep 2
open "$DESKTOP"
COLD_OK=0
for _ in {1..20}; do
  if /usr/bin/curl -sf "http://127.0.0.1:13026/health" >/dev/null 2>&1; then
    echo "✓ Cold-start PASS — heart up after double-click"
    COLD_OK=1
    break
  fi
  sleep 1
done
if [[ "$COLD_OK" != "1" ]]; then
  echo "WARN: cold-start failed — see ~/.sina/n8n-integration-app-launch.log" >&2
  tail -5 "$HOME/.sina/n8n-integration-app-launch.log" 2>/dev/null || true
fi

echo ""
echo "✓ ${APP_NAME} v1.1 — double-click only"
echo "  Desktop:       $DESKTOP"
echo "  Applications:  $APPS_HOME"
echo "  Entry:         native N8nIntegrationShell (starts bundled server + own window)"
echo "  Log:           ~/.sina/n8n-integration-app-launch.log"
