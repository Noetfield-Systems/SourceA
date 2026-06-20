#!/usr/bin/env bash
# Install launchd supervisors for Mac Law :8781 + Routing Panel :8780 (KeepAlive + RunAtLoad).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UID_NUM="$(id -u)"
DOMAIN="gui/${UID_NUM}"
mkdir -p "${HOME}/.sina" "${HOME}/Library/LaunchAgents"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:${PATH:-/usr/bin:/bin}"

resolve_mono() {
  for d in "$HOME/Desktop/SinaaiMonoRepo" "$HOME/Desktop/Noetfield/SinaaiMonoRepo"; do
    [[ -f "$d/routing-panel/server.py" ]] && echo "$d" && return 0
  done
  return 1
}

MONO="$(resolve_mono)" || { echo "FAIL: SinaaiMonoRepo not found" >&2; exit 1; }
PY="${MONO}/SinaaiRuntime/.venv/bin/python3"
[[ -x "$PY" ]] || PY="$(command -v python3)"

install_one() {
  local label="$1" src="$2" port="$3" health_path="$4" py_override="${5:-}"
  local dst="${HOME}/Library/LaunchAgents/${label}.plist"
  cp "$src" "$dst"
  if [[ -n "$py_override" ]]; then
    /usr/bin/sed -i '' "s|/Users/sinakazemnezhad/Desktop/SinaaiMonoRepo|${MONO}|g" "$dst" 2>/dev/null || \
      sed -i "s|/Users/sinakazemnezhad/Desktop/SinaaiMonoRepo|${MONO}|g" "$dst"
    /usr/bin/sed -i '' "s|${MONO}/SinaaiRuntime/.venv/bin/python3|${PY}|g" "$dst" 2>/dev/null || \
      sed -i "s|${MONO}/SinaaiRuntime/.venv/bin/python3|${PY}|g" "$dst"
  fi
  # Stop orphan listeners so launchd owns the port.
  local pid
  pid=$(lsof -ti ":${port}" -sTCP:LISTEN 2>/dev/null | head -1 || true)
  if [[ -n "$pid" ]]; then
    kill "$pid" 2>/dev/null || true
    sleep 0.5
  fi
  launchctl bootout "$DOMAIN" "$dst" 2>/dev/null || launchctl unload "$dst" 2>/dev/null || true
  if launchctl bootstrap "$DOMAIN" "$dst" 2>/dev/null; then
    :
  else
    launchctl load "$dst"
  fi
  launchctl enable "$DOMAIN/${label}" 2>/dev/null || true
  launchctl kickstart -k "$DOMAIN/${label}" 2>/dev/null || true
  local curl_bin
  curl_bin="$(command -v curl 2>/dev/null || echo /usr/bin/curl)"
  for _ in {1..40}; do
    if "$curl_bin" -sf "http://127.0.0.1:${port}${health_path}" >/dev/null 2>&1; then
      echo "OK: ${label} → http://127.0.0.1:${port}/"
      return 0
    fi
    sleep 0.25
  done
  echo "FAIL: ${label} not healthy — see ~/.sina/*-launchd.err" >&2
  tail -10 "${HOME}/.sina/${label//com.sourcea./}-launchd.err" 2>/dev/null >&2 || true
  return 1
}

FAIL=0
install_one "com.sourcea.mac-law" "$ROOT/launch/com.sourcea.mac-law.plist" 8781 "/api/mac-law/health" || FAIL=1
install_one "com.sourcea.routing-panel" "$ROOT/launch/com.sourcea.routing-panel.plist" 8780 "/api/panel/health" "yes" || FAIL=1

if [[ "$FAIL" -eq 0 ]]; then
  echo "OK: Mac Law surfaces supervised via launchd (:8781 · :8780)"
  exit 0
fi
exit 1
