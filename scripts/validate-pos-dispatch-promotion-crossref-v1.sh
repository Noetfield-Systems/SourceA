#!/usr/bin/env bash
# validate-pos-dispatch-promotion-crossref-v1.sh — sa-0981 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0981-pos-dispatch-promotion-t3-crossref_LOCKED_v1.md"
canonical = root / "archive/attachments/2026-06-14/sa-0956-pos-dispatch-promotion-criteria_LOCKED_v1.md"
receipt = root / "receipts/sa-0956-receipt.json"

assert cross.is_file(), "missing sa-0981 cross-ref doc"
text = cross.read_text(encoding="utf-8")
assert "sa-0956" in text
assert "sa-0956-pos-dispatch-promotion-criteria_LOCKED_v1.md" in text
assert canonical.is_file(), "canonical sa-0956 attachment missing"
assert receipt.is_file(), "canonical sa-0956 receipt missing"
for marker in ("| # | Criterion |", "| 1 | **Eval-1b live** |", "## Promotion criteria matrix"):
    assert marker not in text, f"T3 cross-ref must not duplicate matrix ({marker})"

print("OK: validate-pos-dispatch-promotion-crossref-v1 · canonical=sa-0956 · no duplicate table · sa-0981")
PY
