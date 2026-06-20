#!/usr/bin/env bash
# sa-0201 — build-sina-command-panel _run_audit must invoke .sh via bash, not python3.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export ROOT

python3 - <<'PY'
import os
import re
import sys
from pathlib import Path

path = Path(os.environ["ROOT"]) / "scripts/build-sina-command-panel.py"
text = path.read_text(encoding="utf-8")

m = re.search(r"def _run_audit\([^)]*\)[^:]*:\n(.*?)(?=\ndef |\nclass )", text, re.S)
if not m:
    print("FAIL: _run_audit not found")
    sys.exit(1)
body = m.group(1)

if not re.search(
    r'if name\.endswith\("\.sh"\):\s*\n\s*cmd = \["bash", str\(path\)\]',
    body,
):
    print("FAIL: .sh branch must be cmd = [\"bash\", str(path)]")
    sys.exit(1)

print("OK: validate-build-run-audit-v1 · _run_audit .sh → bash")
PY
