#!/usr/bin/env bash
# validate-program-progress-sync-crossref-v1.sh — sa-0999 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0999-program-progress-sync-t3-crossref_LOCKED_v1.md"
canonical = root / "archive/attachments/2026-06-14/sa-0974-program-progress-machine-sync-vs-manual-asf-edit-incidents_LOCKED_v1.md"
receipt = root / "receipts/sa-0974-receipt.json"

assert cross.is_file(), "missing sa-0999 cross-ref doc"
text = cross.read_text(encoding="utf-8")
assert "sa-0974" in text
assert "sa-0974-program-progress-machine-sync-vs-manual-asf-edit-incidents_LOCKED_v1.md" in text
assert canonical.is_file(), "canonical sa-0974 attachment missing"
assert receipt.is_file(), "canonical sa-0974 receipt missing"
for marker in ("## Two-speed progress model", "| Clock | SSOT |", "## Thesis"):
    assert marker not in text, f"T3 cross-ref must not duplicate table ({marker})"

print("OK: validate-program-progress-sync-crossref-v1 · canonical=sa-0974 · no duplicate table · sa-0999")
PY
