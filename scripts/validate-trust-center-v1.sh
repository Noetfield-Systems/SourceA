#!/usr/bin/env bash
# validate-trust-center-v1.sh — DL-U1 Trust Center publish
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

test -f data/trust-center-v1.json || { echo "FAIL missing trust-center SSOT"; exit 1; }
test -f scripts/trust_center_publish_v1.py || { echo "FAIL missing publish script"; exit 1; }

python3 scripts/trust_center_publish_v1.py --json >/dev/null
test -f SourceA-landing/green-unified/trust/index.html || { echo "FAIL missing trust index.html"; exit 1; }
test -f SourceA-landing/green-unified/data/trust-signals-public-v1.json || { echo "FAIL missing public signals json"; exit 1; }
test -f "${SINA}/trust-center-receipt-v1.json" || { echo "FAIL missing trust center receipt"; exit 1; }

grep -q 'T0 public tier' SourceA-landing/green-unified/trust/index.html || { echo "FAIL missing T0 marker"; exit 1; }
grep -q 'session gate' SourceA-landing/green-unified/trust/index.html && { echo "FAIL forbidden term on page"; exit 1; } || true

python3 - <<'PY'
import json
from pathlib import Path
r = json.loads((Path.home() / ".sina/trust-center-receipt-v1.json").read_text())
assert r.get("schema") == "trust-center-receipt-v1"
assert r.get("ok") is True
print("OK:", r.get("trust_center_line", "")[:72])
PY

echo "PASS: validate-trust-center-v1"
