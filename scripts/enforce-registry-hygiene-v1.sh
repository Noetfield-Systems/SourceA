#!/usr/bin/env bash
# Mechanical hygiene — run before Brain status + after every 30-pack. Same steps every time.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

echo "=== enforce-registry-hygiene-v1 ==="

bash validate-registry-honest-gate-v1.sh

python3 registry_updater_v1.py

python3 quarantine-blocked-receipts-v1.py

python3 - <<'PY'
import sys
sys.path.insert(0, ".")
from monitor_honesty_lib_v1 import quarantine_batch_yaml_on_honest_done
q = quarantine_batch_yaml_on_honest_done(dry_run=False)
print(f"batch_yaml_quarantine: sa={q.get('sa_count')} files={q.get('file_count')}")
PY

python3 repair-broker-gaps-from-receipt-v1.py --all-partial

python3 prune-stale-broker-backlog-events-v1.py

bash validate-monitor-honesty-v1.sh

python3 brain_sync_lib_v1.py --mode light >/dev/null 2>&1 || true
python3 track_validate_backlog_v1.py --write --run-validators >/dev/null 2>&1 || true

echo "OK: enforce-registry-hygiene-v1 · complete"
