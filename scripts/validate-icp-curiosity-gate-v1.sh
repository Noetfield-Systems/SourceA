#!/usr/bin/env bash
# validate-icp-curiosity-gate-v1.sh — U028 curiosity before link block
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"

python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path("scripts")))
from icp_curiosity_gate_v1 import check_curiosity_before_link

for name in ("fundmore-approved-v1.txt", "ocree-approved-v1.txt", "sourcea-factory-approved-v1.txt"):
    body = (Path("data/icp-compile") / name).read_text(encoding="utf-8")
    row = check_curiosity_before_link(body)
    if not row.get("ok"):
        raise SystemExit(f"FAIL {name}: {row.get('issues')}")
    print(f"OK: {name}")

print("PASS: validate-icp-curiosity-gate-v1")
PY
