#!/usr/bin/env bash
# Founder one-tap — start n8n (wraps monorepo script). Log: ~/.sina/n8n.log
set -euo pipefail
MONO="${SINAAI_MONO_ROOT:-$HOME/Desktop/SinaaiMonoRepo}"
SCRIPT="$MONO/scripts/start-n8n.sh"
if [[ ! -f "$SCRIPT" ]]; then
  echo "Missing: $SCRIPT" >&2
  exit 1
fi
mkdir -p "$HOME/.sina"
exec bash "$SCRIPT" 2>&1 | tee -a "$HOME/.sina/n8n.log"
