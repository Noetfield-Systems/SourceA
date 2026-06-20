#!/usr/bin/env bash
# validate-mono-pick-workflow-crossref-v1.sh — sa-0986 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0986-mono-pick-workflow-t3-crossref_LOCKED_v1.md"
canonical = root / "archive/attachments/2026-06-14/sa-0961-mono-sourcea-1000-pick-workflow-compare_LOCKED_v1.md"
receipt = root / "receipts/sa-0961-receipt.json"

assert cross.is_file(), "missing sa-0986 cross-ref doc"
text = cross.read_text(encoding="utf-8")
assert "sa-0961" in text
assert "sa-0961-mono-sourcea-1000-pick-workflow-compare_LOCKED_v1.md" in text
assert canonical.is_file(), "canonical sa-0961 attachment missing"
assert receipt.is_file(), "canonical sa-0961 receipt missing"
for marker in ("## Pack registry compare", "## Pick algorithm compare", "| Field | SourceA (`sourcea-1000`) |"):
    assert marker not in text, f"T3 cross-ref must not duplicate table ({marker})"

print("OK: validate-mono-pick-workflow-crossref-v1 · canonical=sa-0961 · no duplicate table · sa-0986")
PY
