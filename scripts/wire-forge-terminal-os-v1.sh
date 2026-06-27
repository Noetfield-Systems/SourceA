#!/usr/bin/env bash
# Wire Forge Terminal into SourceA OS stack — Mac .app · Chat Unify :13023 · Expo/Tailscale bridge.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export SINA_SOURCE_A="$ROOT"
export FORGE_OS_BRIDGE=1
export FORGE_TERMINAL_BIND_ALL=1

BUILD=0
NO_OPEN=0
for arg in "$@"; do
  case "$arg" in
    --build) BUILD=1 ;;
    --no-open) NO_OPEN=1 ;;
  esac
done

echo "→ Forge Terminal OS wire (Chat Unify :13023 + standalone .app :13029)"

# Mobile / remote Forge API — inherits Chat Unify + model_dispatch (no duplicate server)
bash "$ROOT/scripts/serve-chat-unify.sh"

# Standalone macOS .app (Swift WebKit shell — Sina Prompt OS pattern)
if [[ "$BUILD" -eq 1 ]] || [[ ! -d "$HOME/Desktop/Forge Terminal.app" ]]; then
  bash "$ROOT/scripts/build-forge-terminal-standalone-app-v1.sh"
fi

python3 "$ROOT/scripts/forge_terminal_os_bridge_v1.py" --ensure-chat-unify --sync --print

if [[ "$NO_OPEN" -eq 0 ]]; then
  if [[ -d "$HOME/Desktop/Forge Terminal.app" ]]; then
    open "$HOME/Desktop/Forge Terminal.app"
  elif [[ -d "$HOME/Applications/Forge Terminal.app" ]]; then
    open "$HOME/Applications/Forge Terminal.app"
  fi
fi

echo "Done. Bridge receipt: ~/.sina/forge-terminal-os-bridge-v1.json"
