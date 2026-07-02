#!/usr/bin/env bash
# sync-mac-launchd-wrappers-v1.sh — install ~/.sina launchd wrappers (TCC-safe entrypoints)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/scripts/sourcea-python-v1.sh"
[[ -x "$PY" ]] || PY="/usr/bin/python3"
"$PY" "$ROOT/scripts/mac_launchd_tcc_guard_v1.py" --sync-wrappers --json
