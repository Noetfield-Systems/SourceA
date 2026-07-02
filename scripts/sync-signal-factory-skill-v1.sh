#!/usr/bin/env bash
# sync-signal-factory-skill-v1.sh — install project skill to ~/.cursor/skills/signal-factory
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/.cursor/skills/signal-factory"
DEST="${HOME}/.cursor/skills/signal-factory"

[[ -f "$SRC/SKILL.md" ]] || { echo "FAIL: missing $SRC/SKILL.md" >&2; exit 1; }

mkdir -p "$DEST/tests" "$DEST/reports"
cp "$SRC/SKILL.md" "$DEST/SKILL.md"
cp -R "$SRC/tests/." "$DEST/tests/"
if [[ -f "$SRC/reports/test-report-v1.json" ]]; then
  cp "$SRC/reports/test-report-v1.json" "$DEST/reports/test-report-v1.json"
fi

echo "OK: sync-signal-factory-skill-v1 → $DEST"
