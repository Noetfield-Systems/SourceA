#!/usr/bin/env bash
# sourcea-python-v1.sh — Mac-safe python resolver (INCIDENT-042)
# Framework bin/python3 -c and heredoc get SIGKILL on some Mac bodies; /usr/bin/python3 is safe.
set -euo pipefail

_resolve_sourcea_python() {
  local app_py="/Library/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python"
  if [[ -x /usr/bin/python3 ]]; then
    echo /usr/bin/python3
  elif [[ -x "$app_py" ]]; then
    echo "$app_py"
  elif [[ -x /opt/homebrew/bin/python3 ]]; then
    echo /opt/homebrew/bin/python3
  else
    command -v python3
  fi
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  PY="$(_resolve_sourcea_python)"
  exec "$PY" "$@"
fi
