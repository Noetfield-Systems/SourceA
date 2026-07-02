#!/usr/bin/env bash
# validate-signal-factory-v1.sh — Signal Factory v1 structural verifier (Mac-safe, light)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-signal-factory-v1 — $*" >&2; exit 1; }
PY="${SIGNAL_FACTORY_PYTHON:-/usr/bin/python3}"

SKILL="$ROOT/.cursor/skills/signal-factory/SKILL.md"
SSOT="$ROOT/data/signal-factory-v1.json"
CORE="$ROOT/scripts/signal_factory_core_v1.py"
TESTS="$ROOT/.cursor/skills/signal-factory/tests"

[[ -f "$SKILL" ]] || fail "missing SKILL.md"
[[ -f "$SSOT" ]] || fail "missing data/signal-factory-v1.json"
[[ -f "$CORE" ]] || fail "missing signal_factory_core_v1.py"
[[ -d "$TESTS" ]] || fail "missing tests directory"

grep -q 'name: signal-factory' "$SKILL" || fail "SKILL frontmatter missing signal-factory name"
grep -q 'risk ≥ 4' "$SKILL" || fail "SKILL missing risk override law"
grep -q 'sender_declared' "$SKILL" || fail "SKILL missing sender_declared rule"
grep -q 'adapter_hooks' "$SKILL" || fail "SKILL missing adapter_hooks"
grep -q 'production_connected' "$SKILL" || fail "SKILL missing production_connected guard"

test_count="$(find "$TESTS" -maxdepth 1 -name 'test_*.json' | wc -l | tr -d ' ')"
[[ "$test_count" -eq 6 ]] || fail "expected 6 synthetic tests, found $test_count"

"$PY" "$CORE" --run-tests --json >/tmp/signal-factory-test-run.json \
  || fail "synthetic test run failed"

"$PY" -c "
import json, sys
from pathlib import Path

root = Path('$ROOT')
ssot = json.loads((root / 'data/signal-factory-v1.json').read_text())
summary = json.loads(Path('/tmp/signal-factory-test-run.json').read_text())
errors = []

if not summary.get('ok'):
    errors.append('test suite not ok')
if summary.get('total') != 6:
    errors.append(f'expected 6 tests, got {summary.get(\"total\")}')
if summary.get('production_scan_errors'):
    errors.extend(summary['production_scan_errors'])

# Sample analyze + verify receipt contract
import subprocess
proc = subprocess.run(
    ['$PY', str(root / 'scripts/signal_factory_core_v1.py'),
     '--text', 'SourceA governance autorun signal intake',
     '--json'],
    capture_output=True, text=True, check=True,
)
payload = json.loads(proc.stdout)
report = payload['report']
verification = payload['verification']
if not verification.get('ok'):
    errors.append(f'sample analyze verify failed: {verification.get(\"errors\")}')

for field in ssot['required_report_fields']:
    if field not in report:
        errors.append(f'sample missing {field}')

if report.get('risk_score', 0) >= 4 and report.get('decision') != 'route':
    errors.append('risk override failed on sample')

hooks = (report.get('receipt') or {}).get('adapter_hooks') or {}
for name, value in hooks.items():
    if value not in (None, {}, []):
        errors.append(f'adapter hook {name} not empty')

if (report.get('receipt') or {}).get('production_connected') is True:
    errors.append('production_connected must be false')

# No production wiring in skill package files
for rel in ['.cursor/skills/signal-factory/SKILL.md', 'scripts/signal_factory_core_v1.py']:
    text = (root / rel).read_text(encoding='utf-8', errors='replace').lower()
    for needle in ('gmail.googleapis.com', 'linkedin.com/api', 'imap.', 'smtp.'):
        if needle in text:
            errors.append(f'production pattern {needle} in {rel}')

if errors:
    print('FAIL: validate-signal-factory-v1')
    for e in errors:
        print(f'  - {e}')
    sys.exit(1)

print('PASS: validate-signal-factory-v1.sh · tests=6 · structural checks ok')
"
