#!/usr/bin/env bash
# validate-forge-vocabulary-disambiguation-v1.sh — Forge product name purity
set -euo pipefail
cd "$(dirname "$0")/.."
test -f data/sourcea-forge-vocabulary-disambiguation-v1.json || {
  echo "FAIL: missing vocabulary SSOT" >&2
  exit 1
}
python3 scripts/validate_forge_vocabulary_disambiguation_v1.py || exit 1
echo "PASS: validate-forge-vocabulary-disambiguation-v1"
