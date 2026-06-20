#!/usr/bin/env bash
# Governance zero-drift live wire — chain must PASS logged
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"

test -f scripts/governance_zero_drift_live_wire_v1.py || {
  echo "FAIL: missing governance_zero_drift_live_wire_v1.py"
  exit 1
}

python3 scripts/governance_zero_drift_live_wire_v1.py --role any --tier session --skip-anti-staleness --json >/dev/null

python3 - <<'PY'
import json
from pathlib import Path

sina = Path.home() / ".sina"
receipt = sina / "governance-zero-drift-live-wire-v1.json"
surfaces = sina / "agent-live-surfaces-v1.json"

assert receipt.is_file(), "missing governance-zero-drift-live-wire-v1.json"
row = json.loads(receipt.read_text(encoding="utf-8"))
assert row.get("schema") == "governance-zero-drift-live-wire-v1", row.get("schema")
assert row.get("zero_drift_line"), "missing zero_drift_line"
assert row.get("drift_score") is not None, "missing drift_score"
assert row.get("chains"), "missing chains block"

chains = row["chains"]
for key in ("L0_5_L1_L2", "cross_layer", "governance_drift", "SASCIP", "vocabulary", "monitor_pulse"):
    assert key in chains, f"missing chain key {key}"

assert surfaces.is_file(), "missing agent-live-surfaces-v1.json"
surf = json.loads(surfaces.read_text(encoding="utf-8"))
assert surf.get("zero_drift_line"), "surfaces missing zero_drift_line"

# Session gate must reference zero drift step
gate = (Path("scripts") / "agent_session_gate_run_v1.py").read_text(encoding="utf-8")
assert "governance_zero_drift_live_wire" in gate, "session gate not wired"

print(
    f"OK: validate-governance-zero-drift-live-wire-v1 · ok={row.get('ok')} · "
    f"score={row.get('drift_score')} · queue={row.get('queue_sa')}"
)
PY
