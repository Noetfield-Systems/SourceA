#!/usr/bin/env bash
# Print next ENFORCEMENT-6MO plan for Worker chat (PLAN WITH NO ASF ENFORCEMENT)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/pick-enforcement-no-asf-plan.py --any-tier --limit 1 --prompt
