#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
python3 - <<'PY'
import json
import sys

sys.path.insert(0, ".")
from healthy_pack_bind_lib_v1 import bind_status, heal_bind_mismatch

st = bind_status()
if not st.get("match"):
    heal = heal_bind_mismatch(force_deliver=False)
    st = bind_status()
    if not st.get("match"):
        print("FAIL: healthy-pack bind mismatch", json.dumps(st))
        raise SystemExit(1)
print(f"OK: validate-healthy-pack-bind-v1 · queue={st.get('queue_sa')} inbox={st.get('inbox_sa')} bind={st.get('bind_sa') or 'none'}")
PY
