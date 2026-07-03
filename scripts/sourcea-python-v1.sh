#!/usr/bin/env bash
# sourcea-python-v1.sh — Mac-safe python resolver
set -euo pipefail
if [[ -x /usr/bin/python3 ]]; then
  exec /usr/bin/python3 "$@"
fi
exec python3 "$@"
