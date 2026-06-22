#!/usr/bin/env bash
# validate-cursor-alwaysapply-cap-v1.sh — eight alwaysApply rules only
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/validate_cursor_alwaysapply_cap_v1.py"
