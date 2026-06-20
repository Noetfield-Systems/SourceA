#!/usr/bin/env bash
# validate-bowl-duties-fresh-v1.sh — forbid stale AUTO-RUN / RunReceipt strings (AS-11)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BOWL="$ROOT/sina-bowl/state.json"

fail() { echo "FAIL: validate-bowl-duties-fresh-v1 — $*" >&2; exit 1; }

[[ -f "$BOWL" ]] || fail "missing sina-bowl/state.json"

python3 <<'PY'
import json
import sys
from pathlib import Path

b = json.loads(Path("sina-bowl/state.json").read_text(encoding="utf-8"))
text = " ".join(b.get("asf_duties") or []).lower()
for bad in ("confirm p0: runreceipt", "start auto run", "goal 1 auto-run", "▶ start"):
    if bad in text:
        print(f"FAIL: stale duty string: {bad!r}")
        sys.exit(1)
print("OK: validate-bowl-duties-fresh-v1")
PY
