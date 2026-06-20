#!/usr/bin/env bash
# validate-critic-boot-v1.sh — Layer 1 local boot gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
fail=0
check() { [[ "$1" == "true" ]] && echo "PASS: $2" || { echo "FAIL: $2"; fail=1; }; }

[[ -f "$ROOT/scripts/critic_boot_v1.py" ]] && check true "critic_boot script" || check false "critic_boot script"

python3 "$ROOT/scripts/critic_boot_v1.py" --json >/dev/null
[[ -f "$SINA/critic-boot-v1.json" ]] && check true "critic-boot receipt" || check false "critic-boot receipt"

python3 - <<'PY' || { echo "FAIL: receipt schema"; fail=1; }
import json
from pathlib import Path
r = json.loads((Path.home() / ".sina/critic-boot-v1.json").read_text())
assert r.get("schema") == "critic-boot-v1"
assert r.get("verdict") in ("PASS", "BLOCK")
assert len(r.get("checks") or []) == 4
names = {c.get("name") for c in r["checks"]}
assert names == {"ssot_brief", "voyage_provider", "truth_match", "gate_fresh"}
print("PASS: receipt schema + 4 checks")
PY

python3 - <<'PY' || { echo "FAIL: check functions"; fail=1; }
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "Desktop/SourceA/scripts"))
from critic_boot_v1 import check_ssot_brief, check_voyage, check_truth_match, check_gate_fresh
for fn in (check_ssot_brief, check_voyage, check_truth_match, check_gate_fresh):
    row = fn() if fn.__name__ != "check_ssot_brief" else fn()
    assert "ok" in row and "reason" in row, row
print("PASS: check functions callable")
PY

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-critic-boot-v1"
  exit 0
fi
echo "FAIL: validate-critic-boot-v1"
exit 1
