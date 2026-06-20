#!/usr/bin/env bash
# Registry remediated rows must have REMEDIATED in body footer (no OPEN contradiction).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 <<'PY'
import re
import sys
from pathlib import Path

reg = Path("brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md").read_text(encoding="utf-8")
inc_dir = Path("brain-os/incidents")
errors = []
seen: set[str] = set()
for m in re.finditer(r"\|\s*\*\*(\d{3})\*\*[^\n]*\*\*remediated\*\*", reg, re.I):
    iid = m.group(1)
    if iid in seen:
        continue
    seen.add(iid)
    if iid == "017":
        continue  # partial — registry says canonical partial
    bodies = sorted({p for p in inc_dir.glob("*.md") if f"INCIDENT_{iid}" in p.name or f"INCIDENT-{iid}" in p.name or f"_{iid}_" in p.name})
    if not bodies:
        continue
    for body in bodies:
        text = body.read_text(encoding="utf-8", errors="replace")
        if re.search(r"\*\*Status:\*\*\s*OPEN", text, re.I):
            errors.append(f"{iid} registry remediated but {body.name} Status OPEN")
        elif not re.search(r"REMEDIATED|remediated", text):
            errors.append(f"{iid} body {body.name} missing REMEDIATED marker")

if errors:
    for e in errors:
        print(f"FAIL: {e}")
    sys.exit(1)
print("OK: validate-incident-body-status-v1")
PY
