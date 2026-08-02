#!/usr/bin/env bash
# validate-outbound-forbidden-sources-v1.sh — no Proxycurl / self-score theater in runtime
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/validate_outbound_forbidden_sources_v1.py --json >/dev/null
echo "PASS: validate-outbound-forbidden-sources-v1"
