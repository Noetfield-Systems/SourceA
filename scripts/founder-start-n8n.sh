#!/usr/bin/env bash
# Founder one-tap — start n8n. launchd uses ~/.sina/start-n8n-launchd.sh directly.
set -euo pipefail
LAUNCHD_SH="${HOME}/.sina/start-n8n-launchd.sh"
if [[ -x "$LAUNCHD_SH" ]]; then
  bash "$LAUNCHD_SH"
  exit 0
fi
MONO="${SINAAI_MONO_ROOT:-$HOME/Desktop/SinaaiMonoRepo}"
SCRIPT="$MONO/scripts/start-n8n.sh"
if [[ ! -f "$SCRIPT" ]]; then
  echo "Missing: $SCRIPT" >&2
  exit 1
fi
mkdir -p "$HOME/.sina"
bash "$SCRIPT" >> "$HOME/.sina/n8n.log" 2>&1
