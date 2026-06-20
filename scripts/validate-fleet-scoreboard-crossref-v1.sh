#!/usr/bin/env bash
# validate-fleet-scoreboard-crossref-v1.sh — sa-0984 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0984-fleet-scoreboard-t3-crossref_LOCKED_v1.md"
canonical = root / "archive/attachments/2026-06-14/sa-0959-fleet-scoreboard-auto-check-taxonomy_LOCKED_v1.md"
receipt = root / "receipts/sa-0959-receipt.json"

assert cross.is_file(), "missing sa-0984 cross-ref doc"
text = cross.read_text(encoding="utf-8")
assert "sa-0959" in text
assert "sa-0959-fleet-scoreboard-auto-check-taxonomy_LOCKED_v1.md" in text
assert canonical.is_file(), "canonical sa-0959 attachment missing"
assert receipt.is_file(), "canonical sa-0959 receipt missing"
for marker in ("| ID | Check |", "## Auto-check taxonomy", "`session_report`"):
    assert marker not in text, f"T3 cross-ref must not duplicate matrix ({marker})"

print("OK: validate-fleet-scoreboard-crossref-v1 · canonical=sa-0959 · no duplicate table · sa-0984")
PY
