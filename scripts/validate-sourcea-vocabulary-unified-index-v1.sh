#!/usr/bin/env bash
# validate-sourcea-vocabulary-unified-index-v1.sh — spine cross-refs resolve
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INDEX="$ROOT/data/sourcea-vocabulary-unified-index-v1.json"

test -f "$INDEX" || { echo "FAIL: missing $INDEX"; exit 1; }

python3 - "$ROOT" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
index = json.loads((root / "data/sourcea-vocabulary-unified-index-v1.json").read_text())
law = root / index.get("law_doc", "")
assert law.is_file(), f"missing law_doc {law}"

motor = index["display_names"]["cloud_forge_run"]["display"]
assert motor == "Cloud Forge Run", motor
runtime = index["display_names"]["auto_runtime"]["display"]
assert runtime == "Auto Runtime", runtime

missing = []
for layer in index.get("layers") or []:
    p = layer.get("path")
    if p and not (root / p).is_file():
        missing.append(p)
    law_p = layer.get("law")
    if law_p and not (root / law_p).is_file():
        missing.append(law_p)

for subj, row in (index.get("subjects") or {}).items():
    ssot = row.get("ssot")
    if ssot and not (root / ssot).is_file():
        missing.append(ssot)
    law_p = row.get("law")
    if law_p and not (root / law_p).is_file():
        missing.append(law_p)

motor_ssot = json.loads((root / "data/cloud-motor-founder-vocabulary-v1.json").read_text())
assert motor_ssot["terms"]["drain"]["display_name"] == motor
assert motor_ssot["terms"]["loop"]["display_name"] == runtime

gloss = json.loads((root / "data/founder-reply-glossary-v1.json").read_text())
assert gloss.get("unified_index") == "data/sourcea-vocabulary-unified-index-v1.json"
tr = gloss.get("translations") or {}
assert "Anti-Poison" not in tr.get("drain", "")

if missing:
    print("FAIL missing paths:", ", ".join(missing))
    sys.exit(1)
print("PASS sourcea-vocabulary-unified-index-v1")
PY

echo "validate-sourcea-vocabulary-unified-index-v1: PASS"
