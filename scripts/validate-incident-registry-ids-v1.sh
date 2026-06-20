#!/usr/bin/env bash
# validate-incident-registry-ids-v1.sh — unique incident IDs in registry (AS-16)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REG="$ROOT/brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md"

fail() { echo "FAIL: validate-incident-registry-ids-v1 — $*" >&2; exit 1; }

[[ -f "$REG" ]] || fail "missing AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md"
cd "$ROOT"

python3 <<'PY'
import re
import sys
from collections import Counter
from pathlib import Path

text = Path("brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md").read_text(encoding="utf-8")
ids = re.findall(r"\|\s*\*\*(\d{3})\*\*\s*\|", text)
counts = Counter(ids)
dups = [i for i, c in counts.items() if c > 1]
if dups:
    print(f"FAIL: duplicate incident IDs: {dups}")
    sys.exit(1)
for required in ("022", "023"):
    if required not in ids:
        print(f"FAIL: INCIDENT-{required} missing from registry")
        sys.exit(1)
print("OK: validate-incident-registry-ids-v1")
PY
