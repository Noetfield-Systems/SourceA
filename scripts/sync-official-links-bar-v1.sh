#!/usr/bin/env bash
# Sync canonical official-links-bar to all standalone app folders (one SSOT).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/agent-control-panel/shared/official-links-bar.js"
CSS="$ROOT/agent-control-panel/shared/official-links-bar.css"
TARGETS=(
  "$ROOT/scripts/n8n-standalone"
  "$ROOT/scripts/chat-unify-standalone"
  "$ROOT/scripts/ag-routing-panel-standalone"
  "$ROOT/scripts/cloud-workers-standalone"
)
for d in "${TARGETS[@]}"; do
  [[ -d "$d" ]] || continue
  cp "$SRC" "$d/official-links-bar.js"
  [[ -f "$CSS" ]] && cp "$CSS" "$d/official-links-bar.css"
  echo "✓ $d"
done
echo "Official links bar synced from agent-control-panel/shared/"
