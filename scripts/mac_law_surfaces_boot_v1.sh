#!/usr/bin/env bash
# mac_law_surfaces_boot_v1.sh — ensure Mac Law :8781 + Routing :8780 are up (E2E boot)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ML="${MAC_LAW_ROOT:-$HOME/Desktop/MacLaw}"
LOG_DIR="${HOME}/.sina"
mkdir -p "$LOG_DIR"

resolve_mono() {
  if [[ -n "${MONO_ROOT:-}" && -f "${MONO_ROOT}/scripts/start-routing-panel.sh" ]]; then
    echo "$MONO_ROOT"
    return 0
  fi
  for d in "$HOME/Desktop/Noetfield/SinaaiMonoRepo" "$HOME/Desktop/SinaaiMonoRepo"; do
    [[ -f "$d/scripts/start-routing-panel.sh" ]] && echo "$d" && return 0
  done
  return 1
}

wait_health() {
  local url="$1" tries="${2:-30}"
  for _ in $(seq 1 "$tries"); do
    curl -sf "$url" >/dev/null 2>&1 && return 0
    sleep 0.4
  done
  return 1
}

boot_port() {
  local port="$1" start_cmd="$2" health_url="$3" log="$4"
  if lsof -i ":${port}" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "OK: :${port} already listening"
    return 0
  fi
  echo "BOOT: :${port} → $health_url"
  nohup bash -c "$start_cmd" >>"$log" 2>&1 &
  if wait_health "$health_url"; then
    echo "OK: :${port} healthy"
    return 0
  fi
  echo "FAIL: :${port} not healthy — see $log" >&2
  tail -15 "$log" 2>/dev/null >&2 || true
  return 1
}

FAIL=0
MONO="$(resolve_mono)" || { echo "FAIL: SinaaiMonoRepo not found for :8780"; exit 1; }

# Prefer launchd supervisors (KeepAlive) — install once if missing.
UID_NUM="$(id -u)"
if ! launchctl print "gui/${UID_NUM}/com.sourcea.mac-law" >/dev/null 2>&1; then
  if [[ -f "$ROOT/scripts/install-mac-law-surfaces-launchd-v1.sh" ]]; then
    bash "$ROOT/scripts/install-mac-law-surfaces-launchd-v1.sh" && exit 0
  fi
fi

boot_port 8781 "$ML/start-mac-law-server.sh" "http://127.0.0.1:8781/api/mac-law/health" "$LOG_DIR/mac-law-server.log" || FAIL=1
boot_port 8780 "MONO_ROOT='$MONO' bash '$MONO/scripts/start-routing-panel.sh'" "http://127.0.0.1:8780/api/panel/health" "$LOG_DIR/routing-panel-server.log" || FAIL=1

if curl -sf --max-time 3 "http://127.0.0.1:13020/health" >/dev/null 2>&1; then
  echo "OK: Hub :13020"
else
  echo "WARN: Hub :13020 down — bash $ROOT/scripts/serve-sina-command.sh" >&2
fi

if [[ "$FAIL" -eq 0 ]]; then
  python3 - <<'PY' 2>/dev/null || true
import json
from datetime import datetime, timezone
from pathlib import Path
p = Path.home() / ".sina" / "mac-law-surfaces-boot-receipt-v1.json"
p.write_text(json.dumps({
    "schema": "mac-law-surfaces-boot-receipt-v1",
    "saved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "ok": True,
    "urls": {
        "mac_law": "http://127.0.0.1:8781/",
        "routing_panel": "http://127.0.0.1:8780/",
        "hub": "http://127.0.0.1:13020/",
    },
}, indent=2) + "\n")
PY
  echo "PASS mac-law-surfaces-boot-v1"
  exit 0
fi
exit 1
