#!/usr/bin/env bash
# validate-cloud-motor-founder-vocabulary-v1.sh — Cloud Forge Run + Auto Runtime SSOT
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAIL=0
SSOT="$ROOT/data/cloud-motor-founder-vocabulary-v1.json"
LAW="$ROOT/brain-os/law/enforcement/SOURCEA_CLOUD_FORGE_RUN_AUTO_RUNTIME_VOCABULARY_LOCKED_v1.md"
MANIFEST="$ROOT/data/cloud-forge-run-rename-manifest-v1.json"

test -f "$SSOT" || { echo "FAIL: missing $SSOT"; exit 1; }
test -f "$LAW" || { echo "FAIL: missing $LAW"; exit 1; }
test -f "$MANIFEST" || { echo "FAIL: missing $MANIFEST"; exit 1; }

python3 - "$ROOT" <<'PY' || FAIL=1
import json
import sys
from pathlib import Path
root = Path(sys.argv[1])
ssot = json.loads((root / "data/cloud-motor-founder-vocabulary-v1.json").read_text())
assert ssot.get("physical_rename")
terms = ssot.get("terms") or {}
assert terms["drain"]["display_name"] == "Cloud Forge Run"
assert terms["loop"]["display_name"] == "Auto Runtime"
gloss = json.loads((root / "data/founder-reply-glossary-v1.json").read_text())
tr = gloss.get("translations") or {}
assert "POISON" in tr.get("drain", "")
assert tr.get("Cloud Forge Run")
assert tr.get("Auto Runtime")
assert (root / "scripts/cloud_auto_runtime_v1.py").is_file()
assert (root / "scripts/hub_cloud_forge_run_proceed_v1.py").is_file()
assert (root / "data/cloud-forge-run-queue-active-v1.json").is_file()
print("PASS cloud-motor-founder-vocabulary-v1")
PY

test "$FAIL" -eq 0 && echo "validate-cloud-motor-founder-vocabulary-v1: PASS" || {
  echo "validate-cloud-motor-founder-vocabulary-v1: FAIL"
  exit 1
}
