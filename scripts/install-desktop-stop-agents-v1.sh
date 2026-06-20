#!/usr/bin/env bash
# One double-click on Desktop — STOP all agents. No app, no keyboard, no Terminal typing.
set -euo pipefail
SA="$(cd "$(dirname "$0")/.." && pwd)"
DESKTOP="$HOME/Desktop"
CMD="$DESKTOP/⛔ STOP AGENTS.command"

cat >"$CMD" <<WRAP
#!/bin/bash
SA="${SA}"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:/usr/bin:/bin:/usr/sbin:/sbin"
UID_NUM=\$(id -u)
for L in com.sourcea.autorun-worker com.sourcea.hub com.sourcea.g7-governance-self-heal; do
  launchctl bootout "gui/\${UID_NUM}/\${L}" 2>/dev/null || true
done
/usr/bin/afplay /System/Library/Sounds/Basso.aiff &
/usr/bin/python3 "\$SA/scripts/mac_health_emergency_stop_v1.py" --trigger desktop-stop --fast --json >/dev/null 2>&1 || true
/usr/bin/osascript -e 'display alert "⛔ AGENTS STOPPED" message "Hub + auto-run paused (no respawn). Agents killed. Cursor restarted if it was hot. Reopen Cursor chat when window returns." buttons {"OK"} default button "OK"'
WRAP
chmod +x "$CMD"
xattr -cr "$CMD" 2>/dev/null || true

echo "✓ Desktop stop installed: $CMD"
echo "  Double-click when Mac is laggy — Basso + alert + full panic stop."
