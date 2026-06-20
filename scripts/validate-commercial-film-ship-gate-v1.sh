#!/usr/bin/env bash
# P0 commercial film ship gate validator
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

check "$ROOT/scripts/commercial_film_ship_gate_v1.py"
check "$ROOT/sourcea-commercial-film-ship.sh"
check "$ROOT/witnessbc-commercial-film-ship.sh"

python3 -c "
import importlib.util
from pathlib import Path
root = Path('$ROOT')
for mod in ['commercial_film_ship_gate_v1', 'commercial_film_critic_circle_v1']:
    spec = importlib.util.spec_from_file_location(mod, root / 'scripts' / f'{mod}.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
print('OK python import ship_gate + critic')
"

out="$(python3 "$ROOT/scripts/commercial_film_critic_circle_v1.py" --lane sourcea --no-freeze --json 2>/dev/null || true)"
echo "$out" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('verdict') in ('PASS','BLOCK'); print('OK critic lane filter')"

if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "PASS commercial-film-ship-gate-v1"
