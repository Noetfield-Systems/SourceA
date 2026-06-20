#!/usr/bin/env bash
# Validate cinematic film factory SSOT + module layout
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

check "$ROOT/data/cinematic-film-factory-v1.json"
check "$ROOT/data/cinematic-rules-engine-v1.json"
check "$ROOT/cinematic-film-factory/capture.py"
check "$ROOT/cinematic-film-factory/captions.py"
check "$ROOT/cinematic-film-factory/assemble.py"
check "$ROOT/cinematic-film-factory/film_memory.py"
check "$ROOT/cinematic-film-factory/compiler.py"
check "$ROOT/cinematic-film-factory/build.sh"
check "$ROOT/cinematic-film-factory/lanes/witnessbc/script.txt"
check "$ROOT/cinematic-film-factory/lanes/sourcea/script.txt"
check "$ROOT/witness-film-build.sh"

python3 -c "
import json
from pathlib import Path
root = Path('$ROOT')
for p in [
    'data/cinematic-film-factory-v1.json',
    'data/cinematic-rules-engine-v1.json',
    'cinematic-film-factory/lanes/witnessbc/event_graph.json',
]:
    json.loads((root / p).read_text())
print('OK json parse')
"

if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "PASS cinematic-film-factory-v1"
