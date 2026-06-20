#!/usr/bin/env bash
# validate-model-workflow-gaps-crossref-v1.sh — sa-0976 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0976-model-workflow-gaps-t3-crossref_LOCKED_v1.md"
canonical = root / "archive/attachments/2026-06-14/sa-0951-model-workflow-gaps-research_LOCKED_v1.md"
receipt = root / "receipts/sa-0951-receipt.json"

assert cross.is_file(), "missing sa-0976 cross-ref doc"
text = cross.read_text(encoding="utf-8")
assert "canonical_sa: sa-0951" in text or "canonical_sa** | sa-0951" in text or "**canonical_sa** | sa-0951" in text or "sa-0951" in text
assert "sa-0951-model-workflow-gaps-research_LOCKED_v1.md" in text
assert canonical.is_file(), "canonical sa-0951 attachment missing"
assert receipt.is_file(), "canonical sa-0951 receipt missing"
# T3 stub must not fork duplicate compare table
for marker in ("| **GPT-4o** |", "| GPT-4o |"):
    assert marker not in text, f"T3 cross-ref must not duplicate compare table ({marker})"

print("OK: validate-model-workflow-gaps-crossref-v1 · canonical=sa-0951 · no duplicate table · sa-0976")
PY
