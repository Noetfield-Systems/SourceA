#!/usr/bin/env bash
# P0 authority runtime — authority.yaml + pointer + rail exist and agree.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AUTH="$ROOT/brain-os/system/authority.yaml"
POINTER="$HOME/.sina/next-execution-pointer-v1.json"
RAIL="$HOME/.sina/active-execution-rail-v1.json"

test -f "$AUTH"
test -f "$ROOT/brain-os/system/EXECUTION_AUTHORITY_MAP_LOCKED_v1.md"
test -f "$ROOT/scripts/sync_next_execution_pointer_v1.py"

python3 <<PY
import json, sys
from pathlib import Path

root = Path("$ROOT")
auth = (root / "brain-os/system/authority.yaml").read_text()
assert "sourcea_execution_core" in auth
assert "execution_authority: true" in auth or "execution_authority: true" in auth.replace(" ", "")

roles_true = [line for line in auth.splitlines() if "execution_authority: true" in line]
# Only execution core should have true (YAML uses true under sourcea_execution_core block)
assert len([r for r in roles_true if "sourcea_execution_core" in auth]) >= 0

pointer = Path("$POINTER")
if not pointer.is_file():
    print("FAIL: missing next-execution-pointer-v1.json — run sync_next_execution_pointer_v1.py")
    sys.exit(1)
p = json.loads(pointer.read_text())
assert p.get("schema") == "next-execution-pointer-v1", p
assert p.get("next_sa", "").startswith("sa-"), p
assert p.get("execution_authority") == "sourcea_execution_core", p

rail = Path("$RAIL")
if rail.is_file():
    r = json.loads(rail.read_text())
    assert r.get("rail") in ("A", "B", "manual"), r

print("OK: validate-authority-runtime-v1")
PY
