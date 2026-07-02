#!/usr/bin/env bash
# launchd-safe Routing Panel start — wrapper in ~/.sina (not Desktop) for TCC hygiene.
set -euo pipefail
SINA="${HOME}/.sina"
MONO="${MONO_ROOT:-$HOME/Desktop/SinaaiMonoRepo}"
if [[ -f "${SINA}/mono-root-v1.json" ]]; then
  MONO="$(/usr/bin/python3 -c "import json; print(json.load(open('${SINA}/mono-root-v1.json'))['root'])")"
fi
PY="${MONO}/SinaaiRuntime/.venv/bin/python3"
[[ -x "$PY" ]] || PY="/usr/bin/python3"
[[ -x "$PY" ]] || PY="/Library/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"
cd "$MONO/routing-panel"
exec "$PY" server.py
