#!/usr/bin/env bash
# Read-only inventory of root-level markdown/text/log files.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/infra/cleanup/inventory-root.tsv"

cd "$ROOT"
mkdir -p "$(dirname "$OUT")"

{
  printf "path\tsize\tfirst_line\n"
  find . -maxdepth 1 -type f \( -name '*.md' -o -name '*.txt' -o -name '*.log' \) \
    | sort \
    | while IFS= read -r f; do
        size="$(du -h "$f" | cut -f1)"
        first="$(head -1 "$f" | tr '\t' ' ' | cut -c1-70)"
        printf "%s\t%s\t%s\n" "$f" "$size" "$first"
      done
} > "$OUT"

count="$(($(wc -l < "$OUT") - 1))"
echo "Wrote $OUT ($count files)"
