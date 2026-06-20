#!/usr/bin/env bash
# sa-0504 — Wire G3 in strategic this_week
set -euo pipefail
cd "$(dirname "$0")"
python3 - <<'PY'
import sys
sys.path.insert(0, ".")
from strategic_synthesis_hub import this_week
from pathlib import Path
root = Path("..")
attach = root / "archive/attachments/2026-06-14/sa-0504-wire-g3-this-week_LOCKED_v1.md"
assert attach.is_file()
tw = this_week()
text = str(tw).lower()
assert any("g3" in str(x).lower() for x in tw), tw
assert "wire" in text or "attest" in text
PY
echo "OK: validate-wire-g3-this-week-v1 · sa-0504"
