#!/usr/bin/env bash
# validate-signal-factory-tick-v1.sh — 24/7 motor wiring (Mac-safe, light)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-signal-factory-tick-v1 — $*" >&2; exit 1; }
PY="${SIGNAL_FACTORY_PYTHON:-/usr/bin/python3}"

[[ -f "$ROOT/scripts/signal_factory_tick_v1.py" ]] || fail "missing signal_factory_tick_v1.py"
[[ -f "$ROOT/scripts/fbe_cloud_signal_factory_tick_v1.py" ]] || fail "missing fbe_cloud_signal_factory_tick_v1.py"
[[ -f "$ROOT/data/signal-factory-queue-v1.json" ]] || fail "missing queue SSOT"
[[ -f "$ROOT/data/signal-factory-cloud-contract-v1.json" ]] || fail "missing cloud contract"
[[ -f "$ROOT/cloud/workers/signal-factory-tick-v1/src/index.js" ]] || fail "missing CF worker"

grep -q '/api/fbe/signal-factory/tick/v1' "$ROOT/scripts/fbe_cloud_worker_http_v1.py" \
  || fail "Railway route not wired"
grep -q '/api/signal-factory/tick/v1' "$ROOT/scripts/sina-command-server.py" \
  || fail "Hub route not wired in sina-command-server"
grep -q 'signal_factory_tick' "$ROOT/scripts/worker_hub_v1.py" \
  || fail "worker_hub missing signal_factory_tick"
grep -q '/api/signal-factory/' "$ROOT/scripts/fbe/lib/mac_control_dispatch_v1.py" \
  || fail "mac dispatch policy missing signal-factory prefix"

"$PY" "$ROOT/scripts/signal_factory_tick_v1.py" --local-only --max-batch 2 --json >/tmp/sf-tick-test.json \
  || fail "local tick run failed"

"$PY" -c "
import json
from pathlib import Path

row = json.loads(Path('/tmp/sf-tick-test.json').read_text())
errors = []
if not row.get('ok'):
    errors.append(f'tick not ok: {row}')
if row.get('production_connected') is True:
    errors.append('production_connected must be false')
if int(row.get('processed') or 0) < 1:
    errors.append('expected at least 1 processed signal in local tick')
if not row.get('signal_factory_line'):
    errors.append('missing signal_factory_line')

receipt = Path.home() / '.sina/signal-factory-tick-receipt-v1.json'
if not receipt.is_file():
    errors.append('missing tick receipt on disk')

if errors:
    print('FAIL: validate-signal-factory-tick-v1')
    for e in errors:
        print(f'  - {e}')
    raise SystemExit(1)

print('PASS: validate-signal-factory-tick-v1.sh · local tick + routes wired')
"
