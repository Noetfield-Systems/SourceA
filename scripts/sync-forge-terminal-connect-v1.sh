#!/usr/bin/env bash
# Sync Forge Terminal Connect UI from dev sources → bundle targets.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/apps/forge-terminal-connect-v1"
IDE="$ROOT/apps/forge-terminal-v1"
TARGETS=(
  "$ROOT/brand/macos-apps/Forge Terminal.app/Contents/Resources/forge-terminal-bundle/app/connect"
  "$HOME/Desktop/Forge Terminal.app/Contents/Resources/forge-terminal-bundle/app/connect"
  "$HOME/Applications/Forge Terminal.app/Contents/Resources/forge-terminal-bundle/app/connect"
)
echo "→ Sync Forge Terminal Connect UI…"
for t in "${TARGETS[@]}"; do
  if [[ -d "$(dirname "$t")" ]]; then
    mkdir -p "$t"
    rsync -a --delete "$SRC/" "$t/"
    echo "  ✓ $t"
  fi
done
for t in "${TARGETS[@]}"; do
  term="$(dirname "$t")/terminal"
  if [[ -d "$term" ]]; then
    rsync -a "$IDE/" "$term/"
    echo "  ✓ IDE → $term"
  fi
done
echo "✓ Done — quit and reopen Forge Terminal.app"
