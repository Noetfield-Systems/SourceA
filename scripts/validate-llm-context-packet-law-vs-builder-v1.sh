#!/usr/bin/env bash
# sa-0652 — LLM_CONTEXT_PACKET_SCHEMA_LOCKED_v1 vs packet builder (schema.py)
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
from pathlib import Path

from pre_llm.context_packet.schema import (
    FIELD_PRODUCERS,
    GATE_REQUIRED_SECTIONS,
    LAW_DOC,
    PACKET_VERSION,
    SCHEMA,
    empty_packet_template,
    schema_contract_payload,
)
from system_roadmap import LLM_PACKET_SCHEMA, _build_llm_packet_schema

ROOT = Path("..").resolve()
law_path = ROOT / LAW_DOC
assert law_path.is_file(), f"missing law doc: {law_path}"

law_text = law_path.read_text(encoding="utf-8")
assert LAW_DOC in law_text, "law header must cite canonical filename"
assert "scripts/pre_llm/context_packet/schema.py" in law_text, "law must cite schema module"

LAW_ENVELOPE = (
    "intent",
    "workspace",
    "code",
    "dependencies",
    "retrieval",
    "reasoning",
    "ranking",
    "plan",
    "tools",
    "validation",
    "diff",
    "compression",
    "memory",
    "constraints",
    "compressed_context",
    "provenance",
)
LAW_GATE = (
    "intent",
    "code",
    "dependencies",
    "ranking",
    "plan",
    "compression",
    "compressed_context",
    "constraints",
    "provenance",
)
LAW_FIELD_PRODUCERS = {
    "intent": ["D4"],
    "workspace": ["L1", "hub"],
    "code": ["D1", "D2"],
    "dependencies": ["D3"],
    "retrieval": ["D5", "D6", "D7"],
    "reasoning": ["D8"],
    "ranking": ["D9"],
    "plan": ["D10"],
    "tools": ["D11"],
    "validation": ["D12"],
    "diff": ["D13"],
    "compression": ["D14"],
    "memory": ["D6", "D16"],
    "constraints": ["governance"],
    "compressed_context": ["D14"],
    "provenance": ["D15"],
}

stub = empty_packet_template()
for section in LAW_ENVELOPE:
    assert section in stub, f"empty_packet_template missing law envelope section: {section}"

assert tuple(GATE_REQUIRED_SECTIONS) == LAW_GATE, (
    f"GATE_REQUIRED_SECTIONS drift: {GATE_REQUIRED_SECTIONS} vs law {LAW_GATE}"
)

for section, producers in LAW_FIELD_PRODUCERS.items():
    got = FIELD_PRODUCERS.get(section)
    assert got == producers, f"FIELD_PRODUCERS[{section!r}]={got} law expects {producers}"

api = schema_contract_payload()
assert api.get("ok") is True, api
assert api.get("schema") == SCHEMA
assert api.get("packet_version") == PACKET_VERSION
assert api.get("law_doc") == LAW_DOC
assert api.get("field_producers") == FIELD_PRODUCERS

roadmap_static = LLM_PACKET_SCHEMA.get("law_doc")
assert roadmap_static == LAW_DOC, f"LLM_PACKET_SCHEMA law_doc drift: {roadmap_static}"
roadmap_live = _build_llm_packet_schema()
assert roadmap_live.get("law_doc") == LAW_DOC
assert set((roadmap_live.get("fields") or {}).keys()) >= set(LAW_ENVELOPE) - {"workspace"}, roadmap_live

print(
    "OK: validate-llm-context-packet-law-vs-builder-v1 · "
    f"law={LAW_DOC} schema={SCHEMA} gate_sections={len(LAW_GATE)}"
)
PY
