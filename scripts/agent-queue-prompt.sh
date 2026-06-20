#!/usr/bin/env bash
# Cursor agents: add prompts to the founder queue (no founder typing).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
API="${SINA_COMMAND_API:-http://127.0.0.1:13020}"

py() { python3 "$ROOT/prompt_queue.py" "$@"; }

CMD="${1:-list}"
shift || true

case "$CMD" in
  add)
    TITLE="${1:?title}"
    REPO="${2:-}"
    FILE="${3:?path to prompt .txt}"
    py cli-add "$TITLE" "$REPO" "$FILE"
    ;;
  add-text)
    TITLE="${1:?title}"
    shift
    py cli-add-text "$TITLE" "$*"
    ;;
  list) py cli-list ;;
  load-dispatch) py cli-load-dispatch ;;
  deliver) py cli-deliver ;;
  *)
    echo "Usage: $0 add|add-text|list|load-dispatch|deliver" >&2
    exit 1
    ;;
esac
