#!/usr/bin/env bash
# E2E preflight — run only when drain paused (Phase 5)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
cd "$SCRIPTS"

bash validate-registry-honest-gate-v1.sh
bash validate-monitor-honesty-v1.sh
bash validate-healthy-pack-bind-v1.sh

python3 - <<'PY'
import json
import sys
sys.path.insert(0, ".")
from brain_sync_lib_v1 import sync_brain_snapshot
r = sync_brain_snapshot(mode="light", caller="e2e-preflight")
after = r.get("after") or {}
if not after.get("dual_proof_ok"):
    print("FAIL: dual_proof_ok false", json.dumps(after))
    raise SystemExit(1)
print("OK: dual_proof_ok true · live_vy", after.get("live_vy"), "brain_vy", after.get("brain_vy"))
PY

echo "OK: validate-sourcea-e2e-preflight-v1"
