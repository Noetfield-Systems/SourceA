#!/usr/bin/env bash
# sa-0621 — Claude D16 shipped claim vs packet schema version alignment
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

python3 - <<'PY'
from pathlib import Path

from pre_llm.context_packet.schema import (
    FIELD_PRODUCERS,
    PACKET_VERSION,
    SCHEMA,
    SHIPPED_PRODUCERS,
    schema_contract_payload,
)

synthesis = Path("brain-os/wtm/SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md").read_text(encoding="utf-8")

assert "D16 shipped" in synthesis or "**D16 shipped**" in synthesis, "synthesis must record D16 shipped"
assert "D16 writeback is next" in synthesis, "synthesis must cite stale Claude claim for contrast"

assert "D16" in SHIPPED_PRODUCERS, SHIPPED_PRODUCERS
assert "D16" in FIELD_PRODUCERS.get("memory", []), FIELD_PRODUCERS.get("memory")

api = schema_contract_payload()
assert api.get("ok") is True, api
assert api.get("schema") == SCHEMA
assert api.get("packet_version") == PACKET_VERSION
assert api.get("pre_llm_steps_shipped") == "16/16", api.get("pre_llm_steps_shipped")
assert "D16" in (api.get("shipped_producers") or []), api

print(
    f"OK: validate-claude-d16-shipped-packet-schema-v1 · "
    f"schema={SCHEMA} v={PACKET_VERSION} shipped={api.get('pre_llm_steps_shipped')}"
)
PY
