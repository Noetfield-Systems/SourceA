#!/usr/bin/env bash
# founder-mac-fresh-start-v1.sh — reset Mac like day-one: cloud only, one Cursor window, ~15 processes max
# Usage:
#   bash ~/Desktop/SourceA/scripts/founder-mac-fresh-start-v1.sh
#   bash ~/Desktop/SourceA/scripts/founder-mac-fresh-start-v1.sh --keep ~/Desktop/SourceA
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
echo "▸ Mac Law FRESH START — bootout background · reset Cursor window state · one folder · cloud body"
exec python3 "$ROOT/scripts/founder_mac_fresh_start_v1.py" --json "$@"
