#!/usr/bin/env bash
# Install Mac Health Guard LaunchAgent — heart stays alive after login (no hub).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=resolve_sourcea_root_v1.sh
source "$SCRIPT_DIR/resolve_sourcea_root_v1.sh"
SA="$(resolve_sourcea_root)"
PLIST="$HOME/Library/LaunchAgents/com.sina.mac-health-guard.plist"
WRAPPER="$HOME/.sina/start-mac-health-heart.sh"
LOG="$HOME/.sina/mac-health-launchagent.log"

mkdir -p "$HOME/Library/LaunchAgents" "$HOME/.sina"

cat >"$WRAPPER" <<'WRAP'
#!/usr/bin/env bash
set -euo pipefail
PORT="${MAC_HEALTH_PORT:-13024}"
SOURCEA="${SINA_SOURCEA:-__SOURCEA__}"
PYTHON="$(command -v python3 || echo /usr/bin/python3)"
CURL="$(command -v curl || echo /usr/bin/curl)"
LOG="${HOME}/.sina/mac-health-guard-server.log"
export MAC_HEALTH_PORT="$PORT" MAC_HEALTH_STANDALONE=1 SINA_SOURCEA="$SOURCEA"
export PYTHONPATH="$SOURCEA/scripts:${PYTHONPATH:-}"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${PATH:-}"
mkdir -p "${HOME}/.sina"

health_ok() { "$CURL" -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; }

start_server() {
  if command -v lsof >/dev/null 2>&1; then
    lsof -t -iTCP:"${PORT}" -sTCP:LISTEN 2>/dev/null | xargs kill 2>/dev/null || true
    sleep 0.4
  fi
  "$PYTHON" "$SOURCEA/scripts/mac-health-guard-server.py" >>"$LOG" 2>&1 &
  SERVER_PID=$!
  echo "$SERVER_PID" >"${HOME}/.sina/mac-health-guard-server.pid"
}

# Keep launchd job alive — re-check every 20s and restart heart if :13024 dies
SERVER_PID=""
while true; do
  if health_ok; then
    sleep 20
    continue
  fi
  if [[ -n "${SERVER_PID}" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
  fi
  start_server
done
WRAP
sed -i '' "s|__SOURCEA__|${SA}|g" "$WRAPPER"
chmod +x "$WRAPPER"

cat >"$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.sina.mac-health-guard</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${WRAPPER}</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>MAC_HEALTH_PORT</key>
    <string>13024</string>
    <key>MAC_HEALTH_STANDALONE</key>
    <string>1</string>
    <key>SINA_SOURCEA</key>
    <string>${SA}</string>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${LOG}</string>
  <key>StandardErrorPath</key>
  <string>${LOG}</string>
  <key>ThrottleInterval</key>
  <integer>30</integer>
</dict>
</plist>
PLIST

launchctl bootout "gui/$(id -u)/com.sina.mac-health-guard" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/com.sina.mac-health-guard"
launchctl kickstart -k "gui/$(id -u)/com.sina.mac-health-guard" 2>/dev/null || bash "$WRAPPER" &

for _ in {1..40}; do
  curl -sf "http://127.0.0.1:13024/health" >/dev/null 2>&1 && break
  sleep 0.25
done

if curl -sf "http://127.0.0.1:13024/health" >/dev/null 2>&1; then
  echo "✓ Mac Health LaunchAgent installed — heart auto-starts on login"
  echo "  plist: $PLIST"
  echo "  url:   http://127.0.0.1:13024/"
  echo "  panic: bash $SA/scripts/install-mac-health-panic-hotkey-v1.sh  (⌃⌥⌘S stop all)"
else
  echo "LaunchAgent installed but server not healthy yet — check $LOG"
  exit 1
fi
