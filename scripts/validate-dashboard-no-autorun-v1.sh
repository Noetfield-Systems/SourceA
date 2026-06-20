#!/usr/bin/env bash
# validate-dashboard-no-autorun-v1.sh — monitor dashboard must demote START under FREEZE (AS-18)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DASH="$ROOT/scripts/dashboard_server_v1.py"

fail() { echo "FAIL: validate-dashboard-no-autorun-v1 — $*" >&2; exit 1; }

[[ -f "$DASH" ]] || fail "missing dashboard_server_v1.py"

grep -q 'id="btn-start-autorun"' "$DASH" || fail "missing btn-start-autorun id"
grep -q 'st.kill_flag' "$DASH" || fail "refresh must check kill_flag for START button"
grep -q 'FREEZE' "$DASH" || fail "dashboard must show FREEZE copy when kill_flag"
grep -q 'freeze-banner' "$DASH" || fail "missing freeze-banner element"

cd "$ROOT"
python3 <<'PY'
from pathlib import Path
text = Path("scripts/dashboard_server_v1.py").read_text(encoding="utf-8")
# Raw START AUTO RUN in HTML is OK if JS disables it under kill_flag
assert "startAutorun" in text and "kill_flag" in text
print("OK: validate-dashboard-no-autorun-v1")
PY
