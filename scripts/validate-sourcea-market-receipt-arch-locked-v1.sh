#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOC="$ROOT/SOURCEA_MARKET_RECEIPT_ARCHITECTURE_LOCKED_v1.md"
test -f "$DOC"
grep -q "closeout_gate_v1" "$DOC"
grep -q "VALIDATOR_PASS" "$DOC"
grep -q "honest_done" "$DOC"
grep -q "goal-progress-v1" "$DOC"
grep -q "honest receipts" "$DOC" || grep -q "honest_done" "$DOC"
test -f "$ROOT/scripts/closeout_gate_v1.py"
test -d "$ROOT/receipts"
PRI="$ROOT/brain-os/plan-registry/SOURCEA-PRIORITY.md"
grep -q "SOURCEA_MARKET_RECEIPT_ARCHITECTURE_LOCKED_v1.md" "$PRI"
python3 <<PY
import json
from datetime import datetime, timezone
from pathlib import Path
r = {
    "schema": "sourcea-market-receipt-arch-lock-v1",
    "locked": True,
    "validated_at": datetime.now(timezone.utc).isoformat(),
    "document": "SOURCEA_MARKET_RECEIPT_ARCHITECTURE_LOCKED_v1.md",
}
Path.home().joinpath(".sina/sourcea-market-receipt-arch-lock-v1.json").write_text(
    json.dumps(r, indent=2) + "\n", encoding="utf-8")
print("SOURCEA-MARKET-RECEIPT-ARCH VALID locked=ok")
PY
