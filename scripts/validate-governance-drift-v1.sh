#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -c "from governance_drift_engine import run_drift_report; run_drift_report()"
python3 -c "
import json
from pathlib import Path
p = Path.home() / '.sina/governance_drift_report_v1.json'
d = json.loads(p.read_text())
assert d.get('aggregate_score') is not None
assert d.get('sensors')
print('PASS governance drift v1 score', d['aggregate_score'])
"
