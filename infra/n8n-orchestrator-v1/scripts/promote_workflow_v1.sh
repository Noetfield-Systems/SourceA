#!/usr/bin/env bash
# Export workflow JSON into Git path and print promotion steps (never direct Production activate).
set -euo pipefail
WF="${1:?usage: promote_workflow_v1.sh path/to/workflow.json}"
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DEST_DIR="$ROOT/n8n/workflows"
mkdir -p "$DEST_DIR"
BASE="$(basename "$WF")"
cp "$WF" "$DEST_DIR/$BASE"
echo "Copied to $DEST_DIR/$BASE"
echo "Next: open GitHub PR → CI lint + golden replay → merge → import into Production n8n → set Supabase ACTIVE pointer"
echo "Forbidden: Save to Production from editor without PR"
