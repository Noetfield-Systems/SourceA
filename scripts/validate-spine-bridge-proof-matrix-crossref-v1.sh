#!/usr/bin/env bash
# validate-spine-bridge-proof-matrix-crossref-v1.sh — sa-0998 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0998-spine-bridge-proof-matrix-t3-crossref_LOCKED_v1.md"
canonical = root / "archive/attachments/2026-06-14/sa-0973-spine-bridge-founder-proof-types-matrix_LOCKED_v1.md"
receipt = root / "receipts/sa-0973-receipt.json"

assert cross.is_file(), "missing sa-0998 cross-ref doc"
text = cross.read_text(encoding="utf-8")
assert "sa-0973" in text
assert "sa-0973-spine-bridge-founder-proof-types-matrix_LOCKED_v1.md" in text
assert canonical.is_file(), "canonical sa-0973 attachment missing"
assert receipt.is_file(), "canonical sa-0973 receipt missing"
for marker in ("## Proof types matrix", "| Proof type |", "## Thesis"):
    assert marker not in text, f"T3 cross-ref must not duplicate table ({marker})"

print("OK: validate-spine-bridge-proof-matrix-crossref-v1 · canonical=sa-0973 · no duplicate table · sa-0998")
PY
