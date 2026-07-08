#!/usr/bin/env bash
# lint-cursor-rules-format-v1.sh — rule format lint (Step 7)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0
RULES_DIR=".cursor/rules"

for f in "$RULES_DIR"/*.mdc; do
  base=$(basename "$f")
  # Frontmatter: description + alwaysApply
  if ! head -5 "$f" | grep -q '^description:'; then
    echo "FAIL: $base missing description in frontmatter"
    FAIL=1
  fi
  if ! head -10 "$f" | grep -q 'alwaysApply:'; then
    echo "FAIL: $base missing alwaysApply in frontmatter"
    FAIL=1
  fi
  # Body: Law section (allow **Law:** variant)
  if ! grep -qE '^(\*\*Law:\*\*|# Law|Law:)' "$f" 2>/dev/null; then
    echo "WARN: $base missing Law section"
  fi
done

# Orphan path check: sample Law paths in always-apply rules
for f in "$RULES_DIR"/000-*.mdc "$RULES_DIR"/mac-control-plane.mdc; do
  [[ -f "$f" ]] || continue
  while IFS= read -r path; do
    [[ -z "$path" ]] && continue
    # strip backticks and trailing punctuation
    path=$(echo "$path" | sed 's/`//g' | sed 's/ ·.*//' | sed 's/ (.*//')
    if [[ "$path" == *"*"* ]]; then
      continue
    fi
    if [[ "$path" == brain-os/* || "$path" == docs/* || "$path" == data/* ]]; then
      if [[ ! -e "$path" ]]; then
        echo "WARN: $f references missing path $path"
      fi
    fi
  done < <(grep -oE '(brain-os|docs|data)/[^` ·]+' "$f" 2>/dev/null || true)
done

echo "lint complete (failures: $FAIL)"
exit "$FAIL"
