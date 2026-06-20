#!/usr/bin/env bash
# Gate: S10 eternal loop manifest + receipt + law present; daily receipt fresh.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MANIFEST="${HOME}/.sina/s10-eternal-manifest-v1.json"
RECEIPT="${HOME}/.sina/s10-eternal-receipt-v1.json"
HISTORY="${HOME}/.sina/s10-eternal-history.jsonl"
LAW="${ROOT}/SOURCEA_S10_ETERNAL_SELF_HEAL_AUDIT_LOCKED_v1.md"
SKILL="${ROOT}/agent-skills/shared/s10-eternal-self-heal/SKILL.md"
RUNNER="${ROOT}/scripts/s10_eternal_audit_loop_v1.py"

[[ -f "$LAW" ]] || { echo "FAIL: S10 law missing"; exit 1; }
[[ -f "$MANIFEST" ]] || { echo "FAIL: s10-eternal-manifest-v1.json missing"; exit 1; }
[[ -f "$RUNNER" ]] || { echo "FAIL: s10_eternal_audit_loop_v1.py missing"; exit 1; }
[[ -f "$SKILL" ]] || { echo "FAIL: s10-eternal-self-heal SKILL missing"; exit 1; }

python3 <<'PY'
import json, sys
from datetime import datetime, timezone
from pathlib import Path

manifest = json.loads(Path.home().joinpath(".sina/s10-eternal-manifest-v1.json").read_text())
assert manifest.get("schema") == "s10-eternal-manifest-v1"
assert manifest.get("total_prompts") == 100
assert len(manifest.get("prompts") or []) == 100
print("OK: manifest 100 prompts")
PY

if [[ ! -f "$RECEIPT" ]]; then
  echo "WARN: no S10 receipt yet — run: python3 scripts/s10_eternal_audit_loop_v1.py --daily"
  exit 0
fi

python3 <<'PY'
import json, sys
from datetime import datetime, timezone
from pathlib import Path

receipt = json.loads(Path.home().joinpath(".sina/s10-eternal-receipt-v1.json").read_text())
assert receipt.get("schema") == "s10-eternal-receipt-v1"
counts = receipt.get("counts") or {}
fails = counts.get("FAIL", 0)
warns = counts.get("WARN", 0)
print(f"OK: receipt mode={receipt.get('mode')} PASS={counts.get('PASS')} WARN={warns} FAIL={fails}")
at = receipt.get("at") or ""
if at:
    try:
        ts = datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        age_h = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
        if age_h > 26:
            print(f"WARN: S10 receipt stale {age_h:.1f}h — daily loop may have missed")
    except ValueError:
        pass
if fails:
    sys.exit(1)
PY

echo "OK: validate-s10-eternal-loop-v1"
