#!/usr/bin/env bash
# Permanent poison-free check — scan only (<=60s). NOT a validator marathon.
set -euo pipefail
ROOT="${SOURCEA_ROOT:-$HOME/Desktop/SourceA}"
cd "$ROOT"
python3 scripts/agent_mirror_poison_scrub_v1.py --validate --json
