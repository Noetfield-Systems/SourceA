#!/bin/zsh
# Desktop launcher for Mac Health Guard — SSOT for double-click open.
set -euo pipefail
SA="${SINA_SOURCEA:-/Users/sinakazemnezhad/Desktop/SourceA}"
LOG="$HOME/.sina/mac-health-desktop-launch.log"
PORT="${MAC_HEALTH_PORT:-13024}"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:/usr/bin:/bin:/usr/sbin:/sbin"

{
  echo "=== Mac Health Guard launch $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  bash "$SA/scripts/serve-mac-health-guard.sh" || true
  for i in {1..25}; do
    /usr/bin/curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 && break
    sleep 0.4
  done
  if ! /usr/bin/curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    err=$(grep -E 'Error|Traceback|Address already' "$HOME/.sina/mac-health-guard-server.log" 2>/dev/null | tail -2 | tr '\n' ' ')
    /usr/bin/osascript -e "display alert \"Mac Health Guard\" message \"Server not ready. See ~/.sina/mac-health-guard-server.log ${err}\""
    exit 1
  fi
  /usr/bin/open "http://127.0.0.1:${PORT}/?t=$(date +%s)"
  /usr/bin/osascript -e 'display notification "Opening in your browser…" with title "Mac Health Guard"'
  echo "opened browser OK"
} >>"$LOG" 2>&1
