#!/bin/bash
# SourceA Autorun Worker — launchd installer
# Usage: bash scripts/install-autorun.sh
set -euo pipefail

PLIST_SRC="$HOME/Desktop/SourceA/scripts/com.sourcea.autorun-worker.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.sourcea.autorun-worker.plist"
LOG_DIR="$HOME/.sina"
mkdir -p "$LOG_DIR"

# ── 1. Extract API key from .zshrc ────────────────────────────────────────────
API_KEY=$(grep 'ANTHROPIC_API_KEY' ~/.zshrc 2>/dev/null | head -1 | sed "s/.*ANTHROPIC_API_KEY[='\"] *['\"]//; s/['\"].*//; s/export //")

if [[ -z "$API_KEY" ]]; then
    # Fallback: read from env if already exported
    API_KEY="${ANTHROPIC_API_KEY:-}"
fi

if [[ -z "$API_KEY" ]]; then
    echo "❌  Could not find ANTHROPIC_API_KEY in ~/.zshrc or environment."
    echo "    Add this to ~/.zshrc:  export ANTHROPIC_API_KEY='sk-ant-api03-...'"
    exit 1
fi

echo "✅  API key found (${API_KEY:0:20}...)"

# ── 2. Inject key into plist copy ────────────────────────────────────────────
sed "s|__ANTHROPIC_API_KEY_PLACEHOLDER__|${API_KEY}|g" "$PLIST_SRC" > "$PLIST_DST"
echo "✅  Plist written to $PLIST_DST"

# ── 3. Unload old version if running ─────────────────────────────────────────
launchctl unload "$PLIST_DST" 2>/dev/null || true

# ── 4. Load ───────────────────────────────────────────────────────────────────
launchctl load "$PLIST_DST"
echo "✅  launchd agent loaded — fires every 90 seconds"

# ── 5. Install dashboard daemon (KeepAlive — auto-restarts if it crashes) ─────
DASH_SRC="$HOME/Desktop/SourceA/scripts/com.sourcea.dashboard.plist"
DASH_DST="$HOME/Library/LaunchAgents/com.sourcea.dashboard.plist"
if [[ -f "$DASH_SRC" ]]; then
    cp "$DASH_SRC" "$DASH_DST"
    launchctl unload "$DASH_DST" 2>/dev/null || true
    launchctl load "$DASH_DST"
    echo "✅  Dashboard daemon loaded — auto-restarts on crash, starts on login"
fi

echo ""
echo "Commands:"
echo "  Stop all : python3 scripts/stop_goal1_auto_run_v1.py --json"
echo "  Resume   : python3 scripts/factory_control_v1.py resume --max-turns 1  (ASF only)"
echo "  Logs     : tail -f ~/.sina/autorun-worker.log"
echo "  Monitor  : http://127.0.0.1:13021/monitor"
