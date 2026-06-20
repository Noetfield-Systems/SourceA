#!/usr/bin/env bash
# validate-forge-catalog-tier-caps-v1.sh — P0-10 sandbox tier caps honest
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-forge-catalog-tier-caps-v1 — $*" >&2; exit 1; }

test -f data/fbe_catalog_v1.json || fail "catalog missing"

python3 - <<'PY' || fail "tier caps check"
import json
from pathlib import Path

cat = json.loads(Path("data/fbe_catalog_v1.json").read_text())
sandbox = (cat.get("tiers") or {}).get("sandbox") or {}
demo = next((x for x in (cat.get("items") or []) if x.get("catalog_id") == "cat-sandbox-demo"), None)

assert sandbox.get("label"), "sandbox label missing"
assert "free tier" in json.dumps(sandbox).lower(), "free tier label missing"
assert "microvm" in json.dumps(sandbox).lower(), "MicroVM copy missing"
assert sandbox.get("microvm_cap") == 0, "microvm_cap must be 0"
assert sandbox.get("upgrade_path") == "engines", "upgrade_path must name engines tier"
assert demo and demo.get("status") == "mock_only", "cat-sandbox-demo must be mock_only"
assert demo.get("upgrade_path") == "engines", "demo upgrade_path missing"
assert demo.get("tier_cap_honest"), "demo tier_cap_honest missing"
print("OK: sandbox tier caps honest · microvm_cap=0 · upgrade_path=engines")
PY

echo "PASS: validate-forge-catalog-tier-caps-v1"
