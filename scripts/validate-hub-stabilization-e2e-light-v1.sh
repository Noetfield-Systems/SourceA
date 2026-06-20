#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
bash "$ROOT/scripts/validate-hub-stabilization-ssot-v1.sh" || exit 1
bash "$ROOT/scripts/validate-founder-rebuild-worker-action-v1.sh" || exit 1
bash "$ROOT/scripts/validate-hub-live-sse-v1.sh" || exit 1
bash "$ROOT/scripts/validate-hub-sync-slim-v1.sh" || exit 1
bash "$ROOT/scripts/validate-port-catalog-hub-stabilization-v1.sh" || exit 1
curl -sf "http://127.0.0.1:13020/health" >/dev/null || {
  echo "FAIL: hub :13020 not up — run serve-sina-command.sh"
  exit 1
}
bash "$ROOT/scripts/ensure-hub-rebuild-worker-v1.sh" || exit 1
python3 scripts/audit_backend_e2e_light_v1.py
echo "OK: validate-hub-stabilization-e2e-light-v1"
