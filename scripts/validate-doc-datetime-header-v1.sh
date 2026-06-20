#!/usr/bin/env bash
# validate-doc-datetime-header-v1.sh — doc Saved header must include exact UTC time
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/scripts/validate_doc_datetime_header_v1.py"
if [[ $# -gt 0 ]]; then
  python3 "$PY" "$@"
else
  python3 "$PY" --json
fi
