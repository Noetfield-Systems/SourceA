#!/usr/bin/env bash
# sa-0040 / sa-0090 / sa-0015 — strict build must refresh PROGRAM_PROGRESS signals_auto.synced_at
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
build_py = Path(__file__).resolve().parent / "build-sina-command-panel.py"
text = build_py.read_text(encoding="utf-8")
assert "_run_update_program_progress" in text, "build missing _run_update_program_progress (sa-0040)"
assert "update-program-progress.py" in text, "build must invoke update-program-progress.py (sa-0040)"
assert "SINA_SKIP_NESTED_BOWL" in text, "build must set SINA_SKIP_NESTED_BOWL on progress sync (sa-0040)"

prog = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
synced = (prog.get("signals_auto") or {}).get("synced_at")
assert synced, "PROGRAM_PROGRESS signals_auto.synced_at missing (sa-0040)"
assert prog.get("updated_by") == "update-program-progress.py", prog.get("updated_by")
print(f"OK: validate-program-progress-build-sync-v1 · synced_at={synced}")
PY
