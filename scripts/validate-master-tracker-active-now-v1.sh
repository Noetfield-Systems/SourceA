#!/usr/bin/env bash
# validate-master-tracker-active-now-v1.sh — master tracker must not list AUTO-RUN as ACTIVE P0 (AS-18)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRACKER="$ROOT/brain-os/system/SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md"

fail() { echo "FAIL: validate-master-tracker-active-now-v1 — $*" >&2; exit 1; }

[[ -f "$TRACKER" ]] || fail "missing tracker"

if grep -E 'GOAL-AUTH-LIVE.*AUTO-RUN.*ACTIVE.*P0' "$TRACKER" >/dev/null 2>&1; then
  fail "GOAL-AUTH-LIVE AUTO-RUN still ACTIVE P0"
fi

if grep -i 'live auto-run proof.*active.*p0' "$TRACKER" >/dev/null 2>&1; then
  fail "AUTO-RUN proof still ACTIVE P0"
fi

echo "OK: validate-master-tracker-active-now-v1"
