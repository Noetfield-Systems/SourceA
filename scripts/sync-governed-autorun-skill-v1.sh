#!/usr/bin/env bash
# sync-governed-autorun-skill-v1.sh — install governed-autorun v3 to ~/.cursor/skills
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/.cursor/skills/governed-autorun"
DEST="${HOME}/.cursor/skills/governed-autorun"

[[ -f "$SRC/SKILL.md" ]] || { echo "FAIL: missing $SRC/SKILL.md" >&2; exit 1; }

mkdir -p "$DEST/references"
cp "$SRC/SKILL.md" "$DEST/SKILL.md"
cp -R "$SRC/references/." "$DEST/references/"

echo "OK: sync-governed-autorun-skill-v1 → $DEST (v3)"
