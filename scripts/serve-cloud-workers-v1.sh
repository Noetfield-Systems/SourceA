#!/usr/bin/env bash
# serve-cloud-workers-v1.sh — Cloud Workers cockpit :13027 (UI + factory workflows)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${CLOUD_WORKERS_PORT:-13027}"
PIDFILE="${HOME}/.sina/cloud-workers-server.pid"
LOGFILE="${HOME}/.sina/cloud-workers-server.log"
WRAPPER="${HOME}/.sina/start-cloud-workers-launchd.sh"
LABEL="com.sourcea.cloud-workers"
DOMAIN="gui/$(id -u)"
MODE="${1:-}"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"
if [[ -x "$ROOT/scripts/sourcea-python-v1.sh" ]]; then
  PY="$ROOT/scripts/sourcea-python-v1.sh"
elif [[ -x /usr/bin/python3 ]]; then
  PY="/usr/bin/python3"
else
  PY="/Library/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python"
fi
CURL="$(command -v curl 2>/dev/null || echo /usr/bin/curl)"

mkdir -p "${HOME}/.sina"
cd "$ROOT"

for _w in start-cloud-workers-launchd.sh sourcea-mac-v1.sh; do
  if [[ -f "$ROOT/scripts/launchd-wrappers/$_w" ]]; then
    cp "$ROOT/scripts/launchd-wrappers/$_w" "${HOME}/.sina/$_w"
    chmod +x "${HOME}/.sina/$_w"
  fi
done
printf '{"schema":"sourcea-root-v1","root":"%s"}\n' "$ROOT" > "${HOME}/.sina/sourcea-root-v1.json"

# Desktop repo: launchd needs FDA — skip to nohup unless founder opted in.
if [[ "$ROOT" == *"/Desktop/"* ]] && [[ "${SINA_LAUNCHD_TCC_FALLBACK:-}" != "0" ]]; then
  export SINA_LAUNCHD_TCC_FALLBACK=1
fi

health_ok() { "$CURL" -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; }
launchd_loaded() { launchctl print "${DOMAIN}/${LABEL}" >/dev/null 2>&1; }

stop_launchd_supervisor() {
  local dst="${HOME}/Library/LaunchAgents/${LABEL}.plist"
  launchctl bootout "$DOMAIN" "$dst" 2>/dev/null || launchctl unload "$dst" 2>/dev/null || true
}

start_nohup() {
  pkill -f 'cloud-workers-server.py' 2>/dev/null || true
  sleep 0.3
  : >"$LOGFILE"
  if [[ -x "$WRAPPER" ]]; then
    nohup env SINA_SOURCE_A="$ROOT" CLOUD_WORKERS_PORT="$PORT" bash "$WRAPPER" >>"$LOGFILE" 2>&1 &
  else
    nohup env SINA_SOURCE_A="$ROOT" CLOUD_WORKERS_PORT="$PORT" \
      "$PY" "$ROOT/scripts/cloud-workers-server.py" >>"$LOGFILE" 2>&1 &
  fi
  echo $! >"$PIDFILE"
}

if [[ "$MODE" == "fg" || "$MODE" == "foreground" ]]; then
  stop_launchd_supervisor
  echo "Cloud Workers foreground → http://127.0.0.1:${PORT}/"
  exec env SINA_SOURCE_A="$ROOT" CLOUD_WORKERS_PORT="$PORT" bash "$WRAPPER"
fi

if launchd_loaded && [[ "${SINA_LAUNCHD_TCC_FALLBACK:-}" != "1" ]]; then
  if health_ok; then
    echo "Cloud Workers healthy via launchd → http://127.0.0.1:${PORT}/"
    exit 0
  fi
  launchctl kickstart "${DOMAIN}/${LABEL}" 2>/dev/null || true
  for _ in {1..40}; do
    if health_ok; then
      echo "Cloud Workers healthy via launchd → http://127.0.0.1:${PORT}/"
      exit 0
    fi
    sleep 0.25
  done
fi

if health_ok; then
  echo "Cloud Workers already running → http://127.0.0.1:${PORT}/"
  exit 0
fi

if [[ -f "$ROOT/launch/com.sourcea.cloud-workers.plist" ]] && [[ "${SINA_LAUNCHD_TCC_FALLBACK:-}" != "1" ]]; then
  if bash "$ROOT/scripts/install-cloud-workers-launchd-v1.sh"; then
    exit 0
  fi
  echo "WARN: launchd install failed — nohup fallback" >&2
fi

stop_launchd_supervisor
start_nohup

for _ in {1..40}; do
  if health_ok; then
    echo "Cloud Workers ready (nohup) → http://127.0.0.1:${PORT}/"
    exit 0
  fi
  sleep 0.25
done

echo "FAIL: Cloud Workers did not start — see $LOGFILE" >&2
tail -20 "$LOGFILE" 2>/dev/null >&2 || true
echo "Try foreground (Terminal keeps TCC): bash $0 fg" >&2
exit 1
