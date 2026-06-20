#!/usr/bin/env bash
# founder-mac-pressure-relief-v1.sh — REAL relief when Mac is hot/RAM-starved (one command)
# Usage:
#   bash ~/Desktop/SourceA/scripts/founder-mac-pressure-relief-v1.sh
#   bash ~/Desktop/SourceA/scripts/founder-mac-pressure-relief-v1.sh --fast
#   bash ~/Desktop/SourceA/scripts/founder-mac-pressure-relief-v1.sh --restart-cursor
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
RESTART=0
FAST=0
for arg in "$@"; do
  case "$arg" in
    --restart-cursor) RESTART=1 ;;
    --fast) FAST=1 ;;
  esac
done

echo "▸ Mac Law RAM pressure relief — freezing factory · booting autorun · light validators only"
if [[ "$FAST" -eq 1 ]]; then
  python3 "$ROOT/scripts/mac_health_ram_pressure_v1.py" --fast --json
else
  python3 "$ROOT/scripts/mac_health_ram_pressure_v1.py" --json
fi

if [[ "$RESTART" -eq 1 ]]; then
  echo "▸ Restarting Cursor (frees 6–12 GB when many windows open)"
  python3 "$ROOT/scripts/cursor_session_relief_v1.py" --trim --restart --force-restart --json || true
else
  echo "▸ Cursor kept open — if still hot: bash $0 --restart-cursor"
fi

echo ""
echo "▸ Close extra Cursor windows (keep ONE workspace) — was 9 extension-hosts = RAM death"
echo "▸ Hub + Mac Health only — quit Routing Panel live refresh if open"
echo "Receipt: ~/.sina/mac-health/ram-relief-latest-v1.json"
