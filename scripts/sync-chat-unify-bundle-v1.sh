#!/usr/bin/env bash
# Full Chat Unify bundle sync → Desktop .app (classic UI + IDE motor + form + shared).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC_APP="$ROOT/scripts/chat-unify-standalone"
SHARED="$ROOT/agent-control-panel/shared"
FORM="$ROOT/agent-control-panel/form"

# Chat Unify 4.9.9 SSOT — terminal motor stays in standalone; never rsync forge-terminal-v1.
CU_TERMINAL="$SRC_APP/terminal"
if [[ ! -f "$CU_TERMINAL/terminal.js" ]]; then
  echo "✗ missing $CU_TERMINAL/terminal.js — restore Chat Unify 4.9.9 terminal before bundle sync" >&2
  exit 1
fi
echo "→ Keep Chat Unify terminal motor at $CU_TERMINAL (4.9.9 — not forge-terminal-v1)"

SCRIPTS=(
  chat-unify-server.py
  chat_unify_merge.py chat_unify_proof_pack_v1.py chat_unify_prompt_forge_v1.py
  chat_unify_vocabulary_intelligence_v1.py vocabulary_intelligence_scan_v1.py
  chat_unify_integrations_v1.py chat_unify_platform_catalog_v1.py
  chat_unify_kernel_v1.py chat_unify_truth_gate_v1.py chat_ord_loop_v1.py
  chat_ord_atoms_v1.py chat_ord_claim_rules_v1.py chat_founder_loop_v1.py
  chat_founder_language_v1.py chat_founder_reasoning_v1.py prompt_forge_pipeline_v1.py
  chat_unify_live_http_verify_v1.py chat_unify_update_check_v1.py
  ai_unify_api_v1.py api_station_v1.py hub_pro_skills_v1.py founder_glance_cockpit_v1.py
  clipboard_safe.py cursor_window_preflight_v1.py live_founder_decision_form_v1.py
  form_official_canvas_route_v1.py hub_form_submit_v1.py form_founder_supremacy_guard_v1.py
  governance_paths_v1.py canvas_form_apply_picks_v1.py canvas_form_submit_v1.py
  chat_unify_ide_v1.py chat_unify_terminal_motor_v1.py chat_unify_engine_v1.py chat_unify_smart_router_v1.py forge_terminal_v1.py
  workspace_kernel_v2.py model_dispatch.py worker_inject_lib.py
)
BUNDLES=(
  "$ROOT/brand/macos-apps/Chat Unify.app/Contents/Resources/chat-unify-bundle"
  "$HOME/Desktop/Chat Unify.app/Contents/Resources/chat-unify-bundle"
  "$HOME/Applications/Chat Unify.app/Contents/Resources/chat-unify-bundle"
)
for B in "${BUNDLES[@]}"; do
  [ -d "$(dirname "$(dirname "$(dirname "$B")")")" ] || continue
  mkdir -p "$B/scripts" "$B/app" "$B/form" "$B/shared" "$B/prompts"
  echo "→ Sync $B"
  cp -R "$SRC_APP/." "$B/app/"
  for f in "${SCRIPTS[@]}"; do
    cp "$ROOT/scripts/$f" "$B/scripts/"
  done
  cp -R "$FORM/." "$B/form/"
  cp "$SHARED/official-links-bar.js" "$B/app/official-links-bar.js"
  cp "$SHARED/sina-main-terminal.js" "$B/app/sina-main-terminal.js"
  cp "$SHARED/sina-main-terminal.css" "$B/app/sina-main-terminal.css"
  cp "$SHARED/official-links-bar.css" "$B/app/official-links-bar.css" 2>/dev/null || true
  cp "$SHARED/hub-pro-skills-tab.js" "$B/shared/" 2>/dev/null || true
  cp "$SHARED/hub-pro-skills-tab.css" "$B/shared/" 2>/dev/null || true
  cp "$SRC_APP/api-station-tab.js" "$B/app/api-station-tab.js"
  cp "$SRC_APP/connect-tab.js" "$B/app/connect-tab.js"
  if [[ -f "$B/app/terminal/index.html" ]]; then
    sed -i '' \
      -e 's/Forge Terminal tools/Chat Unify Terminal Motor tools/g' \
      -e 's/built for Forge Terminal only/built for Chat Unify Terminal Motor/g' \
      -e 's/aria-label="Forge Terminal tools"/aria-label="Chat Unify Terminal Motor tools"/g' \
      "$B/app/terminal/index.html"
  fi
  cp "$ROOT/CHAT_EXTRACT_UNIFY_PROMPT.txt" "$B/prompts/" 2>/dev/null || true
  cp "$ROOT/CHAT_UNIFY_ROLLUP_PROMPT.txt" "$B/prompts/" 2>/dev/null || true
  rm -f "$B/app/terminal.js" "$B/app/terminal-desktop.css" "$B/app/terminal.css" 2>/dev/null || true
done
echo "✓ Full Chat Unify bundle sync done — quit and reopen Chat Unify.app from Desktop"
