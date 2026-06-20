#!/usr/bin/env bash
# P0-07 — Forge catalog try-demo engines (demo_seconds · prove_only honest)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail() { echo "FAIL: validate-forge-catalog-try-demo-v1 — $*" >&2; exit 1; }

python3 - <<'PY'
import json
from pathlib import Path

cat = json.loads(Path("data/fbe_catalog_v1.json").read_text())
engines = [x for x in (cat.get("items") or []) if x.get("tier") == "engines"]
if len(engines) < 3:
    raise SystemExit(f"FAIL: expected >=3 engine items, got {len(engines)}")
for row in engines:
    cid = row.get("catalog_id")
    if not row.get("demo_seconds"):
        raise SystemExit(f"FAIL: {cid} missing demo_seconds")
    if row.get("status") != "prove_only":
        raise SystemExit(f"FAIL: {cid} status={row.get('status')} expected prove_only")
    if not row.get("website_slug"):
        raise SystemExit(f"FAIL: {cid} missing website_slug")
print(f"OK: {len(engines)} engine items · demo_seconds · prove_only · slugs wired")
PY

python3 scripts/phase0_freemium_sandbox_pulse_v1.py --json >/dev/null || fail "phase0 pulse failed"
echo "PASS: validate-forge-catalog-try-demo-v1"
