#!/usr/bin/env bash
# validate-ragas-eval1b-crossref-v1.sh — sa-0978 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0978-ragas-eval1b-t3-crossref_LOCKED_v1.md"
canonical = root / "archive/attachments/2026-06-14/sa-0953-ragas-vs-eval1b-research_LOCKED_v1.md"
receipt = root / "receipts/sa-0953-receipt.json"

assert cross.is_file(), "missing sa-0978 cross-ref doc"
text = cross.read_text(encoding="utf-8")
assert "sa-0953" in text
assert "sa-0953-ragas-vs-eval1b-research_LOCKED_v1.md" in text
assert canonical.is_file(), "canonical sa-0953 attachment missing"
assert receipt.is_file(), "canonical sa-0953 receipt missing"
for marker in ("| **RAGAS-style CI** |", "| Dimension | **RAGAS"):
    assert marker not in text, f"T3 cross-ref must not duplicate compare matrix ({marker})"

print("OK: validate-ragas-eval1b-crossref-v1 · canonical=sa-0953 · no duplicate table · sa-0978")
PY
