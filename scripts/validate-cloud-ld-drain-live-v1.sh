#!/usr/bin/env bash
# validate-cloud-ld-drain-live-v1.sh — one live cloud fetch (CI only · network)
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ "${CLOUD_LD_LIVE:-}" == "0" ]]; then
  echo "SKIP: CLOUD_LD_LIVE=0 — live LD fetch disabled"
  exit 0
fi

python3 scripts/cloud_worker_dispatch_v1.py --plan-id CLOUD-LD-001 --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('ok') is True, r
assert r.get('plan_id')=='CLOUD-LD-001', r
assert int(r.get('http_status') or 0)==200, r
assert 'launchdarkly.com' in str(r.get('source_url') or ''), r
snippets = r.get('evidence_snippets') or []
assert len(snippets) >= 3, r
print('OK: CLOUD-LD-001 live fetch', len(snippets), 'snippets')
"

echo "PASS: validate-cloud-ld-drain-live-v1"
