#!/usr/bin/env bash
# validate-mac-law-mandatory-ship-v1.sh — HEAVY · cloud CI / ASF ship window ONLY · NOT Mac founder session
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"

fail() { echo "FAIL: mac-law-mandatory-ship — $*" >&2; exit 1; }

if [[ -f "${HOME}/.sina/mac-light-validators-only-v1.flag" ]] && [[ ! -f "${HOME}/.sina/asf-ship-window-v1.flag" ]]; then
  echo "SKIP: validate-mac-law-mandatory-ship-v1 — Mac founder session (light-only flag ON). Use light assess only." >&2
  exit 0
fi

bash scripts/validate-mac-law-mandatory-v1.sh || fail "light base"
python3 scripts/mac_law_mandatory_v1.py --sync-receipt --enforce --full-stack-sync --json >/dev/null || fail "full stack sync"
bash "$ROOT/scripts/mac_law_surfaces_boot_v1.sh" || fail "surfaces boot :8781/:8780"

echo "PASS: validate-mac-law-mandatory-ship-v1 (ship window / cloud CI)"
