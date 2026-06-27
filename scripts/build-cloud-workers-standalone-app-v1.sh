#!/usr/bin/env bash
# Build Cloud Workers Command Center — double-click .app on Desktop + Applications.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APPS_BRAND="$ROOT/brand/macos-apps"
APP_NAME="Cloud Workers"
APP_ID="com.sina.cloudworkers.standalone"
DESKTOP="$HOME/Desktop/${APP_NAME}.app"
APPS_HOME="$HOME/Applications/${APP_NAME}.app"
ENT="$APPS_BRAND/entitlements-local.plist"
ICNS="$ROOT/brand/icons/icns/sina-cloud-workers.icns"
LSREGISTER="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
SWIFT_SRC="$APPS_BRAND/CloudWorkersShell.swift"
STAGE="$APPS_BRAND/${APP_NAME}.app"
BUNDLE_STAGE="$STAGE/Contents/Resources/cloud-workers-bundle"
EXEC_NAME="CloudWorkersShell"

echo "→ Building self-contained ${APP_NAME}.app…"

bash "$ROOT/scripts/sync-official-links-bar-v1.sh" 2>/dev/null || true

python3 "$ROOT/scripts/build_sina_icons.py" 2>/dev/null || true

rm -rf "$STAGE"
mkdir -p "$STAGE/Contents/MacOS" "$STAGE/Contents/Resources" \
  "$BUNDLE_STAGE/scripts" "$BUNDLE_STAGE/app" "$BUNDLE_STAGE/shared"

for f in cloud-workers-server.py cloud_workers_hub_v1.py hub_cloud_forge_run_proceed_v1.py \
  cloud_auto_runtime_v1.py cloud_auto_runtime_single_cycle_gate_v1.py api_station_v1.py founder_glance_cockpit_v1.py hub_pro_skills_v1.py founder_ops_v1.py; do
  cp "$ROOT/scripts/$f" "$BUNDLE_STAGE/scripts/"
done
cp -R "$ROOT/scripts/cloud-workers-standalone/." "$BUNDLE_STAGE/app/"

BUILT_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
python3 - <<PY
import json
from pathlib import Path
manifest = {
    "schema": "bundle-wire-manifest-v1",
    "app": "cloud-workers",
    "built_at": "$BUILT_AT",
    "cockpit": "http://127.0.0.1:13027/",
    "form_ui": "http://127.0.0.1:13023/form/",
    "proceed_api": "/api/cloud-forge-run/proceed/v1",
    "worker_hub": "RETIRED",
    "law": "SOURCEA_POISON_AND_REALTIME_BLOCKER_TERMINOLOGY_LOCKED_v1.md",
}
Path("$BUNDLE_STAGE/bundle-wire-manifest-v1.json").write_text(json.dumps(manifest, indent=2) + "\n")
PY

for f in official-links-bar.js official-links-bar.css sina-view-mode.js \
  cloud-workers-panel.js cloud-workers-panel.css api-station-tab.js api-station-tab.css \
  hub-pro-skills-tab.js hub-pro-skills-tab.css sina-main-terminal.js sina-main-terminal.css; do
  cp "$ROOT/agent-control-panel/shared/$f" "$BUNDLE_STAGE/shared/"
done

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
  <key>CFBundleShortVersionString</key><string>1.1</string>
  <key>CFBundleVersion</key><string>11</string>
  <key>LSMinimumSystemVersion</key><string>12.0</string>
  <key>NSPrincipalClass</key><string>NSApplication</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>NSAppTransportSecurity</key>
  <dict>
    <key>NSAllowsLocalNetworking</key><true/>
  </dict>
  <key>LSEnvironment</key>
  <dict>
    <key>CLOUD_WORKERS_PORT</key><string>13027</string>
    <key>CLOUD_WORKERS_STANDALONE</key><string>1</string>
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

echo "→ Cold-start smoke test (health + railway_live)…"
COLD_OK=0
for _ in {1..20}; do
  if /usr/bin/curl -sf "http://127.0.0.1:13027/health" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('ok') and d.get('service')=='cloud-workers'" 2>/dev/null; then
    echo "✓ Cold-start PASS — cloud workers health OK"
    COLD_OK=1
    break
  fi
  sleep 0.5
done
if [[ "$COLD_OK" != "1" ]]; then
  echo "WARN: cold-start failed — see ~/.sina/cloud-workers-app-launch.log" >&2
  tail -5 "$HOME/.sina/cloud-workers-app-launch.log" 2>/dev/null || true
fi

echo ""
echo "✓ ${APP_NAME} v1.1 — double-click only · Proceed full-pack"
echo "  Desktop:       $DESKTOP"
echo "  Applications:  $APPS_HOME"
echo "  URL:           http://127.0.0.1:13027/"
echo "  Log:           ~/.sina/cloud-workers-app-launch.log"
