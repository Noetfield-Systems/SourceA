#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

from append_spine_proof_priority_v1 import ROW_MARKER, _latest_bridge_event, maybe_append_spine_proof_row
from runtime.event_bus.bus_v1 import tail

ROOT = Path(__file__).resolve().parents[1]
PRIORITY = ROOT / "brain-os" / "plan-registry" / "SOURCEA-PRIORITY.md"
BUILD = (ROOT / "scripts" / "build-sina-command-panel.py").read_text(encoding="utf-8")

mod = (ROOT / "scripts" / "append_spine_proof_priority_v1.py").read_text(encoding="utf-8")
assert "sa-0425" in mod, "sa-0425 marker missing in append module"
assert "spine.bridge" in mod, "spine.bridge topic missing"
assert "founder_action" in mod, "founder_action gate missing"
assert "append_spine_proof_priority_v1" in BUILD, "build must call append_spine_proof_priority_v1"
assert "validate-spine-proof-priority-v1.sh" in BUILD, "validator must be in strict build chain"

event = _latest_bridge_event()
pri = PRIORITY.read_text(encoding="utf-8")
if event:
    assert ROW_MARKER in pri, f"PRIORITY missing {ROW_MARKER} when spine.bridge event exists"
    assert "spine-smoke-echo" in pri or "spine.bridge" in pri, "proof action_id missing in PRIORITY"
else:
    bridge_rows = [r for r in tail(topic="spine.bridge", n=5)]
    assert not bridge_rows or ROW_MARKER in pri or "spine bridge founder" in pri.lower(), (
        "PRIORITY spine proof row expected when bridge events logged"
    )

out = maybe_append_spine_proof_row()
assert out.get("ok"), out
print("OK: validate-spine-proof-priority-v1 · spine.bridge proof row wired (sa-0425)")
PY
