#!/usr/bin/env bash
# Hub server (UI + API on :13020) — Sina Command museum retired; no auto-start when flagged.
# Law: data/execution-state-desired-observed-v1.json hub_single_owner
# launchd com.sourcea.hub = sole owner when plist loaded; this script delegates, never fights nohup.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${SINA_COMMAND_PORT:-13020}"
RETIRED_FLAG="${HOME}/.sina/sina-command-museum-retired-v1.flag"

if [[ -f "${RETIRED_FLAG}" && "${SINA_HUB_FORCE:-}" != "1" ]]; then
  echo "Sina Command museum retired — no auto-start (flag: ${RETIRED_FLAG})"
  echo "Manual Hub only: SINA_HUB_FORCE=1 $0 fg"
  exit 0
fi
PIDFILE="${HOME}/.sina/command-server.pid"
LOGFILE="${HOME}/.sina/command-server.log"
FAILSNIP="${HOME}/.sina/command-server.fail-snippet.log"
BUILDLOG="${HOME}/.sina/panel-build.log"
MODE="${1:-}"
LOG_MAX_BYTES="${SINA_COMMAND_LOG_MAX_BYTES:-52428800}" # 50 MiB cap before fresh start truncates
HUB_LABEL="com.sourcea.hub"
HUB_DOMAIN="gui/$(id -u)"

export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin:/usr/sbin:/sbin}"

mkdir -p "${HOME}/.sina"
cd "$ROOT"

_log_size_bytes() {
  if [[ -f "$LOGFILE" ]]; then stat -f%z "$LOGFILE" 2>/dev/null || echo 0; else echo 0; fi
}
_rotate_log_if_huge() {
  local sz
  sz="$(_log_size_bytes)"
  if [[ "${sz:-0}" -gt "${LOG_MAX_BYTES}" ]]; then
    : >"$LOGFILE"
  fi
}
_record_start_failure() {
  local sz fail_snip
  sz="$(_log_size_bytes)"
  fail_snip="${FAILSNIP}.$(date +%s)"
  {
    echo "=== serve failed $(date) ==="
    echo "log_bytes=${sz}"
    tail -n 200 "$LOGFILE" 2>/dev/null || true
  } >"$fail_snip" 2>/dev/null || true
  ln -sf "$(basename "$fail_snip")" "${FAILSNIP}" 2>/dev/null || true
}

LOSF="${LOSF:-/usr/sbin/lsof}"
if [[ -z "${CURL:-}" ]]; then
  CURL="$(command -v curl 2>/dev/null || true)"
  CURL="${CURL:-/usr/bin/curl}"
fi

port_up() {
  if [[ -x "$LOSF" ]]; then
    "$LOSF" -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1 && return 0
  fi
  python3 -c "import socket; s=socket.socket(); s.settimeout(0.3); exit(0 if s.connect_ex(('127.0.0.1',${PORT}))==0 else 1)" 2>/dev/null
}

health_ok() { "$CURL" -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; }

launchd_hub_loaded() {
  launchctl print "${HUB_DOMAIN}/${HUB_LABEL}" >/dev/null 2>&1
}

ensure_hub_via_launchd() {
  local waited=0
  if health_ok; then
    bash "$ROOT/scripts/serve-hub-rebuild-worker.sh" 2>/dev/null || true
    echo "Sina Command healthy via launchd → http://127.0.0.1:${PORT}/"
    return 0
  fi
  # Soft kickstart first — no -k when process may still be binding
  launchctl kickstart "${HUB_DOMAIN}/${HUB_LABEL}" 2>/dev/null || true
  for _ in {1..40}; do
    if health_ok; then
      bash "$ROOT/scripts/serve-hub-rebuild-worker.sh" 2>/dev/null || true
      echo "Sina Command healthy after launchd kickstart → http://127.0.0.1:${PORT}/"
      return 0
    fi
    sleep 0.25
    waited=$((waited + 1))
  done
  # Hard restart only when soft kickstart failed
  if port_up && ! health_ok; then
    echo "Port ${PORT} up but unhealthy — launchd hard kickstart…"
    launchctl kickstart -k "${HUB_DOMAIN}/${HUB_LABEL}" 2>/dev/null || true
    for _ in {1..40}; do
      if health_ok; then
        bash "$ROOT/scripts/serve-hub-rebuild-worker.sh" 2>/dev/null || true
        echo "Sina Command healthy after launchd kickstart -k → http://127.0.0.1:${PORT}/"
        return 0
      fi
      sleep 0.25
    done
  fi
  return 1
}

stop_stale_port() {
  # Never fight launchd when it owns a healthy listener
  if launchd_hub_loaded && health_ok; then
    return 0
  fi
  /usr/sbin/lsof -ti:"${PORT}" 2>/dev/null | xargs kill -9 2>/dev/null || true
  if [[ -f "$PIDFILE" ]]; then
    kill -9 "$(cat "$PIDFILE")" 2>/dev/null || true
    rm -f "$PIDFILE"
  fi
  sleep 1
}

_gate_mode_hint() {
  if [[ -n "${SINA_GATE_MODE:-}" ]]; then
    echo "${SINA_GATE_MODE}" > "${HOME}/.sina/gate_mode_v1.txt"
    echo "Gate mode preference → ${SINA_GATE_MODE} (~/.sina/gate_mode_v1.txt)"
  fi
}

# ── 0) launchd sole owner — delegate, do not nohup-fight ──
if launchd_hub_loaded; then
  if ensure_hub_via_launchd; then
    if [[ -n "${SINA_GATE_MODE:-}" && "${SINA_GATE_RESTART:-}" == "1" ]]; then
      echo "Gate mode change with launchd owner — hard kickstart…"
      launchctl kickstart -k "${HUB_DOMAIN}/${HUB_LABEL}" 2>/dev/null || true
      sleep 1
      ensure_hub_via_launchd || true
    fi
    exit 0
  fi
  echo "WARN: launchd ${HUB_LABEL} loaded but hub not healthy — trying install path…"
  bash "$ROOT/scripts/install-hub-launchd-v1.sh" && exit 0 || true
fi

# ── 1) Already up — restart only when founder requests gate/env reload ──
if health_ok; then
  if [[ "${SINA_FORCE_RESTART:-}" == "1" || ( -n "${SINA_GATE_MODE:-}" && "${SINA_GATE_RESTART:-}" == "1" ) ]]; then
    if [[ "${SINA_FORCE_RESTART:-}" == "1" ]]; then
      echo "Restarting hub (founder force restart)…"
    else
      echo "Restarting hub to apply SINA_GATE_MODE=${SINA_GATE_MODE}…"
    fi
    stop_stale_port
    sleep 0.5
  else
    bash "$ROOT/scripts/serve-hub-rebuild-worker.sh" || exit 1
    echo "Sina Command already running → http://127.0.0.1:${PORT}/"
    if [[ -n "${SINA_GATE_MODE:-}" ]]; then
      echo "Note: gate mode changes need restart — run:"
      echo "  SINA_GATE_MODE=${SINA_GATE_MODE} SINA_GATE_RESTART=1 $0"
    fi
    exit 0
  fi
fi

# ── 2) Stale listener without /health ──
if port_up; then
  echo "Port ${PORT} busy but not healthy — restarting…"
  stop_stale_port
fi

# ── 3) Optional panel build in background (must not block server bind) ──
if [[ "${SINA_PANEL_BUILD_ON_START:-}" == "1" && "${SINA_SKIP_PANEL_BUILD:-}" != "1" ]]; then
  (
    if python3 "$ROOT/scripts/build-sina-command-panel.py" >>"$BUILDLOG" 2>&1; then
      rm -f "${HOME}/.sina/panel_build_stale.flag"
    else
      echo "panel_build_failed $(date -u +%Y-%m-%dT%H:%M:%SZ)" >"${HOME}/.sina/panel_build_stale.flag"
      echo "WARN: panel build failed — see ${BUILDLOG}" >>"$BUILDLOG"
    fi
  ) &
fi

if [[ "$MODE" == "fg" || "$MODE" == "foreground" ]]; then
  _gate_mode_hint
  echo "Starting foreground → http://127.0.0.1:${PORT}/"
  exec env SINA_GATE_MODE="${SINA_GATE_MODE:-}" python3 "$ROOT/scripts/sina-command-server.py"
fi

# ── 4) Prefer launchd install when no supervisor yet ──
if [[ -f "$ROOT/launch/com.sourcea.hub.plist" ]]; then
  echo "Installing launchd supervisor (sole owner)…"
  if bash "$ROOT/scripts/install-hub-launchd-v1.sh"; then
    exit 0
  fi
  echo "WARN: launchd install failed — falling back to nohup (dev only)"
fi

# ── 5) Dev fallback: nohup (no launchd) ──
bash "$ROOT/scripts/serve-hub-rebuild-worker.sh" || exit 1
_gate_mode_hint
echo "Starting Sina Command (nohup fallback) → http://127.0.0.1:${PORT}/"
_rotate_log_if_huge
: >"$LOGFILE"
nohup env SINA_GATE_MODE="${SINA_GATE_MODE:-}" python3 "$ROOT/scripts/sina-command-server.py" >>"$LOGFILE" 2>&1 &
echo $! >"$PIDFILE"

for _ in {1..120}; do
  if health_ok; then
    echo "Ready."
    bash "$ROOT/scripts/auto_start_worker_batch_on_hub_v1.sh" >/dev/null 2>&1 &
    exit 0
  fi
  sleep 0.25
done

stop_stale_port
nohup python3 "$ROOT/scripts/sina-command-server.py" >>"$LOGFILE" 2>&1 &
echo $! >"$PIDFILE"
for _ in {1..40}; do
  if health_ok; then
    echo "Ready (after retry)."
    bash "$ROOT/scripts/auto_start_worker_batch_on_hub_v1.sh" >/dev/null 2>&1 &
    exit 0
  fi
  sleep 0.25
done

echo "Failed to start. Server log: $LOGFILE (snippet: $FAILSNIP)"
_record_start_failure
exit 1
