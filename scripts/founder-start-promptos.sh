#!/usr/bin/env bash
# Start Prompt OS UI in background — no Terminal window (founder one-click).
set -euo pipefail
ROOT="${HOME}/Desktop/SinaPromptOS"
cd "$ROOT"

for VAULT in "$HOME/.sina/secrets.env" "$ROOT/secrets.env"; do
  if [[ -f "$VAULT" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$VAULT" 2>/dev/null || true
    set +a
    export SINA_VAULT_LOADED="1"
    break
  fi
done

python3 -m venv .venv 2>/dev/null || true
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null || true

export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_HEADLESS=true

exec streamlit run ui/app.py \
  --server.port 8765 \
  --server.headless true \
  --browser.gatherUsageStats false
