#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
test -f "$ROOT/scripts/healthy-drain-orchestrator-v1.py"
python3 "$ROOT/scripts/healthy-drain-orchestrator-v1.py" status >/dev/null
grep -q "awaiting_worker" "$ROOT/scripts/healthy-drain-orchestrator-v1.py"
grep -q "report_baseline_at" "$ROOT/scripts/healthy-drain-orchestrator-v1.py"
grep -q "inject_worker_prompt" "$ROOT/scripts/healthy-drain-orchestrator-v1.py"
echo "OK: validate-healthy-drain-orchestrator-v1"
