#!/usr/bin/env bash
# sa-0625 — WTM layer gap note when L0-full editor telemetry partial
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
from pathlib import Path

from system_roadmap import _build_layer_comparison

wtm = Path("../brain-os/wtm/SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md").resolve()
text = wtm.read_text(encoding="utf-8")

assert "L0-full gap note" in text, "WTM must document L0-full gap"
assert "editor telemetry" in text.lower() or "editor open_files" in text.lower(), text
assert "partial" in text.lower(), "WTM must mark L0-full as partial"

rows = {r["layer"]: r for r in _build_layer_comparison()}
l0 = rows.get("L0") or {}
assert l0.get("your_status") in ("done", "partial"), l0
gap = str(l0.get("gap") or "").lower()
assert "editor" in gap or "l0-full" in gap or "hub touch" in gap, l0.get("gap")

print("OK: validate-wtm-l0-full-editor-telemetry-gap-v1 · L0 partial editor telemetry documented")
PY
