#!/usr/bin/env bash
# sa-0039 / sa-0089 / sa-0014 — app.js must have zero WORLD_TARGET_MODEL_MAP_LOCKED_v2 hits
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
import re
import sys
from pathlib import Path

import audit_hub_source_alignment as audit
from hub_worker_mode_v1 import worker_hub_mode

if worker_hub_mode():
    print("OK: validate-app-js-no-stale-map-v2-v1 · skipped — Worker Hub (H1) retired app.js")
    raise SystemExit(0)

root = Path(__file__).resolve().parents[1]
app = root / "agent-control-panel" / "assets" / "app.js"
assert app.is_file(), "missing app.js"

text = app.read_text(encoding="utf-8")
hits = re.findall(r"WORLD_TARGET_MODEL_MAP_LOCKED_v2", text)
assert not hits, f"stale v2 map in app.js: {hits!r}"

errors: list[str] = []
for pattern, label in audit.APP_FORBIDDEN:
    if "v2" in pattern and re.search(pattern, text):
        errors.append(f"app.js {label}")

assert not errors, errors
print("OK: validate-app-js-no-stale-map-v2-v1 · zero WORLD_TARGET_MODEL_MAP_LOCKED_v2 hits")
PY
