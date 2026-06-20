#!/usr/bin/env bash
# validate-fbe-factory-builder-bundle-v1.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

BUNDLE="data/fbe_factory_builder_bundle_v1.json"
[[ -f "$BUNDLE" ]] || { echo "FAIL: missing $BUNDLE"; exit 1; }

python3 - <<'PY' || fail=1
import json
from pathlib import Path
ROOT = Path(".")
b = json.loads(Path("data/fbe_factory_builder_bundle_v1.json").read_text())
assert b.get("schema") == "fbe-factory-builder-bundle-v1", "bad schema"
lines = b.get("three_lines") or []
assert len(lines) == 3, f"expected 3 lines got {len(lines)}"
counts = {l["id"]: l for l in lines}
assert counts["refinery"]["node_count"] == 36
assert counts["assembly"]["node_count"] == 22
assert counts["trust_motor"]["compile_target_nodes"] == 18
factories = b.get("first_three_factories") or []
assert len(factories) >= 1, "first_three_factories missing"
assert any(f.get("template_id") == "web-product-factory-v1" for f in factories)
rules = b.get("import_rules") or {}
priority = rules.get("priority") or []
assert len(priority) >= 2, "import_rules.priority missing"
home = Path.home()
ya5 = home / "Desktop/YA5"
for rel in priority[:2]:
    if rel.startswith("PLUS ONE/"):
        p = ya5 / rel
    elif rel.startswith("/"):
        p = Path(rel)
    else:
        p = ROOT / rel
    if not p.is_file():
        raise SystemExit(f"FAIL: import_rules priority path missing: {p}")
print("OK: bundle schema three_lines first_three_factories import_rules")
PY

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-fbe-factory-builder-bundle-v1"
  exit 0
fi
echo "FAIL: validate-fbe-factory-builder-bundle-v1"
exit 1
