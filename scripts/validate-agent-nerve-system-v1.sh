#!/usr/bin/env bash
# validate-agent-nerve-system-v1.sh — unified nerve receipt + surfaces line
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-agent-nerve-system-v1 — $*" >&2; exit 1; }

test -f scripts/agent_nerve_system_v1.py || fail "missing agent_nerve_system_v1.py"
grep -q 'nerve_system' scripts/worker_hub_v1.py || fail "worker_hub must expose nerve_system slice"
grep -q 'nerve_system_pulse' scripts/disk_live_wire_sync_v1.py || fail "disk_live_wire must run nerve pulse"

python3 scripts/agent_nerve_system_v1.py --json >/dev/null || fail "nerve pulse run"
test -f "${SINA}/agent-nerve-system-receipt-v1.json" || fail "missing nerve receipt"

python3 - <<'PY' || fail "nerve receipt schema"
import json
from pathlib import Path
r = json.loads((Path.home() / ".sina/agent-nerve-system-receipt-v1.json").read_text())
if r.get("schema") != "agent-nerve-system-receipt-v1":
    raise SystemExit("bad schema")
if not r.get("nerve_system_line"):
    raise SystemExit("missing nerve_system_line")
if not r.get("queue_sa") and not r.get("queue_exhausted"):
    raise SystemExit("missing queue_sa")
lines = r.get("lines") or {}
for k in ("factory_now_line", "better_loop_line", "best_loop_oqg_line"):
    if not lines.get(k):
        raise SystemExit(f"missing lines.{k}")
if not r.get("ship_gates"):
    raise SystemExit("missing ship_gates block")
sg = r.get("ship_gates") or {}
for gate in ("worker_connected", "outbound_coherence", "execution_honesty_12of12"):
    if gate not in sg:
        raise SystemExit(f"missing ship_gates.{gate}")
print(f"OK: nerve queue={r.get('queue_sa')} aligned={r.get('queue_aligned')} worker={sg.get('worker_connected')}")
PY

python3 - <<'PY' || fail "surfaces nerve_system_line"
import json
from pathlib import Path
s = json.loads((Path.home() / ".sina/agent-live-surfaces-v1.json").read_text())
if not s.get("nerve_system_line"):
    raise SystemExit("surfaces missing nerve_system_line — run disk_live_wire_sync")
print("OK: nerve_system_line on live surfaces")
PY

echo "PASS: validate-agent-nerve-system-v1"
