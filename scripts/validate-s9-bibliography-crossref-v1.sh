#!/usr/bin/env bash
# validate-s9-bibliography-crossref-v1.sh — sa-1000 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-1000-s9-bibliography-t3-crossref_LOCKED_v1.md"
canonical = root / "archive/attachments/2026-06-14/sa-0975-phase-s9-research-index-sourcea-1000-lock-bibliography_LOCKED_v1.md"
receipt = root / "receipts/sa-0975-receipt.json"

assert cross.is_file(), "missing sa-1000 cross-ref doc"
text = cross.read_text(encoding="utf-8")
assert "sa-0975" in text
assert "sa-0975-phase-s9-research-index-sourcea-1000-lock-bibliography_LOCKED_v1.md" in text
assert canonical.is_file(), "canonical sa-0975 attachment missing"
assert receipt.is_file(), "canonical sa-0975 receipt missing"
for marker in ("## Gap audit", "| Item | Present |", "## Proposed bibliography"):
    assert marker not in text, f"T3 cross-ref must not duplicate table ({marker})"

print("OK: validate-s9-bibliography-crossref-v1 · canonical=sa-0975 · no duplicate table · sa-1000")
PY
