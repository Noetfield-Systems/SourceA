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

bash "$ROOT/scripts/sync-official-links-bar-v1.sh" 2>/dev/null || true
CU_TERMINAL="$ROOT/scripts/chat-unify-standalone/terminal"
if [[ ! -f "$CU_TERMINAL/terminal.js" ]]; then
  echo "✗ missing $CU_TERMINAL/terminal.js — restore Chat Unify 4.9.9 terminal before build" >&2
  exit 1
fi
echo "→ Chat Unify 4.9.9 terminal motor at $CU_TERMINAL (not forge-terminal-v1)"

python3 "$ROOT/scripts/build_sina_icons.py" 2>/dev/null || true

rm -rf "$STAGE"
mkdir -p "$STAGE/Contents/MacOS" "$STAGE/Contents/Resources" \
  "$BUNDLE_STAGE/scripts" "$BUNDLE_STAGE/app" "$BUNDLE_STAGE/prompts" \
  "$BUNDLE_STAGE/form" "$BUNDLE_STAGE/shared"

CU_FORM_SCRIPTS=(
  chat-unify-server.py chat_unify_merge.py chat_unify_proof_pack_v1.py chat_unify_prompt_forge_v1.py chat_unify_vocabulary_intelligence_v1.py vocabulary_intelligence_scan_v1.py chat_unify_integrations_v1.py chat_unify_platform_catalog_v1.py
  chat_unify_kernel_v1.py chat_unify_truth_gate_v1.py chat_ord_loop_v1.py
  chat_ord_atoms_v1.py chat_ord_claim_rules_v1.py chat_founder_loop_v1.py
  chat_founder_language_v1.py chat_founder_reasoning_v1.py prompt_forge_pipeline_v1.py
  chat_unify_live_http_verify_v1.py ai_unify_api_v1.py clipboard_safe.py cursor_window_preflight_v1.py chat_unify_update_check_v1.py
  hub_form_submit_v1.py live_founder_decision_form_v1.py form_official_canvas_route_v1.py
  form_founder_supremacy_guard_v1.py governance_paths_v1.py api_station_v1.py
  founder_glance_cockpit_v1.py canvas_form_apply_picks_v1.py canvas_form_submit_v1.py hub_pro_skills_v1.py
  chat_unify_ide_v1.py chat_unify_terminal_motor_v1.py chat_unify_engine_v1.py chat_unify_smart_router_v1.py forge_terminal_v1.py
  workspace_kernel_v2.py model_dispatch.py worker_inject_lib.py
)
for f in "${CU_FORM_SCRIPTS[@]}"; do
  cp "$ROOT/scripts/$f" "$BUNDLE_STAGE/scripts/"
done
cp -R "$ROOT/scripts/chat-unify-standalone/." "$BUNDLE_STAGE/app/"
cp "$ROOT/scripts/chat-unify-standalone/api-station-tab.js" "$BUNDLE_STAGE/app/api-station-tab.js"
cp "$ROOT/scripts/chat-unify-standalone/connect-tab.js" "$BUNDLE_STAGE/app/connect-tab.js"
if [[ -f "$BUNDLE_STAGE/app/terminal/index.html" ]]; then
  sed -i '' \
    -e 's/Forge Terminal tools/Chat Unify Terminal Motor tools/g' \
    -e 's/built for Forge Terminal only/built for Chat Unify Terminal Motor/g' \
    -e 's/aria-label="Forge Terminal tools"/aria-label="Chat Unify Terminal Motor tools"/g' \
    "$BUNDLE_STAGE/app/terminal/index.html"
fi
cp -R "$ROOT/agent-control-panel/form/." "$BUNDLE_STAGE/form/"
for f in official-links-bar.js official-links-bar.css sina-main-terminal.js sina-main-terminal.css \
  api-station-tab.js api-station-tab.css hub-pro-skills-tab.js hub-pro-skills-tab.css sina-view-mode.js; do
  cp "$ROOT/agent-control-panel/shared/$f" "$BUNDLE_STAGE/shared/" 2>/dev/null || true
  cp "$ROOT/agent-control-panel/shared/$f" "$BUNDLE_STAGE/app/" 2>/dev/null || true
done
cp "$ROOT/agent-control-panel/shared/official-links-bar.js" "$BUNDLE_STAGE/app/official-links-bar.js"
cp "$ROOT/agent-control-panel/shared/sina-main-terminal.js" "$BUNDLE_STAGE/app/sina-main-terminal.js"
cp "$ROOT/agent-control-panel/shared/sina-main-terminal.css" "$BUNDLE_STAGE/app/sina-main-terminal.css"
cp "$ROOT/agent-control-panel/shared/official-links-bar.css" "$BUNDLE_STAGE/app/official-links-bar.css" 2>/dev/null || true
cp "$ROOT/CHAT_EXTRACT_UNIFY_PROMPT.txt" "$BUNDLE_STAGE/prompts/" 2>/dev/null || true
cp "$ROOT/CHAT_UNIFY_ROLLUP_PROMPT.txt" "$BUNDLE_STAGE/prompts/" 2>/dev/null || true

BUILT_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
python3 - <<PY
import json
from pathlib import Path
manifest = {
    "schema": "bundle-wire-manifest-v1",
    "app": "chat-unify",
    "built_at": "$BUILT_AT",
    "ui_version": "4.9.9-cu-combined",
    "cockpit": "http://127.0.0.1:13027/",
    "form_ui": "http://127.0.0.1:13023/form/",
    "form_api": "/api/live-founder-decision-form-v1",
    "worker_hub": "RETIRED",
    "law": "SOURCEA_POISON_AND_REALTIME_BLOCKER_TERMINOLOGY_LOCKED_v1.md",
}
Path("$BUNDLE_STAGE/bundle-wire-manifest-v1.json").write_text(json.dumps(manifest, indent=2) + "\n")
PY

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
  <key>CFBundleShortVersionString</key><string>4.9.9</string>
  <key>CFBundleVersion</key><string>499</string>
  <key>LSMinimumSystemVersion</key><string>12.0</string>
  <key>NSPrincipalClass</key><string>NSApplication</string>
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
  # shellcheck source=/dev/null
  source "$ROOT/scripts/sina-macos-codesign-v1.sh"
  sign_sina_app_bundle "$app" "$ENT" "$EXEC_NAME" || {
    local rc=$?
    if [[ "$rc" -eq 2 ]]; then
      echo "  Local dev: Right-click app → Open once, or run: bash scripts/trust-portfolio-desktop-apps-v1.sh" >&2
    fi
    return 0
  }
  [[ -x "$LSREGISTER" ]] && "$LSREGISTER" -f -R -trusted "$app" 2>/dev/null || true
}

echo "→ Installing to Desktop + Applications (real .app, not alias)…"
rm -rf "$DESKTOP" "$APPS_HOME"
ditto "$STAGE" "$DESKTOP"
ditto "$STAGE" "$APPS_HOME"
bash "$ROOT/scripts/sync-chat-unify-bundle-v1.sh"
sign_app "$DESKTOP"
sign_app "$APPS_HOME"

echo "→ Cold-start smoke test (health + form wire)…"
lsof -ti:13023 | xargs kill -9 2>/dev/null || true
sleep 0.5
COLD_OK=0
for _ in {1..20}; do
  if /usr/bin/curl -sf "http://127.0.0.1:13023/health" >/dev/null 2>&1 \
    && /usr/bin/curl -sf -o /dev/null -w "%{http_code}" "http://127.0.0.1:13023/form/" | grep -q 200 \
    && /usr/bin/curl -sf "http://127.0.0.1:13023/api/live-founder-decision-form-v1" | python3 -c "import sys,json; d=json.load(sys.stdin); assert '13023/form' in (d.get('form_page_url') or '')" 2>/dev/null; then
    echo "✓ Cold-start PASS — chat unify health + form API wired"
    COLD_OK=1
    break
  fi
  sleep 0.5
done
if [[ "$COLD_OK" != "1" ]]; then
  echo "WARN: cold-start failed — see ~/.sina/chat-unify-app-launch.log" >&2
  tail -5 "$HOME/.sina/chat-unify-app-launch.log" 2>/dev/null || true
fi

echo ""
echo "✓ ${APP_NAME} v1.3 — double-click only · form at :13023/form/"
echo "  Desktop:       $DESKTOP"
echo "  Applications:  $APPS_HOME"
echo "  Entry:         native ChatUnifyShell (starts bundled server + own window)"
echo "  Log:           ~/.sina/chat-unify-app-launch.log"
