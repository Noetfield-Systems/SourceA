#!/usr/bin/env bash
# sa-0127 — validate-eval-packet-v1b-live wired in strict build default chain.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export ROOT

python3 - <<'PY'
import re
import sys
from pathlib import Path

path = Path(__import__("os").environ["ROOT"]) / "scripts/build-sina-command-panel.py"
text = path.read_text(encoding="utf-8")

if "sa-0127" not in text:
    print("FAIL: sa-0127 marker missing in build-sina-command-panel.py")
    sys.exit(1)

if 'validate-eval-packet-v1b-live.sh' not in text:
    print("FAIL: validate-eval-packet-v1b-live.sh not referenced in build")
    sys.exit(1)

# strict chain order: grounding → live → capture
g = text.find("validate-eval-packet-v1b-grounding.sh")
l = text.find("validate-eval-packet-v1b-live.sh")
c = text.find("validate-eval-report-capture-v1.sh")
f = text.find("validate-governance-fleet-v1.sh")
for name, pos in (
    ("grounding", g),
    ("live", l),
    ("capture", c),
    ("governance-fleet", f),
):
    if pos < 0:
        print(f"FAIL: {name} step missing from build chain")
        sys.exit(1)

if not (g < l < c < f):
    print(f"FAIL: strict eval chain order bad g={g} l={l} c={c} f={f}")
    sys.exit(1)

# must run live only inside strict block
strict_block = re.search(r"if strict:\s*\n\s*code = _run_audit\(\"validate-eval-packet-v1b-grounding", text)
if not strict_block:
    print("FAIL: eval-1b live must run under if strict:")
    sys.exit(1)

print("OK: validate-eval-packet-v1b-strict-build-chain-v1 · live in strict default chain (sa-0127)")
PY
