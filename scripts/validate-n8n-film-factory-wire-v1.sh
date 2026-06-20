#!/usr/bin/env bash
# P1 n8n film factory wire validator
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAIL=0

check() {
  if [[ ! -e "$1" ]]; then
    echo "FAIL missing: $1"
    FAIL=1
  else
    echo "OK $1"
  fi
}

check "$ROOT/scripts/n8n_film_factory_wire_v1.py"
check "$ROOT/n8n/workflows/wf-cinematic-film-compile-v1.json"
check "$ROOT/n8n/workflows/wf-cinematic-film-critic-v1.json"
check "$ROOT/n8n/workflows/wf-film-screen-studio-ingest-v1.json"

python3 -c "
import json
from pathlib import Path
root = Path('$ROOT')
for p in [
    'n8n/workflows/wf-cinematic-film-compile-v1.json',
    'n8n/workflows/wf-cinematic-film-critic-v1.json',
]:
    json.loads((root / p).read_text())
print('OK workflow json')
"

python3 "$ROOT/scripts/n8n_film_factory_wire_v1.py" 2>/dev/null || true
python3 -c "
import importlib.util
from pathlib import Path
root = Path('$ROOT')
spec = importlib.util.spec_from_file_location('wire', root/'scripts/n8n_film_factory_wire_v1.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
s = m.film_status()
assert s.get('ok') is True
assert 'freeze' in s
print('OK film_status')
"

out="$(python3 "$ROOT/scripts/n8n_glue_runner_v1.py" film-status 2>/dev/null || true)"
echo "$out" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('ok'); print('OK glue film-status')" 2>/dev/null || { echo "FAIL glue film-status"; FAIL=1; }

if rg -q 'film_status|film_ship_gate|film_critic' "$ROOT/scripts/n8n_integration_core.py" 2>/dev/null \
  || grep -qE 'film_status|film_ship_gate|film_critic' "$ROOT/scripts/n8n_integration_core.py"; then
  echo "OK integration core actions"
else
  echo "FAIL integration core"
  FAIL=1
fi

if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "PASS n8n-film-factory-wire-v1"
