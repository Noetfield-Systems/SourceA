#!/usr/bin/env bash
# Execute approved cleanup-manifest.md rows for one batch.
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

if ! grep -qE '^\*\*Status:\*\* APPROVED' "$MANIFEST" && ! grep -qE '^# Cleanup manifest.*APPROVED' "$MANIFEST"; then
  if ! grep -q 'Status: APPROVED' "$MANIFEST" && ! grep -q '\*\*APPROVED\*\*' "$MANIFEST"; then
    echo "Manifest not APPROVED — edit infra/cleanup/cleanup-manifest.md line 3 first" >&2
    exit 1
  fi
fi

mkdir -p "$ROOT/archive/root-stubs"
mkdir -p "$ROOT/brain-os/law" "$ROOT/brain-os/law/entry" "$ROOT/brain-os/law/enforcement" "$ROOT/brain-os/system" "$ROOT/brain-os/incidents"

# Pure Python executor — avoids xargs/sandbox failures on Mac (INCIDENT cleanup execute)
PY="$ROOT/infra/cleanup/execute_batch_python_v1.py"
if [[ -f "$PY" ]]; then
  args=(python3 "$PY" --batch "$BATCH")
  [[ "$DRY_RUN" -eq 1 ]] && args+=(--dry-run)
  exec "${args[@]}"
fi

# Pure Python executor — avoids xargs/sandbox failures on Mac (INCIDENT cleanup execute)
PY="$ROOT/infra/cleanup/execute_batch_python_v1.py"
if [[ -f "$PY" ]]; then
  args=(python3 "$PY" --batch "$BATCH")
  [[ "$DRY_RUN" -eq 1 ]] && args+=(--dry-run)
  exec "${args[@]}"
fi

# Pure Python executor — avoids xargs/sandbox failures on Mac (INCIDENT cleanup execute)
PY="$ROOT/infra/cleanup/execute_batch_python_v1.py"
if [[ -f "$PY" ]]; then
  args=(python3 "$PY" --batch "$BATCH")
  [[ "$DRY_RUN" -eq 1 ]] && args+=(--dry-run)
  exec "${args[@]}"
fi

moved=0
skipped=0

while IFS='|' read -r _col1 src _size _heading dest batch action _rest; do
  src="$(echo "$src" | xargs | sed 's/`//g')"
  dest="$(echo "$dest" | xargs | sed 's/`//g')"
  batch="$(echo "$batch" | xargs)"
  action="$(echo "$action" | xargs)"

  [[ "$src" == "source" || -z "$src" || "$src" == _* ]] && continue
  [[ "$batch" != "$BATCH" ]] && continue
  [[ "$action" != "move" && "$action" != "archive" ]] && continue

  src_path="$ROOT/${src#./}"
  base="$(basename "$src_path")"

  if [[ ! -f "$src_path" ]]; then
    echo "SKIP missing: $src"
    skipped=$((skipped + 1))
    continue
  fi

  if [[ "$action" == "archive" ]]; then
    target_dir="$ROOT/archive/root-stubs"
  else
    target_dir="$ROOT/$dest"
  fi

  mkdir -p "$target_dir"
  target="$target_dir/$base"

  if [[ -f "$target" ]]; then
    echo "SKIP exists: $target (source: $src)"
    skipped=$((skipped + 1))
    continue
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "DRY-RUN $action: $src_path -> $target"
  else
    mv "$src_path" "$target"
    echo "OK $action: $src -> $target"
  fi
  moved=$((moved + 1))
done < "$MANIFEST"

echo "Batch $BATCH done: moved/archived=$moved skipped=$skipped dry_run=$DRY_RUN"
