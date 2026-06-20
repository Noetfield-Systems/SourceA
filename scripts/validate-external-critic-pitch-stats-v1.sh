#!/usr/bin/env bash
# validate-external-critic-pitch-stats-v1.sh — pitch-stats attachment wired to commercial stack
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=governance-paths-v1.sh
. "$ROOT/scripts/governance-paths-v1.sh"
cd "$ROOT"

fail() { echo "FAIL: validate-external-critic-pitch-stats-v1 — $*" >&2; exit 1; }

DOC="$ROOT/archive/attachments/commercial/EXTERNAL_CRITIC_PITCH_STATS_BULLETS_2026-06-15_v1.md"
ONEPAGER="$ROOT/NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_LOCKED_v1.md"
BATTLE="$ROOT/NOETFIELD_NW1_BATTLE_CARD_LOCKED_v1.md"
COMPETITOR="$ROOT/archive/attachments/commercial/SOURCEA_COMPETITOR_LANDSCAPE_RESEARCH_REPORT_v1.md"
CRITIC_LAW="$ROOT/brain-os/law/CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md"
SSOT="$SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT"

[[ -f "$DOC" ]] || fail "missing pitch stats doc $DOC"
[[ -f "$ONEPAGER" ]] || fail "missing one-pager $ONEPAGER"
[[ -f "$BATTLE" ]] || fail "missing battle card $BATTLE"
[[ -f "$COMPETITOR" ]] || fail "missing competitor report $COMPETITOR"
[[ -f "$CRITIC_LAW" ]] || fail "missing critic law $CRITIC_LAW"
[[ -f "$SSOT" ]] || fail "missing portfolio SSOT $SSOT"

python3 - <<'PY' || fail "pitch stats contract"
from pathlib import Path

doc = Path("archive/attachments/commercial/EXTERNAL_CRITIC_PITCH_STATS_BULLETS_2026-06-15_v1.md")
text = doc.read_text(encoding="utf-8")

required = (
    "LOCKED v1.1",
    "HYPOTHESIS",
    "DISK",
    "EXTERNAL_CRITIC",
    "not roadmap input",
    "NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_LOCKED_v1.md",
    "NOETFIELD_NW1_BATTLE_CARD_LOCKED_v1.md",
    "SOURCEA_COMPETITOR_LANDSCAPE_RESEARCH_REPORT_v1.md",
    "SOURCEA_NOETFIELD_COMPETITOR_LANDSCAPE_2026-06-15_v1_3.md",
    "Consolidation",
    "validate-external-critic-pitch-stats-v1.sh",
    "NW1",
    "SW1",
    "W1 film",
    "show receipt",
    "Runtime governance infrastructure",
)
for needle in required:
    if needle not in text:
        raise SystemExit(f"pitch stats doc missing {needle}")

forbidden = ("MASTER_NEXT_PLANS_SYNTHESIS", "build-sina-command-panel", "hub_self_refresh")
for bad in forbidden:
    if bad in text:
        raise SystemExit(f"pitch stats must not duplicate factory implementation prose ({bad})")

print("OK: pitch stats doc contract · v1.1 · hypothesis/disk split · commercial wire")
PY

# Wire check — one-pager cites pitch stats in internal table
grep -q "EXTERNAL_CRITIC_PITCH_STATS_BULLETS_2026-06-15_v1.md" "$ONEPAGER" || fail "one-pager missing pitch stats pointer"

echo "OK: validate-external-critic-pitch-stats-v1 · commercial pitch stack wired"
