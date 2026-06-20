#!/usr/bin/env bash
# validate-world-model-v5-v4-crossref-v1.sh — sa-0995 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0995-world-model-v5-v4-t3-crossref_LOCKED_v1.md"
canonical = root / "archive/attachments/2026-06-14/sa-0970-world-model-v5-v4-migration-lessons_LOCKED_v1.md"
receipt = root / "receipts/sa-0970-receipt.json"

assert cross.is_file(), "missing sa-0995 cross-ref doc"
text = cross.read_text(encoding="utf-8")
assert "sa-0970" in text
assert "sa-0970-world-model-v5-v4-migration-lessons_LOCKED_v1.md" in text
assert canonical.is_file(), "canonical sa-0970 attachment missing"
assert receipt.is_file(), "canonical sa-0970 receipt missing"
for marker in ("## Version lineage", "| Version | Path |", "INCIDENT-004"):
    assert marker not in text, f"T3 cross-ref must not duplicate table ({marker})"

print("OK: validate-world-model-v5-v4-crossref-v1 · canonical=sa-0970 · no duplicate table · sa-0995")
PY
