#!/usr/bin/env bash
# validate-cloud-comprehension-bay-v1.sh — cloud bay · not Mac validators
set -euo pipefail
cd "$(dirname "$0")/.."

test -f data/cloud-comprehension-bay-v1.json || { echo "FAIL missing SSOT"; exit 1; }
test -f scripts/fbe_comprehension_bay_v1.py || { echo "FAIL missing bay script"; exit 1; }
test -f scripts/cloud_comprehension_bay_client_v1.py || { echo "FAIL missing client"; exit 1; }

GOOD='You asked why email stays off. WitnessBC still shows old journalism on the live site, so outbound email stays blocked until prod DNS switches. TrustField and Noetfield load fine.'
python3 scripts/fbe_comprehension_bay_v1.py --text "$GOOD" --founder-message "why defer" --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('verdict')=='ACCEPT', r
assert r.get('for_founder',{}).get('show_this'), 'missing show_this'
print('OK: cloud bay ACCEPT')
"

BAD='sites=RED; defer flag ON; gate PASS; wired.'
OUT=$(python3 scripts/fbe_comprehension_bay_v1.py --text "$BAD" --founder-message "why" --json || true)
echo "$OUT" | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('verdict')=='BLOCKED', r
assert r.get('for_founder',{}).get('blocked'), r
print('OK: cloud bay BLOCKED parrot')
"

grep -q 'comprehension-loop/v1' scripts/fbe_cloud_worker_http_v1.py || { echo "FAIL FBE route missing"; exit 1; }
grep -q '/api/comprehension-loop/v1' scripts/sina-command-server.py || { echo "FAIL hub route missing"; exit 1; }
grep -q 'comprehension_cloud' scripts/agentic_conduct_gate_v1.py || { echo "FAIL conduct wired"; exit 1; }

echo "PASS: validate-cloud-comprehension-bay-v1"
