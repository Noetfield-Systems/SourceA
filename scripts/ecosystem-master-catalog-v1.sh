#!/usr/bin/env bash
# ecosystem-master-catalog-v1.sh — run from any cwd
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
exec python3 scripts/ecosystem_master_catalog_v1.py "$@"
