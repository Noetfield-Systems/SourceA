#!/usr/bin/env bash
# Panic Stop status
LOG="$HOME/.sina/mac-health-panic-hotkey.log"
echo "Panic Stop — status"
echo ""
if pgrep -f "Panic Stop.app" >/dev/null 2>&1; then
  echo "  ⛔ menu bar app: RUNNING (look top-right of screen)"
else
  echo "  ⛔ menu bar app: NOT RUNNING"
  echo "  fix: bash ~/Desktop/SourceA/scripts/install-panic-stop-menubar-v1.sh"
fi
echo ""
grep "\[menubar\]" "$LOG" 2>/dev/null | tail -6 || echo "  (no menubar log yet)"
echo ""
echo "Works WITHOUT keyboard:"
echo "  1. Click ⛔ in menu bar → PANIC STOP now"
echo "  2. touch ~/.sina/PANIC.now"
echo ""
echo "For keyboard (⌃⌘P): System Settings → Privacy → Accessibility → Panic Stop ON"
echo "  Then restart: bash ~/Desktop/SourceA/scripts/install-panic-stop-menubar-v1.sh"
