#!/usr/bin/env bash
# sa-0607 — ENFORCE_BYPASS_MAP_LOCKED_v1 hub panel surfaces (doc + payload + API + UI hook)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"
export PYTHONPATH="${PYTHONPATH:-}:$ROOT/scripts"

python3 - <<'PY'
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] if "__file__" in dir() else Path.cwd().parent
BYPASS_DOC = ROOT / "ENFORCE_BYPASS_MAP_LOCKED_v1.md"
APP_JS = ROOT / "agent-control-panel" / "assets" / "app.js"
CMD_DATA = ROOT / "agent-control-panel" / "command-data.json"

assert BYPASS_DOC.is_file(), f"missing {BYPASS_DOC}"
text = BYPASS_DOC.read_text(encoding="utf-8")
assert "agent_loop" in text and "Bypass map" in text, "bypass map table missing"

from gate_receipts_hub import gate_receipts_hub_payload

api = gate_receipts_hub_payload()
assert api.get("ok"), api
assert api.get("bypass_doc") == "ENFORCE_BYPASS_MAP_LOCKED_v1.md", api.get("bypass_doc")
routes = api.get("bypass_routes") or []
assert len(routes) == 8, f"expected 8 bypass routes, got {len(routes)}"
route_names = [r.get("route") for r in routes]
assert "SEMEJ browser chain" in route_names, f"SEMEJ missing from bypass_routes: {route_names}"
assert (ROOT / (api.get("bypass_doc") or "")).is_file(), "bypass_doc path"

assert APP_JS.is_file(), APP_JS
js = APP_JS.read_text(encoding="utf-8")
assert "gate-receipts-panel" in js, "hub panel id missing in app.js"
assert "bypass_routes" in js, "bypass_routes render missing in app.js"
assert "renderGateReceiptsPanel" in js, "renderGateReceiptsPanel missing"

assert CMD_DATA.is_file(), CMD_DATA
cd = json.loads(CMD_DATA.read_text(encoding="utf-8"))
gr = (cd.get("system_roadmap") or {}).get("gate_receipts") or {}
assert gr.get("ok"), gr
assert gr.get("bypass_routes"), "system_roadmap.gate_receipts.bypass_routes missing in command-data"

with urllib.request.urlopen("http://127.0.0.1:13020/api/gate-receipts-v1", timeout=60) as resp:
    live = json.loads(resp.read().decode())
assert live.get("ok"), live
assert live.get("bypass_routes"), "live API bypass_routes missing"
assert live.get("bypass_doc") == "ENFORCE_BYPASS_MAP_LOCKED_v1.md", live.get("bypass_doc")

print(
    f"OK: validate-enforce-bypass-map-v1 · routes={len(routes)} "
    f"mode={api.get('current_mode')} panel=gate-receipts-panel"
)
PY
