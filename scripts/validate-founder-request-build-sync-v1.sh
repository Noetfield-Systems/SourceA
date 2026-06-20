#!/usr/bin/env bash
# sa-0507 — founder_request_tracker build sync
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd .. && pwd)"
python3 - <<PY
from pathlib import Path
root = Path("$ROOT")
build = root / "scripts/build-sina-command-panel.py"
attach = root / "archive/attachments/2026-06-14/sa-0507-founder-request-build-sync_LOCKED_v1.md"
assert "sync_shipped_from_disk" in build.read_text(encoding="utf-8")
assert attach.is_file()
PY
bash validate-program-progress-build-sync-v1.sh
echo "OK: validate-founder-request-build-sync-v1 · sa-0507"
