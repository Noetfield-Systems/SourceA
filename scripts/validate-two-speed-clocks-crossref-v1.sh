#!/usr/bin/env bash
# validate-two-speed-clocks-crossref-v1.sh — sa-0992 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0992-two-speed-clocks-t3-crossref_LOCKED_v1.md"
canonical = root / "archive/attachments/2026-06-14/sa-0967-two-speed-clocks-strategic-slice-lane-p0-case-study_LOCKED_v1.md"
receipt = root / "receipts/sa-0967-receipt.json"

assert cross.is_file(), "missing sa-0992 cross-ref doc"
text = cross.read_text(encoding="utf-8")
assert "sa-0967" in text
assert "sa-0967-two-speed-clocks-strategic-slice-lane-p0-case-study_LOCKED_v1.md" in text
assert canonical.is_file(), "canonical sa-0967 attachment missing"
assert receipt.is_file(), "canonical sa-0967 receipt missing"
for marker in ("## Two-speed model", "| Clock | Namespace |", "**A — Product / slice**"):
    assert marker not in text, f"T3 cross-ref must not duplicate table ({marker})"

print("OK: validate-two-speed-clocks-crossref-v1 · canonical=sa-0967 · no duplicate table · sa-0992")
PY
