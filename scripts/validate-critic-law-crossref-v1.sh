#!/usr/bin/env bash
# validate-critic-law-crossref-v1.sh — sa-0983 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0983-critic-law-t3-crossref_LOCKED_v1.md"
canonical = root / "archive/attachments/2026-06-14/sa-0958-critic-law-wrong-rate-table_LOCKED_v1.md"
receipt = root / "receipts/sa-0958-receipt.json"

assert cross.is_file(), "missing sa-0983 cross-ref doc"
text = cross.read_text(encoding="utf-8")
assert "sa-0958" in text
assert "sa-0958-critic-law-wrong-rate-table_LOCKED_v1.md" in text
assert canonical.is_file(), "canonical sa-0958 attachment missing"
assert receipt.is_file(), "canonical sa-0958 receipt missing"
for marker in ("| Failure mode |", "## External chat wrong-rate table", "**Skipped INPUT CLASS**"):
    assert marker not in text, f"T3 cross-ref must not duplicate matrix ({marker})"

print("OK: validate-critic-law-crossref-v1 · canonical=sa-0958 · no duplicate table · sa-0983")
PY
