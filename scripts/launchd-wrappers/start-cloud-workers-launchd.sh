#!/usr/bin/env bash
# launchd-safe Cloud Workers cockpit — wrapper in ~/.sina (not Desktop) for TCC hygiene.
set -euo pipefail
SINA="${HOME}/.sina"
ROOT_FILE="${SINA}/sourcea-root-v1.json"
if [[ -f "$ROOT_FILE" ]]; then
  ROOT="$(python3 -c "import json; print(json.load(open('${ROOT_FILE}'))['root'])")"
else
  ROOT="${HOME}/Desktop/SourceA"
fi
export CLOUD_WORKERS_PORT="${CLOUD_WORKERS_PORT:-13027}"
export SINA_SOURCE_A="$ROOT"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:${PATH:-/usr/bin:/bin}"
PY="/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
[[ -x "$PY" ]] || PY="$(command -v python3)"
cd "$ROOT"
exec "$PY" "$ROOT/scripts/cloud-workers-server.py"
