#!/usr/bin/env bash
# Build Forge Terminal — true double-click .app (Swift WebKit shell + bundled Python server).
# Verified pattern: Sina Prompt OS native shells (ChatUnifyShell / N8nIntegrationShell).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APPS_BRAND="$ROOT/brand/macos-apps"
APP_NAME="Forge Terminal"
APP_ID="com.sina.forgeterminal.standalone"
DESKTOP="$HOME/Desktop/${APP_NAME}.app"
APPS_HOME="$HOME/Applications/${APP_NAME}.app"
ENT="$APPS_BRAND/entitlements-local.plist"
ICNS="$ROOT/brand/icons/icns/sina-execute.icns"
LSREGISTER="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
SWIFT_SRC="$APPS_BRAND/ForgeTerminalShell.swift"
STAGE="$APPS_BRAND/${APP_NAME}.app"
BUNDLE_STAGE="$STAGE/Contents/Resources/forge-terminal-bundle"
EXEC_NAME="ForgeTerminalShell"
APP_VER="4.0.6-live-window"
APP_VER_BUILD="406"

echo "→ Building self-contained ${APP_NAME}.app v${APP_VER}…"

python3 "$ROOT/scripts/build_sina_icons.py" 2>/dev/null || true

rm -rf "$STAGE"
mkdir -p "$STAGE/Contents/MacOS" "$STAGE/Contents/Resources" \
  "$BUNDLE_STAGE/scripts/fbe/lib" "$BUNDLE_STAGE/app/terminal" \
  "$BUNDLE_STAGE/app/connect" "$BUNDLE_STAGE/form" "$BUNDLE_STAGE/shared" "$BUNDLE_STAGE/prompts"

FT_SCRIPTS=(
  forge-terminal-server.py
  forge_terminal_connect_server_v1.py
  forge_agent_kernel_v1.py
  forge_swarm_blackboard_v1.py
  forge_agent_kernel_v3_swarm.py
  forge_swarm_cloud_dispatch_v1.py
  forge_repo_intel_v1.py
  forge_execution_mesh_v1.py
  forge_civilization_memory_v1.py
  forge_agent_registry_v1.py
  forge_civilization_loop_v1.py
  forge_governance_kernel_v1.py
  forge_governance_legal_v3.py
  forge_geopolitical_legal_v4.py
  forge_economy_v1.py
  forge_prompt_os_compiler_v1.py
  forge_prompt_os_compiler_v2.py
  forge_prompt_os_compiler_v3.py
  forge_world_state_v1.py
  forge_self_build_v1.py
  forge_self_build_v2.py
  forge_self_build_v3.py
  forge_civilization_code_v4.py
  forge_digital_nation_v5.py
  forge_world_system_v6.py
  forge_planetary_consciousness_v7.py
  forge_reality_consciousness_v8.py
  forge_advisor_orchestrator_v1.py
  forge_agent_self_improve_l3_v1.py
  forge_l3_auto_runtime_v1.py
  forge_terminal_v1.py
  forge_quality_gate_v1.py
  forge_terminal_desktop_mesh_v1.py
  forge_terminal_local_auth_v1.py
  forge_terminal_os_bridge_v1.py
  forge_workspace_v1.py
  forge_terminal_e2e_verify_v1.py
  forge_terminal_quality_e2e_verify_v1.py
  forge_terminal_critic_verify_v1.py
  forge_terminal_ui_e2e_verify_v1.py
  forge_terminal_living_ui_e2e_verify_v1.py
  forge_terminal_reply_contract_v1.py
  forge_terminal_execution_matrix_v1.py
  forge_workspace_open_v1.py
  forge_workspace_catalog_v2.py
  forge_terminal_telemetry_v1.py
  workspace_kernel_v2.py
  ai_unify_api_v1.py
  model_dispatch.py
  chat_unify_kernel_v1.py
  chat_unify_prompt_forge_v1.py
  chat_unify_integrations_v1.py
  chat_unify_merge.py
  chat_unify_proof_pack_v1.py
  chat_unify_vocabulary_intelligence_v1.py
  chat_unify_platform_catalog_v1.py
  chat_unify_truth_gate_v1.py
  chat_ord_loop_v1.py
  chat_ord_atoms_v1.py
  chat_ord_claim_rules_v1.py
  chat_founder_loop_v1.py
  chat_founder_language_v1.py
  chat_founder_reasoning_v1.py
  prompt_forge_pipeline_v1.py
  chat_unify_live_http_verify_v1.py
  cloud_workers_hub_v1.py
  mac_focus_freeze_v1.py
  worker_inject_lib.py
  api_station_v1.py
  hub_pro_skills_v1.py
  founder_glance_cockpit_v1.py
  live_founder_decision_form_v1.py
  hub_form_submit_v1.py
  form_official_canvas_route_v1.py
  vocabulary_intelligence_scan_v1.py
)
for f in "${FT_SCRIPTS[@]}"; do
  cp "$ROOT/scripts/$f" "$BUNDLE_STAGE/scripts/"
done
cp -R "$ROOT/scripts/fbe/lib/." "$BUNDLE_STAGE/scripts/fbe/lib/"
cp -R "$ROOT/apps/forge-terminal-v1/." "$BUNDLE_STAGE/app/terminal/"
cp -R "$ROOT/apps/forge-terminal-connect-v1/." "$BUNDLE_STAGE/app/connect/"
# Never sync Connect → Chat Unify during Forge Terminal build (wipes Chat Unify shell).
# Re-run scripts/sync-forge-connect-to-chat-unify-v1.sh only on explicit founder order.
cp -R "$ROOT/agent-control-panel/form/." "$BUNDLE_STAGE/form/"
for f in official-links-bar.js official-links-bar.css sina-main-terminal.js sina-main-terminal.css \
  api-station-tab.js api-station-tab.css hub-pro-skills-tab.js hub-pro-skills-tab.css sina-view-mode.js; do
  cp "$ROOT/agent-control-panel/shared/$f" "$BUNDLE_STAGE/shared/" 2>/dev/null || true
done
cp "$ROOT/CHAT_EXTRACT_UNIFY_PROMPT.txt" "$BUNDLE_STAGE/prompts/" 2>/dev/null || true
cp "$ROOT/CHAT_UNIFY_ROLLUP_PROMPT.txt" "$BUNDLE_STAGE/prompts/" 2>/dev/null || true
mkdir -p "$BUNDLE_STAGE/templates"
cp -R "$ROOT/templates/sourcea-workspace-v2" "$BUNDLE_STAGE/templates/"

BUILT_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
python3 - <<PY
import json
from pathlib import Path
manifest = {
    "schema": "forge-terminal-bundle-manifest-v1",
    "app": "forge-terminal",
    "built_at": "$BUILT_AT",
    "ui_version": "$APP_VER",
    "default_model": "gpt-4o",
    "models": [
        "gpt-4o",
        "gemini-1.5-flash",
        "deepseek-v4",
        "gpt-4o",
        "gemini-1.5-pro",
        "claude-3.5-sonnet",
        "openai-o1",
    ],
    "port": 13029,
}
Path("$BUNDLE_STAGE/bundle-manifest-v1.json").write_text(json.dumps(manifest, indent=2) + "\n")
PY

SWIFT_COMMON="$APPS_BRAND/SinaStandaloneShell.swift"
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
    <key>FORGE_TERMINAL_PORT</key><string>13029</string>
    <key>FORGE_TERMINAL_STANDALONE</key><string>1</string>
  </dict>
</dict>
</plist>
PLIST

sign_app() {
  local app="$1"
  # shellcheck source=/dev/null
  source "$ROOT/scripts/sina-macos-codesign-v1.sh"
  sign_sina_app_bundle "$app" "$ENT" "$EXEC_NAME" || {
    xattr -cr "$app" 2>/dev/null || true
    codesign --force --deep --sign - --timestamp=none "$app" 2>/dev/null || true
  }
  [[ -x "$LSREGISTER" ]] && "$LSREGISTER" -f -R -trusted "$app" 2>/dev/null || true
}

echo "→ Installing to Desktop + Applications…"
rm -rf "$DESKTOP" "$APPS_HOME"
ditto "$STAGE" "$DESKTOP"
ditto "$STAGE" "$APPS_HOME"
sign_app "$DESKTOP"
sign_app "$APPS_HOME"

echo "→ Cold-start smoke test…"
lsof -ti:13029 | xargs kill -9 2>/dev/null || true
sleep 0.5
FORGE_TERMINAL_BUNDLE_ROOT="$STAGE/Contents/Resources/forge-terminal-bundle" \
FORGE_TERMINAL_PORT=13029 \
python3 "$STAGE/Contents/Resources/forge-terminal-bundle/scripts/forge-terminal-server.py" >/dev/null 2>&1 &
SMOKE_PID=$!
COLD_OK=0
for _ in {1..20}; do
  if /usr/bin/curl -sf "http://127.0.0.1:13029/health" >/dev/null 2>&1 \
    && /usr/bin/curl -sf "http://127.0.0.1:13029/?ui=smoke" | grep -q "Forge Terminal" \
    && /usr/bin/curl -sf "http://127.0.0.1:13029/terminal/index.html" | grep -q "chat-thread" \
    && /usr/bin/curl -sf "http://127.0.0.1:13029/api/integrations/v1" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('lanes')" 2>/dev/null \
    && grep -q 'id="dock-resize"' "$BUNDLE_STAGE/app/terminal/index.html" \
    && grep -q 'initDockResize' "$BUNDLE_STAGE/app/terminal/terminal.js" \
    && grep -q 'forge-quality-bridge.js' "$BUNDLE_STAGE/app/connect/index.html" \
    && mkdir -p "$HOME/.sina/forge-terminal-quality" \
    && touch "$HOME/.sina/forge-terminal-quality/.bundle-write-test" \
    && rm -f "$HOME/.sina/forge-terminal-quality/.bundle-write-test" \
    && FORGE_TERMINAL_BUNDLE_ROOT="$STAGE/Contents/Resources/forge-terminal-bundle" \
       python3 -c "import sys; sys.path.insert(0, '$STAGE/Contents/Resources/forge-terminal-bundle/scripts'); import forge_quality_gate_v1; import forge_terminal_local_auth_v1" 2>/dev/null; then
    echo "✓ Cold-start PASS — health + terminal UI + model matrix + quality gate import"
    COLD_OK=1
    break
  fi
  sleep 0.5
done
kill "$SMOKE_PID" 2>/dev/null || true
lsof -ti:13029 | xargs kill -9 2>/dev/null || true
if [[ "$COLD_OK" != "1" ]]; then
  echo "FAIL: bundle cold-start smoke test failed" >&2
  exit 1
fi

echo ""
echo "✓ ${APP_NAME} v${APP_VER} — double-click · native WebKit window (no browser)"
echo "  Desktop:       $DESKTOP"
echo "  Applications:  $APPS_HOME"
echo "  Entry:         ForgeTerminalShell → :13029/terminal/"
echo "  Log:           ~/.sina/forge-terminal-app-launch.log"
echo ""
echo "Launch:"
echo "  open \"$DESKTOP\""
