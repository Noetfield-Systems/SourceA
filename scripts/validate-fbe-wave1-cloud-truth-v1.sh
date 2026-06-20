#!/usr/bin/env bash
# Wave 1 cloud truth — unified FBE probe + config + Mac Law flag alignment
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export SOURCEA_ROOT="$ROOT"

python3 -c "
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ['SOURCEA_ROOT'])
sys.path.insert(0, str(ROOT / 'scripts'))
from fbe.lib.public_worker_url_v1 import fbe_health_ok, resolve_public_fbe_url

cfg = json.loads((ROOT / 'data/fbe_cloud_worker_config_v1.json').read_text())
url, src = resolve_public_fbe_url()
fail = []

if not url or not fbe_health_ok(url):
    fail.append(f'public_fbe_url missing/unhealthy src={src}')
if str(cfg.get('worker_url') or '').startswith('http://127.'):
    fail.append('config worker_url still local')
if not str(cfg.get('worker_url') or '').startswith('https://'):
    fail.append('config worker_url not https')

mac = json.loads((ROOT / 'data/mac-law-mandatory-v1.json').read_text())
present = mac.get('mandatory_flags', {}).get('present') or []
absent = mac.get('mandatory_flags', {}).get('absent') or []
if '~/.sina/auto-run-disabled-v1.flag' in absent:
    fail.append('mac-law auto-run-disabled still in absent[]')
if '~/.sina/auto-run-disabled-v1.flag' not in present:
    fail.append('mac-law auto-run-disabled missing from present[]')

if fail:
    print('FAIL validate-fbe-wave1-cloud-truth-v1')
    for f in fail:
        print(' -', f)
    sys.exit(1)

print(f'PASS validate-fbe-wave1-cloud-truth-v1 · {url} · src={src}')
"

python3 scripts/cloud_factories_online_only_v1.py --json >/dev/null
python3 scripts/commercial_email_send_defer_v1.py --json >/dev/null
echo "PASS: cloud assessors synced"
