#!/usr/bin/env bash
# RunReceipt CLI — pack DevBridge evidence → jsonl + summary + HTML + zip
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
exec python3 "$ROOT/scripts/runreceipt/pack_v1.py" "$@"
