#!/usr/bin/env bash
# Execute approved cleanup-manifest.md moves for one batch.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MANIFEST="$ROOT/infra/cleanup/cleanup-manifest.md"
DRY_RUN=0
BATCH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --batch) BATCH="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) echo "Unknown: $1" >&2; exit 1 ;;
  esac
done

[[ -n "$BATCH" ]] || { echo "Usage: $0 --batch N [--dry-run]" >&2; exit 1; }

if ! grep -q 'Status:.*APPROVED' "$MANIFEST" 2>/dev/null && ! grep -q '\*\*APPROVED\*\*' "$MANIFEST" 2>/dev/null; then
  echo "Manifest not APPROVED — edit infra/cleanup/cleanup-manifest.md first" >&2
  exit 1
fi

# Parse markdown table rows: | ./file | size | ... | batch | move |
moved=0
while IFS='|' read -r _ src _ _ _ batch action _; do
  src="$(echo "$src" | xargs)"
  batch="$(echo "$batch" | xargs)"
  action="$(echo "$action" | xargs)"
  [[ "$src" == source ]] && continue
  [[ -z "$src" || "$src" == _* ]] && continue
  [[ "$batch" != "$BATCH" ]] && continue
  [[ "$action" != "move" && "$action" != "archive" ]] && continue

  # dest is column 5 (proposed_dest)
done < "$MANIFEST"

echo "Batch executor stub — populate manifest rows first."
echo "For safety, use explicit rows in manifest then extend this script or move manually per batch."
echo "Dry-run=$DRY_RUN batch=$BATCH"
