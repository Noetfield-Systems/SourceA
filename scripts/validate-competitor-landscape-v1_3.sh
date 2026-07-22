#!/usr/bin/env bash
# validate-competitor-landscape-v1_3.sh — Downloads v1_3 merged into commercial stack
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-competitor-landscape-v1_3 — $*" >&2; exit 1; }

INTAKE="$ROOT/archive/attachments/commercial/SOURCEA_NOETFIELD_COMPETITOR_LANDSCAPE_2026-06-15_v1_3.md"
REPORT="$ROOT/archive/attachments/commercial/SOURCEA_COMPETITOR_LANDSCAPE_RESEARCH_REPORT_v1.md"
GATHER="$ROOT/knowledge-library/fields/commercial-governance/02-gathered/GATHER_v2_SOURCEA_COMPETITOR_LANDSCAPE_2026-06-15.md"
BATTLE="$ROOT/NOETFIELD_NW1_BATTLE_CARD_LOCKED_v1.md"
PITCH="$ROOT/archive/attachments/commercial/EXTERNAL_CRITIC_PITCH_STATS_BULLETS_2026-06-15_v1.md"

for f in "$INTAKE" "$REPORT" "$GATHER" "$BATTLE" "$PITCH"; do
  [[ -f "$f" ]] || fail "missing $f"
done

python3 - <<'PY' || fail "intake v1.3 contract"
from pathlib import Path
text = Path("archive/attachments/commercial/SOURCEA_NOETFIELD_COMPETITOR_LANDSCAPE_2026-06-15_v1_3.md").read_text(encoding="utf-8")
required = (
    "v1.3",
    "Portkey",
    "AgentOps",
    "Arize",
    "consolidating by acquisition",
    "SOURCEA_ASSET_B_GOVERNED_AGENTIC_AUTOMATION_LOCKED_v1.md",
    "SOURCEA_AGENCY_PRODUCT_DEMO_SCRIPT_LOCKED_v1.md",
    "30 (grouped by category)",
)
for needle in required:
    if needle not in text:
        raise SystemExit(f"intake v1.3 missing {needle}")
print("OK: intake v1.3 contract · 30-map · disk SKUs")
PY

grep -q "v1_3" "$REPORT" || fail "research report missing v1_3 intake pointer"
grep -q "v1.2" "$REPORT" || fail "research report missing v1.2 header"
grep -q "v1_3" "$GATHER" || fail "GATHER missing v1_3"
grep -q "v1_3" "$BATTLE" || fail "battle card missing v1_3"
grep -q "v1_3" "$PITCH" || fail "pitch stats missing v1_3"

bash scripts/validate-external-critic-pitch-stats-v1.sh || fail "pitch stats validator failed"

echo "OK: validate-competitor-landscape-v1_3 · commercial stack wired"
