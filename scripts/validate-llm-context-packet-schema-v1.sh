#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
from pre_llm.context_packet.schema import (
    SCHEMA,
    FIELD_PRODUCERS,
    SHIPPED_PRODUCERS,
    empty_packet_template,
    validate_packet,
    hydrate_from_disk_substrate,
    schema_contract_payload,
)

stub = empty_packet_template()
assert stub.get('schema') == SCHEMA
assert 'intent' in stub and 'plan' in stub and 'compressed_context' in stub

# Every gate section must have a producer mapping
for section in ('intent','code','dependencies','ranking','plan','compression','compressed_context','constraints','provenance'):
    assert section in FIELD_PRODUCERS, section

v = validate_packet(stub)
assert v.get('ok') is True, v
assert v.get('gate_eligible') is False, 'empty stub must not pass gate'

h = hydrate_from_disk_substrate(stub)
assert h.get('dependencies', {}).get('impact_ready') is True, 'D3 should hydrate'
assert 'D1' in (h.get('provenance') or {}).get('producer_steps', [])

api = schema_contract_payload()
assert api.get('ok') is True
assert api.get('pre_llm_steps_shipped') == f'{len(SHIPPED_PRODUCERS)}/16', api.get('pre_llm_steps_shipped')

print('PASS llm context packet schema v1', 'shipped', sorted(SHIPPED_PRODUCERS), 'gate_eligible', v.get('gate_eligible'))
"
