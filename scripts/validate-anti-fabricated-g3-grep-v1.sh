#!/usr/bin/env bash
# sa-0511 — anti fabricated G3 in scripts
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd .. && pwd)"
python3 - <<PY
from pathlib import Path
root = Path("$ROOT")
attach = root / "archive/attachments/2026-06-14/sa-0511-anti-fabricated-g3_LOCKED_v1.md"
hub = root / "scripts/strategic_synthesis_hub.py"
assert attach.is_file()
assert "Fabricate physical G3" in hub.read_text(encoding="utf-8")
PY
echo "OK: validate-anti-fabricated-g3-grep-v1 · sa-0511"
