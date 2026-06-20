#!/usr/bin/env bash
# validate-noetfield-onepager-merge-v1.sh — 2 PAGER intake merged into SourceA send stack
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-noetfield-onepager-merge-v1 — $*" >&2; exit 1; }

MERGED="$ROOT/NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_MERGED_EXTERNAL_v1.md"
LOCKED="$ROOT/NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_LOCKED_v1.md"
INTAKE="$ROOT/archive/attachments/commercial/NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_2026-06-15_v1.md"
PACK="$ROOT/archive/attachments/commercial/SOURCEA_NOETFIELD_STRATEGY_PACK_2026-06-15_v1.md"
ROADMAP="$ROOT/archive/attachments/commercial/SOURCEA_NOETFIELD_COMMERCIAL_ROADMAP_MERGED_v1.md"
BATTLE="$ROOT/NOETFIELD_NW1_BATTLE_CARD_LOCKED_v1.md"
CHECKLIST="$ROOT/archive/attachments/commercial/COMMERCIAL_ONEPAGER_MERGE_CHECKLIST_2026-06-15_v1.md"
SEND="$ROOT/scripts/send_nw1_single_v1.py"

for f in "$MERGED" "$LOCKED" "$INTAKE" "$PACK" "$ROADMAP" "$BATTLE" "$CHECKLIST" "$SEND"; do
  [[ -f "$f" ]] || fail "missing $f"
done

python3 - <<'PY' || fail "merged external contract"
from pathlib import Path
text = Path("NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_MERGED_EXTERNAL_v1.md").read_text(encoding="utf-8")
required = (
    "MERGED v1",
    "NF-RD",
    "CAD $5,000–$10,000",
    "CAD $2,000 minimum",
    "Copilot",
    "tamper-FAIL",
    "operations@noetfield.com",
    "Shadow",
    "TLE",
    "Board PDF",
    "noetfield.com/copilot/pilot",
)
for needle in required:
    if needle not in text:
        raise SystemExit(f"merged one-pager missing {needle}")
# Must not imply whole pilot is only $2K
if "CAD $2,000 deposit —" in text and "5,000" not in text:
    raise SystemExit("price framing wrong — flat $2K only")
print("OK: merged external one-pager contract")
PY

grep -q "MERGED_EXTERNAL" "$LOCKED" || fail "LOCKED pilot missing merged external pointer"
grep -q "MERGED_EXTERNAL" "$BATTLE" || fail "battle card missing merged attach pointer"
grep -q "MERGED_EXTERNAL" "$SEND" || fail "send_nw1 missing merged default attach"
grep -q "§3b BUYER 1" SOURCEA_ICP_MARKET_IDENTITY_LOCKED_v1.md || fail "ICP missing §3b scorecard"

echo "OK: validate-noetfield-onepager-merge-v1 · 2 PAGER merged for SourceA"
