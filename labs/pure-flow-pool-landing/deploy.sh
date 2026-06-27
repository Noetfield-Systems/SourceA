#!/usr/bin/env bash
# Full e2e deploy — Pages + Functions + KV + email + custom domain
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 scripts/publish_pureflow_landing_v1.py
