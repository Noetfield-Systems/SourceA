#!/usr/bin/env bash
# validate-comprehension-golden-v1.sh — offline golden batch (local, not Railway E2E)
set -euo pipefail
cd "$(dirname "$0")/.."

test -f data/comprehension-golden-v1.json || { echo "FAIL missing golden SSOT"; exit 1; }
test -f scripts/fbe_comprehension_eval_batch_v1.py || { echo "FAIL missing batch script"; exit 1; }

python3 scripts/fbe_comprehension_eval_batch_v1.py --no-write --require-escalation-case --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('total', 0) >= 9, r
assert r.get('evaluated', 0) >= 9, r
assert r.get('pass_rate', 0) >= 0.875, r
assert r.get('config_version'), r
assert r.get('escalation_ok', 0) >= 1, r
print('OK: golden batch default pass_rate', r.get('pass_rate'))
"

python3 scripts/fbe_comprehension_eval_batch_v1.py --no-write --variation-key strong --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('skipped', 0) >= 1, r
assert r.get('evaluated', 0) >= 8, r
assert r.get('pass_rate', 0) >= 0.875, r
assert r.get('passed', 0) >= r.get('evaluated', 0), r
print('OK: golden batch strong pass_rate', r.get('pass_rate'), 'evaluated', r.get('evaluated'))
"

python3 <<'PY'
import json
import subprocess
from pathlib import Path

golden = json.loads(Path("data/comprehension-golden-v1.json").read_text())
draft = golden.get("escalation_probe_draft") or ""
founder = golden.get("escalation_probe_founder_message") or "why defer"
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
print("OK: escalated ACCEPT path")
PY

grep -q 'comprehension-eval-batch' scripts/fbe_cloud_worker_http_v1.py || { echo "FAIL FBE eval route missing"; exit 1; }

python3 scripts/test_comprehension_golden_modes_v1.py || { echo "FAIL golden modes unit"; exit 1; }

echo "PASS: validate-comprehension-golden-v1"
