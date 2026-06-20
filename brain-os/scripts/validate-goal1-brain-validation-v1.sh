#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

test -f scripts/brain_validate_goal1_v1.py
python3 scripts/brain_validate_goal1_v1.py --json --write-receipt | python3 -c "
import json, sys
from pathlib import Path
d = json.load(sys.stdin)
assert d.get('status') == 'BRAIN_VALIDATION_REPORT', d
assert 'chain' in d and 'worker_report' in d, d
assert Path.home().joinpath('.sina/brain-goal1-validation-v1.json').is_file()
print('PASS: BRAIN_VALIDATION_REPORT shape')
"
python3 scripts/goal1_lane_broker.py brain-poll --json 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert 'validation' in d, d.keys()
print('PASS: brain-poll embeds validation')
" || python3 -c "
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('b', Path('scripts/goal1_lane_broker.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
d = m.brain_poll(as_yaml=False)
assert d.get('validation'), 'missing validation'
print('PASS: brain-poll embeds validation')
"

echo "OK: validate-goal1-brain-validation-v1"
