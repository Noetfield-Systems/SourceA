#!/usr/bin/env bash
# validate-landing-factories-catalog-v1.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== Build landing catalog ==="
python3 scripts/build-landing-factories-catalog-v1.py --json >/tmp/landing-fact-build.json

echo "=== Static JSON ==="
[[ -f SourceA-landing/green-unified/data/factories-catalog.json ]] || { echo "FAIL: json"; fail=1; }

python3 - <<'PY' || fail=1
import json
from pathlib import Path
disk = json.loads(Path("data/fbe_catalog_v1.json").read_text())
landing = json.loads(Path("SourceA-landing/green-unified/data/factories-catalog.json").read_text())
assert len(landing.get("factories") or []) == len(disk.get("items") or []), (len(landing.get("factories")), len(disk.get("items")))
for f in landing["factories"]:
    slug = f.get("website_slug")
    path = Path(f"SourceA-landing/green-unified/factories/{slug}.html")
    assert path.is_file(), slug
print("OK: landing catalog", len(landing["factories"]), "factories + HTML")
PY

echo "=== Frontend files ==="
for f in factories/index.html sourcea-factories-hub.js; do
  [[ -f "SourceA-landing/green-unified/$f" ]] || { echo "FAIL: missing $f"; fail=1; }
done

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-landing-factories-catalog-v1"
  exit 0
fi
echo "FAIL: validate-landing-factories-catalog-v1"
exit 1
