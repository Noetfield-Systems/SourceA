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

APP_VER="$(python3 -c "import re; m=re.search(r'VERSION = \"([^\"]+)\"', open('$ROOT/scripts/n8n_integration_core.py').read()); print(m.group(1) if m else '1.8.0')")"
APP_VER_BUILD="$(echo "$APP_VER" | tr -d '.')"
echo "→ Building self-contained ${APP_NAME}.app v${APP_VER}…"

bash "$ROOT/scripts/sync-official-links-bar-v1.sh" 2>/dev/null || true

python3 "$ROOT/scripts/build_sina_icons.py" 2>/dev/null || true

rm -rf "$STAGE"
mkdir -p "$STAGE/Contents/MacOS" "$STAGE/Contents/Resources" "$BUNDLE_STAGE/scripts" "$BUNDLE_STAGE/app"

for f in n8n-integration-server.py n8n_integration_core.py n8n_automation.py n8n_intelligence.py n8n_glue_runner_v1.py n8n_glue_config_v1.py n8n_bootstrap_substrate_v1.py n8n_workflow_factory_v1.py n8n_chat_unify_wire_v1.py portfolio_mail_integration_wire_v1.py n8n_commercial_grade_v1.py api_station_v1.py founder_glance_cockpit_v1.py governance_n8n_openrouter_wire_v1.py founder-start-n8n.sh living_system_chain_validate_v1.py cloud_workers_hub_v1.py validator_machine_v1.py hub_pro_skills_v1.py; do
  cp "$ROOT/scripts/$f" "$BUNDLE_STAGE/scripts/"
done
cp -R "$ROOT/scripts/fixtures/n8n" "$BUNDLE_STAGE/scripts/fixtures/" 2>/dev/null || mkdir -p "$BUNDLE_STAGE/scripts/fixtures"
if [[ -d "$ROOT/scripts/fixtures/n8n" ]]; then
  cp -R "$ROOT/scripts/fixtures/n8n" "$BUNDLE_STAGE/scripts/fixtures/"
fi
cp -R "$ROOT/scripts/n8n-standalone/." "$BUNDLE_STAGE/app/"
cp "$ROOT/agent-control-panel/shared/official-links-bar.js" "$BUNDLE_STAGE/app/official-links-bar.js"
cp "$ROOT/agent-control-panel/shared/sina-view-mode.js" "$BUNDLE_STAGE/app/sina-view-mode.js"
cp "$ROOT/agent-control-panel/shared/api-station-tab.js" "$BUNDLE_STAGE/app/api-station-tab.js"
cp "$ROOT/agent-control-panel/shared/hub-pro-skills-tab.js" "$BUNDLE_STAGE/app/hub-pro-skills-tab.js"
cp "$ROOT/agent-control-panel/shared/sina-main-terminal.js" "$BUNDLE_STAGE/app/sina-main-terminal.js"
cp "$ROOT/agent-control-panel/shared/sina-main-terminal.css" "$BUNDLE_STAGE/app/sina-main-terminal.css"
cp "$ROOT/agent-control-panel/shared/official-links-bar.css" "$BUNDLE_STAGE/app/official-links-bar.css" 2>/dev/null || true
cp "$ROOT/agent-control-panel/shared/api-station-tab.css" "$BUNDLE_STAGE/app/api-station-tab.css" 2>/dev/null || true
cp "$ROOT/agent-control-panel/shared/hub-pro-skills-tab.css" "$BUNDLE_STAGE/app/hub-pro-skills-tab.css" 2>/dev/null || true

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

echo "→ Cold-start smoke test (health only, no open)…"
COLD_OK=0
for _ in {1..15}; do
  if /usr/bin/curl -sf "http://127.0.0.1:13026/health" >/dev/null 2>&1; then
    echo "✓ Cold-start PASS — n8n integration health OK"
    COLD_OK=1
    break
  fi
  sleep 0.5
done
if [[ "$COLD_OK" != "1" ]]; then
  echo "WARN: cold-start failed — see ~/.sina/n8n-integration-app-launch.log" >&2
  tail -5 "$HOME/.sina/n8n-integration-app-launch.log" 2>/dev/null || true
fi

echo ""
echo "✓ ${APP_NAME} v${APP_VER} — double-click only"
echo "  Desktop:       $DESKTOP"
echo "  Applications:  $APPS_HOME"
echo "  Entry:         native N8nIntegrationShell (starts bundled server + own window)"
echo "  Log:           ~/.sina/n8n-integration-app-launch.log"
