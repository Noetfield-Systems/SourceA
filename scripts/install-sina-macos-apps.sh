#!/bin/zsh
# Install beautiful macOS .app shortcuts on Desktop (custom icons, no .command circus).
set -euo pipefail

SA="$(cd "$(dirname "$0")/.." && pwd)"
POS="$HOME/Desktop/SinaPromptOS"
DESKTOP="$HOME/Desktop"
ICNS_DIR="$SA/brand/icons/icns"
APPS_DIR="$SA/brand/macos-apps"

python3 "$SA/scripts/build_sina_icons.py"

# ── Build .app bundle ─────────────────────────────────────────────────────────
mkapp() {
  local app_name="$1"
  local icon_id="$2"
  local bundle_id="$3"
  local launch_script="$4"

  local app_path="$APPS_DIR/${app_name}.app"
  local contents="$app_path/Contents"
  local macos="$contents/MacOS"
  local resources="$contents/Resources"

  rm -rf "$app_path"
  mkdir -p "$macos" "$resources"

  local icns="$ICNS_DIR/${icon_id}.icns"
  if [[ -f "$icns" ]]; then
    cp "$icns" "$resources/AppIcon.icns"
  fi

  cat > "$contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key><string>en</string>
  <key>CFBundleExecutable</key><string>launch</string>
  <key>CFBundleIconFile</key><string>AppIcon</string>
  <key>CFBundleIdentifier</key><string>${bundle_id}</string>
  <key>CFBundleInfoDictionaryVersion</key><string>6.0</string>
  <key>CFBundleName</key><string>${app_name}</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>2.0</string>
  <key>CFBundleVersion</key><string>2</string>
  <key>LSMinimumSystemVersion</key><string>11.0</string>
  <key>LSUIElement</key><false/>
  <key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
PLIST

  cat > "$macos/launch" <<'HEADER'
#!/bin/zsh
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:/usr/bin:/bin:/usr/sbin:/sbin"
HEADER
  cat >> "$macos/launch" <<LAUNCH
${launch_script}
LAUNCH
  chmod +x "$macos/launch"

  # Copy to Desktop (replace old .command with real app)
  rm -f "$DESKTOP/${app_name}.command" 2>/dev/null || true
  rm -rf "$DESKTOP/${app_name}.app" 2>/dev/null || true
  ditto "$app_path" "$DESKTOP/${app_name}.app"
  # Gatekeeper: clear quarantine + ad-hoc sign so Finder double-click works
  xattr -cr "$DESKTOP/${app_name}.app" 2>/dev/null || true
  ENT="$SA/brand/macos-apps/entitlements-local.plist"
  if [[ -f "$ENT" ]]; then
    codesign -s - --force --deep --entitlements "$ENT" --timestamp=none "$DESKTOP/${app_name}.app" 2>/dev/null || \
      codesign -s - --force --deep "$DESKTOP/${app_name}.app" 2>/dev/null || true
  else
    codesign -s - --force --deep "$DESKTOP/${app_name}.app" 2>/dev/null || true
  fi
  LSREG="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
  [[ -x "$LSREG" ]] && "$LSREG" -f -R -trusted "$DESKTOP/${app_name}.app" 2>/dev/null || true
  echo "✓ Desktop/${app_name}.app"
}

LAUNCHER="$SA/scripts/sina-unified-launcher.sh"
SERVE="$SA/scripts/serve-sina-command.sh"
RUN_UI="$POS/scripts/run-ui.sh"

# Sina Command — hub (silent server + browser)
mkapp "Sina Command" "sina-command" "com.sina.command" "
export SINA_COMMAND_PORT=\"\${SINA_COMMAND_PORT:-13020}\"
export PATH=\"/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:/usr/bin:/bin:/usr/sbin:/sbin\"
\"$SERVE\" || true
for i in 1 2 3 4 5 6 7 8 9 10; do
  /usr/bin/curl -sf \"http://127.0.0.1:\${SINA_COMMAND_PORT}/health\" >/dev/null 2>&1 && break
  sleep 0.5
done
if ! /usr/bin/curl -sf \"http://127.0.0.1:\${SINA_COMMAND_PORT}/health\" >/dev/null 2>&1; then
  err=\$(grep -E 'Error|Traceback|Address already' \"\$HOME/.sina/command-server.log\" 2>/dev/null | tail -2 | tr '\n' ' ')
  osascript -e \"display alert \\\"Sina Command\\\" message \\\"Server not ready. See ~/.sina/command-server.log \${err}\\\"\"
  exit 1
fi
open \"http://127.0.0.1:\${SINA_COMMAND_PORT}/?tab=command\"
"

# Prompt OS UI — Streamlit in background, no Terminal window
mkapp "Sina Prompt OS" "sina-promptos" "com.sina.promptos" "
POS=\"$POS\"
LOG=\"\$HOME/.sina/promptos-ui.log\"
mkdir -p \"\$HOME/.sina\"
if [[ -f \"\$HOME/.sina/secrets.env\" ]]; then set -a; source \"\$HOME/.sina/secrets.env\"; set +a; fi
if ! curl -sf http://127.0.0.1:8765/_stcore/health >/dev/null 2>&1; then
  \"\$POS/scripts/start-promptos-ui.sh\" >>\"\$LOG\" 2>&1 || true
  for i in {1..30}; do
    curl -sf http://127.0.0.1:8765/_stcore/health >/dev/null 2>&1 && break
    sleep 0.5
  done
fi
open \"http://127.0.0.1:8765\"
"

# Mini-apps → hub Connected Apps (auto-run engine or open UI)
mkapp "Sina Dispatch" "sina-dispatch" "com.sina.dispatch" "exec \"$LAUNCHER\" dispatch"
mkapp "Sina Execute All" "sina-execute" "com.sina.execute" "exec \"$LAUNCHER\" execute"
mkapp "Sina Decide" "sina-decide" "com.sina.decide" "exec \"$LAUNCHER\" decide"
mkapp "Sina Run Now" "sina-run" "com.sina.run" "exec \"$LAUNCHER\" run"
mkapp "Sina Status" "sina-status" "com.sina.status" "exec \"$LAUNCHER\" status"

# Hub entry that opens Connected Apps tab
mkapp "Sina Command Apps" "sina-command" "com.sina.command.apps" "exec \"$LAUNCHER\" apps"

# Mac Health Guard — self-contained double-click app (no hub, no browser)
bash "$SA/scripts/build-mac-health-standalone-app-v1.sh" 2>/dev/null || mkapp "Mac Health Guard" "sina-mac-health" "com.sina.machealth" "exec \"$SA/scripts/mac-health-desktop-open.sh\""

# Apple Health — self-contained double-click app (no hub, no browser)
bash "$SA/scripts/build-apple-health-standalone-app-v1.sh" 2>/dev/null || mkapp "Apple Health" "sina-apple-health" "com.sina.applehealth" "exec \"$LAUNCHER\" apple-health"

# Chat Unify — self-contained double-click app (no hub, no browser)
bash "$SA/scripts/build-chat-unify-standalone-app-v1.sh" 2>/dev/null || mkapp "Chat Unify" "sina-chat-unify" "com.sina.chatunify" "exec \"$LAUNCHER\" chat-unify"

# Cloud Workers — command center standalone
bash "$SA/scripts/build-cloud-workers-standalone-app-v1.sh" 2>/dev/null || true

# Retire legacy Terminal shortcuts
for old in \
  "Sina Command.command" "Sina Dispatch.command" "Sina Execute All.command" \
  "Sina Decide.command" "Sina Run Now.command" "Sina Status.command" \
  "Sina Prompt OS.command" "Sina Prompt OS UI.command" "Sina Prompt OS Hub.command" \
  "Sina Command Apps.command"; do
  [[ -f "$DESKTOP/$old" ]] && rm -f "$DESKTOP/$old" && echo "  removed legacy $old"
done

echo ""
echo "Done. Desktop .app shortcuts have custom icons."
echo "First launch: if macOS blocks, right-click the app → Open once."
