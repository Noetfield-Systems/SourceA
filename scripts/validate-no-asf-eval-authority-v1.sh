#!/usr/bin/env bash
# Reject ASF/founder as eval or progress verify authority in scoreboard + progress scripts.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export ROOT

python3 - <<'PY'
import os
import re
import sys
from pathlib import Path

root = Path(os.environ["ROOT"])
targets = [
    root / "scripts/agent_scoreboard.py",
    root / "scripts/update-program-progress.py",
    root / "scripts/update-program-progress.sh",
]

# Forbidden: ASF/founder as eval or progress verify authority (not doc path constants)
forbidden = [
    re.compile(r"ASF\s+verif", re.I),
    re.compile(r"founder\s+verif", re.I),
    re.compile(r"ASF.*eval.*authority", re.I),
    re.compile(r"eval.*authority.*ASF", re.I),
    re.compile(r"manual\s+verify.*progress", re.I),
    re.compile(r"progress.*ASF.*confirm", re.I),
    re.compile(r"verified_by.*[\"']ASF", re.I),
    re.compile(r"ASF\s+confirm", re.I),
    re.compile(r"tagline.*ASF\s+verif", re.I),
]

# Allowlisted lines (doc filenames / maintainer override — not founder eval law)
allow_substrings = [
    "ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md",
    "ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md",
    'verified_by": "force_override"',
    "no_asf_eval_authority",
    "No ASF eval/progress authority",
    "not ASF verify",
]

errors: list[str] = []
for path in targets:
    if not path.is_file():
        errors.append(f"missing {path.relative_to(root)}")
        continue
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if any(a in line for a in allow_substrings):
            continue
        for pat in forbidden:
            if pat.search(line):
                errors.append(f"{path.relative_to(root)}:{i}: forbidden ASF/founder eval authority — {line.strip()[:80]}")

scoreboard = root / "scripts/agent_scoreboard.py"
sb_text = scoreboard.read_text(encoding="utf-8") if scoreboard.is_file() else ""
if "no_asf_eval_authority" not in sb_text:
    errors.append("agent_scoreboard.py: missing no_asf_eval_authority payload flag")
if 'verified_by": "manual"' in sb_text:
    errors.append('agent_scoreboard.py: verified_by must not be "manual" (use force_override)')
if "auto_pass" not in sb_text:
    errors.append("agent_scoreboard.py: auto_pass machine path required")

progress = root / "scripts/update-program-progress.py"
if progress.is_file() and "No ASF eval/progress authority" not in progress.read_text(encoding="utf-8"):
    errors.append("update-program-progress.py: missing no-ASF authority docstring")

if errors:
    for e in errors:
        print(f"FAIL: {e}")
    sys.exit(1)
print("OK: validate-no-asf-eval-authority-v1 · scoreboard/progress scripts reject ASF eval authority")
PY
