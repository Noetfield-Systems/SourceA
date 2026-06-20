#!/usr/bin/env bash
# Install launchd supervisor for Sina Command hub (:13020) — KeepAlive + RunAtLoad.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_SRC="$ROOT/launch/com.sourcea.hub.plist"
PLIST_DST="${HOME}/Library/LaunchAgents/com.sourcea.hub.plist"
LABEL="com.sourcea.hub"
PORT="${SINA_COMMAND_PORT:-13020}"
UID_NUM="$(id -u)"
DOMAIN="gui/${UID_NUM}"

export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:${PATH:-/usr/bin:/bin}"

mkdir -p "${HOME}/.sina" "${HOME}/Library/LaunchAgents"
cp "$PLIST_SRC" "$PLIST_DST"

# Stop manual/nohup instances so launchd owns the port.
pkill -f 'sina-command-server.py' 2>/dev/null || true
sleep 0.5

launchctl bootout "$DOMAIN" "$PLIST_DST" 2>/dev/null || launchctl unload "$PLIST_DST" 2>/dev/null || true
if launchctl bootstrap "$DOMAIN" "$PLIST_DST" 2>/dev/null; then
  :
else
  launchctl load "$PLIST_DST"
fi
launchctl enable "$DOMAIN/${LABEL}" 2>/dev/null || true
launchctl kickstart -k "$DOMAIN/${LABEL}" 2>/dev/null || true

CURL="$(command -v curl 2>/dev/null || echo /usr/bin/curl)"
for _ in {1..40}; do
  if "$CURL" -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    echo "OK: hub supervised via launchd → http://127.0.0.1:${PORT}/"
    bash "$ROOT/scripts/install-autorun-launchd-v1.sh" 2>/dev/null || true
    exit 0
  fi
  sleep 0.25
done

echo "FAIL: hub did not become healthy after launchd install" >&2
exit 1
