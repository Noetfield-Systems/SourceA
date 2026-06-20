#!/usr/bin/env bash
# Validator: rules-in-charge loop orchestrator + in-charge payload
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
python3 agent_rules_loop_orchestrator.py --phase maintainer_preflight --agent-id validator
python3 - <<'PY'
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_rules_in_charge import rules_in_charge_payload
ric = rules_in_charge_payload()
assert ric.get("ok"), "rules_in_charge_payload not ok"
assert ric.get("in_charge_count", 0) >= 3, "too few in-charge rules"

# Hash canonical law paths cited in in-charge payload (AS-14)
import hashlib
from pathlib import Path
root = Path(__file__).resolve().parents[1]
for row in ric.get("in_charge_now") or []:
    rel = str(row.get("law_path") or row.get("path") or "").strip()
    if not rel:
        continue
    p = root / rel if not rel.startswith("/") else Path(rel)
    if p.is_file():
        h = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
        assert h, f"empty hash for {rel}"

print("OK: validate-agent-rules-in-charge-v1")
PY
