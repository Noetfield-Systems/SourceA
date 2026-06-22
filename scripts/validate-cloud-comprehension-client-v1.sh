#!/usr/bin/env bash
# validate-cloud-comprehension-client-v1.sh — client smoke (cloud path · network required)
set -euo pipefail
cd "$(dirname "$0")/.."

test -f scripts/cloud_comprehension_bay_client_v1.py || { echo "FAIL missing client"; exit 1; }

GOOD='You asked why email stays off. WitnessBC still shows old journalism on the live site, so outbound email stays blocked until prod DNS switches. TrustField and Noetfield load fine.'

python3 scripts/cloud_comprehension_bay_client_v1.py \
  --text "$GOOD" \
  --founder-message "why defer" \
  --json 2>/dev/null | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('verdict')=='ACCEPT', r
assert r.get('execution_plane')=='headless_cloud', r
assert r.get('proxied') is True, r
assert r.get('config_version'), r
print('OK: client cloud ACCEPT proxied headless_cloud')
"

# Documented degrade: mac_local_fallback only when ALLOW_MAC_FALLBACK=1 and cloud unreachable
if [[ "${ALLOW_MAC_FALLBACK:-}" == "1" ]]; then
  echo "WARN: ALLOW_MAC_FALLBACK=1 — skipping strict cloud-only assertion"
else
  python3 -c "
import json,sys
from pathlib import Path
p=Path.home()/'.sina/cloud-comprehension-bay-receipt-v1.json'
if p.is_file():
    r=json.loads(p.read_text())
    plane=str(r.get('execution_plane') or '')
    if plane=='mac_local_fallback':
        raise SystemExit('FAIL: client fell back to mac_local_fallback without ALLOW_MAC_FALLBACK=1')
print('OK: no mac_local_fallback on happy path')
"
fi

echo "PASS: validate-cloud-comprehension-client-v1"
