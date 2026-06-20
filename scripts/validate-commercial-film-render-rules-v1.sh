#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 - <<'PY'
import json
from pathlib import Path
root = Path(".")
rules = root / "data/commercial-film-render-rules-v1.json"
guard = root / "scripts/commercial_film_render_guard_v1.py"
for p in (rules, guard):
    if not p.is_file():
        print(f"FAIL: missing {p}")
        raise SystemExit(1)
data = json.loads(rules.read_text())
if data.get("schema") != "commercial-film-render-rules-v1":
    print("FAIL: schema")
    raise SystemExit(1)
if len(data.get("rules") or {}) < 12:
    print("FAIL: rules incomplete")
    raise SystemExit(1)
print(f"PASS: render rules v{data.get('version')} — {len(data['rules'])} rules")
PY
python3 scripts/commercial_film_render_guard_v1.py status --json >/dev/null
echo "PASS: validate-commercial-film-render-rules-v1.sh"
