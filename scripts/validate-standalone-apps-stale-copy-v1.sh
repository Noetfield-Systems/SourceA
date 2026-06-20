#!/usr/bin/env bash
# Fail if founder-facing standalone UI still contains stale Sina Command / Prompt feed copy.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAIL=0
FORBIDDEN='Sina Command|Prompt feed|Confirm auto-send|http://127.0.0.1:13020/'

check_tree() {
  local label="$1" dir="$2"
  [[ -d "$dir" ]] || { echo "⊘ skip $label (no bundle)"; return 0; }
  if grep -rEn "$FORBIDDEN" "$dir/app" "$dir/prompts" 2>/dev/null; then
    echo "✗ stale copy in $label"
    FAIL=1
  else
    echo "✓ clean $label"
  fi
}

check_tree "N8N Integration brand" "$ROOT/brand/macos-apps/N8N Integration.app/Contents/Resources/n8n-integration-bundle"
check_tree "N8N Integration Desktop" "$HOME/Desktop/N8N Integration.app/Contents/Resources/n8n-integration-bundle"
check_tree "Mac Health Guard brand" "$ROOT/brand/macos-apps/Mac Health Guard.app/Contents/Resources/mac-health-bundle"
check_tree "Mac Health Guard Desktop" "$HOME/Desktop/Mac Health Guard.app/Contents/Resources/mac-health-bundle"
check_tree "Chat Unify brand" "$ROOT/brand/macos-apps/Chat Unify.app/Contents/Resources/chat-unify-bundle"
check_tree "Chat Unify Desktop" "$HOME/Desktop/Chat Unify.app/Contents/Resources/chat-unify-bundle"
check_tree "Apple Health brand" "$ROOT/brand/macos-apps/Apple Health.app/Contents/Resources/apple-health-bundle"
check_tree "Apple Health Desktop" "$HOME/Desktop/Apple Health.app/Contents/Resources/apple-health-bundle"

for src in n8n-standalone mac-health-standalone chat-unify-standalone apple-health-standalone; do
  if grep -rEn "$FORBIDDEN" "$ROOT/scripts/$src" 2>/dev/null; then
    echo "✗ stale in scripts/$src"
    FAIL=1
  else
    echo "✓ clean scripts/$src"
  fi
done

[[ "$FAIL" -eq 0 ]] && echo "VALIDATE PASS — standalone stale copy clean" || { echo "VALIDATE FAIL"; exit 1; }
