#!/usr/bin/env bash
# cursor-ultra-light-v1.sh — Cursor ONLY, one window, very very light Mac body
# Real fix: 8 extension-hosts ≈ 5 GB RAM → quit + reopen ONE folder + kill background stack
#
# Usage:
#   bash ~/Desktop/SourceA/scripts/cursor-ultra-light-v1.sh
#   bash ~/Desktop/SourceA/scripts/cursor-ultra-light-v1.sh --keep ~/Desktop/SourceA
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
exec python3 "$ROOT/scripts/cursor_ultra_light_v1.py" --json "$@"
