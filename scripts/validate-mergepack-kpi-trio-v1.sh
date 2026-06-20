#!/usr/bin/env bash
# sa-0509 — MergePack KPI trio payload
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd .. && pwd)"
python3 - <<PY
from pathlib import Path
root = Path("$ROOT")
attach = root / "archive/attachments/2026-06-14/sa-0509-mergepack-kpi-trio_LOCKED_v1.md"
app = root / "agent-control-panel/assets/app.js"
data = root / "agent-control-panel/command-data-shell.json"
assert attach.is_file()
app_text = app.read_text(encoding="utf-8")
assert "mergepack_kpi" in app_text or "kpiTrio" in app_text
blob = data.read_text(encoding="utf-8")
assert "MP-SHIP" in blob or "mergepack" in blob.lower()
PY
echo "OK: validate-mergepack-kpi-trio-v1 · sa-0509"
