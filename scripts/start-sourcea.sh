#!/bin/zsh
# SourceA — Start Everything
# Kills stale processes, starts dashboard, reinstalls daemon, opens monitor
# Usage: bash scripts/start-sourcea.sh

cd ~/Desktop/SourceA

echo "🔄 Stopping old processes..."
pkill -f dashboard_server_v1.py 2>/dev/null
# Law: never clear kill flag on hub restart — ASF resume only (INCIDENT-015)
sleep 0.5

echo "🚀 Starting dashboard server..."
nohup python3 scripts/dashboard_server_v1.py > ~/.sina/dashboard.log 2>&1 &
sleep 1.5

echo "⚙️  Installing autorun daemon..."
bash scripts/install-autorun.sh 2>/dev/null | grep "✅\|❌"

MONITOR_URL="http://127.0.0.1:13021/monitor"
echo "🌐 Waiting for dashboard…"
for _ in {1..12}; do
  if curl -sf "$MONITOR_URL" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done
echo "🌐 Opening live monitor..."
open "$MONITOR_URL"

echo ""
echo "✅ SourceA is running."
echo "   Monitor  : $MONITOR_URL"
echo "   Daemon   : fires every 90s (launchd)"
echo "   Logs     : tail -f ~/.sina/autorun-worker.log"
echo "   Stop all : touch ~/.sina/auto-run-disabled-v1.flag"
