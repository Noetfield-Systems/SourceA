#!/usr/bin/env bash
# Validate enforcement-1000 locked pack — count, registry, sample files
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PACK="$ROOT/brain-os/plan-registry/enforcement-1000"
REG="$PACK/REGISTRY.json"

echo "=== validate-enforcement-1000-pack ==="

python3 <<PY
import json, sys
from pathlib import Path

root = Path("$ROOT")
reg_path = root / "brain-os/plan-registry/enforcement-1000/REGISTRY.json"
reg = json.loads(reg_path.read_text(encoding="utf-8"))
plans = reg.get("plans") or []
count = len(plans)
if count != 1000:
    print(f"FAIL: expected 1000 plans got {count}")
    sys.exit(1)
if not reg.get("locked"):
    print("FAIL: registry locked must be true")
    sys.exit(1)
if reg.get("library") != "enforcement-1000-locked":
    print("FAIL: library id mismatch")
    sys.exit(1)
if reg.get("pivot") != "ENFORCEMENT-6MO":
    print("FAIL: pivot must be ENFORCEMENT-6MO")
    sys.exit(1)
titles = [pl.get("title") for pl in plans]
if len(set(titles)) != count:
    print(f"FAIL: expected {count} unique tier-expanded titles got {len(set(titles))}")
    sys.exit(1)
if not reg.get("categories"):
    print("FAIL: missing categories block — run audit-enforcement-1000-v1.py")
    sys.exit(1)
for pl in plans[:5]:
    for k in ("category", "owner", "month", "win"):
        if not pl.get(k):
            print(f"FAIL: {pl.get('id')} missing {k}")
            sys.exit(1)
print(f"OK: REGISTRY.json count={count} unique_titles={len(set(titles))} pivot=ENFORCEMENT-6MO")

missing = 0
for pl in plans[:20] + plans[500:505] + plans[-5:]:
    p = root / "brain-os/plan-registry/enforcement-1000" / pl["path"]
    if not p.is_file():
        print(f"FAIL: missing {p}")
        missing += 1
    elif "agent_tag: AGENT-AUTO-ENFORCEMENT" not in p.read_text(encoding="utf-8"):
        print(f"FAIL: {p} missing agent_tag")
        missing += 1
if missing:
    sys.exit(1)
print("OK: sample prompt files present")
PY

echo "OK: validate-enforcement-1000-pack"
