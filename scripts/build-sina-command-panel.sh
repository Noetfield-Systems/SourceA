#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 "$ROOT/scripts/build-sina-daily-bowl.py"
python3 "$ROOT/scripts/scan-cursor-agent-fleet.py"
python3 "$ROOT/scripts/build-sina-command-panel.py"
echo "Open: file://$ROOT/agent-control-panel/index.html"
echo "Or:   $ROOT/scripts/serve-sina-command.sh"
