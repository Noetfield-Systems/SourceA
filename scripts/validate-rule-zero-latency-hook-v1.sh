#!/usr/bin/env bash
# validate-rule-zero-latency-hook-v1.sh — hook script + SSOT + fast fanout smoke
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-rule-zero-latency-hook-v1 — $*" >&2; exit 1; }

test -f scripts/rule_zero_latency_hook_v1.py || fail "missing rule_zero_latency_hook_v1.py"
test -f scripts/rule_propagation_fanout_v1.py || fail "missing rule_propagation_fanout_v1.py"
test -f data/rule-propagation-zero-latency-v1.json || fail "missing SSOT"

python3 - <<'PY' || fail "SSOT missing hook_script"
import json
from pathlib import Path
row = json.loads(Path("data/rule-propagation-zero-latency-v1.json").read_text())
assert row.get("hook_script"), "hook_script required"
assert "pre_write_guard_v1.py" in str(row.get("trigger_hooks")), "pre_write hook required"
print("SSOT ok", row.get("version"))
PY

OUT="$(python3 scripts/rule_zero_latency_hook_v1.py --check-path --path ".cursor/rules/021-governance-zero-drift-live-wire.mdc" --json)"
python3 - <<PY || fail "check-path"
import json
row = json.loads("""${OUT}""")
assert row.get("is_rule_governance_path") is True, row
print("check-path ok")
PY

python3 scripts/rule_propagation_fanout_v1.py --fast --reason validate-hook --json >/tmp/rule-fanout-validate.json \
  || fail "fast fanout failed"
python3 - <<'PY' || fail "fanout receipt"
import json
from pathlib import Path
row = json.loads(Path("/tmp/rule-fanout-validate.json").read_text())
assert row.get("tier") == "fast", row
print("fanout", row.get("line"))
PY

python3 - <<'PY' || fail "fanout receipt"
import json
from pathlib import Path
row = json.loads(Path.home().joinpath(".sina/rule-propagation-fanout-receipt-v1.json").read_text())
print("fanout", row.get("line"))
PY

echo "PASS: validate-rule-zero-latency-hook-v1"
