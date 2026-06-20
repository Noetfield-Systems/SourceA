#!/usr/bin/env bash
# sa-0609 — hydrate_from_disk D1–D3 partial rules (not gate-eligible)
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
from pre_llm.context_packet.schema import (
    FIELD_PRODUCERS,
    empty_packet_template,
    hydrate_from_disk_substrate,
    validate_packet,
)

stub = empty_packet_template()
h = hydrate_from_disk_substrate(stub)
v = validate_packet(h)

assert v.get("ok") is True, v
assert v.get("gate_eligible") is False, "D1-D3 partial hydrate must stay not gate-eligible"
missing = v.get("missing_for_gate") or []
assert "constraints" in missing, f"expected constraints missing for partial: {missing}"

code = h.get("code") or {}
deps = h.get("dependencies") or {}
prov = h.get("provenance") or {}
steps = prov.get("producer_steps") or []

assert code.get("files"), "D1 must hydrate code.files"
assert deps.get("impact_ready") is True, "D3 must set impact_ready"
assert "D1" in steps and "D2" in steps and "D3" in steps, steps
assert "D1" in FIELD_PRODUCERS.get("code", []) and "D3" in FIELD_PRODUCERS.get("dependencies", [])

print(
    f"OK: validate-context-packet-d1-d3-hydrate-v1 · files={len(code.get('files') or [])} "
    f"impact_ready={deps.get('impact_ready')} gate_eligible={v.get('gate_eligible')}"
)
PY
