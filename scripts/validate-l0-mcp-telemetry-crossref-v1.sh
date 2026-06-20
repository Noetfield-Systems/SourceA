#!/usr/bin/env bash
# validate-l0-mcp-telemetry-crossref-v1.sh — sa-0980 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0980-l0-mcp-telemetry-t3-crossref_LOCKED_v1.md"
canonical = root / "archive/attachments/2026-06-14/sa-0955-l0-full-mcp-editor-telemetry-defer_LOCKED_v1.md"
receipt = root / "receipts/sa-0955-receipt.json"

assert cross.is_file(), "missing sa-0980 cross-ref doc"
text = cross.read_text(encoding="utf-8")
assert "sa-0955" in text
assert "sa-0955-l0-full-mcp-editor-telemetry-defer_LOCKED_v1.md" in text
assert canonical.is_file(), "canonical sa-0955 attachment missing"
assert receipt.is_file(), "canonical sa-0955 receipt missing"
for marker in ("| **open_files** |", "| Signal | L0-full"):
    assert marker not in text, f"T3 cross-ref must not duplicate matrix ({marker})"

print("OK: validate-l0-mcp-telemetry-crossref-v1 · canonical=sa-0955 · no duplicate table · sa-0980")
PY
