#!/usr/bin/env bash
# Brain snapshot must match live monitor valid_yes (INCIDENT-014 permanent repair).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

python3 - <<'PY'
import sys

sys.path.insert(0, ".")
from brain_sync_lib_v1 import brain_snapshot_status

st = brain_snapshot_status()
live = st.get("live_vy")
brain = st.get("brain_vy")
dual = st.get("dual_proof_ok")
stale = st.get("snapshot_stale")
print(
    f"OK: brain snapshot sync · live_vy={live} · brain_vy={brain} · "
    f"snapshot_stale={stale} · dual_proof={dual} · gap={st.get('gap')}"
)
if stale or not st.get("brain_ok"):
    print(
        f"FAIL: brain snapshot stale — live {live} vs brain {brain}. "
        "Run: python3 scripts/brain_sync_lib_v1.py --mode light",
        file=sys.stderr,
    )
    sys.exit(1)
PY

echo "OK: validate-brain-snapshot-sync-v1"
