#!/usr/bin/env bash
# cursor-day-relief-v1.sh — end-of-day Cursor slowdown fix (trim + optional restart)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"

RESTART=0
FORCE=0
JSON=0
for arg in "$@"; do
  case "$arg" in
    --restart) RESTART=1 ;;
    --force-restart) FORCE=1; RESTART=1 ;;
    --json) JSON=1 ;;
  esac
done

ARGS=(--trim)
[[ "$RESTART" -eq 1 ]] && ARGS+=(--restart)
[[ "$FORCE" -eq 1 ]] && ARGS+=(--force-restart)
[[ "$JSON" -eq 1 ]] && ARGS+=(--json)

exec python3 "$ROOT/scripts/cursor_session_relief_v1.py" "${ARGS[@]}"
