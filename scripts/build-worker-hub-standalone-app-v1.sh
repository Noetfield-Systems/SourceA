#!/usr/bin/env bash
# Build Worker Hub — true double-click .app, no Terminal, own window (WKWebView).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APPS_BRAND="$ROOT/brand/macos-apps"
APP_NAME="Worker Hub"
APP_ID="com.sina.workerhub.standalone"
DESKTOP="$HOME/Desktop/${APP_NAME}.app"
APPS_HOME="$HOME/Applications/${APP_NAME}.app"
ENT="$APPS_BRAND/entitlements-local.plist"
ICNS="$ROOT/brand/icons/icns/sina-worker-hub.icns"
LSREGISTER="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
SWIFT_SRC="$APPS_BRAND/WorkerHubShell.swift"
STAGE="$APPS_BRAND/${APP_NAME}.app"
BUNDLE_STAGE="$STAGE/Contents/Resources/worker-hub-bundle"
EXEC_NAME="WorkerHubShell"

echo "→ Building self-contained ${APP_NAME}.app…"
python3 "$ROOT/scripts/build_sina_icons.py" 2>/dev/null || true

rm -rf "$STAGE"
mkdir -p "$STAGE/Contents/MacOS" "$STAGE/Contents/Resources" "$BUNDLE_STAGE/scripts"
cp "$ROOT/scripts/worker-hub-stack-boot.sh" "$BUNDLE_STAGE/scripts/"
chmod +x "$BUNDLE_STAGE/scripts/worker-hub-stack-boot.sh"

SWIFT_COMMON="$APPS_BRAND/SinaAppRouter.swift $APPS_BRAND/SinaStandaloneShell.swift"
/usr/bin/swiftc -O -o "$STAGE/Contents/MacOS/${EXEC_NAME}" $SWIFT_COMMON "$SWIFT_SRC" -framework Cocoa -framework WebKit
chmod +x "$STAGE/Contents/MacOS/${EXEC_NAME}"

if [[ -f "$ICNS" ]]; then cp "$ICNS" "$STAGE/Contents/Resources/AppIcon.icns"; fi

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
  <key>CFBundleVersion</key><string>12</string>
  <key>LSMinimumSystemVersion</key><string>12.0</string>
  <key>NSPrincipalClass</key><string>NSApplication</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>NSAppTransportSecurity</key>
  <dict><key>NSAllowsLocalNetworking</key><true/></dict>
  <key>LSEnvironment</key>
  <dict>
    <key>SINA_COMMAND_PORT</key><string>13020</string>
    <key>WORKER_HUB_STANDALONE</key><string>1</string>
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
bash "$ROOT/scripts/trust-portfolio-desktop-apps-v1.sh" >/dev/null 2>&1 || true

echo "→ Cold-start smoke test (health only, no open)…"
COLD_OK=0
for _ in {1..15}; do
  if /usr/bin/curl -sf "http://127.0.0.1:13020/health" >/dev/null 2>&1; then
    echo "✓ Cold-start PASS — hub health OK"
    COLD_OK=1
    break
  fi
  sleep 0.5
done
[[ "$COLD_OK" != "1" ]] && echo "WARN: cold-start failed — see ~/.sina/worker-hub-app-launch.log" >&2

echo ""
echo "✓ ${APP_NAME} v1.1 — double-click · Noetfield-Systems/SourceA path"
echo "  Desktop:       $DESKTOP"
echo "  Applications:  $APPS_HOME"
