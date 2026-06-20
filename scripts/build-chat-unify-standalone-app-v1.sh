#!/usr/bin/env bash
# Build Chat Unify — true double-click .app, no Terminal, no hub, no browser.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APPS_BRAND="$ROOT/brand/macos-apps"
APP_NAME="Chat Unify"
APP_ID="com.sina.chatunify.standalone"
DESKTOP="$HOME/Desktop/${APP_NAME}.app"
APPS_HOME="$HOME/Applications/${APP_NAME}.app"
ENT="$APPS_BRAND/entitlements-local.plist"
ICNS="$ROOT/brand/icons/icns/sina-chat-unify.icns"
LSREGISTER="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
SWIFT_SRC="$APPS_BRAND/ChatUnifyShell.swift"
STAGE="$APPS_BRAND/${APP_NAME}.app"
BUNDLE_STAGE="$STAGE/Contents/Resources/chat-unify-bundle"
EXEC_NAME="ChatUnifyShell"

echo "→ Building self-contained ${APP_NAME}.app…"

python3 "$ROOT/scripts/build_sina_icons.py" 2>/dev/null || true

rm -rf "$STAGE"
mkdir -p "$STAGE/Contents/MacOS" "$STAGE/Contents/Resources" "$BUNDLE_STAGE/scripts" "$BUNDLE_STAGE/app" "$BUNDLE_STAGE/prompts"

for f in chat-unify-server.py chat_unify_merge.py clipboard_safe.py cursor_window_preflight_v1.py \
  chat_founder_language_v1.py chat_founder_reasoning_v1.py chat_founder_loop_v1.py chat_ord_loop_v1.py; do
  cp "$ROOT/scripts/$f" "$BUNDLE_STAGE/scripts/"
done
cp -R "$ROOT/scripts/chat-unify-standalone/." "$BUNDLE_STAGE/app/"
cp "$ROOT/CHAT_EXTRACT_UNIFY_PROMPT.txt" "$BUNDLE_STAGE/prompts/" 2>/dev/null || true
cp "$ROOT/CHAT_UNIFY_ROLLUP_PROMPT.txt" "$BUNDLE_STAGE/prompts/" 2>/dev/null || true

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
  <key>CFBundleShortVersionString</key><string>1.2</string>
  <key>CFBundleVersion</key><string>12</string>
  <key>LSMinimumSystemVersion</key><string>12.0</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>NSAppTransportSecurity</key>
  <dict>
    <key>NSAllowsLocalNetworking</key><true/>
  </dict>
  <key>LSEnvironment</key>
  <dict>
    <key>CHAT_UNIFY_PORT</key><string>13023</string>
    <key>CHAT_UNIFY_STANDALONE</key><string>1</string>
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
pkill -f "chat-unify-server.py" 2>/dev/null || true
pkill -f "ChatUnifyShell" 2>/dev/null || true
sleep 2
open "$DESKTOP"
COLD_OK=0
for _ in {1..20}; do
  if /usr/bin/curl -sf "http://127.0.0.1:13023/health" >/dev/null 2>&1; then
    echo "✓ Cold-start PASS — heart up after double-click"
    COLD_OK=1
    break
  fi
  sleep 1
done
if [[ "$COLD_OK" != "1" ]]; then
  echo "WARN: cold-start failed — see ~/.sina/chat-unify-app-launch.log" >&2
  tail -5 "$HOME/.sina/chat-unify-app-launch.log" 2>/dev/null || true
fi

echo ""
echo "✓ ${APP_NAME} v1.2 — double-click only"
echo "  Desktop:       $DESKTOP"
echo "  Applications:  $APPS_HOME"
echo "  Entry:         native ChatUnifyShell (starts bundled server + own window)"
echo "  Log:           ~/.sina/chat-unify-app-launch.log"
