#!/usr/bin/env bash
# validate-no-auto-screenshot-v1.sh — Mac Law no auto screenshot gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LAW="$HOME/Desktop/MacLaw/MAC_NO_AUTO_SCREENSHOT_LOCKED.md"
fail() { echo "FAIL: validate-no-auto-screenshot-v1 — $*" >&2; exit 1; }

[[ -f "$LAW" ]] || fail "missing Mac Law doc: $LAW"
[[ -f "$ROOT/scripts/no_auto_screenshot_v1.py" ]] || fail "missing no_auto_screenshot_v1.py"

grep -q 'no-auto-screenshot-v1.flag' "$ROOT/scripts/no_auto_screenshot_v1.py" \
  || fail "enforce module missing no-auto flag"
grep -q 'kill_automation_only' "$ROOT/scripts/no_auto_screenshot_v1.py" \
  || fail "enforce module missing kill_automation_only"

for f in founder-mac-reset-v1.sh mac_control_plane_v1.py mac_daily_cleanup_v1.py; do
  if grep -q 'pkill -9 -f screencapture' "$ROOT/scripts/$f" 2>/dev/null \
    || grep -q 'pkill", "-9", "-f", "screencapture' "$ROOT/scripts/$f" 2>/dev/null; then
    fail "forbidden blanket pkill screencapture in scripts/$f"
  fi
done

grep -q 'in_gate_no_capture' "$ROOT/scripts/critic_boot_v1.py" \
  || fail "critic_boot must skip capture in_gate"

python3 "$ROOT/scripts/no_auto_screenshot_v1.py" --dry-run --json >/dev/null \
  || fail "no_auto_screenshot probe failed (run --enforce once if first install)"

echo "PASS: validate-no-auto-screenshot-v1.sh"
