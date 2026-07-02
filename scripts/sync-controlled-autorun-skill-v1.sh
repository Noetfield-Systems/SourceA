#!/usr/bin/env bash
# sync-controlled-autorun-skill-v1.sh — install controlled-autorun v3 to ~/.cursor/skills
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/.cursor/skills/controlled-autorun"
DEST="${HOME}/.cursor/skills/controlled-autorun"

[[ -f "$SRC/SKILL.md" ]] || { echo "FAIL: missing $SRC/SKILL.md" >&2; exit 1; }

mkdir -p "$DEST/references"
cp "$SRC/SKILL.md" "$DEST/SKILL.md"
cp -R "$SRC/references/." "$DEST/references/"

echo "OK: sync-controlled-autorun-skill-v1 → $DEST (v3)"
