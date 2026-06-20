#!/usr/bin/env bash
# sa-0042 / sa-0092 / sa-0017 — FEEDBACK_AGGREGATE execution_truth hub_built_at matches command-data
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"
python3 feedback_hub_sync_assert_v1.py --label sa-0042
echo "OK: validate-feedback-aggregate-hub-sync-v1"
