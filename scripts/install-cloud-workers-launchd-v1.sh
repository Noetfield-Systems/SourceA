#!/usr/bin/env bash
# Install launchd supervisor for Cloud Workers cockpit (:13027)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_SRC="$ROOT/launch/com.sourcea.cloud-workers.plist"
PLIST_DST="${HOME}/Library/LaunchAgents/com.sourcea.cloud-workers.plist"
LABEL="com.sourcea.cloud-workers"
PORT="${CLOUD_WORKERS_PORT:-13027}"
UID_NUM="$(id -u)"
DOMAIN="gui/${UID_NUM}"

export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:${PATH:-/usr/bin:/bin}"
mkdir -p "${HOME}/.sina" "${HOME}/Library/LaunchAgents"
CURL="$(command -v curl 2>/dev/null || echo /usr/bin/curl)"

bash "$ROOT/scripts/sync-mac-launchd-wrappers-v1.sh" >/dev/null 2>&1 || true
bash "$ROOT/scripts/render-launchd-plist-v1.sh" "$PLIST_SRC" "$PLIST_DST"

health_ok() { "$CURL" -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; }

launchctl bootout "$DOMAIN" "$PLIST_DST" 2>/dev/null || launchctl unload "$PLIST_DST" 2>/dev/null || true
if launchctl bootstrap "$DOMAIN" "$PLIST_DST" 2>/dev/null; then
  :
else
  launchctl load "$PLIST_DST" 2>/dev/null || true
fi
launchctl enable "$DOMAIN/${LABEL}" 2>/dev/null || true
launchctl kickstart "$DOMAIN/${LABEL}" 2>/dev/null || true

for _ in {1..40}; do
  if health_ok; then
    echo "OK: Cloud Workers supervised via launchd → http://127.0.0.1:${PORT}/"
    exit 0
  fi
  sleep 0.25
done

launchctl kickstart -k "$DOMAIN/${LABEL}" 2>/dev/null || true
for _ in {1..40}; do
  if health_ok; then
    echo "OK: Cloud Workers supervised via launchd (kickstart -k) → http://127.0.0.1:${PORT}/"
    exit 0
  fi
  sleep 0.25
done

echo "FAIL: Cloud Workers not healthy after launchd install" >&2
echo "TCC on Desktop? bash $ROOT/scripts/open-mac-launchd-fda-v1.sh" >&2
echo "Fallback: bash $ROOT/scripts/serve-cloud-workers-v1.sh" >&2
exit 1
