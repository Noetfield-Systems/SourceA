#!/usr/bin/env bash
# sa-0608 — ENFORCE_BYPASS_MAP_LOCKED_v1.md rows vs gate_receipts_hub.BYPASS_ROUTES
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
export PYTHONPATH="${PYTHONPATH:-}:$ROOT/scripts"

python3 - <<'PY'
import re
from pathlib import Path

ROOT = Path.cwd().parent
DOC = ROOT / "ENFORCE_BYPASS_MAP_LOCKED_v1.md"
from gate_receipts_hub import BYPASS_ROUTES, BYPASS_DOC

text = DOC.read_text(encoding="utf-8")
# Table rows between bypass map header and Receipt logs
section = text.split("## Receipt logs", 1)[0]
rows = []
for line in section.splitlines():
    if not line.startswith("|") or line.startswith("| Route") or line.startswith("|-------"):
        continue
    cols = [c.strip() for c in line.strip("|").split("|")]
    if len(cols) < 3:
        continue
    route, applies, notes = cols[0], cols[1], cols[2]
    rows.append((route, applies, notes))

expected = {
    "agent_loop": ("agent_loop planner", True),
    "Hub Advisor": ("Hub Advisor / loop_advisor", False),
    "Intelligence circle": ("Intelligence circle live agents", False),
    "Cursor IDE": ("Cursor IDE", False),
    "Spine": ("Spine / execution_router", False),
    "Refresh": ("Refresh / build scripts", False),
    "SEMEJ": ("SEMEJ browser chain", False),
    "Pre-LLM": ("Pre-LLM D1–D16 assembly", False),
}

assert len(rows) == 8, f"doc table rows expected 8, got {len(rows)}"
assert len(BYPASS_ROUTES) == 8, f"BYPASS_ROUTES expected 8, got {len(BYPASS_ROUTES)}"

hub_by_route = {r["route"]: r for r in BYPASS_ROUTES}
for doc_route, applies, _notes in rows:
    matched = None
    for key, (hub_route, enforce) in expected.items():
        if key.lower() in doc_route.lower():
            matched = (hub_route, enforce, applies)
            break
    assert matched, f"unmapped doc route: {doc_route}"
    hub_route, hub_enforce, applies = matched
    assert hub_route in hub_by_route, f"missing hub route for doc row: {doc_route}"
    entry = hub_by_route[hub_route]
    if applies.strip() in ("**Yes**", "Yes"):
        assert entry["enforce"] is True, f"{hub_route}: doc Yes but hub enforce={entry['enforce']}"
    else:
        assert entry["enforce"] is False, f"{hub_route}: doc {applies} but hub enforce={entry['enforce']}"

assert "SEMEJ" in (hub_by_route.get("SEMEJ browser chain") or {}).get("route", ""), "SEMEJ route missing"
assert BYPASS_DOC == "ENFORCE_BYPASS_MAP_LOCKED_v1.md"

print(
    f"OK: validate-gate-receipts-route-alignment-v1 · doc_rows=8 "
    f"hub_routes=8 semej=aligned"
)
PY
