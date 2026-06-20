#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

test -f "$ROOT/scripts/gatekeeper_v1.py"
test -f "$ROOT/scripts/sourcea_execute_v1.py"
test -f "$ROOT/brain-os/laws/SOURCEA_INVARIANT_GATEKEEPER_BLUEPRINT_LOCKED_v1.md"

# Heal ACTIVE_NOW ↔ queue SSOT drift before invariant check (E2E strict-build flake class)
python3 -c "
import sys
sys.path.insert(0, '$ROOT/scripts')
from active_now_v1 import sync_active_now_from_queue_head
r = sync_active_now_from_queue_head()
if not r.get('ok'):
    print('WARN: active_now sync before gatekeeper:', r.get('error', r))
"

# Structural checks without broker drift block
python3 "$ROOT/scripts/gatekeeper_v1.py" --no-broker --json | python3 -c "
import sys,json
r=json.load(sys.stdin)
assert r.get('status') in ('PASS','FAIL'), r
assert 'safe_to_execute' in r
print('gatekeeper_json_ok', r.get('status'))
"

python3 "$ROOT/scripts/gatekeeper_v1.py" --no-broker 2>&1 | grep -q "STATUS:"

ROOT="$ROOT" python3 -c '
import json, os, subprocess, sys
from pathlib import Path
root = Path(os.environ["ROOT"])
proc = subprocess.run(
    [sys.executable, str(root / "scripts/gatekeeper_v1.py"), "--role", "act", "--engine", "api", "--no-broker", "--json"],
    capture_output=True, text=True, cwd=str(root),
)
r = json.loads(proc.stdout.strip())
assert r.get("status") == "FAIL", r
print("api_act_blocked_ok")
'

python3 "$ROOT/scripts/sourcea_execute_v1.py" --dry-run | grep -q "SAFE TO EXECUTE"

echo "OK: validate-gatekeeper-v1"
