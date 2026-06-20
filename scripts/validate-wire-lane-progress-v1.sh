#!/usr/bin/env bash
# sa-0512 — WIRE_LANE_PROGRESS.md locally for Wire agent
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd .. && pwd)"

python3 - <<PY
from pathlib import Path
root = Path("$ROOT")
doc = root / "brain-os/law/WIRE_LANE_PROGRESS.md"
attach = root / "archive/attachments/2026-06-14/sa-0512-wire-lane-progress_LOCKED_v1.md"
prog = root / "PROGRAM_PROGRESS.json"
assert doc.is_file(), doc
assert attach.is_file(), attach
text = doc.read_text(encoding="utf-8")
assert "G1" in text and "G2" in text and "G3" in text, "missing G1/G2/G3 sections"
assert "full_m8" in text.lower() or "full_m8" in text
blob = prog.read_text(encoding="utf-8")
assert "WIRE_LANE_PROGRESS.md" in blob
PY
echo "OK: validate-wire-lane-progress-v1 · sa-0512"
