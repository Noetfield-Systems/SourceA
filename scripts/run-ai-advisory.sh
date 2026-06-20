#!/usr/bin/env bash
# Run AI advisory once (OpenRouter). Schedule via cron or Cursor Automations.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
for VAULT in "$HOME/.sina/secrets.env" "$HOME/Desktop/SinaPromptOS/secrets.env"; do
  [[ -f "$VAULT" ]] && set -a && source "$VAULT" 2>/dev/null && set +a && break
done
cd "$ROOT/scripts"
python3 sina_ai_advisory.py
python3 build-sina-command-panel.py
echo "OK: AI advisory → sina-bowl/AI_ADVISORY.json"
