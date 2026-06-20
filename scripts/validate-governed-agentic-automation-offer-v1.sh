#!/usr/bin/env bash
# validate-governed-agentic-automation-offer-v1.sh — Asset B commercial lane wired
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=governance-paths-v1.sh
. "$ROOT/scripts/governance-paths-v1.sh"
cd "$ROOT"

fail() { echo "FAIL: validate-governed-agentic-automation-offer-v1 — $*" >&2; exit 1; }

LAW="$ROOT/SOURCEA_ASSET_B_GOVERNED_AGENTIC_AUTOMATION_LOCKED_v1.md"
SSOT="$SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT"
AGENCY="$ROOT/SOURCEA_AGENCY_PRODUCT_DEMO_SCRIPT_LOCKED_v1.md"
ENGINE="$ROOT/scripts/governed_agentic_automation_offer_v1.py"

[[ -f "$LAW" ]] || fail "missing Asset B law $LAW"
[[ -f "$SSOT" ]] || fail "missing portfolio SSOT $SSOT"
[[ -f "$AGENCY" ]] || fail "missing agency demo $AGENCY"
[[ -f "$ENGINE" ]] || fail "missing offer engine $ENGINE"

python3 - <<'PY' || fail "Asset B law contract"
from pathlib import Path

law = Path("SOURCEA_ASSET_B_GOVERNED_AGENTIC_AUTOMATION_LOCKED_v1.md").read_text(encoding="utf-8")
required = (
    "LOCKED v1",
    "Asset B",
    "SKU-DFY-001",
    "SKU-RET-001",
    "SKU-COMBO-001",
    "$3,000–$10,000",
    "$2,000–$5,000/mo",
    "Speed-to-cash",
    "Combined motion",
    "AB1",
    "governed_agentic_automation_offer_v1.py",
    "validate-governed-agentic-automation-offer-v1.sh",
    "~$200/mo",
)
for needle in required:
    if needle not in law:
        raise SystemExit(f"Asset B law missing {needle}")
print("OK: Asset B law contract")
PY

grep -qE "## 2c\.|§2c" "$SSOT" || fail "SSOT missing §2c Asset B pointer"
grep -q "SOURCEA_ASSET_B_GOVERNED_AGENTIC_AUTOMATION_LOCKED_v1.md" "$SSOT" || fail "SSOT missing Asset B law pointer"
grep -q "hello@sourcea.com" "$LAW" || fail "Asset B law missing hello@sourcea.com sender"
grep -q "send_ab1_single_v1.py" "$LAW" || fail "Asset B law missing send script"
[[ -f "$ROOT/scripts/send_ab1_single_v1.py" ]] || fail "missing send_ab1_single_v1.py"

grep -q "SKU-DFY-001" "$LAW" || fail "Asset B law missing DFY SKU"

python3 - <<'PY' || fail "email templates sender"
import json
from pathlib import Path
p = Path.home() / ".sina/governed-agentic-automation-email-templates-v1.json"
data = json.loads(p.read_text())
sender = (data.get("templates") or {}).get("sender") or {}
assert sender.get("from_email") == "hello@sourcea.com", sender
body = (data.get("templates") or {}).get("ab1_primary", {}).get("body", "")
subj = (data.get("templates") or {}).get("ab1_primary", {}).get("subject", "")
assert "hello@sourcea.com" in body
assert 'Reply "stop"' in body
assert "executed last night" in subj
assert "ab1_short_punchy" in (data.get("templates") or {})
print("OK: AB1 templates · proof-led · CASL opt-out · A/B")
PY

python3 scripts/governed_agentic_automation_offer_v1.py --pack --json >/dev/null || fail "offer pack failed"

RECEIPT="${HOME}/.sina/governed-agentic-automation-offer-v1.json"
[[ -f "$RECEIPT" ]] || fail "missing receipt $RECEIPT"

python3 - <<'PY' || fail "receipt contract"
import json
from pathlib import Path

data = json.loads(Path.home().joinpath(".sina/governed-agentic-automation-offer-v1.json").read_text())
assert data.get("asset") == "B"
assert data.get("law", "").endswith("SOURCEA_ASSET_B_GOVERNED_AGENTIC_AUTOMATION_LOCKED_v1.md")
skus = {s["id"] for s in data.get("skus", [])}
for sid in ("SKU-DFY-001", "SKU-RET-001", "SKU-COMBO-001"):
    assert sid in skus, sid
assert "AB1" in data.get("win_codes", {})
print("OK: Asset B receipt contract")
PY

echo "OK: validate-governed-agentic-automation-offer-v1 · Asset B lane wired"
