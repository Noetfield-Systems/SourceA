#!/usr/bin/env bash
# launchd-safe Hub start — wrapper lives in ~/.sina (not Desktop) for TCC hygiene.
set -euo pipefail
SINA="${HOME}/.sina"
ROOT_FILE="${SINA}/sourcea-root-v1.json"
if [[ -f "$ROOT_FILE" ]]; then
  ROOT="$(/usr/bin/python3 -c "import json; print(json.load(open('${ROOT_FILE}'))['root'])")"
else
  ROOT="${HOME}/Desktop/SourceA"
fi
export SINA_COMMAND_PORT="${SINA_COMMAND_PORT:-13020}"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"
if [[ -x "$ROOT/scripts/sourcea-python-v1.sh" ]]; then
  PY="$ROOT/scripts/sourcea-python-v1.sh"
elif [[ -x /usr/bin/python3 ]]; then
  PY="/usr/bin/python3"
else
  PY="/Library/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python"
fi
cd "$ROOT"
exec "$PY" "$ROOT/scripts/sina-command-server.py"
