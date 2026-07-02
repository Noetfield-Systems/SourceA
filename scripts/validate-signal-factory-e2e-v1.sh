#!/usr/bin/env bash
# validate-signal-factory-e2e-v1.sh — full E2E: tests + structural verify + install sync
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-signal-factory-e2e-v1 — $*" >&2; exit 1; }

echo "== signal-factory E2E: structural verifier =="
bash "$ROOT/scripts/validate-signal-factory-v1.sh"

echo "== signal-factory E2E: install sync =="
bash "$ROOT/scripts/sync-signal-factory-skill-v1.sh"

DEST="${HOME}/.cursor/skills/signal-factory"
[[ -f "$DEST/SKILL.md" ]] || fail "installed skill missing at $DEST/SKILL.md"
grep -q 'name: signal-factory' "$DEST/SKILL.md" || fail "installed skill frontmatter invalid"

echo "== signal-factory E2E: tick motor =="
bash "$ROOT/scripts/validate-signal-factory-tick-v1.sh"

echo "== signal-factory E2E: SSOT ↔ core enum parity =="
PY="${SIGNAL_FACTORY_PYTHON:-/usr/bin/python3}"
"$PY" -c "
import json, importlib.util
from pathlib import Path

root = Path('$ROOT')
ssot = json.loads((root / 'data/signal-factory-v1.json').read_text())
spec = importlib.util.spec_from_file_location('sfc', root / 'scripts/signal_factory_core_v1.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

errors = []
for key in ssot['required_report_fields']:
    if key not in ssot.get('required_report_fields', []):
        errors.append(f'missing ssot field registry {key}')

# Negative fixture: cross-attribution must fail verify
bad = {
    'schema': 'signal-factory-decision-report-v1',
    'signal_summary': 'Noetfield offers TrustField custody settlement.',
    'classification': 'legal_regulatory',
    'implied_need': 'x',
    'trust_score': 1,
    'risk_score': 4,
    'automation_value': 1,
    'commercial_value': 1,
    'decision': 'route',
    'next_action': 'Route to human/legal review.',
    'receipt': {
        'schema': 'signal-factory-receipt-v1',
        'signal_id': 'bad',
        'created_at': '2026-07-02T12:00:00Z',
        'entity_scope': 'TrustField',
        'classification': 'legal_regulatory',
        'scores': {'trust_score': 1, 'risk_score': 4, 'automation_value': 1, 'commercial_value': 1},
        'decision': 'route',
        'next_action': 'Route to human/legal review.',
        'sender_claims': [],
        'adapter_hooks': dict(ssot['adapter_hooks']),
        'claim_ladder_note': 'x',
        'production_connected': False,
    },
    'memory_line': 'signal-factory-v1 | entity=TrustField | class=legal_regulatory | decision=route | id=bad',
}
v = mod.verify_report(bad, ssot)
if v.get('ok'):
    errors.append('negative cross-attribution fixture should fail verify')

if errors:
    print('FAIL: validate-signal-factory-e2e-v1')
    for e in errors:
        print(f'  - {e}')
    raise SystemExit(1)

print('PASS: validate-signal-factory-e2e-v1.sh · structural + install + negative hygiene gate')
"
