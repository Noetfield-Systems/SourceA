#!/usr/bin/env bash
# TRACE: AUTO-TRACE-WORKER-BATCH-GATE-10-v1.0 · agent Auto · validate-goal1-batch-gate-10-v1.sh
# Mechanical 10/10 broker=yes gate — last 10 AGENT DONE lines must be exit=0 broker=yes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -c "
import sys
sys.path.insert(0, 'scripts')
from goal1_batch_log_v1 import broker_yes_gate
g = broker_yes_gate(need=10)
if not g.get('ok'):
    print('FAIL: validate-goal1-batch-gate-10-v1', g.get('blocker') or g)
    sys.exit(1)
print(f\"OK: validate-goal1-batch-gate-10-v1 count={g.get('count')}/{g.get('need')}\")
"
