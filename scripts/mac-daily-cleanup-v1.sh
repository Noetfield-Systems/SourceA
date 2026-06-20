#!/usr/bin/env bash
# mac-daily-cleanup-v1.sh — daily Mac + Cursor cleanup (morning · mid · night · full)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"

TIER="mid"
RESTART=0
FORCE=0
QUIET=0
JSON=0

for arg in "$@"; do
  case "$arg" in
    --morning) TIER="morning" ;;
    --mid) TIER="mid" ;;
    --night) TIER="night" ;;
    --full) TIER="full" ;;
    --restart|--restart-cursor) RESTART=1 ;;
    --force-cursor-restart) FORCE=1; RESTART=1 ;;
    --quiet) QUIET=1 ;;
    --json) JSON=1 ;;
  esac
done

ARGS=(--tier "$TIER")
[[ "$RESTART" -eq 1 ]] && ARGS+=(--restart-cursor)
[[ "$FORCE" -eq 1 ]] && ARGS+=(--force-cursor-restart)
[[ "$QUIET" -eq 1 ]] && ARGS+=(--quiet)
[[ "$JSON" -eq 1 ]] && ARGS+=(--json)

exec python3 "$ROOT/scripts/mac_daily_cleanup_v1.py" "${ARGS[@]}"
