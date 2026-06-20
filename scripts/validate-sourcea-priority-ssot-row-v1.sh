#!/usr/bin/env bash
# sa-0025 / sa-0075 — SOURCEA-PRIORITY must have SSOT alignment PASS row with timestamp
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import re
from pathlib import Path

from append_ssot_alignment_priority_v1 import ROW_TITLE

ROOT = Path(__file__).resolve().parents[1]
PRIORITY = ROOT / "brain-os" / "plan-registry" / "SOURCEA-PRIORITY.md"
text = PRIORITY.read_text(encoding="utf-8")

assert "## Evidence log" in text, "SOURCEA-PRIORITY missing Evidence log"
assert "SSOT alignment PASS" in text, "PRIORITY missing SSOT alignment PASS phrase"

mod = (ROOT / "scripts" / "append_ssot_alignment_priority_v1.py").read_text(encoding="utf-8")
assert "sa-0025" in mod, "append module missing sa-0025 marker"
assert "sa-0075" in mod, "append module missing sa-0075 marker"

checked = []
for marker in ("sa-0025", "sa-0075"):
    assert marker in text, f"PRIORITY missing {marker} row"
    rows = [ln for ln in text.splitlines() if marker in ln and ln.strip().startswith("|")]
    assert rows, f"no evidence table row for {marker}"
    row = rows[0]
    assert re.match(r"^\|\s*\d{4}-\d{2}-\d{2}\s*\|", row), f"row missing date timestamp: {row!r}"
    assert "validate-phase-s0-ssot-alignment-v1" in row, row
    assert "@" in row or re.search(r"\d{4}-\d{2}-\d{2}T", row), f"row missing ISO timestamp detail: {row!r}"
    checked.append(f"{marker} · {row[:56]}…")

print(f"OK: validate-sourcea-priority-ssot-row-v1 · {' · '.join(checked)}")
PY
