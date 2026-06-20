#!/usr/bin/env bash
# validate-phase-s1-tier-dedup-crossref-v1.sh — close T1/T2/T3 eval-dispatch tier echoes
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-s1-tier-dedup-crossref_LOCKED_v1.md"
assert cross.is_file(), "missing sa-s1 tier dedup cross-ref doc"
text = cross.read_text(encoding="utf-8")

canonical = {
    "sa-0101": "live eval",
    "sa-0102": "strict build",
    "sa-0104": "dispatch policy",
    "sa-0106": "SINA_AUDIT_STRICT",
    "sa-0110": "runner live",
    "sa-0115": "scaffold arm",
}
backlog = [
    "sa-0126", "sa-0127", "sa-0129", "sa-0131", "sa-0135", "sa-0140",
    "sa-0151", "sa-0152", "sa-0160", "sa-0165",
    "sa-0176", "sa-0177", "sa-0179", "sa-0181", "sa-0185",
]
for sa in backlog:
    assert sa in text, f"backlog {sa} missing from cross-ref map"

for cid in canonical:
    receipt = root / f"receipts/{cid}-receipt.json"
    assert receipt.is_file(), f"missing canonical receipt {cid}"

print("OK: validate-phase-s1-tier-dedup-crossref-v1 · 15 tier echoes · canonical T0 receipts present")
PY
