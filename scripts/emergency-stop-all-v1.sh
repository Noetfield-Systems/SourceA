#!/bin/bash
# EMERGENCY STOP — kills everything SourceA
echo "⛔ EMERGENCY STOP TRIGGERED"

# Kill flag
mkdir -p ~/.sina
touch ~/.sina/auto-run-disabled-v1.flag

# Kill all SourceA processes
pkill -f "sina-command-server" 2>/dev/null
pkill -f "auto_run_worker_batch" 2>/dev/null
pkill -f "goal1_worker_batch_loop" 2>/dev/null
pkill -f "healthy-drain-orchestrator" 2>/dev/null
pkill -f "brain_run_loop" 2>/dev/null
pkill -f "brain_watch_loop" 2>/dev/null
pkill -f "goal1_lane_broker" 2>/dev/null

# Clear inbox and locks
rm -f ~/.sina/worker-prompt-inbox-v1.json
rm -f ~/.sina/goal1-worker-batch-lock-v1.json

# Stop launchd services
launchctl stop com.sourcea.hub 2>/dev/null
launchctl stop com.sourcea.autorun-worker 2>/dev/null

echo "✅ ALL STOPPED"
osascript -e 'display notification "All SourceA processes killed" with title "⛔ EMERGENCY STOP" sound name "Basso"'
