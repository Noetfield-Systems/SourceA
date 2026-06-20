#!/usr/bin/env bash
# Sync standalone app sources → brand + Desktop + ~/Applications bundles (no rebuild).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

sync_app() {
  local name="$1" bundle_dir="$2" app_src="$3"
  shift 3
  local scripts=("$@")
  for base in \
    "$ROOT/brand/macos-apps/${name}.app/Contents/Resources/${bundle_dir}" \
    "$HOME/Desktop/${name}.app/Contents/Resources/${bundle_dir}" \
    "$HOME/Applications/${name}.app/Contents/Resources/${bundle_dir}"; do
    [[ -d "$base/app" ]] || continue
    cp -R "$ROOT/scripts/${app_src}/." "$base/app/"
    for s in "${scripts[@]}"; do
      [[ -f "$ROOT/scripts/$s" ]] && cp "$ROOT/scripts/$s" "$base/scripts/"
    done
    echo "synced $name → $base"
  done
}

sync_app "N8N Integration" "n8n-integration-bundle" "n8n-standalone" \
  n8n-integration-server.py n8n_integration_core.py n8n_automation.py n8n_intelligence.py n8n_commercial_grade_v1.py

sync_app "Mac Health Guard" "mac-health-bundle" "mac-health-standalone" \
  mac-health-guard-server.py mac_health_guard.py mac_health_cpu_relief_v1.py mac_health_live_v1.py \
  mac_health_prevention_v1.py mac_health_emergency_stop_v1.py mac_health_settings_v1.py mac_health_version_v1.py \
  mac_health_log_shield_v1.py \
  mac_performance_snapshot.py n8n_glue_runner_v1.py n8n_glue_config_v1.py

sync_app "Chat Unify" "chat-unify-bundle" "chat-unify-standalone" \
  chat-unify-server.py chat_unify_merge.py chat_founder_language_v1.py chat_founder_reasoning_v1.py \
  chat_founder_loop_v1.py chat_ord_loop_v1.py chat_ord_atoms_v1.py chat_ord_claim_rules_v1.py \
  chat_unify_kernel_v1.py chat_unify_truth_gate_v1.py chat_unify_live_http_verify_v1.py ai_unify_api_v1.py
for base in \
  "$ROOT/brand/macos-apps/Chat Unify.app/Contents/Resources/chat-unify-bundle/data" \
  "$HOME/Desktop/Chat Unify.app/Contents/Resources/chat-unify-bundle/data" \
  "$HOME/Applications/Chat Unify.app/Contents/Resources/chat-unify-bundle/data"; do
  mkdir -p "$base"
  cp "$ROOT/data/chat-unify-ord-claim-rules-v1.json" "$base/" 2>/dev/null || true
  echo "synced Chat Unify rules → $base"
done
for base in \
  "$ROOT/brand/macos-apps/Chat Unify.app/Contents/Resources/chat-unify-bundle/prompts" \
  "$HOME/Desktop/Chat Unify.app/Contents/Resources/chat-unify-bundle/prompts" \
  "$HOME/Applications/Chat Unify.app/Contents/Resources/chat-unify-bundle/prompts"; do
  [[ -d "$base" ]] || continue
  cp "$ROOT/CHAT_EXTRACT_UNIFY_PROMPT.txt" "$ROOT/CHAT_UNIFY_ROLLUP_PROMPT.txt" "$base/" 2>/dev/null || true
  echo "synced Chat Unify prompts → $base"
done

sync_app "Apple Health" "apple-health-bundle" "apple-health-standalone" \
  apple-health-server.py roadmaps_goals.py

echo "OK: sync-standalone-apps-to-bundles-v1"
