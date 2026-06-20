#!/usr/bin/env bash
# validate-agent-rule-live-wire-v1.sh — disk + machines + nerves rule wire chain
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

test -f data/agent-rule-live-wire-registry-v1.json || { echo "FAIL missing registry SSOT"; exit 1; }
test -f scripts/agent_rule_live_wire_v1.py || { echo "FAIL missing orchestrator"; exit 1; }

python3 scripts/agent_rule_live_wire_v1.py --validate --json >/dev/null
test -f "${SINA}/agent-rule-live-wire-receipt-v1.json" || python3 scripts/agent_rule_live_wire_v1.py --wire-sync --json >/dev/null
test -f "${SINA}/agent-rule-live-wire-receipt-v1.json" || { echo "FAIL missing wire receipt"; exit 1; }
test -f "${SINA}/disk-live-wire-receipt-v1.json" || { echo "FAIL missing disk-live-wire receipt"; exit 1; }
test -f "${SINA}/h2-pending-registry-v1.json" || { echo "FAIL missing H2 registry"; exit 1; }

python3 - <<'PY'
import json
from pathlib import Path

sina = Path.home() / ".sina"
surfaces = json.loads((sina / "agent-live-surfaces-v1.json").read_text())
assert surfaces.get("rule_live_wire_line"), "missing rule_live_wire_line on surfaces"

h2 = json.loads((sina / "h2-pending-registry-v1.json").read_text())
rlw = h2.get("rule_live_wire") or {}
assert int(rlw.get("count") or 0) >= 1, "H2 missing rule_live_wire rows"
ids = [r.get("id") for r in (h2.get("maintainer_ship") or []) if str(r.get("id", "")).startswith("RULE-WIRE-")]
assert ids, "H2 maintainer_ship missing RULE-WIRE-* entries"
PY

echo "PASS: validate-agent-rule-live-wire-v1"
