#!/usr/bin/env bash
# validate-cursor-skills-index-v1.sh — master skills index + controlled-autorun v3 wired (light)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-cursor-skills-index-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/data/sourcea-cursor-skills-index-v1.json" ]] || fail "missing skills index"
[[ -x "$ROOT/scripts/sync-all-cursor-skills-v1.sh" ]] || fail "missing sync-all script"
[[ -x "$ROOT/scripts/write-cursor-skills-index-v1.sh" ]] || fail "missing index writer"

bash "$ROOT/scripts/validate-controlled-autorun-skill-v1.sh"

PY="$ROOT/scripts/sourcea-python-v1.sh"
[[ -x "$PY" ]] || PY="/usr/bin/python3"
"$PY" -c "
import json
from pathlib import Path
root = Path('${ROOT}')
idx = json.loads((root / 'data/sourcea-cursor-skills-index-v1.json').read_text())
assert idx.get('schema') == 'sourcea-cursor-skills-index-v1'
assert idx.get('skill_count', 0) >= 30
ids = {s['id'] for s in idx.get('skills', [])}
for need in ('controlled-autorun', 'signal-factory', 'hub-pro-master', 'skill-foundational-agentic-systems'):
    assert need in ids, f'missing skill id: {need}'
print(f\"OK index: {idx['skill_count']} skills\")
"

echo "PASS: validate-cursor-skills-index-v1.sh"
