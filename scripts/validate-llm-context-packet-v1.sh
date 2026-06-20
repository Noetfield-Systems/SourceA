#!/usr/bin/env bash
# D15 assembled packet — alias for LAW/roadmap references (sa-0627).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec bash "$ROOT/scripts/validate-context-assembly-v1.sh"
