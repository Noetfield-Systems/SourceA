#!/usr/bin/env bash
# validate-cloud-ld-drain-v1.sh — thin wrapper → archive (disk-only) validator
set -euo pipefail
cd "$(dirname "$0")/.."
exec bash scripts/validate-cloud-ld-drain-archive-v1.sh
