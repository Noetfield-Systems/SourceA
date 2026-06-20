#!/usr/bin/env bash
# sa-0021 / sa-0096 — COUNCIL_BRIEF must document SSOT trust order one bullet + hub payload
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
from pathlib import Path

from council_strategic_brief import SSOT_TRUST_ORDER, strategic_brief_payload

root = Path(__file__).resolve().parents[1]
brief_path = root / "COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md"
assert brief_path.is_file(), "missing COUNCIL_BRIEF (sa-0021)"

text = brief_path.read_text(encoding="utf-8")
assert "SSOT trust order" in text, "COUNCIL_BRIEF missing SSOT trust order bullet (sa-0021)"
for needle in ("~/.sina", "validators", "hub Refresh", "external"):
    assert needle in text, f"COUNCIL_BRIEF trust order missing {needle!r}"

payload = strategic_brief_payload()
assert payload.get("ssot_trust_order") == SSOT_TRUST_ORDER, payload.get("ssot_trust_order")
assert SSOT_TRUST_ORDER in (payload.get("copy_block") or ""), payload.get("copy_block")
assert SSOT_TRUST_ORDER in (payload.get("body_markdown") or ""), "trust order not in brief body"

print(f"OK: validate-council-ssot-trust-order-v1 · {SSOT_TRUST_ORDER}")
PY
