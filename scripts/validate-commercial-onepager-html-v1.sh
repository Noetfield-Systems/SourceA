#!/usr/bin/env bash
# validate-commercial-onepager-html-v1.sh — professional outbound HTML surfaces
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 scripts/generate_commercial_onepager_html_v1.py all --json >/tmp/commercial-html-gen.json

python3 - <<'PY'
import json
import sys
from pathlib import Path

gen = json.loads(Path("/tmp/commercial-html-gen.json").read_text())
if not gen.get("ok"):
    print("FAIL: generator returned not ok")
    sys.exit(1)

checks = [
    ("noetfield", "operations@noetfield.com", "NF-RD", "tamper-FAIL"),
    ("ab1", "hello@sourcea.app", "Agent Loop Build", "policy at dispatch"),
]

for key, *needles in checks:
    path = Path(gen["paths"][key])
    if not path.is_file():
        print(f"FAIL: missing {path}")
        sys.exit(1)
    text = path.read_text(encoding="utf-8")
    for n in needles:
        if n not in text:
            print(f"FAIL: {path.name} missing {n!r}")
            sys.exit(1)
    print(f"PASS: {path}")

print("validate-commercial-onepager-html-v1.sh: ALL PASS")
PY
