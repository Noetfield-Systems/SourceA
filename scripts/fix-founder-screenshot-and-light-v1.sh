#!/usr/bin/env bash
# fix-founder-screenshot-and-light-v1.sh — drag fix + fresh light Cursor (one command)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
echo "▸ 1/2 Screenshot drag shield (auto capture OFF · hub/cleanup OFF · thumbnail ON)"
python3 "$ROOT/scripts/fix_screenshot_drag_v1.py" --json
echo ""
echo "▸ 2/2 Fresh light Cursor (one window · cloud body) — saves rules & files, clears chat RAM"
echo "   Run in Terminal.app if this shell is slow:"
echo "   bash $ROOT/scripts/founder-mac-fresh-start-v1.sh"
