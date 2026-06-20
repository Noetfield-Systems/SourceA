#!/usr/bin/env bash
# validate-trustfield-msb-sandbox-story-v1.sh — P0-06 TrustField MSB sandbox story gate
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

test -f data/trustfield-msb-compliance-sandbox-story-v1.json || { echo "FAIL missing SSOT"; exit 1; }
test -f data/trustfield-commercial-film-beats-v1.json || { echo "FAIL missing beats"; exit 1; }
test -f scripts/trustfield_msb_sandbox_story_v1.py || { echo "FAIL missing script"; exit 1; }

python3 - <<'PY' || { echo "FAIL beats acceptance"; exit 1; }
import json
from pathlib import Path
beats = json.loads(Path("data/trustfield-commercial-film-beats-v1.json").read_text())
sandbox = next((b for b in beats.get("beats", []) if str(b.get("id")).upper() == "SANDBOX"), None)
assert sandbox, "SANDBOX beat missing"
assert sandbox.get("live_sandbox") is True, "live_sandbox flag missing on SANDBOX beat"
text = json.dumps(beats).lower()
assert "rpaa" in text and "pilot" in text and "sandbox" in text
print("OK: live SANDBOX beat + RPAA pilot narrative logged")
PY

python3 scripts/trustfield_msb_sandbox_story_v1.py --json >/dev/null
test -f "${SINA}/trustfield-msb-sandbox-story-receipt-v1.json" || { echo "FAIL missing receipt"; exit 1; }

echo "PASS: validate-trustfield-msb-sandbox-story-v1"
