#!/usr/bin/env bash
# validate-no-archive-as-law-v1.sh — authority index must not point only to archive (AS-15)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INDEX="$ROOT/SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md"

fail() { echo "FAIL: validate-no-archive-as-law-v1 — $*" >&2; exit 1; }

[[ -f "$INDEX" ]] || fail "missing authority index"
cd "$ROOT"

python3 <<'PY'
import re
import sys
from pathlib import Path

index = Path("SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md").read_text(encoding="utf-8")
bad = []
for line in index.splitlines():
    if not line.startswith("| `"):
        continue
    cols = [c.strip() for c in line.split("|")]
    if len(cols) < 3:
        continue
    canonical = cols[2]
    if "archive/attachments/" in canonical and not canonical.endswith("_LOCKED_v1.md"):
        if "never canonical" not in canonical.lower() and "examples" not in canonical.lower():
            bad.append(line.strip()[:120])
    elif canonical.startswith("`archive/"):
        bad.append(line.strip()[:120])

if bad:
    print("FAIL: archive-only law rows (sample):")
    for b in bad[:10]:
        print(f"  {b}")
    sys.exit(1)

print("OK: validate-no-archive-as-law-v1")
PY
