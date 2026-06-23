#!/bin/bash
# SourceA Dashboard — double-click to open
cd ~/Desktop/SourceA

# Kill old dashboard server if running
pkill -f "dashboard_server_v1.py" 2>/dev/null
sleep 0.5

# Source environment (picks up ANTHROPIC_API_KEY)
source ~/.zshrc 2>/dev/null || true

# Start dashboard server in background
python3 scripts/dashboard_server_v1.py &
DASH_PID=$!

# Wait for it to bind
sleep 1.5

# Open in default browser
open http://127.0.0.1:13021

echo "Dashboard running at http://127.0.0.1:13021 (pid $DASH_PID)"
echo "Close this window to stop the dashboard server."
wait $DASH_PID
