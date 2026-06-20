#!/usr/bin/env bash
# Validate AEG pipeline — structure + critic_boot --aeg hook
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"

[[ -f "$ROOT/scripts/aeg_capture_v1.py" ]] || { echo "FAIL: missing aeg_capture_v1.py"; exit 1; }

python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('aeg', '$ROOT/scripts/aeg_capture_v1.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert hasattr(mod, 'emit_block_evidence')
assert hasattr(mod, 'capture_terminal_cast')
print('OK: aeg_capture_v1 imports')
"

grep -q 'attach_block_evidence' "$ROOT/scripts/critic_boot_v1.py" || {
  echo "FAIL: critic_boot_v1.py missing auto AEG attach_block_evidence"
  exit 1
}

[[ -f "$ROOT/scripts/evidence_capture_v1.py" ]] || { echo "FAIL: missing evidence_capture_v1.py"; exit 1; }
python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('ec', '$ROOT/scripts/evidence_capture_v1.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert hasattr(mod, 'evidence_capture')
assert hasattr(mod, 'attach_block_evidence')
print('OK: evidence_capture_v1 decorator')
"

# Dry-run compile with synthetic BLOCK receipt
TMP="$(mktemp -d)"
BOOT="${TMP}/critic-boot-v1.json"
python3 -c "
import json
from pathlib import Path
boot = {
  'schema': 'critic-boot-v1',
  'at': '2026-06-15T12:00:00Z',
  'verdict': 'BLOCK',
  'ok': False,
  'blockers': ['synthetic test blocker'],
  'checks': [{'name': 'ssot_brief', 'ok': False, 'reason': 'synthetic test blocker'}],
}
Path('$BOOT').write_text(json.dumps(boot, indent=2))
"

AEG_ROOT_BAK="${AEG_ROOT:-}"
export AEG_BASE_URL=""
OUT="$(python3 "$ROOT/scripts/aeg_capture_v1.py" --from-boot-receipt "$BOOT" --skip-ui --json)"
EVID="$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['evidence_id'])" "$OUT")"
BUNDLE="$SINA/aeg/$EVID"

for f in manifest.json evidence_report.md index.html critic_boot_receipt.json; do
  [[ -f "$BUNDLE/$f" ]] || { echo "FAIL: missing $BUNDLE/$f"; exit 1; }
done

grep -q 'System Blocked' "$BUNDLE/index.html" || { echo "FAIL: proof page missing header"; exit 1; }
grep -q 'synthetic test blocker' "$BUNDLE/evidence_report.md" || { echo "FAIL: report missing blocker"; exit 1; }

echo "PASS: validate-aeg-capture-v1 — bundle $EVID"
