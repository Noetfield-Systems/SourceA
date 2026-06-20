#!/usr/bin/env bash
# validate-h2-enforce-shadow-maintainer-slice-t3-crossref-v1.sh — sa-0898 T3 dedup cross-ref → canonical sa-0823
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
fail() { echo "FAIL: validate-h2-enforce-shadow-maintainer-slice-t3-crossref-v1 — $*" >&2; exit 1; }
CROSS="$ROOT/archive/attachments/2026-06-17/sa-0898-enforce-shadow-maintainer-slice-t3-crossref_LOCKED_v1.md"
T2_CROSS="$ROOT/archive/attachments/2026-06-15/sa-0873-enforce-shadow-maintainer-slice-t2-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-h2-enforce-shadow-maintainer-slice-v1.sh"
RECEIPT="$ROOT/receipts/sa-0823-receipt.json"
[[ -f "$CROSS" && -f "$T2_CROSS" && -f "$CANONICAL" && -f "$RECEIPT" ]] || fail "missing chain files"
python3 - <<'PY' || fail "cross-ref doc audit"
from pathlib import Path
text = Path("../archive/attachments/2026-06-17/sa-0898-enforce-shadow-maintainer-slice-t3-crossref_LOCKED_v1.md").read_text(encoding="utf-8")
for n in ("sa-0823","sa-0848","sa-0873","sa-0898","validate-h2-enforce-shadow-maintainer-slice-v1.sh","validate-h2-enforce-shadow-maintainer-slice-t2-crossref-v1.sh","maintainer_enforce_slice","h2-maintainer-enforce-slice-v1","cross_check_ok","gate_mode","packet_gate_mode","h2_maintainer_enforce_slice_v1","/machines/"):
    if n not in text: raise SystemExit(f"cross-ref missing {n}")
print("OK: sa-0898 cross-ref doc cites sa-0823 canonical")
PY
bash "$CANONICAL" >/dev/null || fail "canonical"
bash "$ROOT/scripts/validate-h2-enforce-shadow-maintainer-slice-t2-crossref-v1.sh" >/dev/null || fail "T2 chain"
echo "OK: validate-h2-enforce-shadow-maintainer-slice-t3-crossref-v1 · canonical=sa-0823 · sa-0898"
