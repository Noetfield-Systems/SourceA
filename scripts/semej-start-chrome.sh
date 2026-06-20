#!/usr/bin/env bash
# Start Google Chrome with remote debugging so SEMEJ can drive your signed-in AI tabs.
set -euo pipefail
PORT="${SEMEJ_CHROME_PORT:-9222}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE="${SEMEJ_CHROME_PROFILE:-$HOME/Library/Application Support/Google/Chrome}"

if [[ ! -x "$CHROME" ]]; then
  echo "Google Chrome not found at $CHROME" >&2
  exit 1
fi

if curl -sf "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
  echo "Chrome already listening on port $PORT"
  exit 0
fi

# Quit other Chrome instances only if SEMEJ_FORCE=1 (profile lock otherwise)
if [[ "${SEMEJ_FORCE:-}" == "1" ]]; then
  osascript -e 'quit app "Google Chrome"' 2>/dev/null || true
  sleep 2
fi

nohup "$CHROME" \
  --remote-debugging-port="$PORT" \
  --user-data-dir="$PROFILE" \
  --no-first-run \
  --no-default-browser-check \
  about:blank \
  >>"$HOME/.sina/semej-chrome.log" 2>&1 &

for _ in $(seq 1 15); do
  if curl -sf "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
    echo "Chrome listening on port $PORT"
    exit 0
  fi
  sleep 1
done
echo "Chrome did not open debug port $PORT — close other Chrome or set SEMEJ_FORCE=1" >&2
exit 1
