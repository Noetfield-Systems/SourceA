#!/usr/bin/env bash
# Founder docs — no ```bash blocks in ASF-facing cards (SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

export ROOT
python3 - <<'PY'
import os
import re
import sys
from pathlib import Path

root = Path(os.environ["ROOT"])
# ASF-facing founder docs — must be hub-tap instructions only
asf_facing = [
    root / "founder/ASF_DAILY_CARD.md",
    root / "founder/ASF_FOUNDER_FAQ.md",
    root / "founder/ASF_WIRE_AND_PHONE.md",
    root / "founder/ASF_SECRETS_AND_INFRA.md",
]
fence_re = re.compile(r"```(?:bash|sh|zsh|shell)\b", re.IGNORECASE)
errors: list[str] = []
for path in asf_facing:
    if not path.is_file():
        errors.append(f"missing {path.relative_to(root)}")
        continue
    text = path.read_text(encoding="utf-8")
    if fence_re.search(text):
        errors.append(f"{path.relative_to(root)}: forbidden shell code fence for ASF")
    # Inline founder-facing one-liners (not in maintainer-only sections)
    body = text.split("## Maintainer", 1)[0].split("### Maintainer", 1)[0]
    if re.search(r"(?m)^\s*(cd |bash |python3 |curl -s)", body):
        errors.append(f"{path.relative_to(root)}: ASF section has shell one-liner")

if errors:
    for e in errors:
        print(f"FAIL: {e}")
    sys.exit(1)
print("OK: validate-founder-docs-no-terminal-v1 · ASF-facing docs hub-only")
PY
