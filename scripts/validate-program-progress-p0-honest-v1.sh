#!/usr/bin/env bash
# sa-0508 — PROGRAM_PROGRESS parallel_plans P0 honest
set -euo pipefail
cd "$(dirname "$0")"
bash validate-program-progress-factory-divergence-v1.sh
bash validate-no-fake-progress-form-v1.sh
echo "OK: validate-program-progress-p0-honest-v1 · sa-0508"
