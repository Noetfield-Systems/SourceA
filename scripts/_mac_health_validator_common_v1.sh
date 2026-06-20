#!/usr/bin/env bash
# _mac_health_validator_common_v1.sh — shared Mac Health validator helpers (no marathon)
# Law: INCIDENT-039/040 · data/mac-pipeline-validator-pressure-registry-v1.json
set -euo pipefail

_mh_root() {
  if [[ -z "${MH_ROOT:-}" ]]; then
    MH_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  fi
  printf '%s' "$MH_ROOT"
}

_mh_port() {
  printf '%s' "${MAC_HEALTH_PORT:-13024}"
}

_mh_base() {
  printf 'http://127.0.0.1:%s' "$(_mh_port)"
}

_mh_founder_session() {
  python3 -c "
from mac_pipeline_validator_pressure_v1 import founder_session_active
raise SystemExit(0 if founder_session_active() else 1)
" 2>/dev/null
}

_mh_ship_window() {
  [[ -f "${HOME}/.sina/asf-ship-window-v1.flag" ]]
}

_mh_red_flag_marathon() {
  cat <<'EOF' >&2
MARATHON RED FLAG — Mac Health validator chain forbidden on Mac founder session.
Use ONE light gate only: bash scripts/validate-mac-health-ship-fast-v1.sh  (≤90s · read-only)
Full E2E recipe: cloud CI or ASF ship window only (touch ~/.sina/asf-ship-window-v1.flag).
EOF
}

# Ensure :13024 up — never pkill heart during founder session.
_mh_ensure_heart() {
  local root base port
  root="$(_mh_root)"
  port="$(_mh_port)"
  base="$(_mh_base)"
  export PYTHONPATH="${root}/scripts:${PYTHONPATH:-}"
  if curl -sf "${base}/health" >/dev/null 2>&1; then
    return 0
  fi
  bash "${root}/scripts/serve-mac-health-guard.sh" >/dev/null 2>&1 || true
  curl -sf "${base}/health" >/dev/null 2>&1
}

_mh_block_marathon_or_redirect() {
  local redirect="${1:-$(_mh_root)/scripts/validate-mac-health-ship-fast-v1.sh}"
  if _mh_founder_session && ! _mh_ship_window; then
    _mh_red_flag_marathon
    if [[ -x "$redirect" ]] || [[ -f "$redirect" ]]; then
      exec bash "$redirect"
    fi
    exit 2
  fi
}

_mh_write_ship_receipt() {
  local ok="${1:-0}" tier="${2:-ship-fast}" steps_file="${3:-}"
  local root sina receipt port version
  root="$(_mh_root)"
  sina="${HOME}/.sina"
  receipt="${sina}/mac-health/ship-fast-latest-v1.json"
  port="$(_mh_port)"
  version="$(curl -sf "$(_mh_base)/health" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null || echo "?")"
  STEPS_FILE="${steps_file:-}" RECEIPT="$receipt" VERSION="$version" FAIL="$ok" PORT="$port" TIER="$tier" python3 <<'PY'
import json, os
from datetime import datetime, timezone
from pathlib import Path
steps = []
path = os.environ.get("STEPS_FILE", "")
if path and Path(path).is_file():
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            steps.append(json.loads(line))
out = {
    "schema": "mac-health-ship-fast-latest-v1",
    "tier": os.environ.get("TIER", "ship-fast"),
    "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "version": os.environ.get("VERSION", "?"),
    "port": int(os.environ.get("PORT", "13024")),
    "overall_ok": os.environ.get("FAIL", "1") == "0",
    "steps": steps,
}
Path(os.environ["RECEIPT"]).parent.mkdir(parents=True, exist_ok=True)
Path(os.environ["RECEIPT"]).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(f"receipt: {os.environ['RECEIPT']}")
PY
}
