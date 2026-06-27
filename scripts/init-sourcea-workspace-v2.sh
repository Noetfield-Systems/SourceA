#!/usr/bin/env bash
# Bootstrap .sourcea/ workspace kernel on any project folder.
# Usage: init-sourcea-workspace-v2.sh <project_path> [name] [profile]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:?Usage: init-sourcea-workspace-v2.sh <project_path> [name] [profile]}"
NAME="${2:-$(basename "$TARGET")}"
PROFILE="${3:-startup}"

python3 "$ROOT/scripts/workspace_kernel_v2.py" init \
  --path "$TARGET" \
  --name "$NAME" \
  --profile "$PROFILE"

echo ""
echo "Workspace kernel ready:"
echo "  $TARGET/.sourcea/"
echo ""
echo "Verify:"
echo "  python3 $ROOT/scripts/workspace_kernel_v2.py status --path \"$TARGET\""
