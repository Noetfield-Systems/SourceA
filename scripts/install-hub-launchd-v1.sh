#!/usr/bin/env bash
# Install launchd supervisor for Hub (:13020) — blocked when Sina Command museum retired.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RETIRED_FLAG="${HOME}/.sina/sina-command-museum-retired-v1.flag"
if [[ -f "${RETIRED_FLAG}" && "${SINA_HUB_FORCE:-}" != "1" ]]; then
  echo "SKIP: Sina Command museum retired — no launchd install (${RETIRED_FLAG})"
  exit 0
fi
PLIST_SRC="$ROOT/launch/com.sourcea.hub.plist"
PLIST_DST="${HOME}/Library/LaunchAgents/com.sourcea.hub.plist"
LABEL="com.sourcea.hub"
PORT="${SINA_COMMAND_PORT:-13020}"
UID_NUM="$(id -u)"
DOMAIN="gui/${UID_NUM}"

export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:${PATH:-/usr/bin:/bin}"

mkdir -p "${HOME}/.sina" "${HOME}/Library/LaunchAgents"
CURL="$(command -v curl 2>/dev/null || echo /usr/bin/curl)"

bash "$ROOT/scripts/sync-mac-launchd-wrappers-v1.sh" >/dev/null 2>&1 || true
bash "$ROOT/scripts/render-launchd-plist-v1.sh" "$PLIST_SRC" "$PLIST_DST"

health_ok() { "$CURL" -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; }

# Healthy hub — bootstrap only; never pkill a working listener
if health_ok; then
  launchctl bootout "$DOMAIN" "$PLIST_DST" 2>/dev/null || launchctl unload "$PLIST_DST" 2>/dev/null || true
  if launchctl bootstrap "$DOMAIN" "$PLIST_DST" 2>/dev/null; then
    :
  else
    launchctl load "$PLIST_DST" 2>/dev/null || true
  fi
  launchctl enable "$DOMAIN/${LABEL}" 2>/dev/null || true
  echo "OK: hub already healthy — launchd registered → http://127.0.0.1:${PORT}/"
  exit 0
fi

# Unhealthy or down — clear orphan nohup fights, then bootstrap
pkill -f 'sina-command-server.py' 2>/dev/null || true
sleep 0.5

launchctl bootout "$DOMAIN" "$PLIST_DST" 2>/dev/null || launchctl unload "$PLIST_DST" 2>/dev/null || true
if launchctl bootstrap "$DOMAIN" "$PLIST_DST" 2>/dev/null; then
  :
else
  launchctl load "$PLIST_DST"
fi
launchctl enable "$DOMAIN/${LABEL}" 2>/dev/null || true
# Soft kickstart first
launchctl kickstart "$DOMAIN/${LABEL}" 2>/dev/null || true

for _ in {1..40}; do
  if health_ok; then
    echo "OK: hub supervised via launchd → http://127.0.0.1:${PORT}/"
    exit 0
  fi
  sleep 0.25
done

# Hard restart only if still down
launchctl kickstart -k "$DOMAIN/${LABEL}" 2>/dev/null || true
for _ in {1..40}; do
  if health_ok; then
    echo "OK: hub supervised via launchd (after kickstart -k) → http://127.0.0.1:${PORT}/"
    exit 0
  fi
  sleep 0.25
done

echo "FAIL: hub did not become healthy after launchd install" >&2
python3 "$ROOT/scripts/mac_launchd_tcc_guard_v1.py" --assess --json 2>/dev/null || true
echo "TCC on Desktop? bash $ROOT/scripts/open-mac-launchd-fda-v1.sh" >&2
echo "Fallback: SINA_LAUNCHD_TCC_FALLBACK=1 bash $ROOT/scripts/serve-sina-command.sh" >&2
exit 1
