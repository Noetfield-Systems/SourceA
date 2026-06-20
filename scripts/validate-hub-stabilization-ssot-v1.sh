#!/usr/bin/env bash
# SSOT gate — HUB_STABILIZATION_v5.1_FINAL.md must not claim embedded worker on :13020 (Phase P7).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOC="$ROOT/HUB_STABILIZATION_v5.1_FINAL.md"

python3 - "$DOC" <<'PY'
import sys
from pathlib import Path

doc = Path(sys.argv[1])
lines = doc.read_text(encoding="utf-8").splitlines()

FORBIDDEN = (
    "daemon thread on :13020",
    "daemon thread inside the :13020",
    "daemon thread inside `:13020`",
    "server boot hook",
    "ports_unchanged",
)

in_superseded = False
violations: list[str] = []

for i, line in enumerate(lines, start=1):
    stripped = line.strip()
    if stripped.startswith("### C3 — SUPERSEDED"):
        in_superseded = True
        continue
    if in_superseded and stripped.startswith("### "):
        in_superseded = False

    if in_superseded:
        continue
    if stripped.startswith(">") or "HISTORICAL" in line or "SUPERSEDED" in line:
        continue

    for phrase in FORBIDDEN:
        if phrase in line:
            violations.append(f"line {i}: {phrase!r}")

if violations:
    print("FAIL: stale hub stabilization SSOT phrases in active sections:")
    for v in violations:
        print(f"  {v}")
    sys.exit(1)

print("OK: validate-hub-stabilization-ssot-v1 · no embedded-worker claims in active law")
PY
