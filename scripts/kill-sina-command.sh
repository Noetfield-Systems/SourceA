#!/usr/bin/env bash
# Stop ALL Sina Command background automation (hub, panel builds, inject).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"

echo "Stopping Sina Command hub and builds…"
pkill -f 'sina-command-server.py' 2>/dev/null || true
pkill -f 'build-sina-command-panel.py' 2>/dev/null || true
pkill -f 'sina-command-api.py' 2>/dev/null || true
pkill -9 -f 'remote_ops.service' 2>/dev/null || true
pkill -f 'm8_ui.py' 2>/dev/null || true
pkill -f 'm8-dispatch' 2>/dev/null || true
pkill -f 'osascript.*Cursor' 2>/dev/null || true
if command -v lsof >/dev/null 2>&1; then
  lsof -tiTCP:13020 2>/dev/null | xargs kill 2>/dev/null || true
fi
bash "$ROOT/scripts/kill-hub-rebuild-worker.sh" || true
sleep 0.5

python3 -c "
import json
from pathlib import Path
from auto_prompt_guard import ensure_kill_on, disable_auto_feed_everywhere
from intelligence_circle import disable_live_agent_automation
ensure_kill_on()
disable_auto_feed_everywhere()
disable_live_agent_automation()
# Prompt OS — no automatic pbcopy on dispatch / morning scripts
settings = Path.home() / 'Desktop/SinaPromptOS/config/settings.json'
if settings.is_file():
    data = json.loads(settings.read_text(encoding='utf-8'))
    data['copy_primary_to_clipboard'] = False
    m8 = data.get('m8') or {}
    if isinstance(m8, dict):
        m8['ui_enabled'] = False
        data['m8'] = m8
    settings.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
# Pause Prompt OS remote scheduler (was auto-dispatching on file changes)
rops = Path.home() / 'Desktop/SinaPromptOS/logs/remote_ops_state.json'
if rops.is_file():
    st = json.loads(rops.read_text(encoding='utf-8'))
    st['paused'] = True
    rops.write_text(json.dumps(st, indent=2) + '\n', encoding='utf-8')
"

echo "OK: Hub + rebuild worker stopped · remote_ops paused · auto-paste blocked"
echo "Blocked attempts log: ~/.sina/cursor-inject-blocked.log"
echo "To start again: open Sina Command.app (or run serve-sina-command.sh)"
echo "Alias: ~/Desktop/SourceA/scripts/emergency-stop.sh"
