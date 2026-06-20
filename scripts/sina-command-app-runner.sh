#!/usr/bin/zsh
# Sina Command.app runner — start hub, open UI, POST /shutdown on exit (normal quit).
set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:/usr/bin:/bin:/usr/sbin:/sbin"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${SINA_COMMAND_PORT:-13020}"
CURL="${CURL:-/usr/bin/curl}"
if [[ -z "${SINA_GATE_MODE:-}" && -f "${HOME}/.sina/gate_mode_v1.txt" ]]; then
  export SINA_GATE_MODE="$(tr -d '[:space:]' < "${HOME}/.sina/gate_mode_v1.txt")"
fi

shutdown_hub() {
  "$CURL" -sf -X POST "http://127.0.0.1:${PORT}/shutdown" \
    -H "Content-Type: application/json" \
    -d '{}' >/dev/null 2>&1 || true
}

trap shutdown_hub EXIT INT TERM

"$ROOT/scripts/serve-sina-command.sh" || true
for _ in {1..20}; do
  "$CURL" -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 && break
  sleep 0.5
done
open "http://127.0.0.1:${PORT}/?tab=command"
echo "Sina Command running — close this window or press Ctrl+C to stop hub."
while "$CURL" -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; do
  sleep 2
done
