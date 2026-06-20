#!/usr/bin/env bash
# sa-0309 — governance-fleet nudges + verify_gap SSOT wired in strict build
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

bash validate-governance-fleet-v1.sh

python3 - <<'PY'
from pathlib import Path

build = Path("build-sina-command-panel.py").read_text(encoding="utf-8")
assert "validate-governance-fleet-v1.sh" in build, "governance-fleet must be in strict build"
print("OK: validate-governance-fleet-nudges-ssot-v1 · nudges + verify_gap SSOT (sa-0309)")
PY
