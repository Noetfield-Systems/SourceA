#!/usr/bin/env bash
# worker_verify_ultra_v1.sh — L0 Worker VERIFY: anti-staleness heal + hub check (~1–8s)
set -euo pipefail
export SINA_WORKER_LOOP=1
export SINA_COMMERCIAL_LOOP=1
export SINA_BROKER_FAST=1
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
BASE="${SINA_COMMAND_URL:-http://127.0.0.1:13020}"

fail() { echo "FAIL: worker_verify_ultra_v1 — $*" >&2; exit 1; }

python3 worker_anti_staleness_heal_v1.py --reason verify --force --json >/dev/null || fail "anti-staleness heal"

curl -sf "${BASE}/health" >/dev/null || fail "hub not up"
python3 - <<'PY' || fail "worker-hub schema"
import json, os, urllib.request
base = os.environ.get("SINA_COMMAND_URL", "http://127.0.0.1:13020")
with urllib.request.urlopen(base + "/api/worker-hub/v1", timeout=5) as r:
    d = json.loads(r.read().decode())
assert d.get("ok") and d.get("schema") == "worker-hub-v1"
h = d.get("health") or {}
print(f"OK: worker-hub task={d.get('task_id')} health={h.get('status')}")
PY

echo "OK: worker_verify_ultra_v1 · anti-staleness auto-heal + hub · L0 tier"
