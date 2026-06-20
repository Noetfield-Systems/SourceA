#!/usr/bin/env bash
# founder-mac-reset-v1.sh — after heavy day: cool Mac, stop factory junk, trim Cursor, clear terminal
# Mac Law: never blanket-kill native screencapture (founder drag-to-app thumbnail).
#          Use: python3 no_auto_screenshot_v1.py --kill-automation-only
# Law: ~/Desktop/MacLaw/MAC_NO_AUTO_SCREENSHOT_LOCKED.md
# Usage:
#   bash ~/Desktop/SourceA/scripts/founder-mac-reset-v1.sh           # soft (keeps Cursor open)
#   bash ~/Desktop/SourceA/scripts/founder-mac-reset-v1.sh --hard    # + restart Cursor
#   bash ~/Desktop/SourceA/scripts/founder-mac-reset-v1.sh --terminal-only
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
HARD=0
TERMINAL_ONLY=0

for arg in "$@"; do
  case "$arg" in
    --hard|--restart-cursor) HARD=1 ;;
    --terminal-only) TERMINAL_ONLY=1 ;;
  esac
done

say() { printf '\n▸ %s\n' "$*"; }

# Mac Law — stop SourceA capture automation only; founder ⌘⇧4/5 stays sacred.
kill_capture_automation_lawful() {
  python3 "${ROOT}/scripts/no_auto_screenshot_v1.py" --kill-automation-only 2>/dev/null || true
}

terminal_cleanup() {
  say "Terminal cleanup"
  # Orphan heavy shell jobs from old sessions (safe patterns only)
  pkill -f 'fbe_motor_delegate_v1' 2>/dev/null || true
  pkill -f 'autorun_dispatcher_v1' 2>/dev/null || true
  pkill -f 'agent_rules_loop_orchestrator' 2>/dev/null || true
  pkill -f 'find_critical_bugs' 2>/dev/null || true
  kill_capture_automation_lawful
  pkill -9 afplay 2>/dev/null || true
  # Trim bloated zsh session files (not your history)
  find "${HOME}/.zsh_sessions" -type f -mtime +7 -delete 2>/dev/null || true
  # Free page cache if allowed (no sudo — skip if unavailable)
  sync 2>/dev/null || true
  if command -v memory_pressure >/dev/null 2>&1; then
    memory_pressure -S -l critical 2>/dev/null || true
  fi
  clear 2>/dev/null || printf '\033[2J\033[H'
  printf 'Terminal reset — clean prompt.\n'
}

if [[ "$TERMINAL_ONLY" -eq 1 ]]; then
  terminal_cleanup
  exit 0
fi

say "Control plane — quiet Mac, factory off, cloud APIs on"
python3 "$ROOT/scripts/mac_control_plane_v1.py" --enter --no-wire-sync 2>/dev/null | tail -6 || true

say "Kill background factory hogs"
pkill -f 'fbe_motor_delegate_v1' 2>/dev/null || true
pkill -f 'autorun_dispatcher_v1' 2>/dev/null || true
pkill -f 'anti_staleness_auto_wire_v1' 2>/dev/null || true
pkill -f 'auto_run_worker_batch' 2>/dev/null || true
pkill -f 'playwright' 2>/dev/null || true
kill_capture_automation_lawful
pkill -9 afplay 2>/dev/null || true
UID_N="$(id -u)"
launchctl bootout "gui/${UID_N}/com.sourcea.autorun-worker" 2>/dev/null || true

say "Mac Health cool down"
printf '  (sweeping CPU hogs — up to ~12s)\n'
if curl -sf -m 2 "http://127.0.0.1:13024/health" >/dev/null 2>&1; then
  curl -sf -m 12 -X POST "http://127.0.0.1:13024/api/mac-health" \
    -H 'Content-Type: application/json' \
    -d '{"action":"cpu_cool_down"}' >/dev/null 2>&1 || true
  launchctl kickstart -k "gui/${UID_N}/com.sina.mac-health-guard" 2>/dev/null || true
else
  launchctl kickstart -k "gui/${UID_N}/com.sina.mac-health-guard" 2>/dev/null || true
  sleep 2
fi
# Mac Law cloud-body: do NOT restart hub during founder reset (hub poll + CPU = drag breaks)
if [[ ! -f "${SINA}/mac-cloud-body-only-v1.flag" ]]; then
  launchctl kickstart -k "gui/${UID_N}/com.sourcea.hub" 2>/dev/null || true
  sleep 1
fi

say "Cursor session trim"
python3 "$ROOT/scripts/cursor_session_relief_v1.py" --trim 2>/dev/null || true

terminal_cleanup

if [[ "$HARD" -eq 1 ]]; then
  say "Restart Cursor (drops chat RAM — save work first)"
  bash "$ROOT/scripts/cursor-day-relief-v1.sh" --restart 2>/dev/null || \
    python3 "$ROOT/scripts/cursor_session_relief_v1.py" --restart 2>/dev/null || true
else
  python3 "$ROOT/scripts/cursor_session_relief_v1.py" 2>/dev/null || true
fi

say "Done — status"
curl -sf -m 2 "http://127.0.0.1:13024/health" | python3 -c "
import json,sys
try:
  d=json.load(sys.stdin)
  print('Mac Health:', d.get('version','?'), 'OK')
except Exception:
  print('Mac Health: starting — open http://127.0.0.1:13024/')
" 2>/dev/null || echo "Mac Health: http://127.0.0.1:13024/"
curl -sf -m 2 "http://127.0.0.1:13020/health" | python3 -c "
import json,sys
try:
  d=json.load(sys.stdin)
  print('Hub:', 'OK' if d.get('ok') else 'check')
except Exception:
  print('Hub: down')
" 2>/dev/null || echo "Hub: http://127.0.0.1:13020/"
echo ""
echo "SOFT reset done. For max relief after huge chat: run again with --hard"
echo "  bash ~/Desktop/SourceA/scripts/founder-mac-reset-v1.sh --hard"
