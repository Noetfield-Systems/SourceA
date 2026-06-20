#!/usr/bin/env bash
# validate-agent-verify-gates-crossref-v1.sh — sa-0977 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0977-agent-verify-gates-t3-crossref_LOCKED_v1.md"
canonical = root / "archive/attachments/2026-06-14/sa-0952-agent-verify-gates-spike_LOCKED_v1.md"
receipt = root / "receipts/sa-0952-receipt.json"

assert cross.is_file(), "missing sa-0977 cross-ref doc"
text = cross.read_text(encoding="utf-8")
assert "sa-0952" in text
assert "sa-0952-agent-verify-gates-spike_LOCKED_v1.md" in text
assert canonical.is_file(), "canonical sa-0952 attachment missing"
assert receipt.is_file(), "canonical sa-0952 receipt missing"
for marker in ("| **Cognition Devin** |", "| **SWE-agent"):
    assert marker not in text, f"T3 cross-ref must not duplicate compare matrix ({marker})"

print("OK: validate-agent-verify-gates-crossref-v1 · canonical=sa-0952 · no duplicate table · sa-0977")
PY
