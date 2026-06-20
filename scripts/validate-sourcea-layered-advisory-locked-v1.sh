#!/usr/bin/env bash
# LOCK seal — layered advisory draft v1.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

DOC="$ROOT/SOURCEA_LAYERED_ADVISORY_DRAFT_v1.md"
test -f "$DOC"

for pat in \
  "LAYER 0" \
  "LAYER 11" \
  "EMBED-014" \
  "COMMERCIAL_GOAL-REF-1000PACK-AUDIT-018" \
  "declared advisory focus" \
  "β+ Hybrid"; do
  grep -q "$pat" "$DOC"
done

PRI="$ROOT/brain-os/plan-registry/SOURCEA-PRIORITY.md"
grep -q "SOURCEA_LAYERED_ADVISORY_DRAFT_v1.md" "$PRI"

PIN="$ROOT/SOURCEA_FOUNDER_PINNED_ACTIONS_LOCKED_v1.md"
grep -q "SOURCEA_LAYERED_ADVISORY_DRAFT_v1.md" "$PIN"

python3 <<PY
import json
from datetime import datetime, timezone
from pathlib import Path

receipt = {
    "schema": "sourcea-layered-advisory-lock-v1",
    "locked": True,
    "validated_at": datetime.now(timezone.utc).isoformat(),
    "validator": "validate-sourcea-layered-advisory-locked-v1.sh",
    "document": "SOURCEA_LAYERED_ADVISORY_DRAFT_v1.md",
    "sequence_id": "SA-2026-06-10-LAYERED-ADVISORY",
}
path = Path.home() / ".sina" / "sourcea-layered-advisory-lock-v1.json"
path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(f"OK: receipt {path}")
PY

echo "SOURCEA-LAYERED-ADVISORY VALID locked=ok"
