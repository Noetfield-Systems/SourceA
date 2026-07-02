#!/usr/bin/env bash
# write-cursor-skills-index-v1.py — emit data/sourcea-cursor-skills-index-v1.json
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/scripts/sourcea-python-v1.sh"
[[ -x "$PY" ]] || PY="/usr/bin/python3"
exec "$PY" "$ROOT/scripts/write_cursor_skills_index_v1.py"
