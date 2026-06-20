#!/usr/bin/env bash
# sa-0608 — gate_receipts_hub BYPASS_ROUTES vs ENFORCE_BYPASS_MAP_LOCKED_v1.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
export PYTHONPATH="${PYTHONPATH:-}:$ROOT/scripts"

python3 - <<'PY'
import re
from pathlib import Path

ROOT = Path.cwd().parent
DOC = ROOT / "brain-os/law/enforcement/ENFORCE_BYPASS_MAP_LOCKED_v1.md"
assert DOC.is_file(), DOC

from gate_receipts_hub import BYPASS_ROUTES, gate_receipts_hub_payload

# Parse bypass map table rows only (stop before Receipt logs)
doc_routes: list[str] = []
in_table = False
for line in DOC.read_text(encoding="utf-8").splitlines():
    if line.strip() == "## Bypass map":
        in_table = True
        continue
    if in_table and line.startswith("## "):
        break
    if not in_table or not line.startswith("|"):
        continue
    if "---" in line or line.startswith("| Route |"):
        continue
    cells = [c.strip() for c in line.split("|")[1:-1]]
    if cells:
        doc_routes.append(cells[0].strip("`"))

hub_routes = [r["route"] for r in BYPASS_ROUTES]
assert len(hub_routes) == len(doc_routes), f"count hub={len(hub_routes)} doc={len(doc_routes)}"

# Fuzzy token match — hub short names ⊆ doc row text
for hub in hub_routes:
    key = hub.split("/")[0].split()[0].lower()
    if not any(key in d.lower() or hub.lower() in d.lower() for d in doc_routes):
        raise AssertionError(f"hub route unmapped in doc: {hub}")

api = gate_receipts_hub_payload()
assert api.get("ok"), api
assert len(api.get("bypass_routes") or []) == 8, api

print(
    f"OK: validate-gate-receipts-routes-v1 · hub={len(hub_routes)} doc={len(doc_routes)} "
    f"SEMEJ={'SEMEJ browser chain' in hub_routes}"
)
PY
