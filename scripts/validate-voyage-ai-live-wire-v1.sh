#!/usr/bin/env bash
# validate-voyage-ai-live-wire-v1.sh — Voyage L8 provider + hybrid search wired
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

test -f scripts/voyage_ai_live_wire_v1.py || {
  echo "FAIL: missing voyage_ai_live_wire_v1.py"
  exit 1
}

python3 scripts/voyage_ai_live_wire_v1.py --tier session --json >/dev/null

python3 - <<'PY'
import json
from pathlib import Path

sina = Path.home() / ".sina"
receipt = sina / "voyage-ai-live-wire-v1.json"
surfaces = sina / "agent-live-surfaces-v1.json"

assert receipt.is_file(), "missing voyage-ai-live-wire-v1.json"
row = json.loads(receipt.read_text(encoding="utf-8"))
assert row.get("schema") == "voyage-ai-live-wire-v1", row.get("schema")
assert row.get("voyage_line"), "missing voyage_line"
prov = row.get("provider") or {}
assert prov.get("mode") == "voyage", f"expected voyage mode, got {prov.get('mode')}"
assert prov.get("semantic") is True, "semantic must be true when Voyage active"

assert surfaces.is_file(), "missing agent-live-surfaces-v1.json"
surf = json.loads(surfaces.read_text(encoding="utf-8"))
assert surf.get("voyage_line"), "surfaces missing voyage_line"

gate = (Path("scripts") / "governance_zero_drift_live_wire_v1.py").read_text(encoding="utf-8")
assert "voyage_ai_live_wire" in gate, "zero-drift chain not wired to Voyage"

print(
    f"OK: validate-voyage-ai-live-wire-v1 · ok={row.get('ok')} · "
    f"mode={prov.get('mode')} · chunks={(row.get('index') or {}).get('chunk_count')} · "
    f"hits={(row.get('search') or {}).get('hits')}"
)
PY
