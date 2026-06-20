#!/usr/bin/env bash
# Install launchd AUTO-RUN worker daemon — no Hub taps.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_SRC="$ROOT/launch/com.sourcea.autorun-worker.plist"
PLIST_DST="${HOME}/Library/LaunchAgents/com.sourcea.autorun-worker.plist"
LABEL="com.sourcea.autorun-worker"
UID_NUM="$(id -u)"
DOMAIN="gui/${UID_NUM}"

export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:${PATH:-/usr/bin:/bin}"

mkdir -p "${HOME}/.sina" "${HOME}/Library/LaunchAgents"
cp "$PLIST_SRC" "$PLIST_DST"

launchctl bootout "$DOMAIN" "$PLIST_DST" 2>/dev/null || launchctl unload "$PLIST_DST" 2>/dev/null || true
if launchctl bootstrap "$DOMAIN" "$PLIST_DST" 2>/dev/null; then
  :
else
  launchctl load "$PLIST_DST"
fi
launchctl enable "$DOMAIN/${LABEL}" 2>/dev/null || true
launchctl kickstart -k "$DOMAIN/${LABEL}" 2>/dev/null || true

# Hub must be up — install hub supervisor if missing.
if ! curl -sf "http://127.0.0.1:13020/health" >/dev/null 2>&1; then
  bash "$ROOT/scripts/install-hub-launchd-v1.sh" || true
fi

sleep 2
python3 "$ROOT/scripts/auto_run_worker_batch_v1.py" --once --json 2>/dev/null || true

echo "OK: AUTO-RUN worker daemon loaded → ${LABEL}"
