#!/usr/bin/env bash
# One-tap Remotion artifact factory — sample reel or pipeline row
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 "$ROOT/scripts/remotion_artifact_factory_v1.py" "$@"
