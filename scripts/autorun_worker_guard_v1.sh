#!/usr/bin/env bash
# Autorun launchd wrapper — never spawn dispatcher when Mac focus freeze is on.
set -euo pipefail
FREEZE="${HOME}/.sina/auto-run-disabled-v1.flag"
if [[ -f "$FREEZE" ]]; then
  exit 0
fi
ROOT="${HOME}/Desktop/SourceA"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:${PATH:-/usr/bin:/bin}"
cd "$ROOT"
exec python3 "$ROOT/scripts/autorun_dispatcher_v1.py"
