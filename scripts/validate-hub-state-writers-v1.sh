#!/usr/bin/env bash
# Track 2 L5 — audit known queue-truth writers (informational until N2).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 - <<'PY'
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
target = "run-inbox-disk-truth-v1.json"
writers = []
for path in (root / "scripts").rglob("*.py"):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    if target not in text:
        continue
    if ".write_text(" in text or 'open(' in text and '"w"' in text or "'.write(" in text:
        if "read_text" in text and text.count("write") <= text.count("read_text"):
            continue
    if "write" in text.lower() and target in text:
        writers.append(str(path.relative_to(root)))

# Known pre-N2 writers — gate passes with documented count until State service owns writes
known_ok = len(writers) <= 25
print(f"queue_truth_references: {len(writers)} files with write-ish patterns")
if not known_ok:
    print("FAIL: excessive queue-truth writer candidates", flush=True)
    for w in writers[:15]:
        print(f"  {w}")
    raise SystemExit(1)
print("OK: validate-hub-state-writers-v1 · pre-N2 writer audit within threshold")
PY

echo "OK: validate-hub-state-writers-v1"
