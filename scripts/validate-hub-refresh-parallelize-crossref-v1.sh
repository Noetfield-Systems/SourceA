#!/usr/bin/env bash
# validate-hub-refresh-parallelize-crossref-v1.sh — sa-0987 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0987-hub-refresh-parallelize-t3-crossref_LOCKED_v1.md"
canonical = root / "archive/attachments/2026-06-14/sa-0962-hub-refresh-parallelize-progress-bowl_LOCKED_v1.md"
receipt = root / "receipts/sa-0962-receipt.json"

assert cross.is_file(), "missing sa-0987 cross-ref doc"
text = cross.read_text(encoding="utf-8")
assert "sa-0962" in text
assert "sa-0962-hub-refresh-parallelize-progress-bowl_LOCKED_v1.md" in text
assert canonical.is_file(), "canonical sa-0962 attachment missing"
assert receipt.is_file(), "canonical sa-0962 receipt missing"
for marker in ("## Current pipeline", "## Perf baseline", "| Step | Script |"):
    assert marker not in text, f"T3 cross-ref must not duplicate table ({marker})"

print("OK: validate-hub-refresh-parallelize-crossref-v1 · canonical=sa-0962 · no duplicate table · sa-0987")
PY
