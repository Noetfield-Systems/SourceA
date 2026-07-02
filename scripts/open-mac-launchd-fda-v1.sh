#!/usr/bin/env bash
# open-mac-launchd-fda-v1.sh — one-tap Full Disk Access for launchd + Desktop repo
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
mkdir -p "$SINA"

python3 "$ROOT/scripts/mac_launchd_tcc_guard_v1.py" --sync-wrappers --json >/dev/null 2>&1 || true

echo "=== Mac launchd + Desktop TCC fix ==="
echo ""
echo "launchd background agents cannot read ~/Desktop without Full Disk Access."
echo "Add these binaries in System Settings → Privacy & Security → Full Disk Access:"
echo ""

python3 - <<'PY'
import json
from pathlib import Path
p = Path.home() / ".sina" / "mac-launchd-tcc-receipt-v1.json"
if p.is_file():
    row = json.loads(p.read_text())
    bins = row.get("fda_binaries") or []
else:
    bins = ["/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"]
for b in bins:
    print(f"  + {b}")
PY

echo ""
echo "Then reload Hub launchd:"
echo "  bash $ROOT/scripts/install-hub-launchd-v1.sh"
echo ""
echo "Or skip launchd (Hub still starts from Terminal):"
echo "  SINA_LAUNCHD_TCC_FALLBACK=1 bash $ROOT/scripts/serve-sina-command.sh"
echo ""

open "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles" 2>/dev/null \
  || open "x-apple.systempreferences:com.apple.settings.PrivacySecurity.extension?Privacy_AllFiles" 2>/dev/null \
  || open "/System/Applications/System Settings.app" 2>/dev/null \
  || true

echo "Opened Privacy → Full Disk Access (add Python 3.12, toggle ON)."
