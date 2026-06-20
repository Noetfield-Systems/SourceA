#!/usr/bin/env bash
# validate-hub-only-terminal-first-crossref-v1.sh — sa-0997 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0997-hub-only-terminal-first-t3-crossref_LOCKED_v1.md"
canonical = root / "archive/attachments/2026-06-14/sa-0972-founder-hub-only-vs-terminal-first-agent-products_LOCKED_v1.md"
receipt = root / "receipts/sa-0972-receipt.json"

assert cross.is_file(), "missing sa-0997 cross-ref doc"
text = cross.read_text(encoding="utf-8")
assert "sa-0972" in text
assert "sa-0972-founder-hub-only-vs-terminal-first-agent-products_LOCKED_v1.md" in text
assert canonical.is_file(), "canonical sa-0972 attachment missing"
assert receipt.is_file(), "canonical sa-0972 receipt missing"
for marker in ("## Comparison matrix", "| Dimension | Terminal-first", "## Thesis"):
    assert marker not in text, f"T3 cross-ref must not duplicate table ({marker})"

print("OK: validate-hub-only-terminal-first-crossref-v1 · canonical=sa-0972 · no duplicate table · sa-0997")
PY
