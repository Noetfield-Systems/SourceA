#!/usr/bin/env bash
# validate-governance-events-taxonomy-v1.sh — §7.6 last-500 rows resolvable kind
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-governance-events-taxonomy-v1 — $*" >&2; exit 1; }

python3 - <<'PY' || fail "taxonomy check"
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("scripts").resolve()))
from governance_event_kind_v1 import normalize_kind

path = Path.home() / ".sina" / "agent-governance-events.jsonl"
if not path.is_file():
    print("OK: validate-governance-events-taxonomy-v1 · no events file yet")
    raise SystemExit(0)

rows = []
for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        rows.append(json.loads(line))
    except json.JSONDecodeError:
        continue

sample = rows[-500:]
bad = []
skipped = 0
for i, row in enumerate(sample):
    raw = str(row.get("kind") or row.get("event") or "").strip()
    if not raw:
        skipped += 1
        continue
    if not normalize_kind(row):
        bad.append((len(rows) - len(sample) + i + 1, raw))

if bad:
    print("FAIL: unresolvable kinds in last 500 rows:")
    for ln, k in bad[:15]:
        print(f"  line~{ln}: {k!r}")
    raise SystemExit(1)

print(
    f"OK: validate-governance-events-taxonomy-v1 · "
    f"last {len(sample)} rows · skipped_blank={skipped} · orphans=0"
)
PY
