#!/usr/bin/env bash
# validate-cloud-comprehension-bay-v1.sh — cloud bay · runtime config + adaptive fallback
set -euo pipefail
cd "$(dirname "$0")/.."

test -f data/cloud-comprehension-bay-v1.json || { echo "FAIL missing SSOT"; exit 1; }
test -f scripts/agent_runtime_config_v1.py || { echo "FAIL missing runtime config loader"; exit 1; }
test -f scripts/fbe_comprehension_bay_v1.py || { echo "FAIL missing bay script"; exit 1; }
test -f scripts/cloud_comprehension_bay_client_v1.py || { echo "FAIL missing client"; exit 1; }
test -f data/comprehension-golden-v1.json || { echo "FAIL missing golden SSOT"; exit 1; }

GOOD='You asked why email stays off. WitnessBC still shows old journalism on the live site, so outbound email stays blocked until prod DNS switches. TrustField and Noetfield load fine.'
python3 scripts/fbe_comprehension_bay_v1.py --text "$GOOD" --founder-message "why defer" --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('verdict')=='ACCEPT', r
assert r.get('config_version'), 'missing config_version'
assert r.get('variation_key'), 'missing variation_key'
assert r.get('for_founder',{}).get('show_this'), 'missing show_this'
assert isinstance(r.get('attempts'), list), 'missing attempts'
print('OK: cloud bay ACCEPT with runtime config')
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

# strong variation accepts translated borderline (relax_language_gate)
BORDER='The defer flag is on because the site check failed, so email stays blocked for you until DNS is fixed.'
python3 scripts/fbe_comprehension_bay_v1.py --text "$BORDER" --founder-message "why defer" --variation-key strong --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('variation_key')=='strong', r
assert r.get('verdict')=='ACCEPT', r
print('OK: strong variation ACCEPT path')
"

# adaptive fallback — golden-009 draft via SSOT constant
python3 <<'PY'
import json
import subprocess
from pathlib import Path

golden = json.loads(Path("data/comprehension-golden-v1.json").read_text())
draft = golden.get("escalation_probe_draft") or ""
founder = golden.get("escalation_probe_founder_message") or "why defer"
assert draft, "missing escalation_probe_draft in golden SSOT"

out = subprocess.check_output(
    [
        "python3",
        "scripts/fbe_comprehension_bay_v1.py",
        "--text",
        draft,
        "--founder-message",
        founder,
        "--json",
    ],
    text=True,
)
r = json.loads(out)
assert r.get("verdict") == "ACCEPT", r
assert r.get("escalated") is True, r
assert len(r.get("attempts") or []) == 2, r
assert r.get("attempts")[0].get("verdict") == "BLOCKED", r
print("OK: golden-009 escalated ACCEPT with attempts[]")
PY

grep -q 'comprehension-loop/v1' scripts/fbe_cloud_worker_http_v1.py || { echo "FAIL FBE route missing"; exit 1; }
grep -q '/api/comprehension-loop/v1' scripts/sina-command-server.py || { echo "FAIL hub route missing"; exit 1; }

python3 <<'PY'
from pathlib import Path
text = Path("scripts/sina-command-server.py").read_text(encoding="utf-8")
assert 'code = 200 if slim.get("verdict")' in text or "code = 200 if slim.get('verdict')" in text, \
    "hub must return HTTP 200 when verdict present"
print("OK: hub slim HTTP 200-on-verdict contract (static)")
PY

grep -q 'comprehension_cloud' scripts/agentic_conduct_gate_v1.py || { echo "FAIL conduct wired"; exit 1; }

echo "PASS: validate-cloud-comprehension-bay-v1"
