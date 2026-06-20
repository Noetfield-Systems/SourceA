#!/usr/bin/env bash
# sa-0028 / sa-0078 — strategic_synthesis_hub this_week spine + fleet auto-pass + Wire G3
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
from strategic_synthesis_hub import strategic_synthesis_payload, this_week

tw = this_week()
assert any("spine" in (x.get("action") or "").lower() for x in tw), f"missing spine Action: {tw!r}"
assert any(
    "fleet" in (x.get("action") or "").lower() and "auto-pass" in (x.get("action") or "").lower()
    for x in tw
), f"missing fleet auto-pass: {tw!r}"
wire = next((x for x in tw if (x.get("who") or "").lower() == "wire"), {})
assert "g3" in (wire.get("action") or "").lower(), f"missing Wire G3: {wire!r}"

payload = strategic_synthesis_payload()
assert payload.get("this_week") == tw, "payload this_week drift vs this_week()"
print("OK: validate-strategic-synthesis-this-week-v1 · sa-0078 · spine + fleet auto-pass + Wire G3")
PY
