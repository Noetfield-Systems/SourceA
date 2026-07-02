#!/usr/bin/env bash
# launchd-safe Mac Law start — wrapper in ~/.sina (not Desktop) for TCC hygiene.
set -euo pipefail
SINA="${HOME}/.sina"
ML="${MAC_LAW_ROOT:-$HOME/Desktop/MacLaw}"
if [[ -f "${SINA}/mac-law-root-v1.json" ]]; then
  ML="$(python3 -c "import json; print(json.load(open('${SINA}/mac-law-root-v1.json'))['root'])")"
fi
export MAC_LAW_PORT="${MAC_LAW_PORT:-8781}"
export MAC_LAW_HOST="${MAC_LAW_HOST:-127.0.0.1}"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:${PATH:-/usr/bin:/bin}"
PY="/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
[[ -x "$PY" ]] || PY="$(command -v python3)"
cd "$ML"
exec "$PY" "$ML/mac-law-server.py"
