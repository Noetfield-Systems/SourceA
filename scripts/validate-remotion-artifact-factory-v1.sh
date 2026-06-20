#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAIL=0

check() {
  if ! eval "$2"; then
    echo "FAIL: $1"
    FAIL=1
  fi
}

check "commercial-video-factory exists" "test -d '$ROOT/commercial-video-factory'"
check "package.json" "test -f '$ROOT/commercial-video-factory/package.json'"
check "ProspectReel component" "test -f '$ROOT/commercial-video-factory/src/ProspectReel.tsx'"
check "orchestrator script" "test -f '$ROOT/scripts/remotion_artifact_factory_v1.py'"
check "sample JSON" "test -f '$ROOT/commercial-video-factory/data/sample-prospect-reel-v1.json'"

python3 -c "
import json
from pathlib import Path
p = Path('$ROOT/commercial-video-factory/data/sample-prospect-reel-v1.json')
d = json.loads(p.read_text())
assert d.get('schema') == 'remotion-prospect-reel-v1'
assert d.get('company')
assert d.get('receipt_hash')
print('OK: sample prospect reel JSON valid')
"

if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "PASS: remotion-artifact-factory-v1 structure"
