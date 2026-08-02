#!/usr/bin/env bash
# open-sourcea-cursor-v1.sh — ONE Cursor window · SourceA only (founder daily start)
set -euo pipefail
SOURCEA="$HOME/Desktop/SourceA"
# Quit extra Cursor windows first (optional — comment out if you have unsaved work elsewhere)
osascript -e 'tell application "Cursor" to quit saving yes' 2>/dev/null || true
sleep 2
open -a "/Applications/Cursor.app" "$SOURCEA/sourcea-founder.code-workspace"
