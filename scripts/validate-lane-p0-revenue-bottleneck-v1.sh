#!/usr/bin/env bash
# sa-0510 — lane P0 revenue bottleneck one_line
set -euo pipefail
cd "$(dirname "$0")"
python3 - <<'PY'
import sys
sys.path.insert(0, ".")
from strategic_synthesis_hub import strategic_synthesis_payload
from pathlib import Path
root = Path("..")
attach = root / "archive/attachments/2026-06-14/sa-0510-lane-p0-revenue-bottleneck_LOCKED_v1.md"
assert attach.is_file()
p = strategic_synthesis_payload()
line = (p.get("one_line") or "").lower()
assert line and ("revenue" in line or "p0" in line or "dispatch" in line), line
PY
echo "OK: validate-lane-p0-revenue-bottleneck-v1 · sa-0510"
