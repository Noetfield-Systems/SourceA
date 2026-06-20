#!/usr/bin/env bash
# validate-mac-daily-cleanup-wire-v1.sh — daily cleanup + live cockpit wire
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
fail=0

check() { if "$@"; then echo "PASS: $*"; else echo "FAIL: $*"; fail=1; fi; }

echo "=== Mac daily cleanup + live wire ==="

check test -f "$ROOT/brain-os/law/enforcement/SINA_MAC_DAILY_CLEANUP_LOCKED_v1.md"
check test -f "$ROOT/scripts/mac_daily_cleanup_v1.py"
check test -f "$ROOT/scripts/cursor_session_relief_v1.py"
check test -x "$ROOT/scripts/mac-daily-cleanup-v1.sh"
check grep -q probe_cursor_session "$ROOT/scripts/mac_health_live_v1.py"

python3 "$ROOT/scripts/mac_daily_cleanup_v1.py" --tier morning --quiet --json >/dev/null && echo "PASS: morning tier dry run" || { echo "FAIL: morning tier"; fail=1; }

for port in 13023 13024 13025 13026; do
  curl -sf -m 3 "http://127.0.0.1:${port}/health" >/dev/null && echo "PASS: :${port} LIVE" || { echo "FAIL: :${port} down"; fail=1; }
done

bash "$ROOT/scripts/validate-founder-glance-cockpit-apps-v1.sh" >/dev/null && echo "PASS: founder-glance cockpit" || { echo "FAIL: cockpit"; fail=1; }

python3 <<'PY' || { echo "FAIL: live cursor_session"; fail=1; }
import json, urllib.request
live = json.loads(urllib.request.urlopen("http://127.0.0.1:13024/api/mac-health/live", timeout=8).read())
assert live.get("ok"), live
cs = live.get("cursor_session") or {}
assert cs.get("founder_line") or cs.get("rss_mb") is not None, cs
print("PASS: Mac Health live cursor_session wired")
PY

if [[ "$fail" -eq 0 ]]; then
  echo "validate-mac-daily-cleanup-wire-v1: ALL PASS"
  exit 0
fi
echo "validate-mac-daily-cleanup-wire-v1: FAILED"
exit 1
