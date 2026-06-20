#!/usr/bin/env bash
# Install G7 governance self-heal launchd agent (hourly --heal).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_SRC="$ROOT/scripts/com.sourcea.g7-governance-self-heal.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.sourcea.g7-governance-self-heal.plist"
LABEL="com.sourcea.g7-governance-self-heal"

[[ -f "$PLIST_SRC" ]] || { echo "FAIL: missing $PLIST_SRC" >&2; exit 1; }
mkdir -p "$HOME/Library/LaunchAgents" "$HOME/.sina"
cp "$PLIST_SRC" "$PLIST_DST"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"
launchctl enable "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl kickstart -k "gui/$(id -u)/$LABEL" 2>/dev/null || true
echo "OK: G7 self-heal launchd loaded — hourly python3 scripts/governance_self_heal_daemon_v1.py --heal"
echo "Log: ~/.sina/g7-governance-self-heal.log"
